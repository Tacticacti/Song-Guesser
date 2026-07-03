import os
import tempfile
import unittest
from unittest.mock import patch

import leaderboard
from leaderboard import load_leaderboard, submit_score


class LeaderboardTestCase(unittest.TestCase):
    """Runs the real queries against a throwaway SQLite database."""

    def setUp(self):
        handle, self.temp_db = tempfile.mkstemp(suffix='.sqlite')
        os.close(handle)
        self.patcher = patch.object(leaderboard, 'DATABASE_URL', f'sqlite:///{self.temp_db}')
        self.patcher.start()
        leaderboard.reset_engine()

    def tearDown(self):
        leaderboard.reset_engine()
        self.patcher.stop()
        os.remove(self.temp_db)


class TestLoadLeaderboard(LeaderboardTestCase):

    def test_empty_on_a_fresh_database(self):
        self.assertEqual(load_leaderboard(), [])

    def test_returns_entries_sorted_by_score_descending(self):
        submit_score('Low', 1)
        submit_score('High', 9)
        submit_score('Mid', 4)
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

    def test_scores_survive_a_reconnect(self):
        submit_score('Ed', 3)
        # a new engine on the same database sees the stored score
        leaderboard.reset_engine()
        self.assertEqual(load_leaderboard(), [{'name': 'Ed', 'score': 3}])

    def test_leaderboard_stays_sorted_after_submissions(self):
        submit_score('Mid', 4)
        submit_score('High', 9)
        _, _, entries = submit_score('Low', 1)
        self.assertEqual([entry['name'] for entry in entries], ['High', 'Mid', 'Low'])


if __name__ == '__main__':
    unittest.main()
