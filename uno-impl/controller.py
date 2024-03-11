# enables lazy type annotation resolving
from __future__ import annotations

from typing import Optional

from card import Card, Wild, PlusFour, Color
from deck import Deck
from player import Player

# only import what we need if we are doing type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from uno import UNO
  


# TODO: separate the controller from the displayer, I think that makes the most sense, although
# maybe it doesn't make sense though, since the way you display it is probably the same as the GUI or whatever


# Base class for the functionality that a Controller must support
class Controller:
  
  def __init__(self):
    pass

  # reset any instantiated objects
  def reset(self) -> None:
    pass

  # given a player, ask them for a card
  # here, None means they want to draw a card
  def get_card(self, player: Player) -> Optional[Card]:
    pass

  # get whether or not the player wants to play the card they were just dealt
  def get_draw_card_response(self, player: Player, card: Card) -> bool:
    pass

  def get_bluff_answer(self, player: Player) -> bool:
    pass

  def get_color_choice(self, player: Player) -> Color:
    pass

  # advance to the next player
  # dir is either +/- 1, depending on the direction 
  def advance_turn(self, dir: int) -> None:
    pass

  # here, I guess the software controller will have to maintain it's own draw deck in the controller
  def deal_card(self) -> Card:
    pass


# Handles game state interactions through the terminal
class TerminalController(Controller):
  def __init__(self):
    self.reset()

  def reset(self) -> None:
    # TODO: make this a real shuffled deck with random.shuffle
    self.draw_pile: Deck = Deck(Deck.TOTAL_CARDS)

  # TODO: should get_card have knowledge of the player's cards? I guess why not?
  def get_card(self, player: Player) -> Optional[Card]:
    enumerated_hand = list(enumerate(player.hand))
    print(player.name + ' actions:')
    print(Player._hand_to_str(map(lambda x: x[1], enumerated_hand)) + f'\n{len(enumerated_hand)}: Draw card')

    while (action := int(input('Enter action: '))) not in range(len(enumerated_hand)+1):
      pass

    # they want to draw a card
    if action == len(player.hand):
      return None
    
    _, card_to_play = enumerated_hand[action]

    return card_to_play
  
  def get_draw_card_response(self, player: Player, card: Card) -> bool:
    return input(f'{player.name}, would you like to play the drawn card ({card}) (y/n)? ') == 'y'
  
  def get_bluff_answer(self, player: Player) -> bool:
    return input(f'{player.name}, would you like to call a bluff (y/n)? ') == 'y'
  
  def get_color_choice(self, player: Player) -> Color:
    return Color(int(input('\n'.join(['0: red', '1: yellow', '2: green', '3: blue']))))
  

  def advance_turn(self, dir: int) -> None:
    pass

  # here, I guess the software controller will have to maintain it's own draw deck in the controller
  def deal_card(self) -> Card:
    return self.draw_pile.pop()


# Handles game state interactions through a visual interface 
class GUIController(Controller):
  def __init__(self):
    pass


# print(f'Player {self.turn}\'s turn')
# print(f'Your hand:\n{self.players[self.turn].hand}')
# print(f'Top card: {self.discard_pile.peek()}')
# print(f'{len(self.draw_pile.cards)} cards remaining.\n\n')