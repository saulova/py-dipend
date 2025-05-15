from dataclasses import dataclass
from typing import Callable, Any, Optional


@dataclass
class ImplementationDetails:
    class_constructor: Optional[Callable]
    class_constructor_dependencies_ids: list[str]
    builder: Optional[Callable]
    instance: Optional[Any]
