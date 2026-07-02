import os
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import artist_pool
import server

SONG = ('Ado', 'Show', '2022-01-01', 'http://preview.example/show.m4a')

class ServerTestCase(unittest.TestCase):
    """Integration tests running the real app, artist file, and round store."""

    def setUp(self):
        handle, self.temp_file = tempfile.mkstemp(suffix='.txt')
        os.close(handle)
        with open(self.temp_file, 'w') as file:
            file.write('Ado\nEminem')
        self.patcher = patch.object(artist_pool, 'ARTIST_FILE', self.temp_file)
        self.patcher.start()
        server.rounds.clear()
        self.client = TestClient(server.app)

    def tearDown(self):
        self.patcher.stop()
        os.remove(self.temp_file)

class TestArtistEndpoints(ServerTestCase):

    def test_get_artists(self):
        response = self.client.get('/api/artists')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'artists': ['Ado', 'Eminem']})

    def test_add_artist_persists_to_file(self):
        response = self.client.post('/api/artists', json={'name': '  Queen  '})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['artists'], ['Ado', 'Eminem', 'Queen'])
        self.assertEqual(artist_pool.populate_artist_pool(), ['Ado', 'Eminem', 'Queen'])

    def test_add_duplicate_artist_rejected_case_insensitively(self):
        response = self.client.post('/api/artists', json={'name': 'ado'})
        self.assertEqual(response.status_code, 400)

    def test_add_empty_artist_rejected(self):
        response = self.client.post('/api/artists', json={'name': '   '})
        self.assertEqual(response.status_code, 400)

    def test_remove_artist_case_insensitively(self):
        response = self.client.delete('/api/artists/ADO')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['artists'], ['Eminem'])
        self.assertEqual(artist_pool.populate_artist_pool(), ['Eminem'])

    def test_remove_missing_artist_returns_404(self):
        response = self.client.delete('/api/artists/Nobody')
        self.assertEqual(response.status_code, 404)

    def test_cannot_remove_last_artist(self):
        self.client.delete('/api/artists/Eminem')
        response = self.client.delete('/api/artists/Ado')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(artist_pool.populate_artist_pool(), ['Ado'])

