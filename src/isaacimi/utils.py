import importlib.util
import os
from typing import Type, TypeVar, Dict, List, Optional
import inspect

T = TypeVar("T")
def load_subclasses_from_file(
    filepath: str,
    base_class: Type[T],
    allowed_names: Optional[List[str]] = None
) -> Dict[str, Type[T]]:
    """Returns all subclasses of `base_class` defined in the given file.
    Keyed by class name.

    Args:
        filepath (str): the path to the Python file
        base_class (Type[T]): the base class that the subclasses derives from
        allowed_names (Optional[List[str]], optional): a list of subclass names to return. Any subclass names not in this list will not be returned. Defaults to None.

    Raises:
        ValueError: if the provided file is not a Python (.py) file
        FileNotFoundError: if the provided file cannot be found
        ImportError: if the provided file cannot be loaded as a module
        ValueError: if a subclass name is listed in allowed_names but cannot be found in the Python file

    Returns:
        Dict[str, Type[T]]: a dictionary containing the subclasses of `base_class`, keyed by class name
    """
    if not filepath.endswith(".py"):
        raise ValueError(f"{filepath} is not a Python (.py) file.")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    file_name = os.path.basename(filepath)
    module_name = os.path.splitext(file_name)[0]

    spec = importlib.util.spec_from_file_location(module_name, filepath)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {filepath}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore

    subclasses: Dict[str, Type[T]] = dict()
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if (
            obj.__module__ == module.__name__
            and issubclass(obj, base_class)
            and obj is not base_class
        ):
            subclasses[obj.__name__] = obj
    
    if allowed_names is not None:
        missing = [name for name in allowed_names if name not in subclasses]
        if missing:
            raise ValueError(f"The following class(es) were not found in {filepath} as subclasses of {base_class.__name__}: {', '.join(missing)}")
        
        return {name: subclasses[name] for name in allowed_names}