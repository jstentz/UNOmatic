'''
References:
 * Official uno rules -> https://service.mattel.com/instruction_sheets/42001pr.pdf
'''

from typing import Collection, Optional
from enum import IntEnum
import numpy as np # for now this is just used for weighted sampling

#################################################### GAME STATE ####################################################

# TODO: I could have some notion of a Hand class, but that might be overkill... it would have printing, adding, getting playable cards, etc
# NOTE: I think the main thing to separate from this file would be the Player class. That will likely be where all of the IO interfaces are,
# since all physical actions with the machine go to / from the Player.
# TODO: add better printing for player hands

class UNO:
  def __init__(self, num_players: int, hand_size: int = 7):
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
    selected_card: Optional[Card] = curr_player.get_card(self.discard_pile.peek(), self.color)

    # if they give a card back, play it
    if selected_card is not None:
      selected_card.play_card(self)
    # otherwise, they should draw a card
    else:
      drawn_card = self.draw_pile.pop()
      print(f'Drawn card: {drawn_card}')
      # ask them if they want to play
      if drawn_card.is_playable(self.discard_pile.peek(), self.color) and input('Call bluff (y/n)?') == 'y':
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
    
#################################################### CARDS ####################################################

class Color(IntEnum):
  RED = 0
  YELLOW = 1
  GREEN = 2
  BLUE = 3
  NUM_COLORS = 4

class Card:
  def __init__(self, color: Optional[Color], number: Optional[int]):
    self.color = color
    self.number = number
    self.type = type(self)
    
    # ensure that we've created a valid card
    if not self._validate():
      raise ValueError('Invalid card')

  # ensures that we have valid entries for all cards
  def _validate(self) -> bool:
    if self.type == Number:
      return self.color is not None and self.number is not None
    elif self.type in [PlusTwo, Reverse, Skip]:
      return self.color is not None and self.number is None
    elif self.type in [PlusFour, Wild]:
      return self.color is None and self.number is None
    else:
      return False
    
  # this is just here so any instance of a Card has this method 
  def play_card(self, state: UNO) -> None:
    pass 

  # this is just here so any instance of a Card has this method 
  def is_playable(self, top_card, deck_color: Color) -> bool:
    pass
  
  def __eq__(self, other) -> bool:
    return isinstance(other, Card) \
           and self.type == other.type \
           and self.color == other.color \
           and self.number == other.number 
  
  def __repr__(self) -> str:
    res = ''
    res += f'{self.color.name:<8}' if self.color is not None else ''
    res += f'{self.type.__name__:<8}' if self.type != Number else ''
    res += f'{self.number}' if self.number is not None else ''
    return res
  
class Number(Card):
  def is_playable(self, top_card: Card, deck_color: Color) -> bool:
    return self.color == deck_color or (top_card.type == Number and top_card.number == self.number)
  
  def play_card(self, state: UNO) -> None:
    # place the card on the discard pile
    state.discard_pile.push(self)

    # update the color of the deck
    state.color = self.color

    # advance to the next player
    state.go_next_player()
    

class PlusTwo(Card):
  def __init__(self, color: Optional[Color]):
    super().__init__(color=color, number=None)

  # NOTE: this function will never be called in the case where the control flow
  # doesn't let a player play the card... these functions are unaware of the rest
  # of the game state 
  def is_playable(self, top_card: Card, deck_color: Color) -> bool:
    return self.color == deck_color or top_card.type == PlusTwo
  
  def play_card(self, state: UNO) -> None:
    # place the card on the discard pile
    state.discard_pile.push(self)

    # update the color of the deck
    state.color = self.color

    # advance to the next player
    state.go_next_player()

    # give them two cards
    state.players[state.turn].receive_card(state.draw_pile.pop())
    state.players[state.turn].receive_card(state.draw_pile.pop())

    # go to the next player
    state.go_next_player()

