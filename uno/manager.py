'''
Houses the controller and displayer(s)
'''

from __future__ import annotations

from typing import Optional, Collection
import logging
import datetime
import os

from uno.card import Card, Wild, PlusFour, Color
from uno.player import Player
from uno.controller import Controller
from uno.displayer import Displayer

# only import what we need if we are doing type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from uno.uno import UNO


# TODO: in the future, maybe it's best to not explicitly have a display_state method


class Manager:
  def __init__(self, controller: Controller, displayers: Collection[Displayer], logger: logging.Logger):
    self.logger = logger
    self.controller = controller
    self.displayers = displayers

  # reset any instantiated objects
  def reset(self) -> None:
    self.logger.info('Resetting controllers and displayers')
    self.controller.reset()
    for displayer in self.displayers:
      displayer.reset()

  # given a player, ask them for a card
  # here, None means they want to draw a card
  def get_card(self, player: Player) -> Optional[Card]:
    self.logger.info(f'[{player.name}] asking for card; Current hand: {player.hand}')
    card = self.controller.get_card(player)
    self.logger.info(f'[{player.name}] responded with {card}')
    return card

  # get whether or not the player wants to play the card they were just dealt
  def get_draw_card_response(self, player: Player, card: Card) -> bool:
    self.logger.info(f'[{player.name}] asking for draw card response for [{card}]')
    response = self.controller.get_draw_card_response(player, card)
    self.logger.info(f'[{player.name}] responded with [{card}]')
    return response

  def get_bluff_answer(self, player: Player) -> bool:
    self.logger.info(f'[{player.name}] asking for bluff answer')
    response = self.controller.get_bluff_answer(player)
    self.logger.info(f'[{player.name}] responded with [{response}]')
    return response

  def get_color_choice(self, player: Player) -> Color:
    self.logger.info(f'[{player.name}] asking for color choice')
    response = self.controller.get_color_choice(player)
    self.logger.info(f'[{player.name}] responded with [{response}]')
    return response

  # advance to the next player
  # dir is either +/- 1, depending on the direction 
  def advance_turn(self, dir: int) -> None:
    self.logger.info(f'Advancing turn in direction {dir}')
    self.controller.advance_turn(dir)

  # here, I guess the software controller will have to maintain it's own draw deck in the controller
  # TODO: this function should add the card to the players hand
  def deal_card(self, player: Optional[Player]) -> Card:
    self.logger.info(f'[{player.name if player else None}] dealing card; Current hand: {player.hand if player else None}')
    card = self.controller.deal_card()
    self.logger.info(f'[{player.name if player else None}] received [{card}]')
    return card

  # show what the game state looks like
  def display_state(self, state: UNO) -> None:
    for displayer in self.displayers:
      displayer.display_state(state)

  # signal that we have entered an invalid state
  def signal_invalid_state(self, state: UNO) -> None:
    self.logger.error('Entered invalid state. Exiting...')
    for displayer in self.displayers:
      displayer.signal_invalid_state(state)