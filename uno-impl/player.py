# enables lazy type annotation resolving
from __future__ import annotations


from typing import Collection, Optional

from card import Color, Card


class Player:
  def __init__(self, hand: Collection[Card], position: int, name: Optional[str] = None):
    self.hand = hand
    self.position = position
    self.name = name if name is not None else f'Player {position}'

    # sort the hand
    self._sort_hand()

  def receive_card(self, card : Card) -> None:
    self.hand.append(card)

    # keep hand sorted
    self._sort_hand()

  def can_play(self, top_card: Card, deck_color: Color) -> bool:
    return self.get_playable_cards(top_card, deck_color) == []
  
  def get_playable_cards(self, top_card: Card, deck_color: Color):
    return list(filter(lambda c: c.is_playable(top_card, deck_color), self.hand))
  
  # def get_bluff_answer(self):
  #   return input('Call bluff (y/n)?') == 'y'
  
  def _sort_hand(self) -> None:
    # sort by card color, then card type, then card number
    self.hand.sort(key=lambda c: (
                   c.color if c.color is not None else -1, 
                   c.type.__name__, 
                   c.number if c.number is not None else -1))
  
  @staticmethod
  def _hand_to_str(hand) -> str:
    return '\n'.join(map(lambda x: f'{x[0]}: {x[1]}', enumerate(hand)))

  def __repr__(self):
    # join the list of cards into a single string
    return self.name + '\n' + Player._hand_to_str(self.hand)