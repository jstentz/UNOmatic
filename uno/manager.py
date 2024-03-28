'''
Houses the controller and displayer(s)
'''

from __future__ import annotations

from typing import Optional, Collection

from uno.card import Card, Wild, PlusFour, Color
from uno.deck import Deck
from uno.player import Player
from uno.controller import Controller
from uno.displayer import Displayer

# only import what we need if we are doing type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from uno.uno import UNO


# TODO: in the future, maybe it's best to not explicitly have a display_state method


class Manager:
  def __init__(self, controller: Controller, displayers: Collection[Displayer]):
    self.controller = controller
    self.displayers = displayers

  # reset any instantiated objects
  def reset(self) -> None:
    self.controller.reset()
    for displayer in self.displayers:
      displayer.reset()

  # given a player, ask them for a card
  # here, None means they want to draw a card
  def get_card(self, player: Player) -> Optional[Card]:
    return self.controller.get_card(player)

  # get whether or not the player wants to play the card they were just dealt
  def get_draw_card_response(self, player: Player, card: Card) -> bool:
    return self.controller.get_draw_card_response(player, card)

  def get_bluff_answer(self, player: Player) -> bool:
    return self.controller.get_bluff_answer(player)

  def get_color_choice(self, player: Player) -> Color:
    return self.controller.get_color_choice(player)

  # advance to the next player
  # dir is either +/- 1, depending on the direction 
  def advance_turn(self, dir: int) -> None:
    self.controller.advance_turn(dir)

  # here, I guess the software controller will have to maintain it's own draw deck in the controller
  def deal_card(self) -> Card:
    return self.controller.deal_card()

  # show what the game state looks like
  def display_state(self, state: UNO) -> None:
    for displayer in self.displayers:
      displayer.display_state(state)

  # signal that we have entered an invalid state
  def signal_invalid_state(self, state: UNO) -> None:
    for displayer in self.displayers:
      displayer.signal_invalid_state()