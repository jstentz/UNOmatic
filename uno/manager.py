'''
Houses the controller and displayer(s)
'''

from __future__ import annotations

from typing import Optional, Collection
import logging
import datetime
import os

from uno.controller import Controller
from uno.displayer import Displayer

from queue import Queue
from uno.uno import UNO
from uno.requests import *

from typing import Collection

# TODO: have the manager read everything from all the queues then put a reset on the queue

class Manager:
  # TODO: add info about state correction from displayers
  TO_CONTROLLER = [GoNextPlayer, DealCard, GetUserInput]
  TO_STATE = [PlayCard, DealtCard, SkipTurn, SetColor, Bluff, CallUNO, UNOFail, CorrectedState]
  TO_DISPLAYERS = [CurrentState]

  def __init__(self, controller_type: type[Controller], displayer_types: Collection[type[Displayer]], logger: logging.Logger, url: str) -> None:
    # make all of the queues for communication
    self.manager_queue = Queue()
    self.controller_queue = Queue()
    self.state_queue = Queue()
    self.displayer_queues = [Queue() for _ in range(len(displayer_types))]
    self.logger = logger

    self.controller = controller_type(self.controller_queue, self.manager_queue)
    self.logger.info(f'Initialized {controller_type.__name__}')
    self.state = UNO(self.state_queue, self.manager_queue) # TODO: change this
    self.logger.info(f'Initialized UNO state')
    # self.displayers = [displayer_type(displayer_queue, self.manager_queue) for displayer_type, displayer_queue in zip(displayer_types, self.displayer_queues)] # TODO: change this
    self.displayers = []
    for displayer_type, displayer_queue in zip(displayer_types, self.displayer_queues):
      if displayer_type.__name__ == 'WebsiteDisplayer':
        self.displayers.append(displayer_type(displayer_queue, self.manager_queue, url))
      else:
        self.displayers.append(displayer_type(displayer_queue, self.manager_queue))
    
    self.logger.info(f'Initialized {", ".join([displayer_type.__name__ for displayer_type in displayer_types])}')

  def clear_queues(self):
    # clear everyone's queues
    queues_to_clear = [self.manager_queue, self.controller_queue, self.state_queue] + self.displayer_queues
    for queue in queues_to_clear:
      while not queue.empty():
        queue.get()

  def reset_controller(self):
    self.controller.reset()

  def reset_state(self, request: Request):
    self.state.reset(request)

  def reset_displayers(self):
    for displayer in self.displayers:
      displayer.reset()

  def start(self):
    self.controller.start()
    self.logger.info('Started controller')
    self.state.start()
    self.logger.info('Started UNO state')
    for displayer in self.displayers:
      displayer.start()
    self.logger.info('Started displayers')

    # main control flow loop
    while True:
      request = self.manager_queue.get()
      self.logger.info(f'Manager received {request}')

      if type(request) in [Reset, RoundReset]:
        self.clear_queues()
        self.reset_controller()
        self.reset_state(request)
        self.reset_displayers()

      elif type(request) in [GameOver, RoundOver]:
        self.clear_queues()
        self.reset_controller()
        
        for displayer_queue in self.displayer_queues:
          displayer_queue.put(request)

      elif type(request) in Manager.TO_CONTROLLER:
        self.controller_queue.put(request)
      elif type(request) in Manager.TO_STATE:
        self.state_queue.put(request)
      elif type(request) in Manager.TO_DISPLAYERS:
        for displayer_queue in self.displayer_queues:
          displayer_queue.put(request)
      else:
        print('Unknown request in Manager!')
      
