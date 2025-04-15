import pytest

from serverless.functions.fhelpers import validate_s3bucket


class TestFHelpers:

    def test_validate_s3bucket(self, mocker, mock_aws_clients):
        # Arrange
        s3_client_mock, _, _ = mock_aws_clients

        mock_check_bucket_exists = mocker.patch(
            "serverless.functions.fhelpers.check_bucket_exists"
        )

        # Act
        result = validate_s3bucket(s3_client_mock)

        # Assert
        assert result == ("source-bucket", "dest-bucket", "fail-bucket")
        mock_check_bucket_exists.assert_called()

    # TODO: convert tests below to pytest-style test functions.

    # @patch('serverless.functions.fhelpers.safeget')
    # def test_get_s3_key_from_event(self, mock_safeget):
    #     mock_safeget.return_value = 'test/key.png'
    #     event = {'Records': [{'s3': {'object': {'key': 'test/key.png'}}}]}

    #     result = get_s3_key_from_event(event)

    #     self.assertEqual(result, 'test/key.png')

    # def test_convert_time_string_to_epoch(self):
    #     time_string = "Mon, 01 Jan 2023 00:00:00 GMT"
    #     format_string = "%a, %d %b %Y %H:%M:%S %Z"

    #     result = convert_time_string_to_epoch(time_string, format_string)

    #     expected_epoch = int(datetime.strptime(time_string, format_string).timestamp())
    #     self.assertEqual(result, expected_epoch)

    # def test_convert_to_json(self):
    #     data = {'key': 'value'}

    #     result = convert_to_json(data)

    #     self.assertEqual(result, json.dumps(data, indent=4))

    # def test_gen_item_dict1_from_s3key(self):
    #     s3_key = "hash/client/batch-1234/2023-01-01/1672531200.png"
    #     s3_bucket = "source-bucket"

    #     result = gen_item_dict1_from_s3key(s3_key, s3_bucket)

    #     expected_result = {
    #         "batch_id": "1234",
    #         "img_fprint": "hash",
    #         "client_id": "client",
    #         "s3img_key": "source-bucket/hash/client/batch-1234/2023-01-01/1672531200.png",
    #         "op_status": "pending",
    #         "current_date": "2023-01-01",
    #         "upload_ts": "1672531200",
    #         "ttl": None,  # Assuming dyndb_ttl is None for the test
    #     }
    #     self.assertEqual(result, expected_result)

    # @patch('serverless.functions.fhelpers.convert_to_json')
    # @patch('serverless.functions.fhelpers.safeget')
    # def test_gen_item_dict2_from_rek_resp(self, mock_safeget, mock_convert_to_json):
    #     mock_safeget.side_effect = [
    #         "Mon, 01 Jan 2023 00:00:00 GMT",  # rek_long_time_string
    #         200  # rek_status_code
    #     ]
    #     mock_convert_to_json.return_value = '{"rekog_resp": "mocked"}'
    #     rekog_results = {
    #         "rekog_resp": {"ResponseMetadata": {"HTTPHeaders": {"date": "Mon, 01 Jan 2023 00:00:00 GMT"}}},
    #         "rek_match": True
    #     }

    #     result = gen_item_dict2_from_rek_resp(rekog_results)

    #     expected_result = {
    #         "batch_id": None,  # Assuming global_context is not set for the test
    #         "img_fprint": None,  # Assuming global_context is not set for the test
    #         "op_status": "success",
    #         "rek_resp": '{"rekog_resp": "mocked"}',
    #         "rek_iscat": True,
    #         "rek_ts": int(datetime.strptime("Mon, 01 Jan 2023 00:00:00 GMT", "%a, %d %b %Y %H:%M:%S %Z").timestamp()),
    #     }
    #     self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
