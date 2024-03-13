'''
References:
 * Official uno rules -> https://service.mattel.com/instruction_sheets/42001pr.pdf
'''

# enables lazy type annotation resolving
from __future__ import annotations

from typing import Collection, Optional
from queue import Queue # used for golang-style channels
from threading import Thread

from deck import Deck
from card import Color
from card import Card, Wild, PlusFour
from player import Player
from manager import Manager
from controller import TerminalController
from displayer import TerminalDisplayer, TkDisplayer

class UNO:
  def __init__(self, manager: Manager, num_players: int, hand_size: int = 7):
    self.num_players: int = num_players
    self.hand_size: int = hand_size
    self._async_action_queue = manager.controller.get_channel()
    self._async_thread = Thread(target=self._action_handler)
    self._async_thread.daemon = True # kill the thread when the process dies
    self._async_thread.start()
    
    # set up the controller (terminal is default)
    self.manager = manager
    self.reset()
    
  def reset(self):
    self.manager.reset()

    # empty the action queue
    while not self._async_action_queue.empty():
      self._async_action_queue.get_nowait()

    self.discard_pile: Deck = Deck(0)
    self.color: Optional[Color] = None # this is extra info for when the top card is wild or plus4
    self.turn: int = 0 # stores the index of the current player's turn
    self.dir: int = +1 # stores which direction the game is moving in 

    # generate players and their hands
    self.players: Collection[Player] = [Player([self.manager.deal_card() for _ in range(self.hand_size)], pos) for pos in range(self.num_players)]

    # repeatedly check if we are drawing wilds or plus4s
    # if we are, put them on the discard pile
    while (initial_card := self.manager.deal_card()).type in [Wild, PlusFour]:
      self.discard_pile.push(initial_card)

    # we now have a non wild / plus4 card
    # play this card
    initial_card.play_card(self)

  def is_game_over(self):
    return any(map(lambda p: p.hand == [], self.players))
    
  def start(self):
    # continue the game while everyone still has at least one card
    while not self.is_game_over():
    
      self.manager.display_state(self)

      # do one turn
      self.play_one_turn()

    # display the final game state
    self.manager.display_state(self)    

  def play_one_turn(self):
    # ask the player for a card
    curr_player: Player = self.players[self.turn]

    # TODO: this part will be different, since now I have to get it from the model
    # selected_card: Optional[Card] = curr_player.get_card(self.discard_pile.peek(), self.color)

    selected_card = self.manager.get_card(curr_player)

    if selected_card is not None and selected_card not in curr_player.get_playable_cards(self.discard_pile.peek(), self.color):
      self.manager.signal_invalid_state()


    # if they give a card back, play it
    if selected_card is not None:
      selected_card.play_card(self)

      # TODO: this validation should probably happen inside the player class
      # TODO: there should still be stuff in the player, this shouldn't be here
      # remove the card from the player's hand
      curr_player.hand.remove(selected_card)
      curr_player._sort_hand()
      
    # otherwise, they should draw a card
    else:
      drawn_card = self.manager.deal_card()
      print(f'Drawn card: {drawn_card}')
      # ask them if they want to play
      if drawn_card.is_playable(self.discard_pile.peek(), self.color) \
         and self.manager.get_draw_card_response(curr_player, drawn_card):
        # play the card
        drawn_card.play_card(self)
      else:
        # otherwise, put the card in their hand
        curr_player.receive_card(drawn_card)

        # advance the turn
        self.go_next_player()

  def _action_handler(self) -> None:
    # while not self.is_game_over():
    while True:
      # grab an action (blocks until something is on the queue)
      action = self._async_action_queue.get()
      print(action)
  

  def go_next_player(self) -> None:
    self.manager.advance_turn(self.dir)
    self.turn = (self.turn + self.dir) % self.num_players

  def go_prev_player(self) -> None:
    self.manager.advance_turn(-self.dir)
    self.turn = (self.turn - self.dir) % self.num_players

  def reverse(self) -> None:
    self.dir = -self.dir

  def __repr__(self) -> str:
    return ''

if __name__ == '__main__':
  controller = TerminalController()
  terminal_displayer = TerminalDisplayer()
  # tk_displayer = TkDisplayer()
  manager = Manager(controller, [terminal_displayer])
  game = UNO(manager=manager, num_players=4)
  game.start()
