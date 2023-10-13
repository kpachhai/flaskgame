import logging
import random

from app.models.card import Card
from app.utils.exceptions import (InsufficientMoneyError,
                                  InsufficientSupplementError,
                                  InvalidCardIndexError)

logging.basicConfig(level=logging.INFO)

class Game:
    def __init__(self, opponent_type="A"):
        self.aggressive = opponent_type in ["A", "Aggressive"]
        self.central = {
            'name': 'central',
            'active': [],
            'activeSize': 5,
            'supplement': [],
            'deck': []
        }
        self.pO = self._initialize_player('player one')
        self.pC = self._initialize_player('player computer')
        self._initialize_game()

    def _initialize_player(self, name):
        return {
            'name': name,
            'health': 30,
            'deck': [],
            'hand': [],
            'active': [],
            'handsize': 5,
            'discard': [],
            'money': 0,
            'attack': 0
        }

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
        
        logging.info("Available Cards")
        for card in self.central['active']:
            logging.info(f"Name {card.name} costing {card.cost} with attack {card.attack} and money {card.money}")
        logging.info("Supplement")
        for card in self.central['supplement']:
            logging.info(f"Name {card.name} costing {card.cost} with attack {card.attack} and money {card.money}")
        logging.info(f"Do you want an aggressive (A) opponent or an acquisative (Q) opponent: {'aggressive' if self.aggressive else 'acquisative'}")
        logging.info(f"Player Health: {self.pO['health']}")
        logging.info(f"Computer Health: {self.pC['health']}")
        logging.info("Your Hand")
        for index, card in enumerate(self.pO['hand']):
            logging.info(f"[{index}] Name {card.name} costing {card.cost} with attack {card.attack} and money {card.money}")
        logging.info("Your Values")
        logging.info(f"Money {self.pO['money']}, Attack {self.pO['attack']}")
        
        return {
            'central_available_cards': [{'card_index': index, **card.to_dict()} for index, card in enumerate(self.central['active'])],
            'central_supplement_card': [{'card_index': index + len(self.central['active']), **card.to_dict()} for index, card in enumerate(self.central['supplement'])]            
        }

    def play_turn(self, action, card_index=None):
        logging.info(f"Enter Action: {action}")
        logging.info(action)            
        
        if(card_index):
            try:
                card_index = int(card_index)
            except InvalidCardIndexError as e:
                logging.info(f"Invalid card index: {card_index}")
                raise InvalidCardIndexError(f"Invalid card index: {card_index}")
        
        if action == "P" or action == "play_all":
            for card in self.pO['hand']:
                self.pO['money'] += card.money
                self.pO['attack'] += card.attack
                self.pO['active'].append(card)
            self.pO['hand'] = []

        elif action == "C" or action == "play_that_card":
            if 0 <= card_index < len(self.pO['hand']):
                card = self.pO['hand'].pop(card_index)
                logging.info(f"Played: {card.to_dict()}")
                self.pO['money'] += card.money
                self.pO['attack'] += card.attack
                self.pO['active'].append(card)
            else:
                logging.info(f"Invalid card index: {card_index}")
                raise InvalidCardIndexError(f"Invalid card index: {card_index}")

        elif action == "B" or action == "buy_card":
            if card_index == len(self.central['active']):  # Buying from the supplement
                if(len(self.central['supplement']) > 0):
                    if self.pO['money'] >= self.central['supplement'][0].cost:
                        self.pO['money'] -= self.central['supplement'][0].cost
                        self.pO['discard'].append(self.central['supplement'].pop())
                        logging.info("Supplement Bought")
                    else:
                        logging.info(f"Insufficient money to buy the supplement card. This card costs {self.central['supplement'][0].cost} but you only have {self.pO['money']}")
                        raise InsufficientMoneyError(f"Insufficient money to buy the supplement card. This card costs {self.central['supplement'][0].cost} but you only have {self.pO['money']}")
                else:
                    logging.info("No supplements left")
                    raise InsufficientSupplementError("No supplements left")
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
                    logging.info(f"Card bought Name {card_to_buy.name} costing {card_to_buy.cost} with attack {card_to_buy.attack} and money {card_to_buy.money}")
                else:
                    logging.info (f"Insufficient money to buy {card_to_buy.name}")
                    raise InsufficientMoneyError(f"Insufficient money to buy {card_to_buy.name}. This card costs {card_to_buy.cost} but you only have {self.pO['money']}")
            else:
                logging.info (f"Invalid card index: {card_index}")
                raise InvalidCardIndexError(f"Invalid card index: {card_index}")

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
                
            logging.info("Available Cards")
            for card in self.central['active']:
                logging.info(f"Name {card.name} costing {card.cost} with attack {card.attack} and money {card.money}")
            logging.info("Supplement")
            for card in self.central['supplement']:
                logging.info(f"Name {card.name} costing {card.cost} with attack {card.attack} and money {card.money}")
                
            logging.info(f"Player Health: {self.pO['health']}")
            logging.info(f"Computer Health: {self.pC['health']}")
        
            # Computer's turn
            money = 0
            attack = 0
            while self.pC['hand']:
                card = self.pC['hand'].pop()
                self.pC['active'].append(card)
                money += card.money
                attack += card.attack
            
            logging.info(f"  Computer player values attack {attack}, money {money}")
            logging.info(f"  Computer attacking with strength {attack}")
            self.pO['health'] -= attack
            attack = 0
            
            logging.info(f"Player Health: {self.pO['health']}")
            logging.info(f"Computer Health: {self.pC['health']}")
            logging.info(f"  Computer player values attack {attack}, money {money}")
            logging.info(f"Computer buying")
            
            # Computer buying logic
            if money > 0:
                logging.info(f"Starting Money {money}")
                while True:
                    templist = []
                    if(len(self.central['supplement']) > 0):
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
                                logging.info(f"Card bought Name {card.name} costing {card.cost} with attack {card.attack} and money {card.money}")
                                self.pC['discard'].append(card)
                                if self.central['deck']:
                                    card = self.central['deck'].pop()
                                    self.central['active'].append(card)
                                else:
                                    # This assumes that 'activeSize' is a property that keeps track of the number of active cards
                                    self.central['activeSize'] -= 1
                            else:
                                logging.info("Error Occurred")
                        else:  # Supplement
                            if money >= self.central['supplement'][0].cost:
                                money -= self.central['supplement'][0].cost
                                card = self.central['supplement'].pop()
                                self.pC['discard'].append(card)
                                logging.info(f"Supplement Bought: {card.to_dict()}")
                            else:
                                logging.info("Error Occurred")
                    else:
                        break
                    if money == 0:
                        break     
            else:
                logging.info("No Money to buy anything")
                
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
            logging.info ("Computer turn ending")
            
            logging.info("Available Cards")
            for card in self.central['active']:
                logging.info(f"Name {card.name} costing {card.cost} with attack {card.attack} and money {card.money}")
            logging.info("Supplement")
            for card in self.central['supplement']:
                logging.info(f"Name {card.name} costing {card.cost} with attack {card.attack} and money {card.money}")
                
            logging.info(f"Player Health: {self.pO['health']}")
            logging.info(f"Computer Health: {self.pC['health']}")
        
        logging.info("Your Hand")
        for card in self.pO['hand']:
            logging.info(f"Name {card.name} costing {card.cost} with attack {card.attack} and money {card.money}")
                
        logging.info("Your Active Cards")
        for card in self.pO['active']:
            logging.info(f"Name {card.name} costing {card.cost} with attack {card.attack} and money {card.money}")
        logging.info("Your Values")
        logging.info(f"Money {self.pO['money']}, Attack {self.pO['attack']}")
            
        logging.info(f"Player Health: {self.pO['health']}")
        logging.info(f"Computer Health: {self.pC['health']}")
                
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
                'supplement_card': [{'card_index': index + len(self.central['active']), **card.to_dict()} for index, card in enumerate(self.central['supplement'])]
            },
            'next_action': [{"endpoint": "/play_turn", "action": "play_all"}, {"endpoint": "/play_turn", "action": "play_that_card", "card_index": '[0-n]'}, {"endpoint": "/play_turn", "action": "buy_card", "card_index": '[0-n]'}, {"endpoint": "/play_turn", "action": "attack"}, {"endpoint": "/play_turn", "action": "end_turn"}]
        }
        
    def get_state(self):
        state = {
            'aggressive': self.aggressive,
            'central': {
                'deck': [card.to_dict() for card in self.central['deck']],
                'active': [card.to_dict() for card in self.central['active']],
                'supplement': [card.to_dict() for card in self.central['supplement']]
            },
            'pO': {
                'health': self.pO['health'],
                'deck': [card.to_dict() for card in self.pO['deck']],
                'hand': [card.to_dict() for card in self.pO['hand']],
                'active': [card.to_dict() for card in self.pO['active']],
                'discard': [card.to_dict() for card in self.pO['discard']],
                'money': self.pO['money'],
                'attack': self.pO['attack']
            },
            'pC': {
                'health': self.pC['health'],
                'deck': [card.to_dict() for card in self.pC['deck']],
                'hand': [card.to_dict() for card in self.pC['hand']],
                'active': [card.to_dict() for card in self.pC['active']],
                'discard': [card.to_dict() for card in self.pC['discard']],
                'money': self.pC['money'],
                'attack': self.pC['attack']
            }
        }
        return state

    def set_state(self, state):
        self.aggressive = state['aggressive']
        self.central['deck'] = [Card(**card_data) for card_data in state['central']['deck']]
        self.central['active'] = [Card(**card_data) for card_data in state['central']['active']]
        self.central['supplement'] = [Card(**card_data) for card_data in state['central']['supplement']]
        
        self.pO['health'] = state['pO']['health']
        self.pO['deck'] = [Card(**card_data) for card_data in state['pO']['deck']]
        self.pO['hand'] = [Card(**card_data) for card_data in state['pO']['hand']]
        self.pO['active'] = [Card(**card_data) for card_data in state['pO']['active']]
        self.pO['discard'] = [Card(**card_data) for card_data in state['pO']['discard']]
        self.pO['money'] = state['pO']['money']
        self.pO['attack'] = state['pO']['attack']
        
        self.pC['health'] = state['pC']['health']
        self.pC['deck'] = [Card(**card_data) for card_data in state['pC']['deck']]
        self.pC['hand'] = [Card(**card_data) for card_data in state['pC']['hand']]
        self.pC['active'] = [Card(**card_data) for card_data in state['pC']['active']]
        self.pC['discard'] = [Card(**card_data) for card_data in state['pC']['discard']]
        self.pC['money'] = state['pC']['money']
        self.pC['attack'] = state['pC']['attack']
