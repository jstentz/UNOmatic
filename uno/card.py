# enables lazy type annotation resolving
from __future__ import annotations

from typing import Optional, Collection
from enum import IntEnum

# only import what we need if we are doing type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from uno.uno import UNO
  from uno.player import Player

from uno.requests import *

'''
what if the play_card is spawned on a thread and a channel is given to it 
to listen on... then we can have the main thread redirect only the requests that matter
can also send quit requests to the card so that it returns 
'''

class Color(IntEnum):
  RED = 0
  YELLOW = 1
  GREEN = 2
  BLUE = 3
  NUM_COLORS = 4

class Card:
  def __init__(self, color: Optional[Color], number: Optional[int]):
    self.color: Color = color
    self.number = number
    self.type = type(self)
    
    # ensure that we've created a valid card
    # if not self._validate():
    #   raise ValueError('Invalid card')
    
    # get the path to the image
    if self.type in [PlusFour, Wild]:
      self.image_name = f'{self.type.__name__.lower()}.png'
    else:
      self.image_name = f'{self.color.name.lower() if self.color is not None else "yellow"}_{self.number if self.type == Number else self.type.__name__.lower()}.png'

  def to_json(self):
    obj = {
      'color': self.color.name if self.color is not None else None,
      'number': int(self.number) if self.number is not None else None,
      'type': self.type.__name__,
      'image_name': self.image_name
    }
    return obj

  # ensures that we have valid entries for all cards
  def _validate(self) -> bool:
    if self.type == Number:
      return self.color is not None and self.number is not None
    elif self.type in [PlusTwo, Reverse, Skip]:
      return self.color is not None and self.number is None
    elif self.type in [PlusFour, Wild]:
      return self.color is None and self.number is None
    else:
      return False
    
  # this is just here so any instance of a Card has this method 
  def play_card(self, state: UNO) -> None:
    pass 

  # this is just here so any instance of a Card has this method 
  def is_playable(self, top_card, deck_color: Color) -> bool:
    pass

  # get's the value of the card for scoring purposes
  def get_value(self):
    pass
  
  def __eq__(self, other) -> bool:
    return isinstance(other, Card) \
           and self.type == other.type \
           and self.color == other.color \
           and self.number == other.number 
  
  def __repr__(self) -> str:
    res = ''
    res += f'{self.color.name} ' if self.color is not None else ''
    res += f'{self.type.__name__} ' if self.type != Number else ''
    res += f'{self.number} ' if self.number is not None else ''
    return res.rstrip()
  
class Number(Card):
  def is_playable(self, top_card: Card, deck_color: Color) -> bool:
    return self.color == deck_color or (top_card.type == Number and top_card.number == self.number)
  
  def play_card(self, state: UNO) -> None:
    # place the card on the discard pile
    state.discard_pile.push(self)

    # update the color of the deck
    state.color = self.color

    # advance to the next player
    state.go_next_player()

  def get_value(self):
    return int(self.number)
    

class PlusTwo(Card):
  def __init__(self, color: Optional[Color]):
    super().__init__(color=color, number=None)

  # NOTE: this function will never be called in the case where the control flow
  # doesn't let a player play the card... these functions are unaware of the rest
  # of the game state 
  def is_playable(self, top_card: Card, deck_color: Color) -> bool:
    return self.color == deck_color or top_card.type == PlusTwo
  
  def play_card(self, state: UNO) -> None:
    # place the card on the discard pile
    state.discard_pile.push(self)


    # update the color of the deck
    state.color = self.color

    # advance to the next player
    state.go_next_player(is_turn_end=False)

    # deal two cards to the player
    curr_player: Player = state.players[state.turn]
    if (received_request := state.transaction_sync(DealCard(curr_player))) is None: return
    curr_player.receive_card(received_request.card, state)
    if (received_request := state.transaction_sync(DealCard(curr_player))) is None: return
    curr_player.receive_card(received_request.card, state)

    # go to the next player
    state.go_next_player()

  def get_value(self):
    return 20

