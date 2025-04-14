"""
general.py

This module provides general utility functions for file operations, hash calculations, and batch file
management. These utilities are used across the application for tasks such as generating file paths,
reading and writing files, and handling JSON data.

Functions:
    - gen_batch_file_path: Generates a file path for batch logs.
    - calculate_file_hash: Computes the SHA-256 hash of a file.
    - read_file_2string: Reads the content of a file into a string.
    - write_string_2file: Writes a string to a file.
    - write_batch_file: Writes batch metadata to a JSON file.
    - read_batch_file: Reads a batch file and returns its contents as a dictionary.

Usage:
    Import the required function from this module to perform file operations or hash calculations.

    Example:
        from helpers.general import calculate_file_hash, gen_batch_file_path

        # Calculate the hash of a file
        file_hash = calculate_file_hash("path/to/file.txt")
        print(file_hash)

        # Generate a batch file path
        batch_file_path = gen_batch_file_path(client_id="client123", batch_id="batch456")
        print(batch_file_path)

Dependencies:
    - Python 3.12 or higher
    - `rich` library for enhanced console output
"""

import hashlib
import json
import os.path

from rich import print


def gen_batch_file_path(client_id, batch_id):
    """
    Generates a file path for batch logs.

    Args:
        client_id (str): The client ID to include in the file name.
        batch_id (str): The batch ID to include in the file name.

    Returns:
        str: The generated file path for the batch log.
    """
    logs_folder = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
    return os.path.join(logs_folder, f"{client_id}_{batch_id}.json")


def calculate_file_hash(file_path):
    """
    Computes the SHA-256 hash of a file.

    Args:
        file_path (str): The path to the file to hash.

    Returns:
        str: The SHA-256 hash of the file.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def read_file_2string(filepath, mode="r"):
    """
    Reads the content of a file into a string.

    Args:
        filepath (str): The path to the file to read.
        mode (str, optional): The mode in which to open the file. Defaults to "r".

    Returns:
        str or None: The content of the file as a string, or None if the file does not exist.
    """
    if not os.path.isfile(filepath):
        print(f"File not found: {filepath}")
        return None

    with open(filepath, mode, encoding="utf-8") as infile:
        filetext = infile.read().strip()
    return filetext


def write_string_2file(filepath, filetext, mode="w"):
    """
    Writes a string to a file.

    Args:
        filepath (str): The path to the file to write.
        filetext (str): The content to write to the file.
        mode (str, optional): The mode in which to open the file. Defaults to "w".

    Returns:
        None
    """
    with open(filepath, mode, encoding="utf-8") as outfile:
        print(f"Writing file: {filepath}")
        outfile.write(filetext)


def write_batch_file(filepath, batch_records):
    """
    Writes batch metadata to a JSON file.

    Args:
        filepath (str): The path to the file to write.
        batch_records (list): A list of batch records to write to the file.

    Returns:
        None
    """
    with open(filepath, "w", encoding="utf-8") as log_file:
        json.dump(batch_records, log_file, indent=4)


def read_batch_file(batch_file_path):
    """
    Reads a batch file and returns its contents as a dictionary.

    Args:
        batch_file_path (str): The path to the batch file to read.

    Returns:
        dict: The contents of the batch file.

    Raises:
        FileNotFoundError: If the batch file does not exist.
        ValueError: If the batch file contains invalid JSON.
    """
    try:
        with open(batch_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Batch file not found: {batch_file_path}")
    except json.JSONDecodeError as err:
        raise ValueError(f"Error decoding JSON from batch file: {err}") from err
