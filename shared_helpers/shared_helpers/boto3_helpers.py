import logging
import os
import sys

import boto3
from botocore.exceptions import ClientError

# from general import safeget

# TODO: check logs propogate into dynamodb
# use without __name__ cos thios module will propogate logs to lambda root logger so we can use LogCollectorHandler
LOG = logging.getLogger()


def gen_boto3_session():
    """
    Creates and returns a Boto3 session using environment variables.

    Returns:
        boto3.Session: A Boto3 session object initialized with AWS credentials
        and region from environment variables.
    """
    return boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        region_name=os.getenv("AWS_REGION"),
    )


def gen_boto3_client(service_name, aws_region="eu-west-1"):
    """
    Creates and returns a Boto3 client for a specified AWS service.

    Args:
        service_name (str): The name of the AWS service (e.g., 's3', 'lambda').
        aws_region (str, optional): The AWS region to use. Defaults to "eu-west-1".

    Returns:
        boto3.Client: A Boto3 client object for the specified service.
    """
    session = gen_boto3_session()
    return session.client(service_name, aws_region)


def safeget(dct, *keys):
    """
    Recover value safely from nested dictionary

    safeget(example_dict, 'key1', 'key2')
    """
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct


################################################################################
# s3 functions
def check_bucket_exists(s3_client, bucket_name):
    """Sanity check whether S3 bucket exists using a Boto3 client."""

    try:
        s3_client.head_bucket(Bucket=bucket_name)
        LOG.info("Verified bucket <%s> exists", bucket_name)
    except ClientError as err:
        error_code = err.response["Error"]["Code"]
        if error_code == "404":
            LOG.info("S3 bucket <%s> does not exist", bucket_name)
        elif error_code == "403":
            LOG.info("Access denied to S3 bucket <%s>", bucket_name)
        else:
            LOG.info("Failed to verify S3 bucket <%s>: <%s>", bucket_name, err)
        sys.exit(1)


