"""
Module: test_gen_boto3_client

This module contains unit tests for the `gen_boto3_client` function in the
`shared_helpers.boto3_helpers` module. The `gen_boto3_client` function is responsible
for creating boto3 clients for various AWS services, using either a default or custom
AWS region.

The tests in this module ensure that:
- Boto3 clients are successfully created for valid service names.
- The default AWS region is used when no custom region is specified.
- Custom AWS regions are correctly applied when provided.
- The `AWS_REGION` environment variable is used when available.
- Proper error handling is implemented for invalid service names, missing credentials,
  and network issues.

Dependencies:
- pytest: For test execution and assertions.
- pytest-mock: For mocking dependencies and boto3 interactions.
- botocore.exceptions: For simulating AWS client errors.
- shared_helpers.boto3_helpers.gen_boto3_client: The function under test.

Test Cases:
- `test_creates_client_with_default_region`: Verifies that a boto3 client is created with the default region.
- `test_creates_client_with_custom_region`: Ensures that a boto3 client is created with a custom region.
- `test_uses_region_from_env_variable`: Confirms that the `AWS_REGION` environment variable is used when available.
- `test_returns_client_for_different_services`: Verifies that clients are created for multiple AWS services.
- `test_uses_session_from_gen_boto3_session`: Ensures that the session created by `gen_boto3_session` is used.
- `test_handles_empty_or_invalid_service_name`: Handles cases where the service name is empty or invalid.
- `test_uses_default_region_when_no_region_specified`: Ensures the default region is used when no region is specified.
- `test_handles_session_with_incomplete_credentials`: Handles cases where the session has incomplete credentials.
- `test_handles_network_issues`: Handles cases where client creation fails due to network issues.
- `test_handles_non_string_service_name`: Handles cases where the service name is not a string.
"""

import pytest
from botocore.exceptions import ClientError, NoCredentialsError, UnknownServiceError

from shared_helpers.boto3_helpers import gen_boto3_client


