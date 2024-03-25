import argparse
from typing import List

from uno.uno import UNO
from uno.manager import Manager
from uno import NAME_TO_CONTROLLER, NAME_TO_DISPLAYER

if __name__ == '__main__':
  parser = argparse.ArgumentParser(prog='main',
                                   description='UNO project for 18-500')
  
  parser.add_argument('-p', '--num_players',
                      help='the number of players in the UNO game',
                      type=int,
                      default=4)
  
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

  # create the objects from the classes
  controller = controller_class()
  displayers = [displayer_class() for displayer_class in displayer_classes]
  manager = Manager(controller, displayers)

  game = UNO(manager=manager, num_players=args.num_players)
  game.start()