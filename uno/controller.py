# enables lazy type annotation resolving
from __future__ import annotations

import os
import time
import numpy as np

from typing import Optional
from queue import Queue

import serial
try:
  from picamera2 import Picamera2
  import gpiod
except ImportError:
  print('WARNING: Hardware modules not installed')

from uno.card import Card, Color
from uno.deck import Deck
from uno.player import Player
from uno.displayer import TkDisplayer

from classification.forward import init_model, get_card
from uno.utils import card_from_classification


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
    ...

  # get whether or not the player wants to play the card they were just dealt
  def get_draw_card_response(self, player: Player, card: Card) -> bool:
    ...

  def get_bluff_answer(self, player: Player) -> bool:
    ...

  def get_color_choice(self, player: Player) -> Color:
    ...

  # advance to the next player
  # dir is either +/- 1, depending on the direction 
  def advance_turn(self, dir: int) -> None:
    ...

  # here, I guess the software controller will have to maintain it's own draw deck in the controller
  def deal_card(self) -> Card:
    ...
  
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
  row_pins = [
  ("r1", 6),
  ("r2", 21),
  ("r3", 20),
  ("r4", 19)]

  col_pins = [
  ("c1", 13),
  ("c2", 5),
  ("c3", 26)]

  RESET = (0,0)
  UNO_FAIL = (0,1)
  PLAY_TURN = (1,0)
  SKIP_TURN = (1,1)
  CALL_BLUFF = (2,0)
  NO_CALL_BLUFF = (2,1)
  RESERVED_1 = (3,0)
  RESERVED_2 = (3,1)
  SET_RED = (0,2)
  SET_BLUE = (1,2)
  SET_GREEN = (2,2)
  SET_YELLOW = (3,2)
  def __init__(self):
    super().__init__()
    self.ser_init()
    self.cam_init()
    self.keypad_init()
    self.model_init()
    self.reset()

  def ser_init(self) -> None:
    self.ser = serial.Serial("/dev/ttyACM0", 9600, timeout=10)
    time.sleep(1)
  
  def ser_wait(self) -> str:
    while True:
        if self.ser.in_waiting > 0:
            line = self.ser.readline().decode("ascii").strip()
            return line


  def cam_init(self) -> None:
    self.cam_bot = Picamera2(0)
    self.cam_config = self.cam_bot.create_still_configuration({"size": (360, 360)})
    self.cam_bot.configure(self.cam_config)
    self.cam_top = Picamera2(1)
    self.cam_top.configure(self.cam_config)
    self.cam_bot.start(show_preview=False)
    self.cam_top.start(show_preview=False)

  def keypad_init(self) -> None:
    # TODO: figure out keypad pin specifics
    chip = gpiod.Chip('gpiochip4')
    self.row_lines = []
    for (consumer, pin) in HWController.row_pins:
        self.row_lines.append(chip.get_line(pin))
        self.row_lines[-1].request(consumer = consumer, type=gpiod.LINE_REQ_DIR_IN, flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_DOWN)
    self.col_lines = []
    for (consumer, pin) in HWController.col_pins:
        self.col_lines.append(chip.get_line(pin))
        self.col_lines[-1].request(consumer = consumer, type=gpiod.LINE_REQ_DIR_OUT)
        self.col_lines[-1].set_value(0)

  def keypad_read(self) -> Optional[tuple[int, int]]:
    for (i, col) in enumerate(self.col_lines):
      col.set_value(1)
      for (j, row) in enumerate(self.row_lines):
        if row.get_value() == 1:
          col.set_value(0)
          return (j, i)
        col.set_value(0)
    return None

  def model_init(self) -> None:
    file_dir = os.path.split(__file__)[0]
    model_dir = os.path.join(file_dir,'../classification/models')
    self.model_top = init_model(os.path.join(model_dir, 'model_top_pretrain.pth'), True)
    self.model_bot = init_model(os.path.join(model_dir, 'model_bot_pretrain.pth'), True)
    self.model_color = init_model(os.path.join(model_dir, 'model_color_pretrain.pth'), True)
    
  def reset(self) -> None:
    pass

  def get_card(self, player: Player) -> Optional[Card]:
    while val := self.keypad_read() != HWController.PLAY_TURN or HWController.SKIP_TURN:
      pass
    if val == HWController.SKIP_TURN:
      return None
    image = self.cam_top.capture_array().astype(np.float32) / 255
    return card_from_classification(*get_card(self.model_top, self.model_color, image, True))

  def get_draw_card_response(self, player: Player, card: Card) -> bool:
    while val := self.keypad_read() != HWController.PLAY_TURN or HWController.SKIP_TURN:
      pass
    return val == HWController.PLAY_TURN

  def get_bluff_answer(self, player: Player) -> bool:
    while val := self.keypad_read() != HWController.CALL_BLUFF or HWController.NO_CALL_BLUFF:
      pass
    return val == HWController.CALL_BLUFF

  def get_color_choice(self, player: Player) -> Color:
    while val := self.keypad_read() != HWController.SET_RED or HWController.SET_BLUE or HWController.SET_GREEN or HWController.SET_GREEN:
      pass
    # TODO: set led
    if val == HWController.SET_RED:
      return Color.RED
    elif val == HWController.SET_BLUE:
      return Color.BLUE
    elif val == HWController.SET_GREEN:
      return Color.GREEN
    else:
      return Color.YELLOW

  def advance_turn(self, dir: int) -> None:
    self.ser.write(f'r{dir}\n'.encode("ascii"))
    _ = self.ser_wait()

  def deal_card(self) -> Card:
    image = self.cam_bot.capture_array().astype(np.float32) / 255

    self.ser.write("d\n".encode("ascii"))
    labels = get_card(self.model_bot, self.model_color, image, False)
    _ = self.ser_wait()

    card = card_from_classification(*labels)
    print(card)
    return card
