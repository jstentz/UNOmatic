'''
All of the atomic requests happening between the nodes in the system.
'''

# enables lazy type annotation resolving
from __future__ import annotations

from typing import Collection, Optional

# only import what we need if we are doing type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from uno.uno import DisplayUNOState
  from uno.player import Player
  from uno.card import Card, Color

class Request:
  pass

############################ Requests to State ############################

# TODO: maybe split this up as to not classify all the time
class PlayCard(Request):
  def __init__(self, card: Card, for_drawn_card: bool = False):
    self.card = card
    self.for_drawn_card = for_drawn_card
  
  def __repr__(self) -> str:
    return f'PlayCard[card={self.card}{"" if not self.for_drawn_card else f", for_drawn_card=True"}]'

class DealtCard(Request):
  def __init__(self, card: Card, player: Player):
    self.card = card
    self.player = player

  def __repr__(self) -> str:
    return f'DealtCard[card={self.card}, player={self.player.name}]' if self.player is not None else f'DealtCard[card={self.card}, player=TOP_CARD]'

class SkipTurn(Request):
  def __init__(self, for_drawn_card: bool = False):
    self.for_drawn_card = for_drawn_card

  def __repr__(self) -> str:
    return f'SkipTurn{"" if not self.for_drawn_card else "[for_drawn_card=True]"}'

class SetColor(Request):
  def __init__(self, color: Color) -> None:
    self.color = color
  
  def __repr__(self) -> str:
    return f'SetColor[color={self.color.name}]'

class Bluff(Request):
  def __init__(self, is_bluff: bool) -> None:
    self.is_bluff = is_bluff

  def __repr__(self) -> str:
    return f'Bluff[is_bluff={self.is_bluff}]'

class CallUNO(Request):
  # the card that they played UNO with
  def __init__(self, card: Card, for_drawn_card: bool = False):
    self.card = card
    self.for_drawn_card = for_drawn_card

  def __repr__(self) -> str:
    return f'CallUNO[card={self.card}{"" if not self.for_drawn_card else f", for_drawn_card=True"}]'

class UNOFail(Request):
  def __repr__(self) -> str:
    return 'UNOFail'

class CorrectedState(Request):
  def __init__(self, state_update: dict) -> None:
    self.state_update = state_update

  def __repr__(self) -> str:
    # TODO: maybe this should be diff
    return 'CorrectedState'

############################ Requests to Controller ############################

class GoNextPlayer(Request):
  def __init__(self, dir: int, num_players: int) -> None:
    self.dir = dir
    self.num_players = num_players

  def __repr__(self) -> str:
    return f'GoNextPlayer[dir={self.dir}]'

class DealCard(Request):
  def __init__(self, player: Player) -> None:
    self.player = player

  def __repr__(self) -> str:
    return f'DealCard[player={self.player.name}]' if self.player is not None else f'DealCard[TOP_CARD]'

class GetUserInput(Request):
  def __init__(self, request_types: Collection[type[Request]], for_drawn_card: bool = False) -> None:
    self.request_types = request_types
    self.for_drawn_card = for_drawn_card

  def __repr__(self) -> str:
    return f'GetUserInput[request_types={",".join([request_type.__name__ for request_type in self.request_types])}{"" if not self.for_drawn_card else f", for_drawn_card=True"}]'

############################ Requests to Displayer ############################

class CurrentState(Request):
  def __init__(self, state: DisplayUNOState) -> None:
    self.state = state

  def __repr__(self) -> str:
    # TODO: add more to this 
    return 'CurrentState'
  
class GameOver(Request):
  def __init__(self, winning_player: Player) -> None:
    self.winning_player = winning_player

  def __repr__(self) -> str:
    return f'GameOver[winning_player={self.winning_player.name}]'

class RoundOver(Request):
  def __init__(self, winning_player: Player) -> None:
    self.winning_player = winning_player

  def __repr__(self) -> str:
    return f'RoundOver[winning_player={self.winning_player.name}]'

############################ Common Requests ############################

# restarts an entire game
class Reset(Request):
  def __init__(self, num_players: int = 4, hand_size: int = 7, end_score: int = 500) -> None:
    self.num_players = num_players
    self.hand_size = hand_size
    self.end_score = end_score

  def __repr__(self) -> str:
    return f'Reset[num_players={self.num_players}, hand_size={self.hand_size}, end_score={self.end_score}]'
  
class RoundReset(Request):
  def __repr__(self) -> str:
    return 'RoundReset'

  

############################ Internal Controller Requests ############################

class ControllerReset(Request):
  pass

class ControllerRoundReset(Request):
  pass

# TODO: add an internal displayer reset 
