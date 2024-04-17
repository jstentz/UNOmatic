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

  def __init__(self, controller_type: type[Controller], displayer_types: Collection[type[Displayer]]) -> None:
    # make all of the queues for communication
    self.manager_queue = Queue()
    self.controller_queue = Queue()
    self.state_queue = Queue()
    self.displayer_queues = [Queue() for _ in range(len(displayer_types))]

    self.controller = controller_type(self.controller_queue, self.manager_queue)
    self.state = UNO(self.state_queue, self.manager_queue) # TODO: change this
    self.displayers = [displayer_type() for displayer_type in displayer_types] # TODO: change this


  def start(self):
    self.controller.start()
    self.state.start()
    # TODO: start the displayer

    # main control flow loop
    while True:
      request = self.manager_queue.get()

      if type(request) is Reset:

        # clear everyone's queues
        queues_to_clear = [self.manager_queue, self.controller_queue, self.state_queue] + self.displayer_queues
        for queue in queues_to_clear:
          while not queue.empty():
            queue.get()
        
        self.controller.reset()
        self.state.reset(request)

        # TODO: uncomment when displayers set up
        # for displayer in self.displayers:
        #   displayer_queue.reset()

      elif type(request) in Manager.TO_CONTROLLER:
        self.controller_queue.put(request)
      elif type(request) in Manager.TO_STATE:
        self.state_queue.put(request)
      elif type(request) in Manager.TO_DISPLAYERS:
        for displayer_queue in self.displayer_queues:
          displayer_queue.put(request)
      else:
        print('Unknown request in Manager!')
      
