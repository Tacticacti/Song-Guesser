import json
import os
import tempfile
import unittest
from unittest.mock import patch

import leaderboard
from leaderboard import load_leaderboard, submit_score


class LeaderboardTestCase(unittest.TestCase):

    def setUp(self):
        handle, self.temp_file = tempfile.mkstemp(suffix='.json')
        os.close(handle)
        os.remove(self.temp_file)  # start without a file, like a fresh install
        self.patcher = patch.object(leaderboard, 'LEADERBOARD_FILE', self.temp_file)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def write_file(self, content):
        with open(self.temp_file, 'w') as file:
            file.write(content)


class TestLoadLeaderboard(LeaderboardTestCase):

    def test_empty_when_file_missing(self):
        self.assertEqual(load_leaderboard(), [])

    def test_empty_when_file_is_corrupt(self):
        self.write_file('not json {')
        self.assertEqual(load_leaderboard(), [])

    def test_empty_when_file_is_not_a_list(self):
        self.write_file('{"name": "Ed", "score": 3}')
        self.assertEqual(load_leaderboard(), [])

    def test_skips_malformed_entries(self):
        self.write_file(json.dumps([
            {'name': 'Ed', 'score': 3},
            {'name': 'NoScore'},
            {'score': 5},
            {'name': 'BadScore', 'score': 'five'},
            'not a dict',
        ]))
        self.assertEqual(load_leaderboard(), [{'name': 'Ed', 'score': 3}])

    def test_returns_entries_sorted_by_score_descending(self):
        self.write_file(json.dumps([
            {'name': 'Low', 'score': 1},
            {'name': 'High', 'score': 9},
            {'name': 'Mid', 'score': 4},
        ]))
        self.assertEqual([entry['name'] for entry in load_leaderboard()], ['High', 'Mid', 'Low'])


class TestSubmitScore(LeaderboardTestCase):

    def test_first_score_is_a_new_best(self):
        new_best, best_score, entries = submit_score('Ed', 3)
        self.assertTrue(new_best)
        self.assertEqual(best_score, 3)
        self.assertEqual(entries, [{'name': 'Ed', 'score': 3}])

    def test_higher_score_overrides_the_same_name(self):
        submit_score('Ed', 3)
        new_best, best_score, entries = submit_score('Ed', 7)
        self.assertTrue(new_best)
        self.assertEqual(best_score, 7)
        self.assertEqual(entries, [{'name': 'Ed', 'score': 7}])

    def test_lower_score_does_not_override(self):
        submit_score('Ed', 7)
        new_best, best_score, entries = submit_score('Ed', 3)
        self.assertFalse(new_best)
        self.assertEqual(best_score, 7)
        self.assertEqual(entries, [{'name': 'Ed', 'score': 7}])

    def test_equal_score_is_not_a_new_best(self):
        submit_score('Ed', 7)
        new_best, best_score, entries = submit_score('Ed', 7)
        self.assertFalse(new_best)
        self.assertEqual(entries, [{'name': 'Ed', 'score': 7}])

    def test_names_match_case_insensitively_and_keep_the_new_casing(self):
        submit_score('ed', 3)
        new_best, best_score, entries = submit_score('ED', 7)
        self.assertTrue(new_best)
        self.assertEqual(entries, [{'name': 'ED', 'score': 7}])

    def test_scores_persist_to_the_file(self):
        submit_score('Ed', 3)
        with open(self.temp_file) as file:
            self.assertEqual(json.load(file), [{'name': 'Ed', 'score': 3}])

    def test_leaderboard_stays_sorted_after_submissions(self):
        submit_score('Mid', 4)
        submit_score('High', 9)
        _, _, entries = submit_score('Low', 1)
        self.assertEqual([entry['name'] for entry in entries], ['High', 'Mid', 'Low'])


if __name__ == '__main__':
    unittest.main()
