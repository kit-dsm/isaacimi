import importlib.util
import os
from typing import Type, TypeVar, Dict, List, Optional
import inspect
from urllib.parse import urlparse
from pathlib import Path

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
    
    return subclasses


def resolve_path_in_blueprint(path: str, blueprint_path: str, allowed_extensions: set = None) -> str:
    """Resolves a file path provided in the simulation blueprint to an absolute, normalized path.

    If the file path is a server or cloud url, leave it unchanged. If the file path provided in the simulation blueprint
    is already a valid absolute path, return it. Otherwise, it is treated as relative to the simulation blueprint file.

    Args:
        path (str): The file path provided in the simulation blueprint
        blueprint_path (str): The path to the simulation blueprint
        allowed_extensions (set, optional): A set of allowed file extensions. Defaults to None.

    Raises:
        FileNotFoundError: If the provided file path does not exist
        IsADirectoryError: If the provided path is a directory instead of a file 
        ValueError: If the provided file path has an invalid extension

    Returns:
        str: Resolved absolute path to the file
    """
    supported_schemes = ("http", "https", "omniverse")
    parsed_url = urlparse(path)
    if parsed_url.scheme in supported_schemes:
        return path
    blueprint_dir = Path(blueprint_path).resolve().parent
    path_obj = Path(path)
    resolved_path = path_obj if path_obj.is_absolute() else (blueprint_dir / path_obj)
    resolved_path = resolved_path.resolve()
    if not resolved_path.exists():
        raise FileNotFoundError(f"The provided path does not exist: {resolved_path}")
    if not resolved_path.is_file():
        raise IsADirectoryError(f"The provided path is not a file: {resolved_path}")
    if allowed_extensions and resolved_path.suffix.lower() not in allowed_extensions:
        raise ValueError(f"The provided path {resolved_path} has an invalid file extension. Allowed: {allowed_extensions}")
    return str(resolved_path)