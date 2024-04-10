'''
References:
 * Official uno rules -> https://service.mattel.com/instruction_sheets/42001pr.pdf
'''

# enables lazy type annotation resolving
from __future__ import annotations

from typing import Collection, Optional
from queue import Queue # used for golang-style channels
from threading import Thread
from enum import Enum
import logging

from uno.deck import Deck
from uno.card import Color
from uno.card import Card, Wild, PlusFour
from uno.player import Player
from uno.requests import *

class UNO:

  class State(Enum):
    INIT_PHASE = 0
    PLAY_CARD_PHASE = 




  def __init__(self, input_queue: Queue[Request], output_queue: Queue[Request]):
    self._input_queue = input_queue # requests coming in from the manager or internally
    self._output_queue = output_queue # requests going out to the manager 
    self._main_loop_thread = Thread(target=self._main_loop, daemon=True)
    self.init_phase = True

  def start(self):
    self._main_loop_thread.start()
    
  def reset(self, request: Reset):

    self.hand_size: int = 7
    self.num_players: int = 4
    self.discard_pile: Deck = Deck(0)
    self.color: Optional[Color] = None # this is extra info for when the top card is wild or plus4
    self.turn: int = 0 # stores the index of the current player's turn
    self.dir: int = +1 # stores which direction the game is moving in 

    # generate players with empty hands
    self.players: Collection[Player] = [Player([], pos) for pos in range(self.num_players)]

    # do the initial dealing phase

    for pos in range(self.num_players):
      # deal all the cards to this player
      # self.players.append(Player([self.manager.deal_card() for _ in range(self.hand_size)], pos))
      for _ in range(self.hand_size):
        player = self.players[pos]
        self._output_queue.put(DealCard(player))
      self.go_next_player()


    while True:
      request = self._input_queue.get()

      if type(request) is Reset:
        self.reset(request)

      elif type(request) is DealtCard:
        player = request.player
        player.receive_card(request.card)

      # TODO: handle state corrections

  
    # do the initial dealing phase
    # for pos in range(self.num_players):
    #   # deal all the cards to this player
    #   # self.players.append(Player([self.manager.deal_card() for _ in range(self.hand_size)], pos))
    #   for _ in range(self.hand_size):
    #     player = self.players[pos]
    #     dealt_card = self.deal_card()
    #     print(f'dealt_card: {dealt_card}')
    #     player.receive_card(dealt_card)

    #   # advance to the next player
    #   self.go_next_player()

    # # repeatedly check if we are drawing wilds or plus4s
    # # if we are, put them on the discard pile

    # while (initial_card := self.deal_card()).type in [Wild, PlusFour]:
    #   self.discard_pile.push(initial_card)

    # # we now have a non wild / plus4 card
    # # play this card
    # initial_card.play_card(self)

  def _main_loop(self):
    while True:
      request = self._input_queue.get()

      if type(request) is Reset:
        self.reset(request)

  def is_game_over(self):
    return any(map(lambda p: p.hand == [], self.players))

  # def play_one_turn(self):
  #   curr_player: Player = self.players[self.turn]

  #   # if the player cannot play, just give them a card and return
  #   # if not curr_player.can_play(self.discard_pile.peek(), self.color):
  #   #   drawn_card = self.manager.deal_card(curr_player)
  #   #   curr_player.receive_card(drawn_card)
  #   #   self.go_next_player()
  #   #   return

  #   # ask the player for a card
  #   selected_card = self.manager.get_card(curr_player)
  #   playable_hand = curr_player.get_playable_cards(self.discard_pile.peek(), self.color)

  #   if selected_card is not None and selected_card not in playable_hand:
  #     self.manager.signal_invalid_state(self)

  #   # if they give a card back, play it
  #   if selected_card is not None:
  #     selected_card.play_card(self)

  #     # TODO: this validation should probably happen inside the player class
  #     # TODO: there should still be stuff in the player, this shouldn't be here
  #     # remove the card from the player's hand
  #     curr_player.hand.remove(selected_card)
  #     curr_player._sort_hand()
      
  #   # otherwise, they should draw a card
  #   else:
  #     drawn_card = self.manager.deal_card(curr_player)
  #     # ask them if they want to play
  #     if drawn_card.is_playable(self.discard_pile.peek(), self.color) \
  #        and self.manager.get_draw_card_response(curr_player, drawn_card):
  #       # play the card
  #       drawn_card.play_card(self)
  #     else:
  #       # otherwise, put the card in their hand
  #       curr_player.receive_card(drawn_card)

  #       # advance the turn
  #       self.go_next_player()
  
  def go_next_player(self) -> None:
    self._output_queue.put(GoNextPlayer(self.dir))
    self.turn = (self.turn + self.dir) % self.num_players

  def go_prev_player(self) -> None:
    self._output_queue.put(GoNextPlayer(-self.dir))
    self.turn = (self.turn - self.dir) % self.num_players

  def reverse(self) -> None:
    self.dir = -self.dir

  def __del__(self) -> None:
    # TODO: send a signal to self to end the thread
    pass

  def __repr__(self) -> str:
    return ''
