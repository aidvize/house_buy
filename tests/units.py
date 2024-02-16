import unittest
from unittest.mock import MagicMock, mock_open, patch

import src.utils.utils


class TestUtils(unittest.TestCase):
    @patch("src.utils.utils.psutil.cpu_percent")
    @patch("src.utils.utils.memory_usage")
    @patch("src.utils.utils.time.time")
    def test_performance_metrics(self, mock_time, mock_memory_usage, mock_cpu_percent):
        """
        Test the performance_metrics decorator for functionality.
        """
        # Setup mock returns
        mock_time.side_effect = [0, 10]
        mock_cpu_percent.side_effect = [0, 10]
        mock_memory_usage.side_effect = [[100], [150]]

        @src.utils.utils.performance_metrics
        def sample_function():
            return "test"

        result = sample_function()

        # Asserts
        self.assertEqual(result, "test")

    @patch("builtins.open", new_callable=mock_open, read_data="test: value")
    def test_load_config(self, mock_file):
        """
        Test the load_config function to ensure it correctly loads and parses YAML files.
        """
        result = src.utils.utils.load_config("dummy/path.yaml")
        self.assertEqual(result, {"test": "value"})

    def test_get_headers(self):
        """
        Test the get_headers function to ensure it returns the correct headers.
        """
        expected_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
        }
        headers = src.utils.utils.get_headers()
        self.assertEqual(headers, expected_headers)

    @patch("src.utils.utils.load_dotenv")
    @patch("os.getenv")
    def test_load_env(self, mock_getenv, mock_load_dotenv):
        """
        Test the load_env function to ensure it correctly loads environment variables.
        """
        mock_getenv.side_effect = ["test_bucket", "test_access_key", "test_secret_key"]
        result = src.utils.utils.load_env()
        self.assertEqual(result, ("test_bucket", "test_access_key", "test_secret_key"))
        mock_load_dotenv.assert_called_once()

    @patch("src.utils.utils.requests.get")
    @patch("src.utils.utils.BeautifulSoup")
    @patch("src.utils.utils.get_headers")
    def test_imovirtual(self, mock_get_headers, mock_beautiful_soup, mock_get):
        """
        Test the imovirtual function to ensure it scrapes data correctly.
        """
        mock_response = MagicMock()
        mock_response.text = "<html></html>"
        mock_get.return_value = mock_response
        mock_beautiful_soup.return_value.find_all.return_value = []
        result = src.utils.utils.imovirtual(
            "https://www.imovirtual.com/comprar/apartamento/" "?search%5Bregion_id%5D=11&page=", 1
        )
        self.assertEqual(result, {})
        mock_get.assert_called_once()
        mock_get_headers.assert_called_once()

    @patch("boto3.client")
    def test_upload_file_s3(self, mock_boto3_client):
        """
        Test the upload_file_s3 function to ensure it uploads files to S3.
        """
        mock_s3_client = MagicMock()
        mock_boto3_client.return_value = mock_s3_client
        src.utils.utils.upload_file_s3("test_bucket", "test_access_key", "test_secret_key")
        mock_boto3_client.assert_called_once_with(
            "s3", aws_access_key_id="test_access_key", aws_secret_access_key="test_secret_key"
        )


if __name__ == "__main__":
    unittest.main()
