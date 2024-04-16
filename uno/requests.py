'''
All of the atomic requests happening between the nodes in the system.
'''


# TODO: add types
from typing import Collection

class Request:
  pass

############################ Requests to State ############################

# TODO: maybe split this up as to not classify all the time
class PlayCard(Request):
  def __init__(self, card):
    self.card = card

class DealtCard(Request):
  def __init__(self, card, player):
    self.card = card
    self.player = player

class SkipTurn(Request):
  pass

class SetColor(Request):
  def __init__(self, color) -> None:
    self.color = color

class Bluff(Request):
  def __init__(self, is_bluff: bool) -> None:
    self.is_bluff = is_bluff

class CallUNO(Request):
  # the card that they played UNO with
  def __init__(self, card):
    self.card = card

class UNOFail(Request):
  pass

class CorrectedState(Request):
  def __init__(self, corrected_state) -> None:
    self.corrected_state = corrected_state

############################ Requests to Controller ############################

class GoNextPlayer(Request):
  def __init__(self, dir: int) -> None:
    self.dir = dir

class DealCard(Request):
  def __init__(self, player) -> None:
    self.player = player

class GetUserInput(Request):
  def __init__(self, request_types: Collection[type[Request]]) -> None:
    self.request_types = request_types

############################ Requests to Displayer ############################

class CurrentState(Request):
  def __init__(self, state) -> None:
    self.state = state


############################ Common Requests ############################

class Reset(Request):
  pass # TODO: add more info