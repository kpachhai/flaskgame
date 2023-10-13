import logging

from flask import Blueprint, jsonify, session
from flask_restful import Api, Resource, reqparse

from app.models.game import Game
from app.utils.exceptions import (InsufficientMoneyError,
                                  InsufficientSupplementError,
                                  InvalidCardIndexError)

game_blueprint = Blueprint('game', __name__)
api = Api(game_blueprint)

logging.basicConfig(level=logging.INFO)

class StartGame(Resource):
    """
    Resource for starting a new game.
    """

    def post(self):
        """
        Starts a new game based on the provided opponent type.

        Returns:
            dict: Response indicating success and the current game status.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('opponent_type', type=str, default="A")
        args = parser.parse_args()

        game_instance = Game(args['opponent_type'])
        game_instance.start()

        session['game_state'] = game_instance.get_state()
        session.modified = True

        return {
            'success': True,
            'current_status': game_instance.get_status()
        }

class PlayTurn(Resource):
    """
    Resource for playing a turn in the game.
    """

    def post(self):
        """
        Executes a turn based on the provided action and card index.

        Returns:
            dict: Response indicating the game status after the turn.
        """
        if 'game_state' not in session:
            return {"error": "Game not started. Please start a game first."}, 400

        parser = reqparse.RequestParser()
        parser.add_argument('action', type=str, required=True)
        parser.add_argument('card_index', type=int)
        args = parser.parse_args()

        game_instance = Game()
        game_instance.set_state(session['game_state'])

        try:
            game_instance.play_turn(args['action'], args['card_index'])
            session['game_state'] = game_instance.get_state()
            session.modified = True

            return self._get_game_status(game_instance)
        except ValueError as e:  # Catch invalid actions
            return {"success": False, "error": str(e)}, 400
        except (InvalidCardIndexError, InsufficientMoneyError, InsufficientSupplementError) as e:
            return {"success": False, "error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 400

    def _get_game_status(self, game_instance):
        """
        Retrieves the current game status.

        Args:
            game_instance (Game): The current game instance.

        Returns:
            dict: Response indicating the current game status.
        """
        # This function checks the game status and returns the appropriate response
        if 'game_state' not in session:
            return jsonify(error="Game not started. Please start a game first."), 400

        game_instance = Game()
        game_instance.set_state(session['game_state'])  # Set the game state from the session

        game_status, message, current_status = '', '', game_instance.get_status();
        # Check game end conditions after the turn is played
        if game_instance.pO['health'] <= 0:
            logging.info("Computer wins")
            game_status = 'ended'
            message = 'Computer wins'
        elif game_instance.pC['health'] <= 0:
            logging.info('Player wins')
            game_status = 'ended'
            message = 'Player wins'
        elif game_instance.central['activeSize'] == 0:
            logging.info("No more cards available")
            if game_instance.pO['health'] > game_instance.pC['health']:
                logging.info("Player wins on Health")
                game_status = 'ended'
                message = 'Player wins on Health'
            elif game_instance.pC['health'] > game_instance.pO['health']:
                logging.info("Computer wins")
                game_status = 'ended'
                message = 'Computer wins'
            else:
                logging.info("Draw")
                game_status = 'ended'
                message = 'The game ends in a draw'
        else:   
            game_status = 'running'
            message = 'The game is still ongoing' 
            
        return jsonify({
            'game_status': game_status,
            'message': message,
            'current_status': current_status if game_status == "running" else game_status
        })

class GameStatus(Resource):
    """
    Resource for retrieving the current game status.
    """

    def get(self):
        """
        Retrieves the current game status.

        Returns:
            dict: Response indicating the current game status.
        """
        if 'game_state' not in session:
            return {"error": "Game not started. Please start a game first."}, 400

        game_instance = Game()
        game_instance.set_state(session['game_state'])

        return PlayTurn()._get_game_status(game_instance)  # Reuse the game status function

api.add_resource(StartGame, '/start')
api.add_resource(PlayTurn, '/play_turn')
api.add_resource(GameStatus, '/status')