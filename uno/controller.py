# enables lazy type annotation resolving
from __future__ import annotations

import os
from threading import Thread, Lock
import time
import numpy as np

from typing import Optional
from queue import Queue
import sys
import select

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
from uno.requests import *
from uno.utils import card_from_string, color_from_string

from typing import Collection


class Controller:
  OutgoingRequests = [PlayCard, DealtCard, SkipTurn, SetColor, Bluff, CallUNO, UNOFail]
  IncomingActionRequests = [GoNextPlayer, DealCard]

  def __init__(self, input_queue: Queue[Request], output_queue: Queue[Request]): 
    self._input_queue = input_queue # requests coming in from the manager or internally
    self._output_queue = output_queue # requests going out to the manager 
    self._listener_queue: Queue[Request] = Queue()
    self._stop_queue: Queue[bool] = Queue()
    self._main_loop_thread = Thread(target=self._main_loop, daemon=True)
    self._input_listener_thread = Thread(target=self._input_listener, daemon=True)

  def start(self):
    self._main_loop_thread.start()
    self._input_listener_thread.start()

  # resets the controller's state, this could happen 
  def reset(self):
    # clear the queue
    while not self._input_queue.empty():
      self._input_queue.get()

    # tell the listener thread to reset
    self._listener_queue.put(Reset())
    
  def _main_loop(self):
    while True:
      # blocks until there is some request to handle (either something from the manager or a button press)
      request = self._input_queue.get()

      if type(request) is ControllerReset:
        self._output_queue.put(Reset())
      elif type(request) is ControllerRoundReset:
        self._output_queue.put(RoundReset())
      elif type(request) is GetUserInput:
        self._handle_action(request)
        self._listener_queue.put(request)
      elif type(request) in Controller.OutgoingRequests:
        self._output_queue.put(request)
      elif type(request) in Controller.IncomingActionRequests:
        self._handle_action(request)
      else:
        print(f'Controller received invalid {type(request)} request!')

  # to be implemented by derived classes
  def _input_listener(self):
    pass

  # to be implemented by derived classes (make _input_listener unresponsive until this is done?)
  def _handle_action(self, request):
    pass


class TerminalController(Controller):
  POLL_RATE = 0.01

  def __init__(self, input_queue: Queue[Request], output_queue: Queue[Request]):
    super().__init__(input_queue, output_queue)

  @staticmethod
  def is_input_available():
    return sys.stdin in select.select([sys.stdin], [], [], 0)[0]

  @staticmethod
  def cmd_to_request(user_input: str) -> Request:
    parsed = user_input.split(' ')
    cmd, rest = parsed[0], parsed[1:]
    if cmd == 'play':
      card = card_from_string(*rest)
      return PlayCard(card)
    elif cmd == 'skip':
      return SkipTurn()
    elif cmd == 'color':
      return SetColor(color_from_string(rest[0]))
    elif cmd == 'call_bluff':
      return Bluff(True)
    elif cmd == 'no_bluff':
      return Bluff(False)
    elif cmd == 'uno':
      card = card_from_string(*rest)
      return CallUNO(card)
    elif cmd == 'uno_fail':
      return UNOFail()
    elif cmd == 'reset':
      return ControllerReset()
    elif cmd == 'round_reset':
      return ControllerRoundReset()
    
  def _input_listener(self):
    allowed_input_types = [ControllerReset, ControllerRoundReset]
    for_drawn_card = False
    # poll forever
    while True:
      if not self._listener_queue.empty():
        # clear input buffer
        while TerminalController.is_input_available():
          input()

        request = self._listener_queue.get()
        if type(request) is Reset:
          allowed_input_types = [ControllerReset, ControllerRoundReset]
          for_drawn_card = False
          continue
        else:
          allowed_input_types += request.request_types
          for_drawn_card = request.for_drawn_card
      
      if TerminalController.is_input_available():
        cmd = input()
        try:
          request = TerminalController.cmd_to_request(cmd)
          # pass along info for CallUNO and PlayCard
          if type(request) in [PlayCard, CallUNO, SkipTurn]:
            request.for_drawn_card = for_drawn_card
          
          # fix this to first construct the types 
          if type(request) in allowed_input_types:
            self._input_queue.put(request)
            allowed_input_types = [ControllerReset, ControllerRoundReset]
            for_drawn_card = False
        except:
          print('Error when parsing command')

      
      time.sleep(TerminalController.POLL_RATE)


  def _handle_action(self, request: Request) -> None:
    if type(request) is DealCard:
      dealt_card = self.draw_pile.pop()
      self._output_queue.put(DealtCard(dealt_card, request.player))

  def reset(self):
    self.draw_pile: Deck = Deck(Deck.TOTAL_CARDS)
    super().reset()
  
