from app.models.game import Game
from app.utils.exceptions import (InsufficientMoneyError,
                                  InsufficientSupplementError,
                                  InvalidCardIndexError)
from tests.base import BaseTestCase


class TestGame(BaseTestCase):

    def setUp(self):
        super().setUp()  # Call the setUp of BaseTestCase
        self.game = Game()

    def test_initialization(self):
        self.assertTrue(isinstance(self.game, Game))
        self.assertEqual(self.game.aggressive, True)
        self.assertEqual(len(self.game.central['deck']), 9)
        self.assertEqual(len(self.game.central['active']), 5)
        self.assertEqual(len(self.game.central['supplement']), 1)
        self.assertEqual(len(self.game.pO['deck']), 10)
        self.assertEqual(len(self.game.pO['hand']), 5)
        self.assertEqual(len(self.game.pC['deck']), 10)
        self.assertEqual(len(self.game.pC['hand']), 5)

    def test_start(self):
        result = self.game.start()
        self.assertIn('central_available_cards', result)
        self.assertIn('central_supplement_card', result)
        
    def test_play_turn_play_all(self):
        self.game.play_turn("P")
        self.assertEqual(len(self.game.pO['hand']), 0)
        self.assertEqual(len(self.game.pO['active']), 5)

    def test_play_turn_play_that_card_valid_index(self):
        self.game.play_turn("C", 0)
        self.assertEqual(len(self.game.pO['hand']), 4)
        self.assertEqual(len(self.game.pO['active']), 1)

    def test_play_turn_play_that_card_invalid_index(self):
        with self.assertRaises(InvalidCardIndexError):
            self.game.play_turn("C", 10)

    def test_play_turn_buy_card_valid_index(self):
        self.game.pO['money'] = 10
        self.game.play_turn("B", 0)
        self.assertEqual(len(self.game.pO['discard']), 1)
        self.assertEqual(self.game.pO['money'], 10 - self.game.central['active'][0].cost)

    def test_play_turn_buy_card_insufficient_money(self):
        with self.assertRaises(InsufficientMoneyError):
            self.game.play_turn("B", 0)

    def test_get_status(self):
        status = self.game.get_status()
        self.assertIn('player', status)
        self.assertIn('computer', status)
        self.assertIn('central', status)

    def test_get_state_and_set_state(self):
        state = self.game.get_state()
        new_game = Game()
        new_game.set_state(state)
        self.assertEqual(self.game.pO['health'], new_game.pO['health'])
        self.assertEqual(self.game.pC['health'], new_game.pC['health'])
        # ... Continue with other assertions ...




