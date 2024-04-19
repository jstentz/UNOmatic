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

import copy

# constructs a display state by copying an uno state
class DisplayUNOState:
  def __init__(self, state: UNO):
    self.hand_size: int = state.hand_size
    self.num_players: int = state.num_players
    self.discard_pile = copy.deepcopy(state.discard_pile)
    self.color: Optional[Color] = copy.deepcopy(state.color)
    self.turn: int = state.turn
    self.dir: int = state.dir 
    self.players: Collection[Player] = copy.deepcopy(state.players)


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
    
  def reset(self, request: Request):
    # check to see if there is a lingering card player thread
    if self._sequence_thread is not None:
      self._internal_queue.put(request)
      self._sequence_thread.join()

    # clear the input queue
    while not self._internal_queue.empty():
      self._internal_queue.get()

    self.discard_pile: Deck = Deck(0)
    self.color: Optional[Color] = None # this is extra info for when the top card is wild or plus4
    self.turn: int = 0 # stores the index of the current player's turn
    self.dir: int = +1 # stores which direction the game is moving in 

    # person who needs to call UNO
    self.call_uno_player: Optional[int] = None

    # stores who is punishable for not calling uno
    self.uno_fail_player: Optional[int] = None

    if type(request) is Reset:
      # generate players with empty hands
      self.hand_size: int = request.hand_size
      self.num_players: int = request.num_players
      self.end_score: int = request.end_score
      self.players: Collection[Player] = [Player([], pos) for pos in range(self.num_players)]
    # else, we received a round reset
    else:
      # clear each players hand
      print('here')
      for player in self.players:
        player.clear_hand()

    self._sequence_thread = Thread(target=self.run_init_phase, daemon=True)

    # handle the sequence of actions to init the game
    self._sequence_thread.start()

  def _main_loop(self):
    while True:
      request = self._input_queue.get()

      if type(request) is CorrectedState:
        # TODO: handle these requests
        pass
      elif type(request) in [PlayCard, CallUNO, SkipTurn] and request.for_drawn_card:
        # just forward along to skip turn handler if we're drawing a card
        if request.for_drawn_card:
          self._internal_queue.put(request)
          continue
      elif type(request) in [PlayCard, CallUNO]:

        self.uno_fail_player = None
        if type(request) is CallUNO:
          self.call_uno_player = None
          
        # reap the thread 
        if self._sequence_thread: self._sequence_thread.join() 
        
        card = request.card
        # check to see if we can play this card
        curr_player: Player = self.players[self.turn]
        if card not in curr_player.get_playable_cards(self.discard_pile.peek(), self.color):
          print('Unplayable card')
          self._output_queue.put(GetUserInput([PlayCard, SkipTurn]))
          continue

        # pop this card off the players hand
        curr_player.remove_card(card, self)


        self._sequence_thread = Thread(target=card.play_card, args=(self,), daemon=True)

        # handle the sequence of actions caused by this card
        self._sequence_thread.start()
      elif type(request) is UNOFail:
        # punish this player
        if self._sequence_thread: self._sequence_thread.join()

        self._sequence_thread = Thread(target=self.run_uno_fail, daemon=True)

        self._sequence_thread.start()

      elif type(request) is SkipTurn:
        if self._sequence_thread: self._sequence_thread.join() 

        self.uno_fail_player = None

        if len(self.players[self.turn].hand) == 1:
          self.call_uno_player = self.turn

        self._sequence_thread = Thread(target=self.run_skip_turn, daemon=True)

        # handle the sequence of actions caused skipping
        self._sequence_thread.start()
      
      else:
        # forward along to card handler
        self._internal_queue.put(request)

  
  def run_init_phase(self):
    for pos in range(self.num_players):
      curr_player: Player = self.players[pos]
      # deal all the cards to this player
      for _ in range(self.hand_size):
        if (received_request := self.transaction_sync(DealCard(curr_player))) is None: return
        curr_player.receive_card(received_request.card, self)
        
      self.go_next_player(is_turn_end=False)

    # get the initial card
    while True:
      if (received_request := self.transaction_sync(DealCard(player=None))) is None: return
      if type(received_request.card) not in [Wild, PlusFour]:
        break
    
    received_request.card.play_card(self)

  # handles the full sequence of a player asking to draw a card 
  def run_skip_turn(self):
    # deal card to the player
    curr_player: Player = self.players[self.turn]
    if (received_request := self.transaction_sync(DealCard(curr_player))) is None: return

    received_card = received_request.card

    # for displaying later, mark received card
    curr_player.drawn_card = received_card

    # TODO: update the displayer here
    self._send_update_to_displayer()

    if received_card.is_playable(self.discard_pile.peek(), self.color):
      # ask them if they want to play the card
      # TODO: handle UNO here?

      request_list = [PlayCard, SkipTurn]

      if self.call_uno_player is not None:
        request_list.append(CallUNO)

      while True:
        if (received_request := self.transaction_sync(GetUserInput(request_list, for_drawn_card=True))) is None: return
        if type(received_request) is SkipTurn:
          # add the card to their hand 
          curr_player.receive_card(received_card, self)
          self.call_uno_player = None
          # reset this to be None
          curr_player.drawn_card = None
          self.go_next_player()
          break
        elif received_request.card == received_card:
          if type(received_request) is CallUNO:
            self.call_uno_player = None
          
          # play the card
          received_card.play_card(self)
          break
        print('Trying to play non-drawn card')
      
    else:
      curr_player.receive_card(received_request.card, self)
      # reset this to be None
      curr_player.drawn_card = None
      self.go_next_player()

  # punish the player at position pos
  def run_uno_fail(self):

    pos = self.uno_fail_player
    self.uno_fail_player = None
    
    assert(self.turn != pos)

    count = 0
    while self.turn != pos:
      count += 1
      self.go_prev_player()

    # punish player with 4 cards
    curr_player: Player = self.players[self.turn]
    for _ in range(4):
      if (received_request := self.transaction_sync(DealCard(curr_player))) is None: return
      curr_player.receive_card(received_request.card, self)
    
    for _ in range(count):
      self.go_next_player(is_turn_end=False)

    request_list = [PlayCard, SkipTurn]

    if self.call_uno_player is not None:
      request_list.append(CallUNO)

    self._output_queue.put(GetUserInput(request_list))

    self._send_update_to_displayer()
    

  # performs a synchronous transaction 
  def transaction_sync(self, request: Request) -> Optional[Request]:
    # send out the request
    self._output_queue.put(request)
    # wait on the internal queue for card-related requests (or reset)
    received_request = self._internal_queue.get()
    return None if type(received_request) is Reset else received_request


  def go_next_player(self, is_turn_end: bool = True) -> None:
    self._output_queue.put(GoNextPlayer(self.dir))
    self.turn = (self.turn + self.dir) % self.num_players

    if is_turn_end:
      self.handle_turn_end()
      

  def handle_turn_end(self) -> None:
    if (round_winner := self.get_round_winner()) is not None:
      # update the winners score
      self.update_score(round_winner)

      # check if someone won the game
      game_winner = self.get_game_winner()

      # game over
      if game_winner is not None:
        self._output_queue.put(GameOver(copy.deepcopy(game_winner)))
      # round over
      else:
        self._output_queue.put(RoundOver(copy.deepcopy(round_winner)))
      return
    
    # handle normal turn over things
    curr_player = self.players[self.turn]
    request_list = [PlayCard, SkipTurn]

    if self.call_uno_player is not None:
      self.uno_fail_player = self.call_uno_player
      self.call_uno_player = None
      request_list.append(UNOFail)

    if len(curr_player.hand) == 2:
      self.call_uno_player = self.turn
      request_list.append(CallUNO)

    self._output_queue.put(GetUserInput(request_list))

    # update the displayer
    self._send_update_to_displayer()

  def go_prev_player(self) -> None:
    self._output_queue.put(GoNextPlayer(-self.dir))
    self.turn = (self.turn - self.dir) % self.num_players

  def _send_update_to_displayer(self) -> None:
    self._output_queue.put(CurrentState(DisplayUNOState(self)))

  def reverse(self) -> None:
    self.dir = -self.dir

  def get_game_winner(self) -> Optional[Player]:
    for player in self.players:
      if player.score >= self.end_score:
        return player
    return None
  
  def get_round_winner(self) -> Optional[Player]:
    for player in self.players:
      if player.hand == [ ]:
        return player
    return None

  # compute the score this person would get if they win
  def update_score(self, round_winner: Player) -> None:
    for other_player in self.players:
      if other_player is not round_winner:
        round_winner.score += sum(map(lambda card: card.get_value(), other_player.hand))

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
Issues to fix:
 * can call uno fail on someone who doesn't have uno when skip turns happen
 * buffering dealing phase
'''