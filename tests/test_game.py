from app.models.game import Game
from app.utils.exceptions import (InsufficientMoneyError,
                                  InsufficientSupplementError,
                                  InvalidCardIndexError)
from tests.base import BaseTestCase
from app.models.card import Card
from unittest.mock import patch

class TestGame(BaseTestCase):

    def setUp(self):
        super().setUp()  # Call the setUp of BaseTestCase
        self.game = Game()
        self.game.start()

    # Initialization and Setup Tests
    def test_initialization(self):
        """Test the initial state of the game after creation."""
        self.assertTrue(isinstance(self.game, Game))
        self.assertEqual(self.game.aggressive, True)
        self.assertEqual(len(self.game.central['deck']), 4)
        self.assertEqual(len(self.game.central['active']), 5)
        self.assertEqual(len(self.game.central['supplement']), 1)
        self.assertEqual(len(self.game.pO['deck']), 5)
        self.assertEqual(len(self.game.pO['hand']), 5)
        self.assertEqual(len(self.game.pC['deck']), 5)
        self.assertEqual(len(self.game.pC['hand']), 5)

    def test_start(self):
        """Test the start method of the game."""
        result = self.game.start()
        self.assertIn('central_available_cards', result)
        self.assertIn('central_supplement_card', result)
        
    # Player Action Tests
    def test_play_turn_play_all(self):
        """Test playing all cards in a turn."""
        self.game.play_turn("P")
        self.assertEqual(len(self.game.pO['hand']), 0)
        self.assertEqual(len(self.game.pO['active']), 5)

    def test_play_turn_play_that_card_valid_index(self):
        """Test playing a specific card with a valid index."""
        self.game.play_turn("C", 0)
        self.assertEqual(len(self.game.pO['hand']), 4)
        self.assertEqual(len(self.game.pO['active']), 1)

    def test_play_turn_play_that_card_invalid_index(self):
        """Test playing a card with an invalid index."""
        with self.assertRaises(InvalidCardIndexError):
            self.game.play_turn("C", 10)

    def test_play_turn_buy_card_valid_index(self):
        """Test buying a card with a valid index."""
        self.game.pO['money'] = 10
        card_cost = self.game.central['active'][0].cost
        self.game.play_turn("B", 0)
        self.assertEqual(len(self.game.pO['discard']), 1)
        self.assertEqual(self.game.pO['money'], 10 - card_cost)

    def test_play_turn_buy_card_insufficient_money(self):
        """Test buying a card with insufficient money."""
        with self.assertRaises(InsufficientMoneyError):
            self.game.play_turn("B", 0)

    def test_play_turn_attack(self):
        """Test player attacking the computer."""
        self.game.pO['attack'] = 5
        initial_computer_health = self.game.pC['health']
        self.game.play_turn("A")
        self.assertEqual(self.game.pC['health'], initial_computer_health - 5)

    def test_play_turn_end_turn(self):
        """Test ending the player's turn."""
        self.game.play_turn("E")
        self.assertEqual(len(self.game.pO['hand']), 5)
        self.assertEqual(len(self.game.pO['active']), 0)
        self.assertEqual(len(self.game.pO['discard']), 5)

    def test_play_turn_buy_supplement(self):
        """Test buying a supplement card."""
        self.game.pO['money'] = 10
        supplement_cost = self.game.central['supplement'][0].cost
        self.game.play_turn("B", len(self.game.central['active']))
        self.assertEqual(len(self.game.pO['discard']), 1)
        self.assertEqual(self.game.pO['money'], 10 - supplement_cost)

    def test_play_turn_buy_supplement_insufficient(self):
        """Test buying a supplement card when none are available."""
        self.game.central['supplement'] = []
        with self.assertRaises(InsufficientSupplementError):
            self.game.play_turn("B", len(self.game.central['active']))
            
    # Edge Cases and Special Scenarios
    def test_deck_refill(self):
        """Test refilling the deck from the discard pile."""
        self.game.pO['deck'] = []
        self.game.pO['discard'] = [Card("TestCard", 1, 1, 1) for _ in range(5)]
        self.game.play_turn("E")
        self.assertEqual(len(self.game.pO['deck']), 5)

    def test_negative_money(self):
        """Test scenarios where player's money might go negative."""
        self.game.pO['money'] = 1
        card_cost = self.game.central['active'][0].cost
        if card_cost > 1:
            with self.assertRaises(InsufficientMoneyError):
                self.game.play_turn("B", 0)

    def test_over_attack(self):
        """Test attacking with a value higher than the opponent's health."""
        self.game.pO['attack'] = 1000
        self.game.play_turn("A")
        self.assertTrue(self.game.pC['health'] <= 0)

    def test_player_health_zero(self):
        self.game.pO['health'] = 1
        self.game.pC['attack'] = 5
        self.game.play_turn("E")  # Assuming computer attacks after player's turn
        self.assertTrue(self.game.pO['health'] <= 0)

    def test_computer_health_zero(self):
        """Test scenarios where player's health drops to zero or below."""
        self.game.pC['health'] = 1
        self.game.pO['attack'] = 5
        self.game.play_turn("A")
        self.assertTrue(self.game.pC['health'] <= 0)

    # Game State Tests
    def test_get_status(self):
        """Test retrieving the current game status."""
        status = self.game.get_status()
        self.assertIn('player', status)
        self.assertIn('computer', status)
        self.assertIn('central', status)

    def test_get_state_and_set_state(self):
        """Test getting and setting the game state."""
        state = self.game.get_state()
        new_game = Game()
        new_game.set_state(state)
        self.assertEqual(self.game.pO['health'], new_game.pO['health'])
        self.assertEqual(self.game.pC['health'], new_game.pC['health'])
