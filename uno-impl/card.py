'''
There are 4 colors, so maybe make an ENUM for that
There are 
'''

from enum import Enum
from typing import Optional

# might have some circular import problems if I import the game state here 

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

    
  def __eq__(self, other):
    return isinstance(other, Card) \
           and self.type == other.type \
           and self.color == other.color \
           and self.number == other.number 
  
class Number(Card):
  def __init__(self, color : Optional[Color], number : Optional[int]):
    super().__init__(color, number)

class PlusTwo(Card):
  def __init__(self, color : Optional[Color]):
    super().__init__(color, None, type=Type.PLUSTWO)

class Reverse(Card):
  def __init__(self, color : Optional[Color]):
    super().__init__(color, None, type=Type.REVERSE)

class PlusFour(Card):
  def __init__(self):
    super().__init__(None, None, type=Type.PLUSFOUR)

class Wild(Card):
  def __init__(self):
    super().__init__(None, None, type=Type.WILD)


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