class TestArtistEdgeCases(ServerTestCase):

    def test_artist_name_with_line_breaks_rejected(self):
        # a newline in the name would corrupt artists.txt into two entries
        response = self.client.post('/api/artists', json={'name': 'Artist A\nArtist B'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(artist_pool.populate_artist_pool(), ['Ado', 'Eminem'])

    def test_artist_with_slash_can_be_added_and_removed(self):
        self.client.post('/api/artists', json={'name': 'AC/DC'})
        response = self.client.delete('/api/artists/AC%2FDC')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['artists'], ['Ado', 'Eminem'])

class TestRoundLifecycle(ServerTestCase):

    def start_round(self):
        with patch('server.fetch_metadata', return_value=SONG):
            return self.client.post('/api/rounds').json()

    def test_start_round_returns_preview_but_not_answers(self):
        round_data = self.start_round()
        self.assertIn('round_id', round_data)
        self.assertEqual(round_data['preview_url'], SONG[3])
        self.assertNotIn('artist', round_data)
        self.assertNotIn('year', round_data)

    def test_start_round_retries_when_artist_not_found(self):
        with patch('server.fetch_metadata', side_effect=[ValueError(), ValueError(), SONG]) as mock_fetch:
            response = self.client.post('/api/rounds')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_fetch.call_count, 3)

    def test_start_round_gives_up_after_max_attempts(self):
        with patch('server.fetch_metadata', side_effect=ValueError()) as mock_fetch:
            response = self.client.post('/api/rounds')
        self.assertEqual(response.status_code, 502)
        self.assertEqual(mock_fetch.call_count, server.MAX_FETCH_ATTEMPTS)

    def test_correct_year_guess(self):
        round_id = self.start_round()['round_id']
        response = self.client.post(f'/api/rounds/{round_id}/guess', json={'year': 2022})
        self.assertEqual(response.json(), {'correct': True, 'points': 1, 'year': 2022})

    def test_wrong_year_guess_reveals_answer_with_hint(self):
        round_id = self.start_round()['round_id']
        result = self.client.post(f'/api/rounds/{round_id}/guess', json={'year': 1990}).json()
        self.assertEqual(result['correct'], False)
        self.assertEqual(result['points'], 0)
        self.assertEqual(result['hint'], 'Way off!')
        self.assertEqual(result['artist'], 'Ado')
        self.assertEqual(result['track'], 'Show')
        self.assertEqual(result['year'], 2022)

    def test_hint_tiers(self):
        for guess, expected_hint in [(2020, 'So Close!'), (2015, 'Close! But not close enough!'), (1990, 'Way off!')]:
            round_id = self.start_round()['round_id']
            result = self.client.post(f'/api/rounds/{round_id}/guess', json={'year': guess}).json()
            self.assertEqual(result['hint'], expected_hint)

    def test_round_is_consumed_after_wrong_guess(self):
        round_id = self.start_round()['round_id']
        self.client.post(f'/api/rounds/{round_id}/guess', json={'year': 1990})
        response = self.client.post(f'/api/rounds/{round_id}/guess', json={'year': 2022})
        self.assertEqual(response.status_code, 404)

    def test_guess_on_unknown_round_returns_404(self):
        response = self.client.post('/api/rounds/not-a-round/guess', json={'year': 2022})
        self.assertEqual(response.status_code, 404)

    def test_second_year_guess_rejected_while_bonus_pending(self):
        round_id = self.start_round()['round_id']
        self.client.post(f'/api/rounds/{round_id}/guess', json={'year': 2022})
        response = self.client.post(f'/api/rounds/{round_id}/guess', json={'year': 2022})
        self.assertEqual(response.status_code, 400)

    def test_bonus_flow_after_correct_guess(self):
        round_id = self.start_round()['round_id']
        self.client.post(f'/api/rounds/{round_id}/guess', json={'year': 2022})
        result = self.client.post(
            f'/api/rounds/{round_id}/bonus',
            json={'artist_guess': ' ado ', 'track_guess': 'Wrong'},
        ).json()
        self.assertEqual(result['artist_correct'], True)
        self.assertEqual(result['track_correct'], False)
        self.assertEqual(result['points'], 1)
        self.assertEqual(result['artist'], 'Ado')
        self.assertEqual(result['track'], 'Show')

    def test_bonus_rejected_before_correct_year_guess(self):
        round_id = self.start_round()['round_id']
        response = self.client.post(
            f'/api/rounds/{round_id}/bonus',
            json={'artist_guess': 'Ado', 'track_guess': 'Show'},
        )
        self.assertEqual(response.status_code, 404)

    def test_empty_artist_list_returns_400(self):
        with open(self.temp_file, 'w') as file:
            file.write('')
        response = self.client.post('/api/rounds')
        self.assertEqual(response.status_code, 400)

    def test_network_error_returns_502(self):
        import requests
        with patch('server.fetch_metadata', side_effect=requests.ConnectionError()):
            response = self.client.post('/api/rounds')
        self.assertEqual(response.status_code, 502)

    def test_abandoned_rounds_are_evicted(self):
        with patch.object(server, 'MAX_ACTIVE_ROUNDS', 3):
            round_ids = [self.start_round()['round_id'] for _ in range(5)]
        self.assertEqual(len(server.rounds), 3)
        # the oldest rounds were dropped, the newest still work
        self.assertNotIn(round_ids[0], server.rounds)
        response = self.client.post(f'/api/rounds/{round_ids[-1]}/guess', json={'year': 2022})
        self.assertEqual(response.status_code, 200)

    def test_round_is_consumed_after_bonus(self):
        round_id = self.start_round()['round_id']
        self.client.post(f'/api/rounds/{round_id}/guess', json={'year': 2022})
        self.client.post(f'/api/rounds/{round_id}/bonus', json={'artist_guess': 'x', 'track_guess': 'y'})
        response = self.client.post(f'/api/rounds/{round_id}/bonus', json={'artist_guess': 'x', 'track_guess': 'y'})
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