class Skip(Card):
  def __init__(self, color: Optional[Color]):
    super().__init__(color=color, number=None)

  def is_playable(self, top_card: Card, deck_color: Color) -> bool:
    return self.color == deck_color or top_card.type == Skip
  
  def play_card(self, state: UNO) -> None:
    # place the card on the discard pile
    state.discard_pile.push(self)

    # update the color of the deck
    state.color = self.color

    # skip a player
    state.go_next_player()
    state.go_next_player()

class Reverse(Card):
  def __init__(self, color: Optional[Color]):
    super().__init__(color=color, number=None)

  def is_playable(self, top_card: Card, deck_color: Color) -> bool:
    return self.color == deck_color or top_card.type == Reverse
  
  def play_card(self, state: UNO) -> None:
    # place the card on the discard pile
    state.discard_pile.push(self)

    # update the color of the deck
    state.color = self.color

    # change direction and go back to prev player
    state.reverse()
    state.go_next_player()

class PlusFour(Card):
  def __init__(self):
    super().__init__(color=None, number=None)

  def is_playable(self, top_card: Card, deck_color: Color) -> bool:
    return True
  
  def play_card(self, state: UNO) -> None:
    # check to see if we had other options than playing this card
    player: Player = state.players[state.turn]
    playable_cards: Collection[Card] = player.get_playable_cards(state.discard_pile.peek(), state.color)

    # check if we have any cards that meet these conditions
    # 1. is not a plus 4
    # 2. matches the color of the top card or is a wild card
    has_other_options: bool = any(map(lambda c: c.type != PlusFour and (c.type == Wild or c.color == state.color), playable_cards))

    # place the card on the discard pile
    state.discard_pile.push(self)

    # ask the user for a color
    # TODO: change this
    color_str = f'0: RED\n1: YELLOW\n2: GREEN\n3: BLUE\n'
    color = Color(int(input(color_str + 'Pick a color!\n')))
    state.color = color

    # go the next player
    state.go_next_player()

    # ask them for a bluff answer
    call_bluff = state.players[state.turn].get_bluff_answer()

    # we're guilty
    if call_bluff and has_other_options:
      # this player must show their cards to the person calling the bluff

      # move back to us
      state.go_prev_player()

      # draw 4 cards
      for _ in range(4):
        state.players[state.turn].receive_card(state.draw_pile.pop())

      # progress to the next player
      state.go_next_player()
    
    # failed bluff
    elif call_bluff and not has_other_options:
      # this player must show their cards to the person calling the bluff
      # draw 6 cards for this player
      for _ in range(6):
        state.players[state.turn].receive_card(state.draw_pile.pop())

      state.go_next_player()

    # no bluff called
    else:
      # draw 4 cards for this player
      for _ in range(4):
        state.players[state.turn].receive_card(state.draw_pile.pop())

      state.go_next_player()


class Wild(Card):
  def __init__(self):
    super().__init__(color=None, number=None)

  def is_playable(self, top_card: Card, deck_color: Color) -> bool:
    return True
  
  def play_card(self, state: UNO) -> None:
    # place the card on the discard pile
    state.discard_pile.push(self)

    # ask the user for a color
    # TODO: change this
    color_str = f'0: RED\n1: YELLOW\n2: GREEN\n3: BLUE\n'
    color = Color(int(input(color_str + 'Pick a color!\n')))
    state.color = color

    # move on to the next player
    state.go_next_player()


#################################################### PLAYERS ####################################################

