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
from enum import IntEnum
import numpy as np # for now this is just used for weighted sampling


#################################################### GAME STATE ####################################################

class UNO:
  def __init__(self, num_players : int):
    self.top_card : Optional[Card] = None
    self.color : Optional[Color] = None # this is extra info for when the top card is wild or plus4
    self.turn : int = 0 # stores the index of the current player's turn


#################################################### CARDS ####################################################

class Color(IntEnum):
  RED = 0
  YELLOW = 1
  GREEN = 2
  BLUE = 3
  NUM_COLORS = 4


class Card:
  def __init__(self, color: Optional[Color], number: Optional[int]):
    self.color = color
    self.number = number
    self.type = type(self)
    
    # ensure that we've created a valid card
    if not self._validate():
      raise ValueError('Invalid card')

  # ensures that we have valid entries for all cards
  def _validate(self):
    if self.type == Number:
      return self.color is not None and self.number is not None
    elif self.type in [PlusTwo, Reverse, Skip]:
      return self.color is not None and self.number is None
    elif self.type in [PlusFour, Wild]:
      return self.color is None and self.number is None
    else:
      return False
  
  # overwrite by derived classes
  def is_playable(self, state: UNO):
    pass

  # overwrite by derived classes
  def play_card(self, state: UNO):
    # TODO: all cards add themselves to the discard pile, so this should do that
    pass
    
  def __eq__(self, other):
    return isinstance(other, Card) \
           and self.type == other.type \
           and self.color == other.color \
           and self.number == other.number 
  
  def __repr__(self):
    # TODO: use text coloring instead of color out front 
    res = ''
    res += f'{self.color.name:<8}' if self.color is not None else ''
    res += f'{self.type.__name__:<8}' if self.type != Number else ''
    res += f'{self.number}' if self.number is not None else ''
    return res
  
class Number(Card):
  def __init__(self, color : Optional[Color], number : Optional[int]):
    super().__init__(color=color, number=number)

  # def play_card(self, game_state):


class PlusTwo(Card):
  def __init__(self, color: Optional[Color]):
    super().__init__(color=color, number=None)

class Skip(Card):
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

class Player:
  def __init__(self, hand: Collection[Card]):
    self.hand = hand

  # A player is just the cards that they have
  def __repr__(self):
    # sort by card color, then card type, then card number
    sorted_cards = sorted(self.hand, key=lambda c: (
                          c.color if c.color is not None else -1, 
                          c.type.__name__, 
                          c.number if c.number is not None else -1))
    
    # join the list of cards into a single string
    return '\n'.join(map(lambda c: str(c), sorted_cards))


# for now, let's create some notion of a deck, but later, that part will be removed in favor
# of just providing card information
    


#################################################### DECK ####################################################

class Deck:
  TOTAL_CARDS = 108

  # 2 per number (1 through 9) + 1 zero 
  NUMBER_CARDS = (2 * 9 + 1) * Color.NUM_COLORS
  PLUSTWO_CARDS = 2 * Color.NUM_COLORS
  SKIP_CARDS = 2 * Color.NUM_COLORS
  REVERSE_CARDS = 2 * Color.NUM_COLORS
  PLUSFOUR_CARDS = 4
  WILD_CARDS = 4


  def __init__(self):
    pass

  # generates non-replacing cards based on distribution of UNO cards
  def generate_card(self):
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

    

if __name__ == '__main__':
  deck = Deck()
  hand = [deck.generate_card() for _ in range(7)]
  player = Player(hand)
  print(player)

