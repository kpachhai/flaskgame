from tests.base import BaseTestCase


class TestGameRoutes(BaseTestCase):

    # Tests related to starting a game
    def test_start_game_with_aggressive_opponent(self):
        """Test starting a game with an aggressive opponent."""
        response = self.client.post('/start', json={'opponent_type': 'A'})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])

    def test_start_game_with_acquisitive_opponent(self):
        """Test starting a game with an acquisitive opponent."""
        response = self.client.post('/start', json={'opponent_type': 'Q'})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])

    def test_start_game_with_default_opponent(self):
        """Test starting a game with an invalid opponent type defaults to 'A'."""
        response = self.client.post('/start', json={'opponent_type': 'INVALID_TYPE'})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])

    def test_start_game_twice(self):
        """Test starting a game twice in a row."""
        self.client.post('/start', json={'opponent_type': 'A'})
        response = self.client.post('/start', json={'opponent_type': 'A'})
        self.assertEqual(response.status_code, 200)  # Should handle gracefully

    def test_start_game_with_empty_opponent_type(self):
        """Test starting a game with an empty opponent type."""
        response = self.client.post('/start', json={'opponent_type': ''})
        self.assertEqual(response.status_code, 200)  # Should default to 'A'

    def test_start_game_with_numeric_opponent_type(self):
        """Test starting a game with a numeric opponent type."""
        response = self.client.post('/start', json={'opponent_type': 123})
        self.assertEqual(response.status_code, 200)  # Should default to 'A'

    def test_start_game_with_special_character_opponent_type(self):
        """Test starting a game with a special character opponent type."""
        response = self.client.post('/start', json={'opponent_type': '@#%'})
        self.assertEqual(response.status_code, 200)  # Should default to 'A'

    # Tests related to playing a turn
    def test_play_turn_without_starting_game(self):
        """Test playing a turn without starting a game."""
        response = self.client.post('/play_turn', json={'action': 'P'})
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertEqual(data['error'], "Game not started. Please start a game first.")

    def test_play_turn_with_invalid_action(self):
        """Test playing a turn with an invalid action."""
        self.client.post('/start', json={'opponent_type': 'A'})
        response = self.client.post('/play_turn', json={'action': 'INVALID_ACTION'})
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)

    # Tests related to game status
    def test_game_status_without_starting_game(self):
        """Test checking game status without starting a game."""
        response = self.client.get('/status')
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertEqual(data['error'], "Game not started. Please start a game first.")

    def test_game_status_after_starting_game(self):
        """Test checking game status after starting a game."""
        self.client.post('/start', json={'opponent_type': 'A'})
        response = self.client.get('/status')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('game_status', data)
        self.assertIn('message', data)
        self.assertIn('current_status', data)

    # Tests related to card actions during a turn
    def test_play_turn_with_valid_card_index(self):
        """Test playing a turn with a valid card index."""
        self.client.post('/start', json={'opponent_type': 'A'})
        response = self.client.post('/play_turn', json={'action': 'play_that_card', 'card_index': 0})
        self.assertEqual(response.status_code, 200)

    def test_play_turn_with_out_of_range_card_index(self):
        """Test playing a turn with an out-of-range card index."""
        self.client.post('/start', json={'opponent_type': 'A'})
        response = self.client.post('/play_turn', json={'action': 'play_that_card', 'card_index': 10})
        self.assertEqual(response.status_code, 400)

    def test_play_turn_with_negative_card_index(self):
        """Test playing a turn with a negative card index."""
        self.client.post('/start', json={'opponent_type': 'A'})
        response = self.client.post('/play_turn', json={'action': 'play_that_card', 'card_index': -1})
        self.assertEqual(response.status_code, 400)

    def test_play_turn_with_non_integer_card_index(self):
        """Test playing a turn with a non-integer card index."""
        self.client.post('/start', json={'opponent_type': 'A'})
        response = self.client.post('/play_turn', json={'action': 'play_that_card', 'card_index': 'invalid'})
        self.assertEqual(response.status_code, 400)

    # Tests related to game status after specific actions
    def test_game_status_after_playing_all_cards(self):
        """Test game status after playing all cards."""
        self.client.post('/start', json={'opponent_type': 'A'})
        self.client.post('/play_turn', json={'action': 'play_all'})
        response = self.client.get('/status')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['game_status'], 'running')

    def test_game_status_after_buying_card(self):
        """Test game status after buying a card."""
        self.client.post('/start', json={'opponent_type': 'A'})
        self.client.post('/play_turn', json={'action': 'buy_card', 'card_index': 0})
        response = self.client.get('/status')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['game_status'], 'running')

    def test_game_status_after_attack(self):
        """Test game status after an attack."""
        self.client.post('/start', json={'opponent_type': 'A'})
        self.client.post('/play_turn', json={'action': 'attack'})
        response = self.client.get('/status')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['game_status'], 'running')

    def test_game_status_after_ending_turn(self):
        """Test game status after ending a turn."""
        self.client.post('/start', json={'opponent_type': 'A'})
        self.client.post('/play_turn', json={'action': 'end_turn'})
        response = self.client.get('/status')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['game_status'], 'running')

    # Tests related to missing or incorrect parameters
    def test_play_turn_missing_action(self):
        """Test playing a turn without specifying an action."""
        self.client.post('/start', json={'opponent_type': 'A'})
        response = self.client.post('/play_turn', json={'card_index': 0})
        self.assertEqual(response.status_code, 400)

    def test_play_turn_missing_card_index(self):
        """Test playing a turn without specifying a card index."""
        self.client.post('/start', json={'opponent_type': 'A'})
        response = self.client.post('/play_turn', json={'action': 'play_that_card'})
        self.assertEqual(response.status_code, 400)
