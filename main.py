import random
import tempfile

from flask import Flask, jsonify, request, session

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'

class Card:
    def __init__(self, name, cost, attack, money):
        self.name = name
        self.cost = cost
        self.attack = attack
        self.money = money

    def to_dict(self):
        return {
            'name': self.name,
            'cost': self.cost,
            'attack': self.attack,
            'money': self.money
        }

class InvalidCardIndexError(Exception):
    """Exception raised for invalid card index."""
    pass

class InsufficientMoneyError(Exception):
    """Exception raised for insufficient money to buy a card."""
    pass

class Game:
    def __init__(self, opponent_type="A"):
        self.aggressive = True if opponent_type == "A" or opponent_type == "Aggressive" else False
        self.central = {
            'name': 'central',
            'active': [],
            'activeSize': 5,
            'supplement': [],
            'deck': []
        }
        self.pO = {
            'name': 'player one',
            'health': 30,
            'deck': [],
            'hand': [],
            'active': [],
            'handsize': 5,
            'discard': [],
            'money': 0,
            'attack': 0
        }
        self.pC = {
            'name': 'player computer',
            'health': 30,
            'deck': [],
            'hand': [],
            'active': [],
            'handsize': 5,
            'discard': [],
            'money': 0,
            'attack': 0
        }
        self._initialize_game()

    def _initialize_game(self):
        # Initialize central deck with a set of cards
        self.central['deck'] = [
            Card("Thug", 1, 2, 0),
            Card("Crossbowman", 3, 4, 0),
            Card("Baker", 2, 0, 3),
            Card("Knight", 5, 6, 0),
            Card("Catapault", 6, 7, 0),
            Card("Swordsman", 3, 4, 0),
            Card("Thief", 1, 1, 1),
            Card("Archer", 2, 3, 0),
            Card("Tailor", 3, 0, 4)
        ]

        # Shuffle the central deck
        random.shuffle(self.central['deck'])

        # Draw 5 cards to form the active central cards
        self.central['active'] = [self.central['deck'].pop() for _ in range(5)]

        # Set the supplement card
        self.central['supplement'] = [Card("Levy", 2, 1, 2)]

        # Initialize player's decks with basic cards
        self.pO['deck'] = [Card("Serf", 0, 0, 1) for _ in range(7)] + [Card("Squire", 0, 1, 0) for _ in range(3)]
        self.pC['deck'] = [Card("Serf", 0, 0, 1) for _ in range(7)] + [Card("Squire", 0, 1, 0) for _ in range(3)]

        # Shuffle player decks
        random.shuffle(self.pO['deck'])
        random.shuffle(self.pC['deck'])

    def start(self):
        # Draw initial cards for players
        for _ in range(self.pO['handsize']):
            self.pO['hand'].append(self.pO['deck'].pop())
            self.pC['hand'].append(self.pC['deck'].pop())
        
        return {
            'central_available_cards': [{'card_index': index, **card.to_dict()} for index, card in enumerate(self.central['active'])],
            'central_supplement_card': {'card_index': len(self.central['active']), **self.central['supplement'][0].to_dict()}
        }

    def play_turn(self, action, card_index=None):
        if action == "P" or action == "play_all":
            for card in self.pO['hand']:
                self.pO['money'] += card.money
                self.pO['attack'] += card.attack
                self.pO['active'].append(card)
            self.pO['hand'] = []

        elif action == "C" or action == "play_that_card":
            if 0 <= card_index < len(self.pO['hand']):
                card = self.pO['hand'].pop(card_index)
                self.pO['money'] += card.money
                self.pO['attack'] += card.attack
                self.pO['active'].append(card)
            else:
                raise InvalidCardIndexError(f"Invalid card index: {card_index}.")

        elif action == "B" or action == "buy_card":
            if card_index == len(self.central['active']):  # Buying from the supplement
                if self.pO['money'] >= self.central['supplement'][0].cost:
                    self.pO['money'] -= self.central['supplement'][0].cost
                    self.pO['discard'].append(self.central['supplement'].pop())
                else:
                    raise InsufficientMoneyError(f"Insufficient money to buy the supplement card.")
            elif 0 <= card_index < len(self.central['active']):
                card_to_buy = self.central['active'][card_index]
                if self.pO['money'] >= card_to_buy.cost:
                    self.pO['money'] -= card_to_buy.cost
                    self.pO['discard'].append(self.central['active'].pop(card_index))
                    
                    # Refill the central active cards if there are cards left in the central deck
                    if self.central['deck']:
                        self.central['active'].append(self.central['deck'].pop())
                    else:
                        self.central['activeSize'] -= 1
                else:
                    raise InsufficientMoneyError(f"Insufficient money to buy {card_to_buy.name}.")
            else:
                raise InvalidCardIndexError(f"Invalid card index: {card_index}.")

        elif action == "A" or action == "attack":
            self.pC['health'] -= self.pO['attack']
            self.pO['attack'] = 0

        elif action == "E" or action == "end_turn":
            # Move all cards from the player's hand to the discard pile
            while self.pO['hand']:
                self.pO['discard'].append(self.pO['hand'].pop())
            
            # Move all active cards to the discard pile
            while self.pO['active']:
                self.pO['discard'].append(self.pO['active'].pop())
            
            # Draw new cards up to the player's hand size
            for _ in range(self.pO['handsize']):
                if not self.pO['deck']:
                    random.shuffle(self.pO['discard'])
                    self.pO['deck'], self.pO['discard'] = self.pO['discard'], self.pO['deck']
                self.pO['hand'].append(self.pO['deck'].pop())
                
        
        # Computer's turn
        money = 0
        attack = 0
        while self.pC['hand']:
            card = self.pC['hand'].pop()
            self.pC['active'].append(card)
            money += card.money
            attack += card.attack
        
        self.pO['health'] -= attack
        attack = 0
        
        # Computer buying logic
        if money > 0:
            cb = True
            while cb:
                templist = []
                if self.central['supplement']:
                    if self.central['supplement'][0].cost <= money:
                        templist.append(("S", self.central['supplement'][0]))
                for intindex in range(len(self.central['active'])):
                    if self.central['active'][intindex].cost <= money:
                        templist.append((intindex, self.central['active'][intindex]))

                if templist:
                    highestIndex = 0
                    for intindex in range(len(templist)):
                        if templist[intindex][1].cost > templist[highestIndex][1].cost:
                            highestIndex = intindex
                        elif templist[intindex][1].cost == templist[highestIndex][1].cost:
                            if self.aggressive:
                                if templist[intindex][1].attack > templist[highestIndex][1].attack:
                                    highestIndex = intindex
                            else:
                                if templist[intindex][1].money > templist[highestIndex][1].money:
                                    highestIndex = intindex

                    source = templist[highestIndex][0]
                    if isinstance(source, int):
                        if money >= self.central['active'][source].cost:
                            money -= self.central['active'][source].cost
                            card = self.central['active'].pop(source)
                            print("Card bought %s" % card)
                            self.pC['discard'].append(card)
                            if self.central['deck']:
                                card = self.central['deck'].pop()
                                self.central['active'].append(card)
                            else:
                                # This assumes that 'activeSize' is a property that keeps track of the number of active cards
                                self.central['activeSize'] -= 1
                        else:
                            print("Error Occurred")
                    else:  # Supplement
                        if money >= self.central['supplement'][0].cost:
                            money -= self.central['supplement'][0].cost
                            card = self.central['supplement'].pop()
                            self.pC['discard'].append(card)
                            print("Supplement Bought %s" % card)
                        else:
                            print("Error Occurred")
                else:
                    cb = False

                if money == 0:
                    cb = False
        
        # Computer ending its turn
        while self.pC['hand']:
            self.pC['discard'].append(self.pC['hand'].pop())
        while self.pC['active']:
            self.pC['discard'].append(self.pC['active'].pop())
        for _ in range(self.pC['handsize']):
            if not self.pC['deck']:
                random.shuffle(self.pC['discard'])
                self.pC['deck'], self.pC['discard'] = self.pC['discard'], self.pC['deck']
            self.pC['hand'].append(self.pC['deck'].pop())

    def get_status(self):
        return {
            'player': {
                'health': self.pO['health'],
                'hand': [{'card_index': index, **card.to_dict()} for index, card in enumerate(self.pO['hand'])],
                'active': [card.to_dict() for card in self.pO['active']],
                'values': {
                    'money': self.pO['money'],
                    'attack': self.pO['attack']
                }                
            },
            'computer': {
                'health': self.pC['health'],
                'hand': [{'card_index': index, **card.to_dict()} for index, card in enumerate(self.pC['hand'])],
                'active': [card.to_dict() for card in self.pC['active']],
                'values': {
                    'money': self.pC['money'],
                    'attack': self.pC['attack']
                }       
            },
            'central': {
                'available_cards': [{'card_index': index, **card.to_dict()} for index, card in enumerate(self.central['active'])],
                'supplement_card': {'card_index': len(self.central['active']), **self.central['supplement'][0].to_dict()}
            },
            'next_action': [{"endpoint": "/play_turn", "action": "play_all"}, {"endpoint": "/play_turn", "action": "play_that_card", "card_index": '[0-n]'}, {"endpoint": "/play_turn", "action": "buy_card", "card_index": '[0-n]'}, {"endpoint": "/play_turn", "action": "attack"}, {"endpoint": "/play_turn", "action": "end_turn"}]
        }
    
    def get_state(self):
        state = {
            'aggressive': self.aggressive,
            'central_deck': [card.to_dict() for card in self.central['deck']],
            'central_active': [card.to_dict() for card in self.central['active']],
            'central_supplement': [card.to_dict() for card in self.central['supplement']],
            'pO_deck': [card.to_dict() for card in self.pO['deck']],
            'pO_hand': [card.to_dict() for card in self.pO['hand']],
            'pO_active': [card.to_dict() for card in self.pO['active']],
            'pO_discard': [card.to_dict() for card in self.pO['discard']],
            'pC_deck': [card.to_dict() for card in self.pC['deck']],
            'pC_hand': [card.to_dict() for card in self.pC['hand']],
            'pC_active': [card.to_dict() for card in self.pC['active']],
            'pC_discard': [card.to_dict() for card in self.pC['discard']]
        }
        return state

    def set_state(self, state):
        self.aggressive = state['aggressive']
        self.central['deck'] = [Card(**card_data) for card_data in state['central_deck']]
        self.central['active'] = [Card(**card_data) for card_data in state['central_active']]
        self.central['supplement'] = [Card(**card_data) for card_data in state['central_supplement']]
        self.pO['deck'] = [Card(**card_data) for card_data in state['pO_deck']]
        self.pO['hand'] = [Card(**card_data) for card_data in state['pO_hand']]
        self.pO['active'] = [Card(**card_data) for card_data in state['pO_active']]
        self.pO['discard'] = [Card(**card_data) for card_data in state['pO_discard']]
        self.pC['deck'] = [Card(**card_data) for card_data in state['pC_deck']]
        self.pC['hand'] = [Card(**card_data) for card_data in state['pC_hand']]
        self.pC['active'] = [Card(**card_data) for card_data in state['pC_active']]
        self.pC['discard'] = [Card(**card_data) for card_data in state['pC_discard']]

