'''
Base class & implementations of the state displayer.
'''


# enables lazy type annotation resolving
from __future__ import annotations

import tkinter as tk
from PIL import Image, ImageTk
import io
import os
from threading import Thread
from queue import Queue
import socketio

from uno.card import Card, Wild, PlusFour
from uno.player import Player
from uno.requests import *

# only import what we need if we are doing type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from uno.uno import DisplayUNOState


class Displayer:
  def __init__(self, input_queue: Queue[Request], output_queue: Queue[Request]):
    self._input_queue = input_queue
    self._output_queue = output_queue
    self._main_loop_thread = Thread(target=self._main_loop, daemon=True)


  # starts the thread to listen on the queues
  def start(self):
    self._main_loop_thread.start()

  # resets the displayer
  def reset(self):
    pass

  def _main_loop(self):
    while True:
      request = self._input_queue.get()

      if type(request) is CurrentState:
        self.display_state(request.state)
      elif type(request) is GameOver:
        print(f'{request.winning_player.name} has won the game! Their total score is {request.winning_player.score} points!')
      elif type(request) is RoundOver:
        print(f'{request.winning_player.name} has won the round! Their current score is {request.winning_player.score} points!')
      else:
        print('Unknown request sent to Displayer')

  # display the game state in a non-blocking way
  def display_state(self, state: DisplayUNOState) -> None:
    pass

  # TODO: need some function that listens for state corrections and forwards them to the manager

  # # signal that we have entered an invalid state
  # def signal_invalid_state(self, state: UNO) -> None:
  #   pass

class WebsiteDisplayer(Displayer):
  def __init__(self, input_queue: Queue[Request], output_queue: Queue[Request], url: str):
    super().__init__(input_queue, output_queue)

    self.url = url
    self.socketio = socketio.Client()

    # connect to the web socket
    try:
      self.socketio.connect(self.url)
    except:
      print(f'Could not connect to {self.url}. Did you start the web server?')

    # initialize the callback for reset
    @self.socketio.on('reset')
    def receive_reset_request(data):
      self.handle_reset_request(data)

    # initialize the callback for reset
    @self.socketio.on('round_reset')
    def receive_round_reset_request():
      self.handle_round_reset_request()



  def reset(self) -> None:
    pass

  def handle_reset_request(self, data):
    # process the data that we get
    try:
      num_players: int = int(data['num_players'])
      hand_size: int = int(data['num_cards'])
    except:
      return
    # construct the request
    request = Reset(num_players, hand_size)

    # send that request in the output queue
    self._output_queue.put(request)

  def handle_round_reset_request(self):
    # construct the request
    request = RoundReset()

    # send that request in the output queue
    self._output_queue.put(request)


  def display_state(self, state: DisplayUNOState) -> None:
    # package up the state and send it to the website
    self.socketio.emit('from_pi', state.to_json())
    # pass


class TerminalDisplayer(Displayer):
  def __init__(self, input_queue: Queue[Request], output_queue: Queue[Request]):
    super().__init__(input_queue, output_queue)

  def reset(self) -> None:
    pass

  # show what the game state looks like
  def display_state(self, state: DisplayUNOState) -> None:
    top_card = state.discard_pile.peek()
    color = state.color

    if type(top_card) in [Wild, PlusFour]:
      print(f'Top card: {top_card}, Color: {color.name}')
    else:
      print(f'Top card: {top_card}')

    # print everyone's hands  
    for player in state.players:
      if player.position == state.turn:
        print('--->', end='')
        if player.drawn_card is not None:
          print(player.hand, end='')
          print(' Drawn card: ' + str(player.drawn_card))
        else:
          print(player.hand)
      else:  
        print('    ', end='')
        print(player.hand)
    print()
  
  # def signal_invalid_state(self, state: UNO) -> None:
  #   print('The board has entered an invalid state. Exiting...')
  #   self.display_state(state)
  #   exit(1)


# DEPRICATED
class TkDisplayer(Displayer):
  def __init__(self, input_queue: Queue[Request], output_queue: Queue[Request]):
    super().__init__(input_queue, output_queue)
    self.window = tk.Tk()
    self.window.title('UNO!')
    self.height = 1080
    self.width = 1920
    self.card_height = 150
    self.card_width = 100
    self.margin = 10
    self.canvas = tk.Canvas(self.window, width=self.width, height=self.height)
    self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
    self.window.update_idletasks()

    # fill a list of all card images
    self.images: dict[str, ImageTk.PhotoImage] = {}

    folder_path = os.path.join(os.path.dirname(__file__), 'images')
    for file_name in os.listdir(folder_path):
      path = os.path.join(folder_path, file_name)
      self.images[file_name] = ImageTk.PhotoImage(Image.open(path).resize((self.card_width, self.card_height)))

  def reset(self) -> None:
    pass

  def _draw_card(self, card: Card, sx: int, sy: int):
    self.canvas.create_image(sx, sy, anchor=tk.NW, image=self.images[card.image_name])

  def display_state(self, state: DisplayUNOState) -> None:
    self.canvas.delete(tk.ALL)
    # curr_player: Player = state.players[state.turn]
    
    # draw all of the player's hands
    for player_idx, player in enumerate(state.players):
      hand_start_x = self.width / 2 - (self.card_width + self.margin) * (len(player.hand) / 2)
      hand_start_y = 5/16 * self.height + player_idx * (self.card_height + 15)
      for i, card in enumerate(player.hand):
        self._draw_card(card, hand_start_x + i * (self.card_width + self.margin), hand_start_y)

      # draw a rectangle around the player whose turn it is
      if player_idx == state.turn:
        self.canvas.create_rectangle(
          hand_start_x - 5, 
          hand_start_y - 5, 
          hand_start_x + (self.card_width + self.margin) * len(player.hand) - self.margin + 5, 
          hand_start_y + self.card_height + 5,
          fill=None,
          outline='purple',
          width=10,
          dash=(5,)
        )

    # draw the top card
    top_card = state.discard_pile.peek()
    if top_card is not None:
      self._draw_card(top_card, self.width/2 - self.card_width/2, 1/12 * self.height)
      self.canvas.create_text(self.width / 2, 1/12 * self.height - 30, text='Top Card', font=('Purisa Bold', 20), fill=state.color.name)
    self.window.update_idletasks()
    
  def signal_invalid_state(self, state: DisplayUNOState) -> None:
    print('The board has entered an invalid state. Exiting...')
    exit(1)


'''
When to update the displayer (send whole state):
 * when a player receives a card
 * when a player plays a card
 * when the color of the deck changes (player sets the color after + 4)
 * when the turn changes 

'''
    
