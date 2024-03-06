'''
References:
 * Official uno rules -> https://service.mattel.com/instruction_sheets/42001pr.pdf
'''

# enables lazy type annotation resolving
from __future__ import annotations

from typing import Collection, Optional
from enum import IntEnum


from deck import Deck
from card import Color
from card import Card, Wild, PlusFour
from player import Player
from controller import Controller

class UNO:
  def __init__(self, num_players: int, hand_size: int = 7, controller: Optional[Controller] = None):
    self.num_players: int = num_players
    self.hand_size: int = hand_size
    self.reset()
    
  def reset(self):
    self.draw_pile: Deck = Deck(Deck.TOTAL_CARDS)
    self.discard_pile: Deck = Deck(0)
    self.color: Optional[Color] = None # this is extra info for when the top card is wild or plus4
    self.turn: int = 0 # stores the index of the current player's turn
    self.dir: int = +1 # stores which direction the game is moving in 

    # generate players and their hands
    self.players: Collection[Player] = [Player([self.draw_pile.pop() for _ in range(self.hand_size)]) for _ in range(self.num_players)]

    # repeatedly check if we are drawing wilds or plus4s
    # if we are, put them on the discard pile
    while (initial_card := self.draw_pile.pop()).type in [Wild, PlusFour]:
      self.discard_pile.push(initial_card)

    # we now have a non wild / plus4 card
    # play this card
    initial_card.play_card(self)

  def is_game_over(self):
    return any(map(lambda p: p.hand == [], self.players))
    
  def start(self):
    # continue the game while everyone still has at least one card

    while not self.is_game_over():
      # print the board
      print(f'Player {self.turn}\'s turn')
      print(f'Your hand:\n{self.players[self.turn].hand}')
      print(f'Top card: {self.discard_pile.peek()}')
      print(f'{len(self.draw_pile.cards)} cards remaining.\n\n')

      # do one turn
      self.play_one_turn()

      print('\n\n')
    
    # TODO: print game over 
    print('Game over!')

  def play_one_turn(self):
    # ask the player for a card
    curr_player: Player = self.players[self.turn]

    # TODO: this part will be different, since now I have to get it from the model
    selected_card: Optional[Card] = curr_player.get_card(self.discard_pile.peek(), self.color)

    # if they give a card back, play it
    if selected_card is not None:
      selected_card.play_card(self)
    # otherwise, they should draw a card
    else:
      drawn_card = self.draw_pile.pop()
      print(f'Drawn card: {drawn_card}')
      # ask them if they want to play
      if drawn_card.is_playable(self.discard_pile.peek(), self.color) and input('Play drawn card (y/n)?') == 'y':
        drawn_card.play_card(self)
      else:
        curr_player.receive_card(drawn_card)

  def go_next_player(self) -> None:
    self.turn = (self.turn + self.dir) % self.num_players

  def go_prev_player(self) -> None:
    self.turn = (self.turn - self.dir) % self.num_players

  def reverse(self) -> None:
    self.dir = -self.dir

  def __repr__(self) -> str:
    # include the each of the players' cards
    # include the draw_pile
    # include the discard_pile
    return ''
    

#################################################### DECK ####################################################
    



'''
for calling UNO we need some kind of interrupt... maybe there should be a method in UNO that
is run via a thread. This thread simply updates a buffer of all the UNO calls and callouts
that have happened. At the end of a turn, the UNO state will process all of these and keep moving

'''




# TODO: will create two deck classes -> draw_deck, discard_deck
    
if __name__ == '__main__':
  game = UNO(num_players=4)
#   game.start()
