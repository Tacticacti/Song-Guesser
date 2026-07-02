import unittest
from unittest.mock import patch

import main
from main import bonus_point, evaluate_guess, change_volume, add_artist, remove_artist

class TestBonusPoint(unittest.TestCase):

    @patch('builtins.input', side_effect=['Ado', 'Show'])
    @patch('builtins.print')
    def test_both_guesses_correct(self, mock_print, mock_input):
        self.assertEqual(bonus_point('Ado', 'Show'), 2)

    @patch('builtins.input', side_effect=['Wrong', 'Wrong'])
    @patch('builtins.print')
    def test_both_guesses_wrong(self, mock_print, mock_input):
        self.assertEqual(bonus_point('Ado', 'Show'), 0)

    @patch('builtins.input', side_effect=['Ado', 'Wrong'])
    @patch('builtins.print')
    def test_one_guess_correct(self, mock_print, mock_input):
        self.assertEqual(bonus_point('Ado', 'Show'), 1)

class TestEvaluateGuess(unittest.TestCase):

    @patch('main.bonus_point', return_value=2)
    @patch('builtins.print')
    def test_correct_year_awards_point_and_bonus(self, mock_print, mock_bonus):
        score, strikes = evaluate_guess('Ado', 'Show', 2022, 2022, strikes=0, score=0)
        self.assertEqual(score, 3)
        self.assertEqual(strikes, 0)

    @patch('builtins.print')
    def test_wrong_year_adds_strike(self, mock_print):
        score, strikes = evaluate_guess('Ado', 'Show', 2022, 1990, strikes=1, score=5)
        self.assertEqual(score, 5)
        self.assertEqual(strikes, 2)

    def get_printed_output(self, mock_print):
        return ' '.join(str(call.args[0]) for call in mock_print.call_args_list if call.args)

    @patch('builtins.print')
    def test_hint_so_close(self, mock_print):
        evaluate_guess('Ado', 'Show', 2022, 2020, strikes=0, score=0)
        self.assertIn('So Close!', self.get_printed_output(mock_print))

    @patch('builtins.print')
    def test_hint_close(self, mock_print):
        evaluate_guess('Ado', 'Show', 2022, 2015, strikes=0, score=0)
        self.assertIn('Close! But not close enough!', self.get_printed_output(mock_print))

    @patch('builtins.print')
    def test_hint_way_off(self, mock_print):
        evaluate_guess('Ado', 'Show', 2022, 1990, strikes=0, score=0)
        self.assertIn('Way off!', self.get_printed_output(mock_print))

class TestChangeVolume(unittest.TestCase):

    def setUp(self):
        self.original_volume = main.game_settings['volume']

    def tearDown(self):
        main.game_settings['volume'] = self.original_volume

    @patch('builtins.input', return_value='55')
    @patch('builtins.print')
    def test_sets_volume(self, mock_print, mock_input):
        change_volume()
        self.assertEqual(main.game_settings['volume'], 55)

    @patch('builtins.input', return_value='500')
    @patch('builtins.print')
    def test_clamps_volume_above_100(self, mock_print, mock_input):
        change_volume()
        self.assertEqual(main.game_settings['volume'], 100)

    @patch('builtins.input', return_value='-20')
    @patch('builtins.print')
    def test_clamps_volume_below_0(self, mock_print, mock_input):
        change_volume()
        self.assertEqual(main.game_settings['volume'], 0)

    @patch('builtins.input', return_value='abc')
    @patch('builtins.print')
    def test_rejects_non_number(self, mock_print, mock_input):
        main.game_settings['volume'] = 70
        change_volume()
        self.assertEqual(main.game_settings['volume'], 70)

class TestArtistListManagement(unittest.TestCase):

    @patch('main.save_artist_pool')
    @patch('builtins.input', return_value='Queen')
    @patch('builtins.print')
    def test_add_artist(self, mock_print, mock_input, mock_save):
        pool = ['Ado']
        add_artist(pool)
        self.assertEqual(pool, ['Ado', 'Queen'])
        mock_save.assert_called_once_with(pool)

    @patch('main.save_artist_pool')
    @patch('builtins.input', return_value='ado')
    @patch('builtins.print')
    def test_add_duplicate_is_rejected_case_insensitively(self, mock_print, mock_input, mock_save):
        pool = ['Ado']
        add_artist(pool)
        self.assertEqual(pool, ['Ado'])
        mock_save.assert_not_called()

    @patch('main.save_artist_pool')
    @patch('builtins.input', return_value='   ')
    @patch('builtins.print')
    def test_add_empty_name_is_rejected(self, mock_print, mock_input, mock_save):
        pool = ['Ado']
        add_artist(pool)
        self.assertEqual(pool, ['Ado'])
        mock_save.assert_not_called()

    @patch('main.save_artist_pool')
    @patch('builtins.input', return_value='ADO')
    @patch('builtins.print')
    def test_remove_artist_case_insensitively(self, mock_print, mock_input, mock_save):
        pool = ['Ado', 'Eminem']
        remove_artist(pool)
        self.assertEqual(pool, ['Eminem'])
        mock_save.assert_called_once_with(pool)

    @patch('main.save_artist_pool')
    @patch('builtins.input', return_value='Ado')
    @patch('builtins.print')
    def test_cannot_remove_last_artist(self, mock_print, mock_input, mock_save):
        pool = ['Ado']
        remove_artist(pool)
        self.assertEqual(pool, ['Ado'])
        mock_save.assert_not_called()

    @patch('main.save_artist_pool')
    @patch('builtins.input', return_value='Nobody')
    @patch('builtins.print')
    def test_remove_missing_artist_does_nothing(self, mock_print, mock_input, mock_save):
        pool = ['Ado', 'Eminem']
        remove_artist(pool)
        self.assertEqual(pool, ['Ado', 'Eminem'])
        mock_save.assert_not_called()

if __name__ == '__main__':
    unittest.main()
