from ftp_csv import FTPClient


class TestFTP:
    def setup_method(self):
        self.ftp_client = FTPClient()

    def test_connect_to_ftp(self):
        is_valid, message = self.ftp_client.connect(
            '127.0.0.1', 'wla', 'wla123')
        assert is_valid is True
        assert message == "Connected to FTP server"

    def test_disconnect_to_ftp(self):
        self.ftp_client.connect('127.0.0.1', 'wla', 'wla123')
        is_valid, message = self.ftp_client.disconnect()
        assert is_valid is False
        assert message == "Disconnected to FTP server"
