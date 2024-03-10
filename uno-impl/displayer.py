'''
Base class & implementations of the state displayer.
'''

# enables lazy type annotation resolving
from __future__ import annotations

from card import Wild, PlusFour

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