def get_filebytes_from_s3(s3_client, bucket_name, s3_key):
    """
    Retrieve a file from an S3 bucket.

    Args:
        bucket_name (str): The name of the S3 bucket.
        s3_key (str): The key of the object in the S3 bucket.

    Returns:
        bytes: The content of the file as bytes.
    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        file_bytes = response["Body"].read()
        return file_bytes
    except ClientError as err:
        LOG.error(
            "ClientError while retrieving file <%s> from bucket <%s>: <%s>",
            s3_key,
            bucket_name,
            err,
        )
        raise
    except Exception as err:
        LOG.error(
            "Unexpected error while retrieving file <%s> from bucket <%s>: <%s>",
            s3_key,
            bucket_name,
            err,
        )
        raise


def copy_s3_object(
    s3_client, source_bucket, dest_bucket, s3_key, acl="bucket-owner-full-control"
):
    """
    Copy an object from one S3 bucket to another.

    Args:
        s3_client (boto3.client): The S3 client instance.
        source_bucket (str): The source S3 bucket name.
        dest_bucket (str): The destination S3 bucket name.
        s3_key (str): The key of the object to copy.
        acl (str): The ACL to apply to the copied object. Default is "bucket-owner-full-control".

    Returns:
        None
    """
    try:
        copy_source = {"Bucket": source_bucket, "Key": s3_key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=dest_bucket,
            Key=s3_key,
            ACL=acl,
        )
        LOG.info(
            "Object <%s> copied from <%s> to %s", s3_key, source_bucket, dest_bucket
        )
    except ClientError as err:
        LOG.error(
            "Error copying object <%s> from <%s> to %s: %s",
            s3_key,
            source_bucket,
            dest_bucket,
            err,
        )
        raise


def move_s3_object_based_on_rekog_response(
    s3_client, rekog_resp, s3bucket_source, s3bucket_dest, s3bucket_fail, s3_key
):
    """
    Handle the Rekognition response and move the image to the appropriate S3 bucket.

    Args:
        rekog_resp (dict): The response from Rekognition.
        s3bucket_source (str): The source S3 bucket name.
        s3bucket_dest (str): The destination S3 bucket name for successful processing.
        s3bucket_fail (str): The destination S3 bucket name for failed processing.
        s3_key (str): The key of the object in the S3 bucket.

    Returns:
        None
    """
    try:
        http_status_code = safeget(rekog_resp, "ResponseMetadata", "HTTPStatusCode")
        if http_status_code == 200:
            # Move to success bucket
            copy_source = {"Bucket": s3bucket_source, "Key": s3_key}
            copy_s3_object(
                s3_client,
                source_bucket=s3bucket_source,
                dest_bucket=s3bucket_dest,
                s3_key=s3_key,
                acl="bucket-owner-full-control",
            )
            LOG.info("Object <%s> copied to success bucket %s", s3_key, s3bucket_dest)

            # Delete from source bucket
            s3_client.delete_object(Bucket=s3bucket_source, Key=s3_key)
            LOG.info(
                "Object <%s> deleted from source bucket %s", s3_key, s3bucket_source
            )
        else:
            # Move to failure bucket
            copy_source = {"Bucket": s3bucket_source, "Key": s3_key}
            copy_s3_object(
                s3_client,
                source_bucket=s3bucket_source,
                dest_bucket=s3bucket_fail,
                s3_key=s3_key,
                acl="bucket-owner-full-control",
            )
            LOG.info("Object <%s> copied to failure bucket %s", s3_key, s3bucket_fail)

            # Delete from source bucket
            s3_client.delete_object(Bucket=s3bucket_source, Key=s3_key)
            LOG.info(
                "Object <%s> deleted from source bucket %s", s3_key, s3bucket_source
            )

    except ClientError as err:
        LOG.error("Error moving object %s: %s", s3_key, err)
        raise
    except Exception as err:
        LOG.error("Unexpected error while handling Rekognition response: %s", err)
        raise


################################################################################
# rekognition functions
def rekog_image_categorise(rekog_client, image_bytes):

    try:
        rekognition_response = rekog_client.detect_labels(
            Image={"Bytes": image_bytes},
            MaxLabels=10,
            MinConfidence=75,
        )

        # Print labels detected
        labels = [label["Name"] for label in rekognition_response["Labels"]]
        LOG.info("Labels detected: <%s>", labels)

        return rekognition_response

    except Exception as err:
        LOG.error("Error processing image from S3: <%s>", err)
        raise


################################################################################
# dynamodb functions


# TODO: but this in seperate helpers file
class DynamoDBHelper:
    def __init__(self, dyndb_client, table_name, required_keys):
        """
        Initialize the DynamoDBHelper class.

        Args:
            table_name (str): The name of the DynamoDB table.
            required_keys (list): A list of required keys that must be present in the item_dict.
        """
        self.dyndb_client = dyndb_client
        self.table_name = table_name
        self.required_keys = required_keys

        # ice-cat-wrangler key types
        self.attribute_types = {
            "img_fprint": "S",
            "batch_id": "N",
            "client_id": "S",
            "s3img_key": "S",
            "file_name": "S",
            "op_status": "S",
            "rek_resp": "M",
            "rek_iscat": "BOOL",
            "logs": "M",
            "current_date": "S",
            "upload_ts": "N",
            "rek_ts": "N",
            "ttl": "N",
        }

    def convert_value_to_dyndb_type(self, key, value):
        """
        Converts a single key-value pair to the correct DynamoDB type.

        Args:
            key (str): The attribute name.
            value: The attribute value.

        Returns:
            dict: A DynamoDB-compatible key-value pair.

        Raises:
            ValueError: If the attribute type is unknown or the value is invalid.
        """
        if key not in self.attribute_types:
            LOG.error("Key: <%s> not found in attribute_types dict", key)
            raise ValueError(f"Key: {key} not found in attribute_types dict")

        attr_type = self.attribute_types[key]

        # Convert the value based on the attribute type
        if attr_type == "S":  # String
            return {"S": str(value)}
        elif attr_type == "N":  # Assume all numbers are integers
            try:
                return {"N": str(int(value))}  # Convert to stringified integer
            except ValueError:
                LOG.error("Invalid number value for key: %s", key)
                raise ValueError(f"Invalid number value for key: {key}")
        elif attr_type == "BOOL":  # Ensure booleans are converted to True/False
            return (
                {"BOOL": value.lower() == "true"}
                if isinstance(value, str)
                else {"BOOL": bool(value)}
            )
        elif attr_type == "M":  # Map (JSON)
            return {"M": value}  # Assume value is already a dictionary
        elif attr_type == "NULL":  # Null
            return {"NULL": True}
        else:
            LOG.error("Unsupported attribute type for key: %s", key)
            raise ValueError(f"Unsupported attribute type for key: {key}")

    def convert_pydict_to_dyndb_item(self, item_dict):
        """
        Converts a Python dictionary to a DynamoDB-compatible item format.

        Args:
            item_dict (dict): The dictionary containing the item data.

        Returns:
            dict: A DynamoDB-compatible item.

        Raises:
            ValueError: If a required key is missing or if an attribute type is unknown.
        """
        # Check for required keys
        for key in self.required_keys:
            if key not in item_dict or item_dict[key] is None:
                LOG.error("Missing required key: %s", key)
                raise ValueError(f"Missing required key: {key}")

        # Convert item_dict to DynamoDB item format
        dyndb_item = {}
        for key, value in item_dict.items():
            dyndb_item[key] = self.convert_value_to_dyndb_type(key, value)

        return dyndb_item

    def write_item(self, item_dict):
        """
        Write an item to the DynamoDB table.

        Args:
            item_dict (dict): A dictionary containing the attributes to write to the table.

        Returns:
            dict: The response from DynamoDB.
        """
        dyndb_item = self.convert_pydict_to_dyndb_item(item_dict)

        LOG.info("DynamoDB item to write: %s", dyndb_item)

        try:
            # The database will overwrite an existing item with the same primary key
            response = self.dyndb_client.put_item(
                TableName=self.table_name, Item=dyndb_item
            )
            LOG.info("Successfully wrote item to DynamoDB: %s", item_dict)
            return response
        except ClientError as err:
            LOG.error("Failed to write item to DynamoDB: %s", err)
            raise


# def convert_value_to_dyndb_type(key, value):
#     """
#     Converts a single key-value pair to the correct DynamoDB type.

