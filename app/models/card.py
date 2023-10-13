class Card:
    """
    Represents a card in the game.

    Attributes:
        name (str): The name of the card.
        cost (int): The cost required to purchase or use the card.
        attack (int): The attack power of the card.
        money (int): The monetary value of the card.
    """

    def __init__(self, name, cost, attack, money):
        """
        Initializes a new card with the given attributes.

        Args:
            name (str): The name of the card.
            cost (int): The cost required to purchase or use the card.
            attack (int): The attack power of the card.
            money (int): The monetary value of the card.
        """
        self.name = name
        self.cost = cost
        self.attack = attack
        self.money = money

    def to_dict(self):
        """
        Converts the card object to a dictionary representation.

        Returns:
            dict: A dictionary representation of the card.
        """
        return {
            'name': self.name,
            'cost': self.cost,
            'attack': self.attack,
            'money': self.money
        }
