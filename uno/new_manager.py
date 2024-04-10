'''
The top level GameManager that handles requests in between the state, controller, and displayers.
'''

'''
This should be pretty simple... I think most of the heavy lifting is going to be inside of the requests.py file


I think it might be too complicated to have the requests themselves have actions inside of them...
 * 
 * Displayer -> State: Get current state
 * 


'''

from uno.controller import Controller
from uno.displayer import Displayer
from uno.uno import UNO
from typing import Collection


class GameManager:
  # not sure what this should take in, maybe the class type of the controller / displayers to init
  def __init__(self, state_type: type[UNO], controller_type: type[Controller], displayer_types: type[Displayer]):
    # this should also create the request queue and pass that down to the controller / state / displayers  
    pass

  # the main loop that responds to requests from the state, controller, and displayers
  def event_loop(self):
    pass



