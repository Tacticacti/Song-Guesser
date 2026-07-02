import os
import tempfile
import unittest
from unittest.mock import patch

import artist_pool
from artist_pool import populate_artist_pool, save_artist_pool

class TestArtistPool(unittest.TestCase):

    def setUp(self):
        handle, self.temp_file = tempfile.mkstemp(suffix='.txt')
        os.close(handle)
        self.patcher = patch.object(artist_pool, 'ARTIST_FILE', self.temp_file)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        os.remove(self.temp_file)

    def write_file(self, content):
        with open(self.temp_file, 'w') as file:
            file.write(content)

    def test_save_and_load_round_trip(self):
        save_artist_pool(['Ado', 'Eminem', 'Twice'])
        self.assertEqual(populate_artist_pool(), ['Ado', 'Eminem', 'Twice'])

    def test_load_strips_whitespace(self):
        self.write_file('Ado \n  Eminem\n')
        self.assertEqual(populate_artist_pool(), ['Ado', 'Eminem'])

    def test_load_skips_blank_lines(self):
        self.write_file('Ado\n\n\nEminem\n   \n')
        self.assertEqual(populate_artist_pool(), ['Ado', 'Eminem'])

    def test_load_empty_file(self):
        self.write_file('')
        self.assertEqual(populate_artist_pool(), [])

    def test_save_overwrites_existing_content(self):
        save_artist_pool(['Old Artist'])
        save_artist_pool(['New Artist'])
        self.assertEqual(populate_artist_pool(), ['New Artist'])

    def test_missing_file_returns_empty_list(self):
        os.remove(self.temp_file)
        try:
            self.assertEqual(populate_artist_pool(), [])
        finally:
            self.write_file('')  # recreate so tearDown can remove it

if __name__ == '__main__':
    unittest.main()
