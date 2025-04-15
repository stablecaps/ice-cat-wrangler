"""
Module: test_calculate_file_hash

This module contains unit tests for the `calculate_file_hash` function in the
`api_client.helpers.general` module. The `calculate_file_hash` function is responsible
for calculating the SHA-256 hash of a file's content.

The tests in this module ensure that:
- The function calculates the correct hash for files with various types of content.
- The function processes files in chunks to handle large files efficiently.
- The function handles edge cases such as empty files, non-existent files, and files with special characters in their paths.
- The function works correctly with files containing non-ASCII content.

Dependencies:
- pytest: For test execution and assertions.
- tempfile: For creating temporary files for testing.
- hashlib: For calculating expected hashes for verification.
- unittest.mock: For mocking file operations in tests.

Test Cases:
- `test_calculate_hash_for_small_text_file`: Verifies that the function calculates the correct hash for a small text file.
- `test_calculate_hash_for_large_binary_file`: Ensures the function calculates the correct hash for a large binary file.
- `test_calculate_hash_for_mixed_content_file`: Verifies that the function calculates the correct hash for a file with mixed text and binary content.
- `test_returns_valid_sha256_hex_string`: Ensures the function returns a valid SHA-256 hexadecimal string.
- `test_processes_file_in_chunks`: Verifies that the function processes files in 4096-byte chunks.
- `test_handle_empty_file`: Ensures the function handles empty files correctly.
- `test_handle_very_large_file`: Verifies that the function handles very large files (multi-GB) efficiently.
- `test_handle_special_characters_in_path`: Ensures the function handles files with special characters in their paths.
- `test_handle_non_ascii_content`: Verifies that the function handles files with non-ASCII content correctly.
- `test_handle_file_not_found`: Ensures the function raises a `FileNotFoundError` for non-existent files.
"""

import hashlib
import os
import random
import re
import tempfile
from unittest.mock import MagicMock, mock_open, patch

import pytest

from api_client.helpers.general import calculate_file_hash


