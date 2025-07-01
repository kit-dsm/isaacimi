import importlib.util
import os
from typing import Type
import inspect

from .imi_robot import ImiRobot

def get_task_from_file(filepath: str) -> Type:
    head, tail = os.path.split(filepath)
    module_name = os.path.splitext(tail)[0]

    spec = importlib.util.spec_from_file_location(module_name, filepath)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module.__name__ and issubclass(obj, ImiRobot):
            return obj
        
    raise ImportError(f"No class found as a subclass of {ImiRobot.__name__} in {filepath}")