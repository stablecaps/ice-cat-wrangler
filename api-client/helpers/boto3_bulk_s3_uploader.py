"""
boto3_bulk_s3_uploader.py

This module provides the `BulkS3Uploader` class, which handles uploading images to an S3 bucket and logging
metadata for each upload. It supports bulk uploads from a local folder and generates structured metadata
for each uploaded file.

Classes:
    - BulkS3Uploader: A class to manage the upload of images to an S3 bucket and log metadata.

Functions:
    - check_bucket_exists: Verifies if the specified S3 bucket exists.
    - calculate_file_hash: Computes a hash for a given file.
    - gen_batch_file_path: Generates a file path for batch logs.
    - write_batch_file: Writes batch metadata to a file.

Usage:
    The `BulkS3Uploader` class can be used to upload all images from a specified folder to an S3 bucket.

    Example:
        from boto3_bulk_s3_uploader import BulkS3Uploader

        uploader = BulkS3Uploader(
            folder_path="path/to/images",
            s3bucket_source="my-s3-bucket",
            client_id="client123",
            debug=True
        )
        uploader.process_files()

Dependencies:
    - Python 3.12 or higher
    - `boto3` for AWS S3 interactions
    - `rich` for enhanced console output
    - Custom helper modules for S3 and file operations
"""

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

    Attributes:
        supported_extensions (tuple): Supported file extensions for upload.
        folder_path (str): Path to the folder containing images to upload.
        s3bucket_source (str): Name of the S3 bucket to upload images to.
        client_id (str): Client ID to include in the S3 key.
        batch_id (str): Unique batch ID for the current upload session.
        batch_file_path (str): Path to the batch log file.
        debug (bool): Whether debug mode is enabled.
    """

    def __init__(self, folder_path, s3bucket_source, client_id, debug=False):
        """
        Initializes the BulkS3Uploader.

        Args:
            folder_path (str): Path to the folder containing images to upload.
            s3bucket_source (str): The name of the S3 bucket.
            client_id (str): The client ID to include in the S3 key.
            debug (bool, optional): If True, enables debug output. Defaults to False.
        """

        self.supported_extensions = (".png", ".jpg", ".jpeg")
        self.folder_path = folder_path

        self.s3bucket_source = s3bucket_source
        check_bucket_exists(s3_client=s3_client, bucket_name=self.s3bucket_source)

        self.client_id = client_id

        self.batch_id = f"batch-{int(time.time())}"

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

        Args:
            file_path (str): Path to the file to upload.
            batch_id (str): The batch ID for the current upload session.

        Returns:
            dict: Metadata for the uploaded file, or None if the upload fails.
        """
        file_name = os.path.basename(file_path)
        file_hash = calculate_file_hash(file_path)
        current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H")
        epoch_timestamp = int(time.time())
        s3_key = self.generate_s3_key(
            file_hash, batch_id, current_date, epoch_timestamp
        )

        try:
            print(f"\nUploading {file_path} to s3://{self.s3bucket_source}/{s3_key}")
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

        Returns:
            None
        """

        print()
        upload_records = []
        for root, _, files in os.walk(self.folder_path):
            for file in files:
                file_path = os.path.join(root, file)

                if not file.lower().endswith(self.supported_extensions):
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

        print("\nAll eligible images have been uploaded successfully.")
        print(f"\nUpload records saved to: {self.batch_file_path}")
