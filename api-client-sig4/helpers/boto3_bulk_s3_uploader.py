import json
import os
import time
from datetime import datetime, timezone

from boto3_helpers import check_bucket_exists, gen_boto3_client
from botocore.exceptions import ClientError
from helpers.general import calculate_file_hash
from rich import print


class BulkS3Uploader:
    """
    A class to handle uploading images to an S3 bucket and logging metadata for each upload.
    """

    def __init__(self, folder_path, s3bucket_source, client_id, debug=False):
        """
        Initializes the BulkS3Uploader.

        Args:
            s3bucket_source (str): The name of the S3 bucket.
            client_id (str): The client ID to include in the S3 key.
            debug (bool, optional): If True, enables debug output. Defaults to False.
        """
        self.folder_path = folder_path

        self.s3bucket_source = s3bucket_source
        check_bucket_exists(bucket_name=self.s3bucket_source)

        self.client_id = client_id
        #
        self.batch_id = f"batch-{int(time.time())}"
        #
        logs_folder = BulkS3Uploader.ensure_logs_folder()
        self.log_file_path = os.path.join(
            logs_folder, f"{self.client_id}_{self.batch_id}.json"
        )
        self.debug = debug
        self.s3_client = gen_boto3_client("s3", "eu-west-1")

    @staticmethod
    def ensure_logs_folder():
        """
        Ensures the logs folder exists in the current working directory.

        Returns:
            str: The path to the logs folder.
        """
        logs_folder = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(logs_folder):
            os.makedirs(logs_folder)
        return logs_folder

    def upload_image(self, file_path, batch_id):
        """
        Processes a single file by uploading it to S3 and generating metadata.

        Args:
            file_path (str): The path to the file to upload.
            batch_id (str): The unique batch ID for the upload session.

        Returns:
            dict: Metadata for the uploaded file, or None if the upload failed.
        """
        file_name = os.path.basename(file_path)

        file_hash = calculate_file_hash(file_path)

        current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H")
        epoch_timestamp = int(time.time())

        s3_key = f"{file_hash}/{self.client_id}/{current_date}/{epoch_timestamp}.png"

        try:
            print(f"Uploading {file_path} to s3://{self.s3bucket_source}/{s3_key}")
            self.s3_client.upload_file(file_path, self.s3bucket_source, s3_key)

            # uploaded file metadata
            return {
                "client_id": self.client_id,
                "batch_id": batch_id,
                "s3bucket_source": self.s3bucket_source,
                "s3_key": s3_key,
                "original_file_name": file_name,
                "upload_time": current_date,
                "file_image_hash": file_hash,
                "epoch_timestamp": epoch_timestamp,
            }
        except ClientError as err:
            print(f"Error uploading {file_path} to S3: {err}")
            return None

    def process_files(self):
        """
        Uploads all images from a local folder to a specified S3 bucket and logs metadata for each upload.

        Args:
            folder_path (str): The path to the local folder containing images.

        Returns:
            None
        """

        upload_records = []
        for root, _, files in os.walk(self.folder_path):
            for file in files:
                file_path = os.path.join(root, file)

                if not file.lower().endswith((".png", ".jpg", ".jpeg")):
                    if self.debug:
                        print(f"Skipping non-image file: {file_path}")
                    continue

                # Process the file and collect metadata
                record = self.upload_image(file_path, self.batch_id)
                if record:
                    upload_records.append(record)

        # Write the upload records to the log file
        with open(self.log_file_path, "w") as log_file:
            json.dump(upload_records, log_file, indent=4)

        print(f"\nAll eligible images have been uploaded successfully.")
        print(f"Upload records saved to: {self.log_file_path}")
