from typing import Any
from inspect import isclass
from builtins import __dict__ as builtins_dict
from ...__seedwork.base_checker import CheckerInterface


class ClassTokenTypeChecker(CheckerInterface[Any]):
    def execute(self, input_data: Any) -> bool:
        return (
            isclass(input_data)
            and hasattr(input_data, "__dict__")
            and input_data not in builtins_dict.values()
        )
