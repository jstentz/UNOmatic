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
import json


from uno.deck import Deck
from uno.card import Color
from uno.card import Card, Wild, PlusFour
from uno.player import Player
from uno.requests import *
import uno.utils

import copy

# constructs a display state by copying an uno state into json-able object
class DisplayUNOState:
  def __init__(self, state: UNO):
    self.hand_size = state.hand_size
    self.num_players = state.num_players
    self.discard_pile = copy.deepcopy(state.discard_pile)
    self.color = copy.deepcopy(state.color)
    self.turn = state.turn
    self.dir = state.dir 
    self.players = copy.deepcopy(state.players)

  def to_json(self) -> str:
    obj = {
      'hand_size': self.hand_size,
      'num_players': self.num_players,
      'discard_pile': self.discard_pile.to_json(),
      'color': self.color.name if self.color is not None else None,
      'turn': self.turn,
      'dir': self.dir,
      'players': [player.to_json() for player in self.players],
    }
    return obj

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
      for player in self.players:
        player.clear_hand()

    self._sequence_thread = Thread(target=self.run_init_phase, daemon=True)

    # handle the sequence of actions to init the game
    self._sequence_thread.start()

  def _main_loop(self):
    while True:
      request = self._input_queue.get()

      if type(request) is CorrectedState:
        self.handle_state_correction(request.state_update)
      elif type(request) in [PlayCard, CallUNO, SkipTurn] and request.for_drawn_card:
        # just forward along to skip turn handler if we're drawing a card
        if request.for_drawn_card:
          self._internal_queue.put(request)
          continue
      elif type(request) in [PlayCard, CallUNO]:

        # reap the thread 
        if self._sequence_thread: self._sequence_thread.join() 
        
        card = request.card
        # check to see if we can play this card
        curr_player: Player = self.players[self.turn]
        if card not in curr_player.get_playable_cards(self.discard_pile.peek(), self.color):
          print('Unplayable card')
          request_list = [PlayCard, SkipTurn]

          if self.uno_fail_player is not None: request_list.append(UNOFail)
          if self.call_uno_player is not None: request_list.append(CallUNO)

          self._output_queue.put(GetUserInput(request_list, for_invalid_card=True))
          continue

        self.uno_fail_player = None
        if type(request) is CallUNO:
          self.call_uno_player = None
          

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
        else:
          self.call_uno_player = None

        self._sequence_thread = Thread(target=self.run_skip_turn, daemon=True)

        # handle the sequence of actions caused skipping
        self._sequence_thread.start()
      
      else:
        # forward along to card handler
        self._internal_queue.put(request)

  def handle_state_correction(self, state_correction):

    position = state_correction['position']
    card_idx = state_correction['card_idx']
    card_color = state_correction['color']
    card_type = state_correction['type']
    new_card = uno.utils.card_from_string(card_color, card_type)

    if position == 'top_card':
      self.discard_pile.set_top_card(new_card)
      self.color = uno.utils.color_from_string(card_color)
    else:
      position = int(position)
      card_idx = int(card_idx)
      self.players[position].hand[card_idx] = new_card
      self.players[position]._sort_hand() 

    # send back the updated state
    self._send_update_to_displayer()
  
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

      for_invalid_card = False
      while True:
        if (received_request := self.transaction_sync(GetUserInput(request_list, for_drawn_card=True, for_invalid_card=for_invalid_card))) is None: return
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
          # reset drawn card
          curr_player.drawn_card = None
          # play the card
          received_card.play_card(self)
          break
        print('Trying to play non-drawn card')
        for_invalid_card = True
      
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
    self._output_queue.put(GoNextPlayer(self.dir, self.num_players))
    self.turn = (self.turn + self.dir) % self.num_players

    if is_turn_end:
      self.handle_turn_end()
      

  def handle_turn_end(self) -> None:
    if (round_winner := self.get_round_winner()) is not None:
      # update the winners score
      
      self.update_score(round_winner)

      self._send_update_to_displayer()

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
    self._output_queue.put(GoNextPlayer(-self.dir, self.num_players))
    self.turn = (self.turn - self.dir) % self.num_players

  def _send_update_to_displayer(self) -> None:
    display_state = DisplayUNOState(self)
    self._output_queue.put(CurrentState(display_state))

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
      if other_player.position != round_winner.position:
        round_winner.score += sum(map(lambda card: card.get_value(), other_player.hand))

  def __del__(self) -> None:
    # TODO: send a signal to self to end the thread
    pass

  def __repr__(self) -> str:
    res = f'Top card: {self.discard_pile.peek()}, Color: {self.color.name if self.color is not None else "None"}\n'

    curr_player = self.players[self.turn]
    res += str(curr_player)
    return res
  
'''
you have 2 cards, you play an unplayable card, you can't call UNO again
'''
  