class HardwareController(Controller):
  POLL_RATE = 0.01

  row_pins = [
  ("r1", 6),
  ("r2", 21),
  ("r3", 20),
  ("r4", 19)]

  col_pins = [
  ("c1", 13),
  ("c2", 5),
  ("c3", 26)]

  status_led_pin = ("status", 16)

  key_map: list[list[Optional[type[Request]]]] = [[PlayCard, CallUNO, SetColor],
                                                  [SkipTurn, UNOFail, SetColor],
                                                  [ControllerRoundReset, Bluff, SetColor],
                                                  [ControllerReset, Bluff, SetColor]]
  bluff_map: dict[int, bool] = {2: True, 3: False}
  color_map: list[Color] = [Color.RED, Color.BLUE, Color.GREEN, Color.YELLOW]

  def __init__(self, input_queue: Queue[Request], output_queue: Queue[Request]):
    super().__init__(input_queue, output_queue)
    self.lock_init()
    self.ser_init()
    self.cam_init()
    self.gpio_init()
    self.model_init()

  def lock_init(self):
    self.keypad_lock = Lock()

  def ser_init(self) -> None:
    self.ser = serial.Serial("/dev/ttyACM0", 9600, timeout=30)
    time.sleep(2)

  def ser_wait(self) -> str:
    while True:
      if self.ser.in_waiting > 0:
        return self.ser.readline().decode("ascii").strip()
      time.sleep(HardwareController.POLL_RATE)
        

  def cam_init(self) -> None:
    self.cam_bot = Picamera2(0)
    self.cam_config = self.cam_bot.create_still_configuration({"size": (360, 360)})
    self.cam_bot.configure(self.cam_config)
    self.cam_top = Picamera2(1)
    self.cam_top.configure(self.cam_config)
    self.cam_bot.start(show_preview=False)
    self.cam_top.start(show_preview=False)

  def gpio_init(self) -> None:
    chip = gpiod.Chip('gpiochip4')
    self.row_lines = []
    for (consumer, pin) in HardwareController.row_pins:
        self.row_lines.append(chip.get_line(pin))
        self.row_lines[-1].request(consumer = consumer, type=gpiod.LINE_REQ_DIR_IN, flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_DOWN)
    self.col_lines = []
    for (consumer, pin) in HardwareController.col_pins:
        self.col_lines.append(chip.get_line(pin))
        self.col_lines[-1].request(consumer = consumer, type=gpiod.LINE_REQ_DIR_OUT)
        self.col_lines[-1].set_value(0)
    self.led_line = chip.get_line(self.status_led_pin[1])
    self.led_line.request(consumer=self.status_led_pin[0], type=gpiod.LINE_REQ_DIR_OUT)

  def keypad_read(self) -> Optional[tuple[int, int]]:
    self.keypad_lock.acquire()
    for (i, col) in enumerate(self.col_lines):
      col.set_value(1)
      for (j, row) in enumerate(self.row_lines):
        if row.get_value() == 1:
          while row.get_value() == 1:
            time.sleep(HardwareController.POLL_RATE)
          time.sleep(0.050)
          col.set_value(0)
          self.keypad_lock.release()
          return (j, i)
      col.set_value(0)
    self.keypad_lock.release()
    return None

  def model_init(self) -> None:
    file_dir = os.path.split(__file__)[0]
    model_dir = os.path.join(file_dir,'../classification/models')
    self.model_top = init_model(os.path.join(model_dir, 'model_top_pretrain.pth'), True)
    self.model_bot = init_model(os.path.join(model_dir, 'model_bot_pretrain.pth'), True)
    self.model_color = init_model(os.path.join(model_dir, 'model_color_pretrain.pth'), True)
    
  def _input_listener(self):
    allowed_input_types = [ControllerRoundReset, ControllerReset]
    for_drawn_card = False
    # poll forever
    while True:
      if not self._listener_queue.empty():

        request = self._listener_queue.get()
        if type(request) is Reset:
          allowed_input_types = [ControllerRoundReset, ControllerReset]
          for_drawn_card = False
          continue
        else:
          allowed_input_types += request.request_types
          for_drawn_card = request.for_drawn_card
      
      if (button_press := self.keypad_read()) is not None:
        request_type = self.key_map[button_press[0]][button_press[1]]

        if request_type not in allowed_input_types:
          continue

        if request_type in [PlayCard, CallUNO]:
          image = self.cam_top.capture_array().astype(np.float32) / 255
          card = card_from_classification(*get_card(self.model_top, self.model_color, image, True))
          request = request_type(card)
        elif request_type == SetColor:
          color = self.color_map[button_press[0]]
          request = request_type(color)
        elif request_type == Bluff:
          is_bluff = self.bluff_map[button_press[0]]
          request = request_type(is_bluff)
        else:
          request = request_type()

        # pass along info for CallUNO and PlayCard
        if request_type in [PlayCard, CallUNO, SkipTurn]:
          request.for_drawn_card = for_drawn_card
        
        # fix this to first construct the types 
        self._input_queue.put(request)
        allowed_input_types = [ControllerRoundReset, ControllerReset]
        for_drawn_card = False
      
      time.sleep(HardwareController.POLL_RATE)

  def _handle_action(self, request: Request) -> None:
    if type(request) is GoNextPlayer:
      steps = request.dir * (200*4) // request.num_players
      self.ser.write(f'r{steps}\n'.encode("ascii"))
      _ = self.ser_wait()
    elif type(request) is GetUserInput:
      if self.invalid_card != request.for_invalid_card:
        self.led_line.set_value(int(request.for_invalid_card))
    elif type(request) is DealCard:
      image = self.cam_bot.capture_array().astype(np.float32) / 255

      self.ser.write("d\n".encode("ascii"))
      labels = get_card(self.model_bot, self.model_color, image, False)
      if self.ser_wait() == "t":
        card = card_from_classification(*labels)
        self._output_queue.put(DealtCard(card, request.player))
        return

      # for _ in range(2):
      #   self.ser.write("u\n".encode("ascii"))
      #   _ = self.ser_wait()
      #   self.ser.write("u\n".encode("ascii"))
      #   _ = self.ser_wait()
      #   self.ser.write("d\n".encode("ascii"))
      #   if self.ser_wait() == "t":
      #     card = card_from_classification(*labels)
      #     self._output_queue.put(DealtCard(card, request.player))
      #     return
      #   self.ser.write("u\n".encode("ascii"))
      #   _ = self.ser_wait()

      while True:
        button_press = self.keypad_read()
        if button_press is None:
          continue
        if self.key_map[button_press[0]][button_press[1]] is PlayCard:
          break

      card = card_from_classification(*labels)
      self._output_queue.put(DealtCard(card, request.player))


  def reset(self):
    self.invalid_card = False
    super().reset()
  
