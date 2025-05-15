from typing import Any, Callable, Optional
from dataclasses import dataclass


@dataclass
class AddDependencyCommand:
    tokens: list[Any]
    lifecycle: str
    class_constructor: Optional[Callable] = None
    builder: Optional[Callable] = None
    instance: Optional[Callable] = None
