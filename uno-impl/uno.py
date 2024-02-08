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

class Card:
  def __init__(self, color: Optional[Color], number: Optional[int]):
    self.color = color
    self.number = number
    self.type = type(self)
    
    if not self._validate():
      raise ValueError('Invalid card')

  # ensures that we have valid entries for all cards
  def _validate(self):
    if self.type == Number:
      return self.color is not None and self.number is not None
    elif self.type == PlusTwo or self.type == Reverse:
      return self.color is not None and self.number is None
    elif self.type == PlusFour or self.type == Wild:
      return self.color is None and self.number is None
    else:
      return False
  
  # overwrite by derived classes
  def is_playable(self, state : UNO):
    pass

  # overwrite by derived classes
  def play_card(self, state : UNO):
    pass
    
  def __eq__(self, other):
    return isinstance(other, Card) \
           and self.type == other.type \
           and self.color == other.color \
           and self.number == other.number 
  
class Number(Card):
  def __init__(self, color : Optional[Color], number : Optional[int]):
    super().__init__(color=color, number=number)

  

  # def play_card(self, game_state):


class PlusTwo(Card):
  def __init__(self, color: Optional[Color]):
    super().__init__(color=color, number=None)

class Reverse(Card):
  def __init__(self, color: Optional[Color]):
    super().__init__(color=color, number=None)

class PlusFour(Card):
  def __init__(self):
    super().__init__(color=None, number=None)

  def is_playable(self, state: UNO):
    return True

class Wild(Card):
  def __init__(self):
    super().__init__(color=None, number=None)

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



if __name__ == '__main__':
  my_card = Number(Color.YELLOW, 0)
  my_card1 = PlusTwo(Color.RED)
  my_card2 = PlusFour()
  my_card3 = Wild()
  my_card4 = Number(Color.YELLOW, 0)
  my_card5 = PlusTwo(Color.RED)

  print(my_card == my_card3) # false
  print(my_card == my_card4) # true
  print(my_card1 == my_card5) # true
