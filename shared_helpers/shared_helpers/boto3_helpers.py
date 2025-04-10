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


def gen_boto3_client(service_name, aws_region=None):
    """
    Creates and returns a Boto3 client for a specified AWS service.

    Args:
        service_name (str): The name of the AWS service (e.g., 's3', 'lambda').
        aws_region (str, optional): The AWS region to use. Defaults to "eu-west-1".

    Returns:
        boto3.Client: A Boto3 client object for the specified service.
    """
    aws_region = aws_region or os.getenv("AWS_REGION", "eu-west-1")
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
            LOG.critical("S3 bucket <%s> does not exist", bucket_name)
        elif error_code == "403":
            LOG.critical("Access denied to S3 bucket <%s>", bucket_name)
        else:
            LOG.critical("Failed to verify S3 bucket <%s>: <%s>", bucket_name, err)
        sys.exit(42)


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


# TODO: return true/false from this so we can set op status to fail if copt fails
def move_s3_object_based_on_rekog_response(
    s3_client, op_status, s3bucket_source, s3bucket_dest, s3bucket_fail, s3_key
):
    """
    Handle the Rekognition response and move the image to the appropriate S3 bucket.

    Args:
        op_status (str): success or failure status of the Rekognition operation.
        s3bucket_source (str): The source S3 bucket name.
        s3bucket_dest (str): The destination S3 bucket name for successful processing.
        s3bucket_fail (str): The destination S3 bucket name for failed processing.
        s3_key (str): The key of the object in the S3 bucket.

    Returns:
        None
    """
    try:
        if op_status == "success":
            target_bucket = s3bucket_dest
        else:
            target_bucket = s3bucket_fail

        copy_source = {"Bucket": s3bucket_source, "Key": s3_key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=target_bucket,
            Key=s3_key,
            ACL="bucket-owner-full-control",
        )
        s3_client.delete_object(Bucket=s3bucket_source, Key=s3_key)
        LOG.info("Moved object <%s> to <%s>", s3_key, target_bucket)
        return True

    except ClientError as err:
        LOG.error("Error moving object %s: %s", s3_key, err)
        raise
    except Exception as err:
        LOG.error("Unexpected error while handling Rekognition response: %s", err)
        raise


################################################################################
# rekognition functions
def rekog_image_categorise(rekog_client, image_bytes, label_pattern="cat"):

    try:
        rekog_resp = rekog_client.detect_labels(
            Image={"Bytes": image_bytes},
            MaxLabels=10,
            MinConfidence=75,
        )

        # Print labels detected
        labels = [label["Name"].lower() for label in rekog_resp["Labels"]]

        rek_match = "False"
        if label_pattern in labels:
            rek_match = "True"

        LOG.info("Labels detected: <%s>", labels)
        LOG.info("rek_match for label_pattern: <%s> is <%s>", label_pattern, rek_match)

        return {"rekog_resp": rekog_resp, "rek_match": rek_match}

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
            raise ValueError("Key: <%s> not found in attribute_types dict", key)

        attr_type = self.attribute_types[key]

        # Convert the value based on the attribute type
        if attr_type == "S":  # String
            return {"S": str(value)}
        elif attr_type == "N":  # Assume all numbers are integers
            try:
                return {"N": str(int(value))}  # Convert to stringified integer
            except ValueError:
                LOG.error("Invalid number value for key: %s", key)
                raise ValueError("Invalid number value for key: %s", key)
        elif attr_type == "BOOL":  # Ensure booleans are converted to True/False
            if isinstance(value, str):
                if value.lower() not in ["true", "false"]:
                    LOG.error("Invalid boolean string for key: %s", key)
                    raise ValueError("Invalid boolean string for key: %s", key)
            else:
                LOG.error("Boolean value not represented as a string for key: %s", key)
                raise ValueError(
                    "Boolean value not represented as a string for key: %s", key
                )
            return {"S": value}
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
                raise ValueError("Missing required key: %s", key)

        # Convert item_dict to DynamoDB item format
        dyndb_item = {}
        for key, value in item_dict.items():
            dyndb_item[key] = self.convert_value_to_dyndb_type(key, value)

        return dyndb_item

    # @staticmethod
    # def preprocess_dynamodb_dict(item):
    #     """
    #     Recursively preprocess an item to ensure it conforms to DynamoDB's type system.

    #     Args:
    #         item: The item to preprocess (can be a dict, list, or primitive type).

    #     Returns:
    #         dict: The item formatted for DynamoDB.
    #     """
    #     if isinstance(item, dict):
    #         # Convert dictionary to DynamoDB Map type
    #         return {"M": {k: DynamoDBHelper.preprocess_dynamodb_dict(v) for k, v in item.items()}}
    #     elif isinstance(item, list):
    #         # Convert list to DynamoDB List type
    #         return {"L": [DynamoDBHelper.preprocess_dynamodb_dict(v) for v in item]}
    #     elif isinstance(item, str):
    #         # Convert string to DynamoDB String type
    #         return {"S": item}
    #     elif isinstance(item, (int, float)):
    #         # Convert number to DynamoDB Number type
    #         return {"N": str(item)}
    #     elif isinstance(item, bool):
    #         # Convert boolean to DynamoDB Boolean type
    #         return {"BOOL": item}
    #     elif item is None:
    #         # Convert None to DynamoDB Null type
    #         return {"NULL": True}
    #     else:
    #         raise ValueError(f"Unsupported type for DynamoDB: {type(item)}")

    def write_item(self, item_dict):
        """
        Write an item to the DynamoDB table.

        Args:
            item_dict (dict): A dictionary containing the attributes to write to the table.

        Returns:
            dict: The response from DynamoDB.
        """

        # TODO: Preprocess the `rek_resp` field if it exists
        # if "rek_resp" in item_dict:
        #     item_dict["rek_resp"] = DynamoDBHelper.preprocess_dynamodb_dict(item_dict["rek_resp"])

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

    def update_item(self, item_dict):
        """
        Update specific attributes in a DynamoDB item without deleting other attributes.

        Args:
            item_dict (dict): A dictionary containing the primary key and attributes to update.
                              The primary key (partition key and sort key) must be included.

        Returns:
            dict: The response from the UpdateItem operation.
        """
        # Extract and convert the primary key attributes
        key = {
            "batch_id": self.convert_value_to_dyndb_type(
                "batch_id", item_dict.pop("batch_id")
            ),
            "img_fprint": self.convert_value_to_dyndb_type(
                "img_fprint", item_dict.pop("img_fprint")
            ),
        }

        # Build the UpdateExpression and ExpressionAttributeValues
        update_expression = "SET " + ", ".join(f"#{k} = :{k}" for k in item_dict.keys())

        expression_attribute_names = {f"#{k}": k for k in item_dict.keys()}

        expression_attribute_values = {
            f":{k}": self.convert_value_to_dyndb_type(k, v)
            for k, v in item_dict.items()
        }

        try:
            response = self.dyndb_client.update_item(
                TableName=self.table_name,
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW",
            )
            LOG.info(
                "Successfully updated item in DynamoDB: %s", response["Attributes"]
            )
            return response
        except ClientError as err:
            LOG.error("Failed to update item in DynamoDB: %s", err)
            raise
