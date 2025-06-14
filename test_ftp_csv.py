from ftp_csv import FTPClient, FileValidator, Logger
from unittest.mock import patch, Mock


class TestFTP:
    def setup_method(self):
        self.ftp_client = FTPClient()
        self.validator = FileValidator()
        self.valid_csv_content = """batch_id,timestamp,reading1,reading2,reading3,reading4,reading5,reading6,reading7,reading8,reading9,reading10
                                    1,2023-01-01,1.234,2.345,3.456,4.567,5.678,6.789,7.890,8.901,9.012,0.123
                                    2,2023-01-02,1.234,2.345,3.456,4.567,5.678,6.789,7.890,8.901,9.012,0.123"""

    def test_connect_to_ftp(self):
        is_valid, message = self.ftp_client.connect(
            '127.0.0.1', 'wla', 'wla123')
        assert is_valid == True
        assert message == "Connected to FTP server"

    def test_disconnect_to_ftp(self):
        self.ftp_client.connect('127.0.0.1', 'wla', 'wla123')
        is_valid, message = self.ftp_client.disconnect()
        assert is_valid == False
        assert message == "Disconnected to FTP server"

    def test_valid_csv_files(self):
        is_valid, message = FileValidator.validate(self.valid_csv_content)
        assert is_valid == True
        assert message == "Valid"

    def test_invalid_headers(self):
        invalid_headers = """wrong_id,timestamp,reading1,reading2,reading3,reading4,reading5,reading6,reading7,reading8,reading9,reading10
                            1,2023-01-01,1.234,2.345,3.456,4.567,5.678,6.789,7.890,8.901,9.012,0.123"""
        is_valid, message = FileValidator.validate(invalid_headers)
        assert is_valid == False
        assert "Incorrect or missing headers" in message

    def test_duplicate_batch_id(self):
        duplicate_batch = """batch_id,timestamp,reading1,reading2,reading3,reading4,reading5,reading6,reading7,reading8,reading9,reading10
                            1,2023-01-01,1.234,2.345,3.456,4.567,5.678,6.789,7.890,8.901,9.012,0.123
                            1,2023-01-02,1.234,2.345,3.456,4.567,5.678,6.789,7.890,8.901,9.012,0.123"""
        is_valid, message = FileValidator.validate(
            duplicate_batch)
        assert is_valid == False
        assert "Duplicate batch_id" in message

    def test_invalid_decimal_format(self):
        invalid_decimal = """batch_id,timestamp,reading1,reading2,reading3,reading4,reading5,reading6,reading7,reading8,reading9,reading10
                            1,2023-01-01,1.234,2.345,3.456,4.567,5.678,6.789,7.890,8.901,9.012,0.1234"""
        is_valid, message = FileValidator.validate(invalid_decimal)
        assert is_valid == False
        assert "Invalid decimal format" in message

    def test_value_exceeds_limit(self):
        exceeds_limit = """batch_id,timestamp,reading1,reading2,reading3,reading4,reading5,reading6,reading7,reading8,reading9,reading10
                            1,2023-01-01,1.234,2.345,3.456,4.567,5.678,6.789,7.890,8.901,9.012,10.123"""
        is_valid, message = FileValidator.validate(exceeds_limit)
        assert is_valid == False
        assert "Value exceeds 9.9" in message

    @patch("requests.get")
    def test_get_uuid_success(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = ["1234-abcd"]
        mock_get.return_value = mock_response

        client = Logger()
        result = client.get_uuid()

        assert result == "1234-abcd"

    @patch("requests.get")
    def test_get_uuid_api_failure(self, mock_get):
        # Simulate a network error
        mock_get.side_effect = Exception("API down")

        client = Logger()
        result = client.get_uuid()

        assert result == "unknown_uuid"
