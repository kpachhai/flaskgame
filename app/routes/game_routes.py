import logging

from flask import Blueprint, jsonify, request, session

from app.models.game import Game
from app.utils.exceptions import (InsufficientMoneyError,
                                  InsufficientSupplementError,
                                  InvalidCardIndexError)

game_blueprint = Blueprint('game', __name__)

logging.basicConfig(level=logging.INFO)

@game_blueprint.route('/start', methods=['POST'])
def start_game():
    opponent_type = request.json.get('opponent_type', "A")
    game_instance = Game(opponent_type)
    game_instance.start()
    
    # Save the game state to the session
    session['game_state'] = game_instance.get_state()
    session.modified = True
    
    response = {
        'success': True,
        'current_status': game_instance.get_status()
    }

    return jsonify(response)

@game_blueprint.route('/play_turn', methods=['POST'])
def play_turn():
    if 'game_state' not in session:
        return jsonify(error="Game not started. Please start a game first."), 400
    
    game_instance = Game()
    game_instance.set_state(session['game_state'])

    action = request.json.get('action')
    
    card_index = request.json.get('card_index')
    
    try:
        game_instance.play_turn(action, card_index)
        # Save the game state to the session
        session['game_state'] = game_instance.get_state()
        session.modified = True
        
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
                print ("Player wins on Health")
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
    except (InvalidCardIndexError, InsufficientMoneyError, InsufficientSupplementError) as e:
        return jsonify(success=False, error=str(e)), 400
    except Exception as e:
        return jsonify(error=str(e)), 400
        

@game_blueprint.route('/status', methods=['GET'])
def get_status():
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

