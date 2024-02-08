'''
state:
 * number of players
 * who's turn it is
 * the cards that a player has 
 * draw_pile -> I won't know this, which is completely fine
  * I'll just have to have them pass in a card that is being dispensed from the draw_pile
 * discard_pile 
  * you actually only need the top card of this 
 * 

Official uno rules: https://service.mattel.com/instruction_sheets/42001pr.pdf

'''

from typing import Collection, Optional
from enum import Enum


#################################################### GAME STATE ####################################################

class UNO:
  def __init__(self, players : int):
    # self.bruh : Card
    pass 

#################################################### CARDS ####################################################

class Color(Enum):
  RED = 0
  YELLOW = 1
  GREEN = 2
  BLUE = 3

class Type(Enum):
  NUMBER = 0
  PLUSTWO = 1
  REVERSE = 2
  PLUSFOUR = 3
  WILD = 4

class Card:
  def __init__(self, color : Optional[Color], number : Optional[int], type : Type = Type.NUMBER):
    self.color = color
    self.number = number
    self.type = type
    
    if not self._validate():
      raise ValueError('Invalid card')

  # ensures that we have valid entries for all cards
  def _validate(self):
    if self.type == Type.NUMBER:
      return self.color is not None and self.number is not None
    elif self.type == Type.PLUSTWO or self.type == Type.REVERSE:
      return self.color is not None and self.number is None
    elif self.type == Type.PLUSFOUR or self.type == Type.WILD:
      return self.color is None and self.number is None
    else:
      return False
  
  # overwrite by derived classes
  def is_playable(self, state : UNO):
    pass
    
  def __eq__(self, other):
    return isinstance(other, Card) \
           and self.type == other.type \
           and self.color == other.color \
           and self.number == other.number 
  
class Number(Card):
  def __init__(self, color : Optional[Color], number : Optional[int]):
    super().__init__(color, number)

  

  # def play_card(self, game_state):


class PlusTwo(Card):
  def __init__(self, color : Optional[Color]):
    super().__init__(color, None, type=Type.PLUSTWO)

class Reverse(Card):
  def __init__(self, color : Optional[Color]):
    super().__init__(color, None, type=Type.REVERSE)

class PlusFour(Card):
  def __init__(self):
    super().__init__(None, None, type=Type.PLUSFOUR)

  def is_playable(self, state: UNO):
    return True

class Wild(Card):
  def __init__(self):
    super().__init__(None, None, type=Type.WILD)

  def is_playable(self, state: UNO):
    return True


#################################################### PLAYERS ####################################################

'''
What info do I need to store in a player?
 * list of cards

What should they be able to do?
 * Play a card when asked
 * Receive a card
 * call or not call a bluff when asked
 * call UNO -> add this in the future

'''




