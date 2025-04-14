# Generated by Qodo Gen

import pytest


class TestCalculateFileHash:

    # Calculate hash for a small text file
    def test_calculate_hash_for_small_text_file(self):
        # Arrange
        import os
        import tempfile

        from api_client.helpers.general import calculate_file_hash

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
        # Arrange
        import os
        import tempfile

        from api_client.helpers.general import calculate_file_hash

        # Create a 1MB binary file with random data
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Generate 1MB of random bytes
            import random

            random_bytes = bytes([random.randint(0, 255) for _ in range(1024 * 1024)])
            temp_file.write(random_bytes)
            temp_path = temp_file.name

        # Act
        result = calculate_file_hash(temp_path)

        # Assert
        assert len(result) == 64  # SHA-256 hash is 64 characters in hex

        # Calculate the expected hash for verification
        import hashlib

        expected_hash = hashlib.sha256(random_bytes).hexdigest()
        assert result == expected_hash

        # Cleanup
        os.unlink(temp_path)

    # Calculate hash for a file with mixed content
    def test_calculate_hash_for_mixed_content_file(self):
        # Arrange
        import os
        import tempfile

        from api_client.helpers.general import calculate_file_hash

        # Create a file with mixed text and binary content
        mixed_content = b"Text content\n\x00\x01\x02\x03\nMore text\xff\xfe\xfd\xfc"

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(mixed_content)
            temp_path = temp_file.name

        # Calculate expected hash
        import hashlib

        expected_hash = hashlib.sha256(mixed_content).hexdigest()

        # Act
        result = calculate_file_hash(temp_path)

        # Assert
        assert result == expected_hash

        # Cleanup
        os.unlink(temp_path)

    # Return a valid SHA-256 hexadecimal string
    def test_returns_valid_sha256_hex_string(self):
        # Arrange
        import os
        import re
        import tempfile

        from api_client.helpers.general import calculate_file_hash

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
        # Arrange
        import hashlib
        import os
        import tempfile
        from unittest.mock import MagicMock, mock_open, patch

        from api_client.helpers.general import calculate_file_hash

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
        # Arrange
        import hashlib
        import os
        import tempfile

        from api_client.helpers.general import calculate_file_hash

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
        # Arrange
        import os
        import tempfile
        from unittest.mock import MagicMock, patch

        from api_client.helpers.general import calculate_file_hash

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

        with patch("builtins.open", return_value=mock_file) as mock_open:
            # Act
            result = calculate_file_hash(mock_file_path)

            # Assert
            assert len(result) == 64  # SHA-256 hash is 64 characters
            # Verify the file was read in chunks
            assert mock_file.read.call_count == 3001  # 3000 chunks + 1 empty read
            mock_file.read.assert_called_with(4096)

    # Handle files with special characters in path
    def test_handle_special_characters_in_path(self):
        # Arrange
        import hashlib
        import os
        import tempfile

        from api_client.helpers.general import calculate_file_hash

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
        # Arrange
        import hashlib
        import os
        import tempfile

        from api_client.helpers.general import calculate_file_hash

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
        # Arrange
        import os

        import pytest

        from api_client.helpers.general import calculate_file_hash

        # Generate a path that definitely doesn't exist
        non_existent_path = "/path/to/non_existent_file_12345.txt"

        # Make sure the file doesn't exist
        if os.path.exists(non_existent_path):
            os.unlink(non_existent_path)

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            calculate_file_hash(non_existent_path)
