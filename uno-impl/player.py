# enables lazy type annotation resolving
from __future__ import annotations


from typing import Collection, Optional

from card import Color, Card


class Player:
  def __init__(self, hand: Collection[Card]):
    self.hand = hand

    # sort the hand
    self._sort_hand()

  def receive_card(self, card : Card) -> None:
    self.hand.append(card)

    # keep hand sorted
    self._sort_hand()

  # NOTE: this function will only ever be called when this player is actually able to play
  def get_card(self, top_card: Card, deck_color: Color) -> Optional[Card]:
    # extracts the playable cards, including their index in the unfiltered hand (for removal)
    enumerated_hand = enumerate(self.hand)
    playable_cards = list(filter(lambda c: c[1].is_playable(top_card, deck_color), enumerated_hand))
    if playable_cards == []:
      return None
    
    # ask them for a card
    print('Possible actions:')
    print(Player._hand_to_str(map(lambda x: x[1], playable_cards)) + f'\n{len(playable_cards)}: Draw card')

    while (action := int(input('Enter action: '))) not in range(len(playable_cards)+1):
      pass

    # they want to draw a card
    if action == len(playable_cards):
      return None
    
    i, card_to_play = playable_cards[action]

    # remove this card from the hand
    self.hand.pop(i)

    # keep hand sorted
    self._sort_hand()

    return card_to_play

  def can_play(self, top_card: Card, deck_color: Color) -> bool:
    return self.get_playable_cards(top_card, deck_color) == []
  
  def get_playable_cards(self, top_card: Card, deck_color: Color):
    return list(filter(lambda c: c.is_playable(top_card, deck_color), self.hand))
  
  def get_bluff_answer(self):
    return input('Call bluff (y/n)?') == 'y'
  
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
    return Player._hand_to_str(self.hand)