class TestGenBoto3Client:
    """
    Test suite for the `gen_boto3_client` function.
    """

    # Creates a boto3 client with a specified service name using default region
    def test_creates_client_with_default_region(self, mocker):
        """
        Test that a boto3 client is created with the default region.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `client` method of the boto3 session is called with the default region.
            - The returned client matches the mocked client.
        """
        # Arrange
        mock_session = mocker.Mock()
        mock_client = mocker.Mock()
        mock_session.client.return_value = mock_client
        mocker.patch(
            "shared_helpers.boto3_helpers.gen_boto3_session", return_value=mock_session
        )
        mocker.patch.dict("os.environ", {}, clear=True)  # Clear environment variables

        # Act
        result = gen_boto3_client("s3")

        # Assert
        mock_session.client.assert_called_once_with(
            "s3", "eu-west-1"
        )  # Update if needed
        assert result == mock_client

    # Creates a boto3 client with a specified service name and custom region
    def test_creates_client_with_custom_region(self, mocker):
        """
        Test that a boto3 client is created with a custom region.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `client` method of the boto3 session is called with the custom region.
            - The returned client matches the mocked client.
        """
        # Arrange
        mock_session = mocker.Mock()
        mock_client = mocker.Mock()
        mock_session.client.return_value = mock_client
        mocker.patch(
            "shared_helpers.boto3_helpers.gen_boto3_session", return_value=mock_session
        )
        custom_region = "us-east-1"

        # Act
        result = gen_boto3_client("s3", custom_region)

        # Assert
        mock_session.client.assert_called_once_with("s3", custom_region)
        assert result == mock_client

    # Creates a boto3 client using region from AWS_REGION environment variable when available
    def test_uses_region_from_env_variable(self, mocker):
        """
        Test that the `AWS_REGION` environment variable is used when available.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `client` method of the boto3 session is called with the region from the environment variable.
        """
        # Arrange
        mock_session = mocker.Mock()
        mock_client = mocker.Mock()
        mock_session.client.return_value = mock_client
        mocker.patch(
            "shared_helpers.boto3_helpers.gen_boto3_session", return_value=mock_session
        )
        env_region = "ap-southeast-1"
        mocker.patch.dict("os.environ", {"AWS_REGION": env_region})

        # Act
        result = gen_boto3_client("s3")

        # Assert
        mock_session.client.assert_called_once_with("s3", env_region)
        assert result == mock_client

    # Successfully returns a boto3 client object for services like 's3' or 'rekognition'
    def test_returns_client_for_different_services(self, mocker):
        """
        Test that boto3 clients are successfully created for multiple AWS services.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - Clients are created for the specified services (e.g., 's3', 'rekognition').
            - The returned clients match the mocked clients.
        """
        # Arrange
        mock_session = mocker.Mock()
        s3_client = mocker.Mock(name="s3_client")
        rekognition_client = mocker.Mock(name="rekognition_client")

        def get_client(service, region):
            if service == "s3":
                return s3_client
            elif service == "rekognition":
                return rekognition_client

        mock_session.client.side_effect = get_client
        mocker.patch(
            "shared_helpers.boto3_helpers.gen_boto3_session", return_value=mock_session
        )

        # Act
        s3_result = gen_boto3_client("s3")
        rekognition_result = gen_boto3_client("rekognition")

        # Assert
        assert s3_result == s3_client
        assert rekognition_result == rekognition_client
        assert mock_session.client.call_count == 2

    # Uses the session created by gen_boto3_session() to generate the client
    def test_uses_session_from_gen_boto3_session(self, mocker):
        """
        Test that the session created by `gen_boto3_session` is used to generate the client.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `gen_boto3_session` function is called once.
            - The `client` method of the session is called once.
        """
        # Arrange
        mock_session = mocker.Mock()
        mock_client = mocker.Mock()
        mock_session.client.return_value = mock_client
        mock_gen_boto3_session = mocker.patch(
            "shared_helpers.boto3_helpers.gen_boto3_session", return_value=mock_session
        )

        # Act
        result = gen_boto3_client("s3")

        # Assert
        mock_gen_boto3_session.assert_called_once()
        mock_session.client.assert_called_once()
        assert result == mock_client

    # Handles case when service_name is empty or invalid
    def test_handles_empty_or_invalid_service_name(self, mocker):
        """
        Test that an `UnknownServiceError` is raised for empty or invalid service names.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - An `UnknownServiceError` is raised with the expected error message.
        """
        # Arrange
        mock_session = mocker.Mock()
        mock_session.client.side_effect = UnknownServiceError(
            service_name="", known_service_names=["s3", "rekognition"]
        )
        mocker.patch(
            "shared_helpers.boto3_helpers.gen_boto3_session", return_value=mock_session
        )

        # Act & Assert
        with pytest.raises(UnknownServiceError):
            gen_boto3_client("")

        # Test with invalid service name
        with pytest.raises(UnknownServiceError):
            gen_boto3_client("invalid_service")

    # Handles case when aws_region is None and AWS_REGION environment variable is not set
    def test_uses_default_region_when_no_region_specified(self, mocker):
        """
        Test that the default region is used when no region is specified.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `client` method of the boto3 session is called with the default region.
        """
        # Arrange
        mock_session = mocker.Mock()
        mock_client = mocker.Mock()
        mock_session.client.return_value = mock_client
        mocker.patch(
            "shared_helpers.boto3_helpers.gen_boto3_session", return_value=mock_session
        )
        # Ensure AWS_REGION is not in environment variables
        mocker.patch.dict("os.environ", {}, clear=True)

        # Act
        result = gen_boto3_client("s3", None)

        # Assert
        mock_session.client.assert_called_once_with("s3", "eu-west-1")
        assert result == mock_client

    # Handles case when gen_boto3_session() returns a session with incomplete credentials
    def test_handles_session_with_incomplete_credentials(self, mocker):
        """
        Test that a `NoCredentialsError` is raised when the session has incomplete credentials.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `NoCredentialsError` is raised with the expected error message.
        """
        # Arrange
        mock_session = mocker.Mock()
        mock_session.client.side_effect = NoCredentialsError()
        mocker.patch(
            "shared_helpers.boto3_helpers.gen_boto3_session", return_value=mock_session
        )

        # Act & Assert
        with pytest.raises(NoCredentialsError):
            gen_boto3_client("s3")

    # Handles case when boto3 client creation fails due to network issues
    def test_handles_network_issues(self, mocker):
        """
        Test that a `ClientError` is raised when client creation fails due to network issues.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ClientError` is raised with the expected error message.
        """
        # Arrange
        mock_session = mocker.Mock()
        mock_session.client.side_effect = ClientError(
            {"Error": {"Code": "RequestTimeout", "Message": "Request timed out"}},
            "client",
        )
        mocker.patch(
            "shared_helpers.boto3_helpers.gen_boto3_session", return_value=mock_session
        )

        # Act & Assert
        with pytest.raises(ClientError) as excinfo:
            gen_boto3_client("s3")

        assert "RequestTimeout" in str(excinfo.value)

    # Handles case when service_name is not a string
    def test_handles_non_string_service_name(self, mocker):
        """
        Test that a `TypeError` is raised when the service name is not a string.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `TypeError` is raised with the expected error message.
        """
        # Arrange
        mock_session = mocker.Mock()
        mock_session.client.side_effect = TypeError("service_name must be a string")
        mocker.patch(
            "shared_helpers.boto3_helpers.gen_boto3_session", return_value=mock_session
        )

        # Act & Assert
        with pytest.raises(TypeError):
            gen_boto3_client(123)  # Passing an integer instead of a string
