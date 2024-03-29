import argparse
import os
import logging
import datetime

from uno.uno import UNO
from uno.manager import Manager
from uno import NAME_TO_CONTROLLER, NAME_TO_DISPLAYER

def print_example_usage():
  print("Example usage:")
  print("python", os.path.basename(__file__), '-c', 'TerminalController', '-d', 'TkDisplayer', 'TerminalDisplayer')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(prog='main',
                                   description='UNO project for 18-500')
  
  parser.add_argument('-l', '--log',
                      help='enable logging',
                      action='store_true',
                      default=False)
  
  parser.add_argument('--num_players',
                      help='the number of players in the UNO game',
                      type=int,
                      default=4)
  
  parser.add_argument('--hand_size',
                      help='the number of cards per hand',
                      type=int,
                      default=7)
  
  parser.add_argument('-c', '--controller_name', 
                      help='the class name of the controller to use', 
                      type=str,
                      default='TerminalController')
  
  parser.add_argument('-d', '--displayer_names', 
                      help='the class name of the displayer(s) to use', 
                      type=str,
                      nargs='+',
                      default=['TkDisplayer', 'TerminalDisplayer'])
  
  args = parser.parse_args()

  # get the classes the user wants to use
  controller_class = NAME_TO_CONTROLLER[args.controller_name]
  displayer_classes = [NAME_TO_DISPLAYER[displayer_name] for displayer_name in args.displayer_names]

  # set up logging
  logger: logging.Logger = logging.Logger(__file__)
  date_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
  path = os.path.join(os.path.dirname(__file__), f'uno/logs/log_{date_time}.log')
  formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
  
  if args.log:
    file_handler = logging.FileHandler(path)
    logger.addHandler(file_handler)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
  else:
    logger.addHandler(logging.NullHandler())

  # create the objects from the classes
  controller = controller_class()
  displayers = [displayer_class() for displayer_class in displayer_classes]
  manager = Manager(controller, displayers, logger=logger)

  game = UNO(manager=manager, logger=logger, num_players=args.num_players, hand_size=args.hand_size)
  game.start()

'''
TODO:
 * what should happen if someone draws a plus4? in terms of bluffing?
 * person didn't call a bluff, and they had to draw a card to receive the cards
'''