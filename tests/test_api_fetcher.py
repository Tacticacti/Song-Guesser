import unittest
from unittest.mock import patch, MagicMock
from api_fetcher import fetch_metadata 

class TestApiFetcher(unittest.TestCase):

    def setUp(self):
        self.fake_api_data_multiple = {
            "resultCount": 2,
            "results": [
                {"trackName": "Song Zero", "artistName": "Artist A", "releaseDate": "1990", "previewUrl": "url0"},
                {"trackName": "Song One", "artistName": "Artist B", "releaseDate": "1995", "previewUrl": "url1"}
            ]
        }
        self.fake_api_data_single = {
            "resultCount": 1,
            "results": [
                {"trackName": "Song Zero", "artistName": "Artist A", "releaseDate": "1990", "previewUrl": "url0"}
            ]
        }
        self.fake_api_data_empty = {
            "resultCount": 0,
            "results": []
        }
        self.ONE = 1
        self.ZERO = 0

    @patch('api_fetcher.requests.get')
    @patch('api_fetcher.random.randint')
    def test_fetch_and_randomize_pipeline_multiple_data(self, mock_randint, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = self.fake_api_data_multiple
        mock_get.return_value = mock_response

        mock_randint.return_value = self.ONE

        artist, track, date, url = fetch_metadata("http://dummy-url.com", {"term": "Artist"})

        self.assertEqual(artist, "Artist B")
        self.assertEqual(track, "Song One")
        self.assertEqual(date, "1995")
        self.assertEqual(url, "url1")

        mock_get.assert_called_once()
        mock_randint.assert_called_once()

    @patch('api_fetcher.requests.get')
    def test_fetch_and_randomize_pipeline_single_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = self.fake_api_data_single
        mock_get.return_value = mock_response

        artist, track, date, url = fetch_metadata("http://dummy-url.com", {"term": "Artist"})

        self.assertEqual(artist, "Artist A")
        self.assertEqual(track, "Song Zero")
        self.assertEqual(date, "1990")
        self.assertEqual(url, "url0")

        mock_get.assert_called_once()

    @patch('api_fetcher.requests.get')
    def test_fetch_and_randomize_pipeline_empty_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = self.fake_api_data_empty
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            fetch_metadata("http://dummy-url.com", {"term": "Artist"})

        mock_get.assert_called_once()