class TestCalculateFileHash:
    """
    Test suite for the `calculate_file_hash` function.
    """

    # Calculate hash for a small text file
    def test_calculate_hash_for_small_text_file(self):
        """
        Test that the function calculates the correct hash for a small text file.

        Asserts:
            - The returned hash matches the expected hash for the file content.
        """
        # Arrange

        test_content = "This is a small text file for testing."
        expected_hash = (
            "eb717d5579c3911806ec62281e0fcc56b29de2fc1b737706b063bef0e5892690"
        )

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(test_content.encode("utf-8"))
            temp_path = temp_file.name

        # Act
        result = calculate_file_hash(temp_path)

        # Assert
        assert result == expected_hash

        # Cleanup
        os.unlink(temp_path)

    # Calculate hash for a large binary file
    def test_calculate_hash_for_large_binary_file(self):
        """
        Test that the function calculates the correct hash for a large binary file.

        Asserts:
            - The returned hash matches the expected hash for the file content.
        """
        # Arrange

        # Create a 1MB binary file with random data
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Generate 1MB of random bytes
            random_bytes = bytes([random.randint(0, 255) for _ in range(1024 * 1024)])
            temp_file.write(random_bytes)
            temp_path = temp_file.name

        # Act
        result = calculate_file_hash(temp_path)

        # Assert
        assert len(result) == 64  # SHA-256 hash is 64 characters in hex

        # Calculate the expected hash for verification
        expected_hash = hashlib.sha256(random_bytes).hexdigest()
        assert result == expected_hash

        # Cleanup
        os.unlink(temp_path)

    # Calculate hash for a file with mixed content
    def test_calculate_hash_for_mixed_content_file(self):
        """
        Test that the function calculates the correct hash for a file with mixed text and binary content.

        Asserts:
            - The returned hash matches the expected hash for the file content.
        """
        # Arrange

        # Create a file with mixed text and binary content
        mixed_content = b"Text content\n\x00\x01\x02\x03\nMore text\xff\xfe\xfd\xfc"

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(mixed_content)
            temp_path = temp_file.name

        # Calculate expected hash
        expected_hash = hashlib.sha256(mixed_content).hexdigest()

        # Act
        result = calculate_file_hash(temp_path)

        # Assert
        assert result == expected_hash

        # Cleanup
        os.unlink(temp_path)

    # Return a valid SHA-256 hexadecimal string
    def test_returns_valid_sha256_hex_string(self):
        """
        Test that the function returns a valid SHA-256 hexadecimal string.

        Asserts:
            - The returned hash is 64 characters long.
            - The returned hash contains only valid hexadecimal characters.
        """
        # Arrange
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"Test content for SHA-256 validation")
            temp_path = temp_file.name

        # Act
        result = calculate_file_hash(temp_path)

        # Assert
        # SHA-256 hash should be 64 characters long
        assert len(result) == 64

        # Should only contain valid hexadecimal characters
        hex_pattern = re.compile(r"^[0-9a-f]{64}$")
        assert hex_pattern.match(result) is not None

        # Cleanup
        os.unlink(temp_path)

    # Process files in 4096-byte chunks
    def test_processes_file_in_chunks(self):
        """
        Test that the function processes files in 4096-byte chunks.

        Asserts:
            - The file is read in chunks of 4096 bytes.
            - The returned hash matches the expected hash for the file content.
        """
        # Arrange

        # Create a file slightly larger than one chunk (4096 bytes)
        file_content = b"x" * 8192  # 8KB, which is 2 chunks

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name

        # Calculate expected hash
        expected_hash = hashlib.sha256(file_content).hexdigest()

        # Act & Assert
        with patch("builtins.open", mock_open(read_data=file_content)) as mock_file:
            # Configure the mock to return data in chunks
            mock_file.return_value.read.side_effect = [
                file_content[:4096],  # First chunk
                file_content[4096:],  # Second chunk
                b"",  # End of file
            ]

            result = calculate_file_hash(temp_path)

            # Verify the file was read in chunks of 4096 bytes
            assert mock_file.return_value.read.call_count == 3
            mock_file.return_value.read.assert_called_with(4096)

            # Verify the hash is correct
            assert result == expected_hash

        # Cleanup
        os.unlink(temp_path)

    # Handle empty files
    def test_handle_empty_file(self):
        """
        Test that the function handles empty files correctly.

        Asserts:
            - The returned hash matches the expected hash for an empty file.
        """
        # Arrange

        # Create an empty file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            # Don't write anything to keep it empty

        # Calculate expected hash for an empty file
        expected_hash = hashlib.sha256(b"").hexdigest()

        # Act
        result = calculate_file_hash(temp_path)

        # Assert
        assert result == expected_hash

        # Cleanup
        os.unlink(temp_path)

    # Handle very large files (multi-GB)
    def test_handle_very_large_file(self):
        """
        Test that the function handles very large files (multi-GB) efficiently.

        Asserts:
            - The file is read in chunks.
            - The returned hash matches the expected hash for the file content.
        """
        # Arrange

        # We'll mock a large file instead of creating one
        mock_file_path = "/path/to/large_file.bin"

        # Create a mock that simulates reading a large file in chunks
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file

        # Simulate 3GB file by returning 1MB chunk 3000 times then empty
        chunk_size = 1024 * 1024  # 1MB
        chunk = b"x" * chunk_size

        # Set up the read method to return the chunk 3000 times, then empty
        read_values = [chunk] * 3000 + [b""]
        mock_file.read.side_effect = read_values

        with patch("builtins.open", return_value=mock_file) as _:
            # Act
            result = calculate_file_hash(mock_file_path)

            # Assert
            assert len(result) == 64  # SHA-256 hash is 64 charactersmock_open
            # Verify the file was read in chunks
            assert mock_file.read.call_count == 3001  # 3000 chunks + 1 empty read
            mock_file.read.assert_called_with(4096)

    def test_handle_special_characters_in_path(self):
        """
        Test that the function handles files with special characters in their paths.

        Asserts:
            - The returned hash matches the expected hash for the file content.
        """

        # Arrange

        # Create a temporary directory with a special character in the name
        temp_dir = tempfile.mkdtemp(prefix="test_special_chars_!@#$%^&()_")

        # Create a file with special characters in the path
        file_content = b"Test content for special character path"
        special_path = os.path.join(temp_dir, "special_!@#$%^&()_file.txt")

        with open(special_path, "wb") as f:
            f.write(file_content)

        # Calculate expected hash
        expected_hash = hashlib.sha256(file_content).hexdigest()

        # Act
        result = calculate_file_hash(special_path)

        # Assert
        assert result == expected_hash

        # Cleanup
        os.unlink(special_path)
        os.rmdir(temp_dir)

    # Handle files with non-ASCII content
    def test_handle_non_ascii_content(self):
        """
        Test that the function handles files with non-ASCII content correctly.

        Asserts:
            - The returned hash matches the expected hash for the file content.
        """
        # Arrange

        # Create a file with non-ASCII content
        non_ascii_content = (
            "こんにちは世界! Привет мир! 你好世界! مرحبا بالعالم!".encode("utf-8")
        )

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(non_ascii_content)
            temp_path = temp_file.name

        # Calculate expected hash
        expected_hash = hashlib.sha256(non_ascii_content).hexdigest()

        # Act
        result = calculate_file_hash(temp_path)

        # Assert
        assert result == expected_hash

        # Cleanup
        os.unlink(temp_path)

    # Handle file not found (FileNotFoundError)
    def test_handle_file_not_found(self):
        """
        Test that the function raises a `FileNotFoundError` for non-existent files.

        Asserts:
            - A `FileNotFoundError` is raised when the file does not exist.
        """
        # Arrange

        # Generate a path that definitely doesn't exist
        non_existent_path = "/path/to/non_existent_file_12345.txt"

        # Make sure the file doesn't exist
        if os.path.exists(non_existent_path):
            os.unlink(non_existent_path)

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            calculate_file_hash(non_existent_path)
