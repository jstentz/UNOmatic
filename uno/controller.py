# enables lazy type annotation resolving
from __future__ import annotations

import time
import os

from typing import Optional
from queue import Queue

import time

import serial
# from picamera2 import Picamera2
# from gpiozero import LED, Button

from uno.card import Card, Wild, PlusFour, Color
from uno.deck import Deck
from uno.player import Player
from uno.displayer import TkDisplayer

from classification.forward import init_model, get_card

# only import what we need if we are doing type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from uno.uno import UNO

# Base class for the functionality that a Controller must support
class Controller:
  
  def __init__(self):
    self._async_action_queue = Queue()

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
  
  # gives the channel used for communication
  def get_channel(self) -> Queue:
    return self._async_action_queue
  
  # TODO: type this action
  def _send_to_state(self, action) -> None:
    # puts action on the queue
    # should I wait here? It may not handle the issue until the end of the turn
    self._async_action_queue.put(action, block=False)

# Handles game state interactions through the terminal
class TerminalController(Controller):
  def __init__(self):
    super().__init__()
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

  # take in the displayer to be able to easily work with the same windows and such
  def __init__(self, displayer: TkDisplayer):
    super().__init__()

    self.displayer = displayer
    self.reset()

  def reset(self) -> None:
    # TODO: make this a real shuffled deck with random.shuffle
    self.draw_pile: Deck = Deck(Deck.TOTAL_CARDS)

  # TODO: should get_card have knowledge of the player's cards? I guess why not?
  def get_card(self, player: Player) -> Optional[Card]:
    
    pass
  
  def get_draw_card_response(self, player: Player, card: Card) -> bool:
    pass

  def get_bluff_answer(self, player: Player) -> bool:
    pass

  def get_color_choice(self, player: Player) -> Color:
    pass

  def advance_turn(self, dir: int) -> None:
    pass

  # here, I guess the software controller will have to maintain it's own draw deck in the controller
  def deal_card(self) -> Card:
    return self.draw_pile.pop()

class HWController(Controller):
  def __init__(self):
    super().__init__()
    self.ser_init()
    self.cam_init()
    self.keypad_init()
    self.model_init()
    self.reset()

  def ser_init(self) -> None:
    self.ser = serial.Serial("/dev/ttyACM0", 9600, timeout=10)
  
  def ser_wait(self) -> str:
    while True:
        if self.ser.in_waiting > 0:
            line = self.ser.readline().decode("ascii").strip()
            return line


  def cam_init(self) -> None:
    # self.cam_bot = Picamera2(0)
    # self.cam_config = self.cam_bot.create_still_configuration({"size": (360, 360)})
    # self.cam_bot.configure(self.cam_config)
    # self.cam_top = Picamera2(1)
    # self.cam_top.configure(self.cam_config)
    # self.cam_bot.start(show_preview=False)
    # self.cam_top.start(show_preview=False)
    pass

  def keypad_init(self) -> None:
    # TODO: figure out keypad pin specifics
    pass

  def model_init(self) -> None:
    file_dir = os.path.split(__file__)[0]
    model_dir = os.path.join(file_dir,'../classification/models')
    self.model_top = init_model(os.path.join(model_dir, 'model_top_pretrain.pth'), True)
    self.model_bot = init_model(os.path.join(model_dir, 'model_bot_pretrain.pth'), True)
    self.model_color = init_model(os.path.join(model_dir, 'model_color_pretrain.pth'), True)
    
  def reset(self) -> None:
    pass

  def get_card(self, player: Player) -> Optional[Card]:
    # TODO: wait for button press
    # image = self.cam_top.capture_array()

    # TODO: classify card
    # TODO: convert classifcation to card type
    return None

  def get_draw_card_response(self, player: Player, card: Card) -> bool:
    # TODO: wait for button press
    return False

  def get_bluff_answer(self, player: Player) -> bool:
    # TODO: wait for button press
    return False

  def get_color_choice(self, player: Player) -> Color:
    # TODO: wait for button press
    return Color.RED

  def advance_turn(self, dir: int) -> None:
    self.ser.write(f'r{dir}200\n'.encode("ascii"))
    _ = self.ser_wait()

  def deal_card(self) -> Card:
    # image = self.cam_bot.capture_array()
    self.ser.write("d\n".encode("ascii"))

    # TODO: classify card
    # TODO: convert classifcation to card type

    _ = self.ser_wait()
    return Card(None, None)
