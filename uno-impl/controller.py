# enables lazy type annotation resolving
from __future__ import annotations


from card import Card

# Base class for the functionality that a Controller must support
class Controller:
  
  def __init__(self):
    pass

  def get_card(self) -> Card:
    pass

  def get_bluff_answer(self):
    pass

  def go_next_player(self):
    pass

  def deal_card(self) -> Card:
    pass