@app.route('/start', methods=['POST'])
def start_game():
    opponent_type = request.json.get('opponent_type', "A")
    game_instance = Game(opponent_type)
    game_instance.start()
    
    # Save the game state to the session after converting all Card objects to dictionaries
    session['game_state'] = game_instance.get_state()

    response = {
        'success': True,
        'current_status': game_instance.get_status()
    }

    return jsonify(response)

@app.route('/play_turn', methods=['POST'])
def play_turn():
    if 'game_state' not in session:
        return jsonify(error="Game not started. Please start a game first."), 400

    game_instance = Game()
    game_instance.set_state(session['game_state'])

    # Check if the game has already ended
    if game_instance.pO['health'] <= 0:
        return jsonify(error="Game has ended. Computer wins."), 400
    elif game_instance.pC['health'] <= 0:
        return jsonify(error="Game has ended. Player wins."), 400

    action = request.json.get('action')
    card_index = request.json.get('card_index')
    
    try:
        game_instance.play_turn(action, card_index)
        session['game_state'] = game_instance.get_state()
        return jsonify(success=True)
    except (InvalidCardIndexError, InsufficientMoneyError) as e:
        return jsonify(error=str(e)), 400

@app.route('/status', methods=['GET'])
def get_status():
    if 'game_state' not in session:
        return jsonify(error="Game not started. Please start a game first."), 400

    game_instance = Game()
    game_instance.set_state(session['game_state'])
    
    # Check for game end condition
    if game_instance.pO['health'] <= 0:
        return jsonify({
            'game_status': 'ended',
            'message': 'Computer wins'
        })
    elif game_instance.pC['health'] <= 0:
        return jsonify({
            'game_status': 'ended',
            'message': 'Player wins'
        })

    return jsonify(game_instance.get_status())

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
