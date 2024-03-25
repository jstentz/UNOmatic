# enables lazy type annotation resolving
from __future__ import annotations
from typing import Optional

import numpy as np

from uno.card import Color
from uno.card import Card, Number, PlusTwo, Skip, Reverse, PlusFour, Wild

class Deck:
  TOTAL_CARDS = 108

  # 2 per number (1 through 9) + 1 zero 
  NUMBER_CARDS = (2 * 9 + 1) * Color.NUM_COLORS
  PLUSTWO_CARDS = 2 * Color.NUM_COLORS
  SKIP_CARDS = 2 * Color.NUM_COLORS
  REVERSE_CARDS = 2 * Color.NUM_COLORS
  PLUSFOUR_CARDS = 4
  WILD_CARDS = 4

  def __init__(self, num_cards: int):
    self.cards = [Deck.generate_card() for _ in range(num_cards)]

  def push(self, card: Card) -> None:
    self.cards.append(card)

  def pop(self) -> Card:
    return self.cards.pop()
  
  def peek(self) -> Optional[Card]:
    return self.cards[-1] if self.cards else None
  
  def __repr__(self) -> str:
    return f'TOP\n' + '\n'.join(map(lambda c: str(c), self.cards[::-1])) + '\nBOTTOM'

  # generates non-replacing cards based on distribution of UNO cards
  @staticmethod
  def generate_card():
    # create distribution for card types 
    types = np.array([Number, PlusTwo, Skip, Reverse, PlusFour, Wild])
    types_dist = np.array([
      Deck.NUMBER_CARDS,
      Deck.PLUSTWO_CARDS,
      Deck.SKIP_CARDS,
      Deck.REVERSE_CARDS,
      Deck.PLUSFOUR_CARDS,
      Deck.WILD_CARDS
    ]) / Deck.TOTAL_CARDS

    # create distribution for card colors
    colors = [Color.RED, Color.YELLOW, Color.GREEN, Color.BLUE]
    colors_dist = np.ones(Color.NUM_COLORS) / Color.NUM_COLORS

    # create distribution for card numbers
    numbers = np.arange(10)
    numbers_dist = np.empty(10)
    numbers_dist[0] = Color.NUM_COLORS
    numbers_dist[1:] = 2 * Color.NUM_COLORS
    numbers_dist /= Deck.NUMBER_CARDS

    # generate card type
    card_type = np.random.choice(types, p=types_dist)

    # generate card color 
    card_color = colors[np.random.choice(Color.NUM_COLORS, p=colors_dist)]

    # generate card number
    card_number = np.random.choice(numbers, p=numbers_dist)

    # create the correct card
    if card_type == PlusFour or card_type == Wild:
      return card_type()
    elif card_type == PlusTwo or card_type == Skip or card_type == Reverse:
      return card_type(color=card_color)
    else: # number card
      return card_type(color=card_color, number=card_number)