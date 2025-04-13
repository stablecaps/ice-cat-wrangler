import json
import os
import time
from datetime import datetime, timezone

from boto3_helpers import check_bucket_exists
from botocore.exceptions import ClientError
from helpers.boto3_clients import s3_client
from helpers.general import calculate_file_hash, gen_batch_file_path, write_batch_file
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

        self.SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg")
        self.folder_path = folder_path

        self.s3bucket_source = s3bucket_source
        check_bucket_exists(s3_client=s3_client, bucket_name=self.s3bucket_source)

        self.client_id = client_id
        #
        self.batch_id = f"batch-{int(time.time())}"
        #

        self.batch_file_path = gen_batch_file_path(
            client_id=client_id, batch_id=client_id
        )
        self.debug = debug

    def generate_s3_key(self, file_hash, batch_id, current_date, epoch_timestamp):
        """
        Generates the S3 key for the uploaded file.

        Args:
            file_hash (str): The hash of the file.
            batch_id (str): The batch ID.
            current_date (str): The current date.
            epoch_timestamp (int): The epoch timestamp.

        Returns:
            str: The S3 key.
        """
        suffix = "-debug.png" if self.debug else ".jpg"
        return f"{file_hash}/{self.client_id}/{batch_id}/{current_date}/{epoch_timestamp}{suffix}"

    def upload_image(self, file_path, batch_id):
        """
        Processes a single file by uploading it to S3 and generating metadata.
        """
        file_name = os.path.basename(file_path)
        file_hash = calculate_file_hash(file_path)
        current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H")
        epoch_timestamp = int(time.time())
        s3_key = self.generate_s3_key(
            file_hash, batch_id, current_date, epoch_timestamp
        )

        try:
            print(f"Uploading {file_path} to s3://{self.s3bucket_source}/{s3_key}")
            s3_client.upload_file(file_path, self.s3bucket_source, s3_key)
            return {
                "client_id": self.client_id,
                "batch_id": batch_id,
                "s3bucket_source": self.s3bucket_source,
                "s3_key": s3_key,
                "original_file_name": file_name,
                "upload_time": current_date,
                "img_fprint": file_hash,
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

                if not file.lower().endswith(self.SUPPORTED_EXTENSIONS):
                    if self.debug:
                        print(f"Skipping non-image file: {file_path}")
                    continue

                # Process the file and collect metadata
                record = self.upload_image(file_path, self.batch_id)
                if record:
                    upload_records.append(record)

        if len(upload_records) == 0:
            print("No images were found to upload.")
            return

        # Write the upload records to the log file
        write_batch_file(filepath=self.batch_file_path, batch_records=upload_records)

        print(f"\nAll eligible images have been uploaded successfully.")
        print(f"Upload records saved to: {self.batch_file_path}")
