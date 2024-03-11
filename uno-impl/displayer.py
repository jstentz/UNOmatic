'''
Base class & implementations of the state displayer.
'''


# enables lazy type annotation resolving
from __future__ import annotations

from card import Wild, PlusFour

import tkinter as tk
from card import Card, Wild, PlusFour, Skip, Reverse, PlusTwo, Number
from player import Player


# only import what we need if we are doing type checking
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from uno import UNO

class Displayer:
  def __init__(self):
    pass

  def reset(self):
    pass

  # show what the game state looks like
  def display_state(self, state: UNO) -> None:
    pass

  # signal that we have entered an invalid state
  def signal_invalid_state(self) -> None:
    pass


class TerminalDisplayer(Displayer):
  def __init__(self):
    self.reset()

  def reset(self) -> None:
    pass

  # show what the game state looks like
  def display_state(self, state: UNO) -> None:
    top_card = state.discard_pile.peek()
    color = state.color

    if type(top_card) in [Wild, PlusFour]:
      print(f'Top card: {top_card}, Color: {color.name}')
    else:
      print(f'Top card: {top_card}')
  
  def signal_invalid_state(self) -> None:
    print('The board has entered an invalid state. Exiting...')
    exit(1)


class TkDisplayer(Displayer):
  def __init__(self):
    self.window = tk.Tk()
    self.window.title('UNO!')
    self.height = 1080
    self.width = 1600
    self.card_height = 150
    self.card_width = 100
    self.margin = 10
    self.canvas = tk.Canvas(self.window, width=self.width, height=self.height)
    self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
    self.reset()

  def reset(self) -> None:
    pass

  def _draw_card(self, card: Card, sx: int, sy: int):
    cx = sx + self.card_width / 2
    cy = sy + self.card_height / 2
    
    # create the rectangle
    card_color = card.color.name if card.color is not None else 'black'
    self.canvas.create_rectangle(sx, sy, sx + self.card_width, sy + self.card_height, fill=card_color)

    text_fill = 'black' if card_color == 'YELLOW' else 'white'

    if type(card) == Number:
      self.canvas.create_text(cx, cy, text=str(card.number), fill=text_fill, font=('Purisa Bold', 14))
    else:
      self.canvas.create_text(cx, cy, text=type(card).__name__, fill=text_fill, font=('Purisa Bold', 14))


  def display_state(self, state: UNO) -> None:
    self.canvas.delete(tk.ALL)
    curr_player: Player = state.players[state.turn]

    # draw the player's hand
    hand_start = self.width / 2 - (self.card_width + self.margin) * (len(curr_player.hand) / 2) 
    for i, card in enumerate(curr_player.hand):
      self._draw_card(card, hand_start + i * (self.card_width + self.margin), 5/8 * self.height)
    self.canvas.create_text(self.width / 2, 5/8 * self.height + self.card_height + 30, text=f'{curr_player.name}\'s Hand', font=('Purisa Bold', 20))

    # draw the top card
    top_card = state.discard_pile.peek()
    if top_card is not None:
      self._draw_card(top_card, self.width/2 - self.card_width/2, 1/4 * self.height)
      self.canvas.create_text(self.width / 2, 1/4 * self.height - 30, text='Top Card', font=('Purisa Bold', 20))
    
  def signal_invalid_state(self) -> None:
    print('The board has entered an invalid state. Exiting...')
    exit(1)
    