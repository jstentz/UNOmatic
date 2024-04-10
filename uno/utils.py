from uno.card import Card, Wild, PlusFour, PlusTwo, Skip, Reverse, Number
from uno.card import Color

def card_from_string(color: str, card_type: str) -> Card:
  card_types = [Wild, PlusFour, PlusTwo, Skip, Reverse]
  card_types_map = {class_type.__name__: class_type for class_type in card_types}
  color = color_from_string(color)

  if card_type in card_types_map:
    card = card_types_map[card_type](color)
  else:
    card = Number(color, int(card_type))

def color_from_string(color: str):
  return None if color == 'None' else Color[color]

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