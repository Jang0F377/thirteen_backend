CARD_SUITS: dict[str, str] = {
    "D": "Diamonds",
    "C": "Clubs",
    "H": "Hearts",
    "S": "Spades",
}

# Rank order is 3 (low) .. 2 (high)
CARD_VALUES: dict[str, str] = {
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "10": "10",
    "J": "Jack",
    "Q": "Queen",
    "K": "King",
    "A": "Ace",
    "2": "2",
}

RANK_ORDER = list(CARD_VALUES.keys())  # ['3', '4', ... '2']
SUIT_ORDER = list(CARD_SUITS.keys())  # ['D','C','H','S']
