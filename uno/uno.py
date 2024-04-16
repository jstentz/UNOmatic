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

  def __init__(self, input_queue: Queue[Request], output_queue: Queue[Request]):
    self._input_queue = input_queue # requests coming in from the manager or internally
    self._output_queue = output_queue # requests going out to the manager 
    self._internal_queue = Queue() # this queue is for passing messages in between card threads and the main thread
    self._main_loop_thread = Thread(target=self._main_loop, daemon=True)

    # this thread is basically a sequence runner 
    self._sequence_thread: Optional[Thread] = None

  def start(self):
    self._main_loop_thread.start()
    
  def reset(self, request: Reset):
    # check to see if there is a lingering card player thread
    if self._sequence_thread is not None and self._sequence_thread.is_alive():
      self._internal_queue.put(request)
      self._sequence_thread.join()

    self.hand_size: int = 7
    self.num_players: int = 4
    self.discard_pile: Deck = Deck(0)
    self.color: Optional[Color] = None # this is extra info for when the top card is wild or plus4
    self.turn: int = 0 # stores the index of the current player's turn
    self.dir: int = +1 # stores which direction the game is moving in 

    # stores who is punishable
    self.is_uno_punishable: Optional[int] = None

    # generate players with empty hands
    self.players: Collection[Player] = [Player([], pos) for pos in range(self.num_players)]


    self._sequence_thread = Thread(target=self.run_init_phase, daemon=True)

    # handle the sequence of actions to init the game
    self._sequence_thread.start()
    

  def _main_loop(self):
    while True:
      request = self._input_queue.get()

      if type(request) is Reset:
        self.reset(request)
      elif type(request) in [CurrentState, CorrectedState]:
        # TODO: handle these requests
        pass
      elif type(request) in [PlayCard, CallUNO]:
        # make sure there isn't another card being played (there shouldn't be lil bro)
        # reap the thread 
        self._sequence_thread.join() 
        
        card = request.card
        # check to see if we can play this card
        curr_player: Player = self.players[self.turn]
        if card not in curr_player.get_playable_cards(self.discard_pile.peek(), self.color):
          # TODO: send something to controller / displayer
          print('Unplayable card')
          self._output_queue.put(GetUserInput([PlayCard, SkipTurn]))
          continue

        # pop this card off the players hand
        curr_player.hand.remove(card)

        self._sequence_thread = Thread(target=card.play_card, args=(self,), daemon=True)

        # handle the sequence of actions caused by this card
        self._sequence_thread.start()

      elif type(request) is SkipTurn:
        # TODO: spawn thread to handle this transaction
        pass
      else:
        # forward along to card handler
        self._internal_queue.put(request)

  def is_game_over(self):
    return any(map(lambda p: p.hand == [], self.players))
  
  def run_init_phase(self):
    for pos in range(self.num_players):
      curr_player: Player = self.players[pos]
      # deal all the cards to this player
      for _ in range(self.hand_size):
        if (received_request := self.transaction_sync(DealCard(curr_player))) is None: return
        curr_player.receive_card(received_request.card)
        
      self.go_next_player(is_turn_end=False)

    # get the initial card
    while True:
      if (received_request := self.transaction_sync(DealCard(player=None))) is None: return
      if type(received_request.card) not in [Wild, PlusFour]:
        break
    
    received_request.card.play_card(self)


  def transaction_sync(self, request: Request) -> Optional[Request]:
    # send out the request
    self._output_queue.put(request)
    # wait on the internal queue for card-related requests (or reset)
    received_request = self._internal_queue.get()
    return None if type(received_request) is Reset else received_request

  
  def go_next_player(self, is_turn_end: bool = True) -> None:
    self._output_queue.put(GoNextPlayer(self.dir))
    prev_turn = self.turn
    self.turn = (self.turn + self.dir) % self.num_players

    # debugging: print out the state
    if is_turn_end:
      print(self)


    # check to see what we should listen for 
    if is_turn_end:
      curr_player = self.players[self.turn]
      prev_player = self.players[prev_turn]

      request_list = [PlayCard, SkipTurn]
      
      if len(curr_player.hand) == 2:
        # self.is_uno_punishable = 
        # TODO: fix using this flag
        request_list.append(CallUNO)

      self._output_queue.put(GetUserInput(request_list))

  def go_prev_player(self) -> None:
    self._output_queue.put(GoNextPlayer(-self.dir))
    self.turn = (self.turn - self.dir) % self.num_players

  def reverse(self) -> None:
    self.dir = -self.dir

  # def player_has_uno(self) -> bool:
  #   return [player for player in self.players if len(player.hand) == 1] != [ ] 

  def __del__(self) -> None:
    # TODO: send a signal to self to end the thread
    pass

  def __repr__(self) -> str:
    res = f'Top card: {self.discard_pile.peek()}, Color: {self.color.name if self.color is not None else "None"}\n'

    curr_player = self.players[self.turn]
    res += str(curr_player)
    return res

'''
Add a button that means "playing with UNO call"

Add "player_that_can_be_bluffed" to the state (UNO VICTIM)

'''