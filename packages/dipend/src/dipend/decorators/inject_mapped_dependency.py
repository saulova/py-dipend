from typing import Any, Callable
from inspect import isclass
from builtins import __dict__ as builtins_dict
from ..exceptions.decorator_exception import DecoratorException


def inject_mapped_dependency(constructor_index: int, qualifier_tokens: list[Any]):
    def decorator(cls: Callable):
        is_class = isclass(cls) and hasattr(cls, "__dict__") and cls not in builtins_dict.values()

        if not is_class:
            raise DecoratorException("inject_mapped_dependency is a class decorator.")

        if not isinstance(constructor_index, int):
            raise DecoratorException("constructor_index must be an int.")

        if not isinstance(qualifier_tokens, list):
            raise DecoratorException("qualifier_tokens must be a list.")

        if not hasattr(cls, "__di_mapped_dependency"):
            setattr(cls, "__di_mapped_dependency", {})

        cls.__di_mapped_dependency[constructor_index] = qualifier_tokens

        return cls

    return decorator
