class InvalidCardIndexError(Exception):
    """Exception raised for invalid card index."""
    pass

class InsufficientMoneyError(Exception):
    """Exception raised for insufficient money to buy a card."""
    pass

class InsufficientSupplementError(Exception):
    """Exception raised for insufficient supplement."""
    pass
