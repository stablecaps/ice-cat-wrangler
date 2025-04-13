import hashlib
import json
import os.path

from rich import print


def gen_batch_file_path(client_id, batch_id):
    """
    Generates a batch file path based on the client ID and batch ID.

    Args:
        client_id (str): The client ID.
        batch_id (str): The batch ID.

    Returns:
        str: The generated batch file path.
    """
    logs_folder = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
    return os.path.join(logs_folder, f"{client_id}_{batch_id}.json")


def calculate_file_hash(file_path):
    """
    Calculates the SHA256 hash of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The SHA256 hash of the file as a hexadecimal string.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def read_file_2string(filepath, mode="r"):
    if not os.path.isfile(filepath):
        print("File not found: %s", filepath)
        return None

    with open(filepath, mode) as infile:
        filetext = infile.read().strip()
    return filetext


def write_string_2file(filepath, filetext, mode="w"):
    with open(filepath, mode) as outfile:
        print("Writing file: %s", filepath)
        outfile.write(filetext)


def write_batch_file(filepath, batch_records):
    # Write the upload records to the log file
    with open(filepath, "w") as log_file:
        json.dump(batch_records, log_file, indent=4)


def read_batch_file(batch_file_path):
    """
    Reads a batch file in JSON format and converts it into a list of Python dictionaries.

    Args:
        batch_file_path (str): The path to the batch file.

    Returns:
        list: A list of dictionaries representing the batch file content.

    Raises:
        FileNotFoundError: If the batch file does not exist.
        json.JSONDecodeError: If the batch file is not valid JSON.
    """
    try:
        with open(batch_file_path, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Batch file not found: {batch_file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON from batch file: {e}")