#     Args:
#         key (str): The attribute name.
#         value: The attribute value.
#         attribute_types (dict): A dictionary mapping attribute names to their DynamoDB types.

#     Returns:
#         dict: A DynamoDB-compatible key-value pair.

#     Raises:
#         ValueError: If the attribute type is unknown or the value is invalid.
#     """
#     if key not in attribute_types:
#         LOG.error("Key: <%s> not found in attribute_types dict", key)
#         raise ValueError("Key: <%s> not found in attribute_types dict", key)

#     attr_type = attribute_types[key]

#     # Convert the value based on the attribute type
#     if attr_type == "S":  # String
#         return {"S": str(value)}
#     elif attr_type == "N":  # assume all numbers are integers
#         try:
#             return {"N": str(int(value))}  # Convert to stringified integer
#         except ValueError:
#             LOG.error("Invalid number value for key: %s", key)
#             raise ValueError(f"Invalid number value for key: {key}")
#     elif attr_type == "BOOL":  # ensure boolean are conveerted to True/False
#         return {"BOOL": value.lower() == "true"} if isinstance(value, str) else {"BOOL": bool(value)}
#     elif attr_type == "M":  # Map (JSON)
#         return {"M": value}  # Assume value is already a dictionary
#     elif attr_type == "NULL":  # Null
#         return {"NULL": True}
#     else:
#         LOG.error("Unsupported attribute type for key: %s", key)
#         raise ValueError(f"Unsupported attribute type for key: {key}")

