from uno.card import Card, Wild, PlusFour, PlusTwo, Skip, Reverse, Number
from uno.card import Color

def card_from_string(color: str, card_type: str) -> Card:
  card_types = [PlusTwo, Skip, Reverse]
  card_types_map = {class_type.__name__: class_type for class_type in card_types}
  card_types_spec = [Wild, PlusFour]
  card_types_map_spec = {class_type.__name__: class_type for class_type in card_types_spec}

  if card_type in card_types_map_spec:
    card = card_types_map_spec[card_type]()
  elif card_type in card_types_map:
    color = color_from_string(color)
    card = card_types_map[card_type](color)
  else:
    color = color_from_string(color)
    card = Number(color, int(card_type))
  return card

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