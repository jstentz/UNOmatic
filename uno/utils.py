from card import Card, Wild, PlusFour, PlusTwo, Skip, Reverse, Number
from card import Color

def card_from_string(card_str: str) -> Card:
  pass

def card_from_classification(card_label: int, color_label: int) -> Card:
  color = Color(color_label) if color_label <= 3 else None

  # check if this is a number card
  if card_label < 10:
    return Number(color, card_label)
  elif card_label == 10:
    return Skip(color)
  elif card_label == 11:
    return Reverse(color)
  elif card_label == 12:
    return PlusTwo(color)
  elif card_label == 13:
    return Wild()
  else:
    return PlusFour()