from inspect import isclass
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module
from typing import Dict, List, Type
from uno.controller import Controller
from uno.displayer import Displayer

CONTROLLERS: List[Type[Controller]] = []
DISPLAYERS: List[Type[Displayer]] = []


# adapted from https://julienharbulot.com/python-dynamical-import.html
# iterate through the modules in the current package
package_dir = Path(__file__).resolve().parent
for (_, module_name, _) in iter_modules([str(package_dir)]):
    
    # import the module and iterate through its attributes
    module = import_module(f"{__name__}.{module_name}")
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)

        if isclass(attribute):
            if issubclass(attribute, Controller):
              CONTROLLERS.append(attribute)
            elif issubclass(attribute, Displayer):
              DISPLAYERS.append(attribute)
        
NAME_TO_CONTROLLER: Dict[str, Type[Controller]] = {controller.__name__: controller for controller in CONTROLLERS}
NAME_TO_DISPLAYER: Dict[str, Type[Displayer]] = {Displayer.__name__: Displayer for Displayer in DISPLAYERS}