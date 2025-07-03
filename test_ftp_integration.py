from ftp_csv import FTPClient, Logger
from unittest.mock import patch, Mock, MagicMock
class TestIntegration:
    def setup_method(self):
        self.ftp_client = FTPClient()

    @patch("ftplib.FTP")
    def test_connect_to_ftp(self, mock_ftp_class):
        mock_ftp_instance = MagicMock()
        mock_ftp_class.return_value = mock_ftp_instance

        is_valid, message = self.ftp_client.connect("host", "user", "pass")

        assert is_valid is True
        assert message == "Connected to FTP server"

    @patch("ftplib.FTP")
    def test_disconnect_to_ftp(self, mock_ftp_class):
        mock_ftp_instance = MagicMock()
        mock_ftp_class.return_value = mock_ftp_instance

        self.ftp_client.connect("host", "user", "pass")
        is_valid, message = self.ftp_client.disconnect()

        mock_ftp_instance.quit.assert_called_once()
        assert is_valid == False
        assert message == "Disconnected from FTP server"

    # Integration Testing
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

