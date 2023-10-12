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