class Player:
  def __init__(self, hand: Collection[Card]):
    self.hand = hand

    # sort the hand
    self._sort_hand()

  def receive_card(self, card : Card) -> None:
    self.hand.append(card)

    # keep hand sorted
    self._sort_hand()

  # NOTE: this function will only ever be called when this player is actually able to play
  def get_card(self, top_card: Card, deck_color: Color) -> Optional[Card]:
    # extracts the playable cards, including their index in the unfiltered hand (for removal)
    enumerated_hand = enumerate(self.hand)
    playable_cards = list(filter(lambda c: c[1].is_playable(top_card, deck_color), enumerated_hand))
    if playable_cards == []:
      return None
    
    # ask them for a card
    print('Possible actions:')
    print(Player._hand_to_str(map(lambda x: x[1], playable_cards)) + f'\n{len(playable_cards)}: Draw card')

    while (action := int(input('Enter action: '))) not in range(len(playable_cards)+1):
      pass

    # they want to draw a card
    if action == len(playable_cards):
      return None
    
    i, card_to_play = playable_cards[action]

    # remove this card from the hand
    self.hand.pop(i)

    # keep hand sorted
    self._sort_hand()

    return card_to_play

  def can_play(self, top_card: Card, deck_color: Color) -> bool:
    return self.get_playable_cards(top_card, deck_color) == []
  
  def get_playable_cards(self, top_card: Card, deck_color: Color):
    return list(filter(lambda c: c.is_playable(top_card, deck_color), self.hand))
  
  def get_bluff_answer(self):
    return input('Call bluff (y/n)?') == 'y'
  
  def _sort_hand(self) -> None:
    # sort by card color, then card type, then card number
    self.hand.sort(key=lambda c: (
                   c.color if c.color is not None else -1, 
                   c.type.__name__, 
                   c.number if c.number is not None else -1))
  
  @staticmethod
  def _hand_to_str(hand) -> str:
    return '\n'.join(map(lambda x: f'{x[0]}: {x[1]}', enumerate(hand)))

  def __repr__(self):
    # join the list of cards into a single string
    return Player._hand_to_str(self.hand)

#################################################### DECK ####################################################

class Deck:
  TOTAL_CARDS = 108

  # 2 per number (1 through 9) + 1 zero 
  NUMBER_CARDS = (2 * 9 + 1) * Color.NUM_COLORS
  PLUSTWO_CARDS = 2 * Color.NUM_COLORS
  SKIP_CARDS = 2 * Color.NUM_COLORS
  REVERSE_CARDS = 2 * Color.NUM_COLORS
  PLUSFOUR_CARDS = 4
  WILD_CARDS = 4

  def __init__(self, num_cards: int):
    self.cards = [Deck.generate_card() for _ in range(num_cards)]

  def push(self, card: Card) -> None:
    self.cards.append(card)

  def pop(self) -> Card:
    return self.cards.pop()
  
  def peek(self) -> Card:
    return self.cards[-1]
  
  def __repr__(self) -> str:
    return f'TOP\n' + '\n'.join(map(lambda c: str(c), self.cards[::-1])) + '\nBOTTOM'

  # generates non-replacing cards based on distribution of UNO cards
  @staticmethod
  def generate_card():
    # create distribution for card types 
    types = np.array([Number, PlusTwo, Skip, Reverse, PlusFour, Wild])
    types_dist = np.array([
      Deck.NUMBER_CARDS,
      Deck.PLUSTWO_CARDS,
      Deck.SKIP_CARDS,
      Deck.REVERSE_CARDS,
      Deck.PLUSFOUR_CARDS,
      Deck.WILD_CARDS
    ]) / Deck.TOTAL_CARDS

    # create distribution for card colors
    colors = [Color.RED, Color.YELLOW, Color.GREEN, Color.BLUE]
    colors_dist = np.ones(Color.NUM_COLORS) / Color.NUM_COLORS

    # create distribution for card numbers
    numbers = np.arange(10)
    numbers_dist = np.empty(10)
    numbers_dist[0] = Color.NUM_COLORS
    numbers_dist[1:] = 2 * Color.NUM_COLORS
    numbers_dist /= Deck.NUMBER_CARDS

    # generate card type
    card_type = np.random.choice(types, p=types_dist)

    # generate card color 
    card_color = colors[np.random.choice(Color.NUM_COLORS, p=colors_dist)]

    # generate card number
    card_number = np.random.choice(numbers, p=numbers_dist)

    # create the correct card
    if card_type == PlusFour or card_type == Wild:
      return card_type()
    elif card_type == PlusTwo or card_type == Skip or card_type == Reverse:
      return card_type(color=card_color)
    else: # number card
      return card_type(color=card_color, number=card_number)


# TODO: will create two deck classes -> draw_deck, discard_deck
    
if __name__ == '__main__':
  game = UNO(num_players=4)
  game.start()