# def convert_pydict_to_dyndb_item(item_dict, required_keys):
#     """
#     Converts a Python dictionary to a DynamoDB-compatible item format.

#     Args:
#         item_dict (dict): The dictionary containing the item data.
#         required_keys (list): A list of required keys that must be present in the item_dict.
#         attribute_types (dict): A dictionary mapping attribute names to their DynamoDB types
#                                 (e.g., {"batch_id": "N", "img_fprint": "S"}).

#     Returns:
#         dict: A DynamoDB-compatible item.

#     Raises:
#         ValueError: If a required key is missing or if an attribute type is unknown.
#     """
#     # Check for required keys
#     for key in required_keys:
#         if key not in item_dict or item_dict[key] is None:
#             LOG.error("Missing required key: %s", key)
#             raise ValueError(f"Missing required key: {key}")

#     # Convert item_dict to DynamoDB item format
#     dyndb_item = {}
#     for key, value in item_dict.items():
#         dyndb_item[key] = convert_value_to_dyndb_type(key, value)

#     return dyndb_item


# def write_item_to_dyndb(dyndb_client, table_name, item_dict, required_keys):
#     """
#     Write an item to the DynamoDB table using a client.

#     Args:
#         table_name (str): The name of the DynamoDB table.
#         item_dict (dict): A dictionary containing the attributes to write to the table.

#     Returns:
#         dict: The response from DynamoDB.
#     """
#     dyndb_item = convert_pydict_to_dyndb_item(
#         item_dict=item_dict, required_keys=required_keys
#     )

#     LOG.info("DynamoDB item to write: %s", dyndb_item)

#     try:
#         # The database will overwrite an existing item with the same primary key
#         response = dyndb_client.put_item(TableName=table_name, Item=dyndb_item)
#         LOG.info("Successfully wrote item to DynamoDB: %s", item_dict)
#         return response
#     except ClientError as err:
#         LOG.error("Failed to write item to DynamoDB: %s", err)
#         raise

# def convert_pydict_to_dyndb_item(item_dict, required_keys):

#     for key in required_keys:
#         if key not in item_dict or item_dict[key] is None:
#             LOG.error("Missing required key: %s", key)
#             raise ValueError(f"Missing required key: {key}")

#     dyndb_item = {}
#     for key, value in item_dict.items():
#         if key not in attribute_types:
#             LOG.error("Unknown attribute type for key: %s", key)
#             raise ValueError(f"Unknown attribute type for key: {key}")

#         attr_type = attribute_types[key]


#         if isinstance(value, str):
#             dyndb_item[key] = {"S": str(value)}
#         elif isinstance(value, (int, float)):
#             dyndb_item[key] = {"N": str(value)}
#         elif isinstance(value, bool):
#             dyndb_item[key] = {"BOOL": value}
#         elif isinstance(value, dict):
#             dyndb_item[key] = {"M": value}
#         elif value is None:
#             dyndb_item[key] = {"NULL": True}
#         else:
#             dyndb_item[key] = {"S": str(value)}

#     return dyndb_item


# def write_item_to_dyndb(dyndb_client, table_name, item_dict, required_keys):
#     """
#     Write an item to the DynamoDB table using a client.

#     Args:
#         table_name (str): The name of the DynamoDB table.
#         item_dict (dict): A dictionary containing the attributes to write to the table.

#     Returns:
#         dict: The response from DynamoDB.
#     """

#     dyndb_item = convert_pydict_to_dyndb_item(
#         item_dict=item_dict, required_keys=required_keys
#     )

#     try:
#         # so cuurently the db will overwrite an existing item with the same primary key
#         response = dyndb_client.put_item(TableName=table_name, Item=dyndb_item)
#         LOG.info("Successfully wrote item to DynamoDB: %s", item_dict)
#         return response
#     except ClientError as err:
#         LOG.error("Failed to write item to DynamoDB: %s", err)
#         raise