class Skip(Card):
  def __init__(self, color: Optional[Color]):
    super().__init__(color=color, number=None)

  def is_playable(self, top_card: Card, deck_color: Color) -> bool:
    return self.color == deck_color or top_card.type == Skip
  
  def play_card(self, state: UNO) -> None:
    # place the card on the discard pile
    state.discard_pile.push(self)


    # update the color of the deck
    state.color = self.color

    # skip a player
    state.go_next_player(is_turn_end=False)
    state.go_next_player()

  def get_value(self):
    return 20

class Reverse(Card):
  def __init__(self, color: Optional[Color]):
    super().__init__(color=color, number=None)

  def is_playable(self, top_card: Card, deck_color: Color) -> bool:
    return self.color == deck_color or top_card.type == Reverse
  
  def play_card(self, state: UNO) -> None:
    # place the card on the discard pile
    state.discard_pile.push(self)


    # update the color of the deck
    state.color = self.color

    # change direction and go back to prev player
    state.reverse()
    state.go_next_player()

  def get_value(self):
    return 20

class PlusFour(Card):
  def __init__(self):
    super().__init__(color=None, number=None)

  def is_playable(self, top_card: Card, deck_color: Color) -> bool:
    return True
  
  def play_card(self, state: UNO) -> None:
    # check to see if we had other options than playing this card
    player: Player = state.players[state.turn]
    playable_cards: Collection[Card] = player.get_playable_cards(state.discard_pile.peek(), state.color)

    # check if we have any cards that meet these conditions
    # 1. is not a plus 4
    # 2. matches the color of the top card or is a wild card
    has_other_options: bool = any(map(lambda c: c.type != PlusFour and (c.type == Wild or c.color == state.color), playable_cards))

    # place the card on the discard pile
    state.discard_pile.push(self)

    state._send_update_to_displayer()

    # ask the user for a color
    if (received_request := state.transaction_sync(GetUserInput([SetColor]))) is None: return
    state.color = received_request.color

    state._send_update_to_displayer()
    

    # go the next player
    state.go_next_player(is_turn_end=False)

    state._send_update_to_displayer()

    
    # ask them for a bluff answer
    # next_player = state.players[state.turn]

    if (received_request := state.transaction_sync(GetUserInput([Bluff]))) is None: return
    call_bluff = received_request.is_bluff

    # we're guilty
    if call_bluff and has_other_options:
      # this player must show their cards to the person calling the bluff

      # move back to us
      state.go_prev_player()

      # draw 4 cards
      for _ in range(4):
        curr_player = state.players[state.turn]
        if (received_request := state.transaction_sync(DealCard(curr_player))) is None: return
        curr_player.receive_card(received_request.card, state)

      # progress to the next player
      state.go_next_player()
    
    # failed bluff
    elif call_bluff and not has_other_options:
      # this player must show their cards to the person calling the bluff
      # draw 6 cards for this player
      for _ in range(6):
        curr_player = state.players[state.turn]
        if (received_request := state.transaction_sync(DealCard(curr_player))) is None: return
        curr_player.receive_card(received_request.card, state)

      state.go_next_player()

    # no bluff called
    else:
      # draw 4 cards for this player
      for _ in range(4):
        curr_player = state.players[state.turn]
        if (received_request := state.transaction_sync(DealCard(curr_player))) is None: return
        curr_player.receive_card(received_request.card, state)

      state.go_next_player()

  def get_value(self):
    return 50

class Wild(Card):
  def __init__(self):
    super().__init__(color=None, number=None)

  def is_playable(self, top_card: Card, deck_color: Color) -> bool:
    return True
  
  def play_card(self, state: UNO) -> None:
    # place the card on the discard pile
    state.discard_pile.push(self)

    state._send_update_to_displayer()

    # ask the user for a color
    # curr_player = state.players[state.turn]
    if (received_request := state.transaction_sync(GetUserInput([SetColor]))) is None: return
    state.color = received_request.color

    state._send_update_to_displayer()

    # move on to the next player
    state.go_next_player()

  def get_value(self):
    return 50
