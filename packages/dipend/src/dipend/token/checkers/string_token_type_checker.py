from typing import Any
from ...__seedwork.base_checker import CheckerInterface


class StringTokenTypeChecker(CheckerInterface[Any]):
    def execute(self, input_data: Any) -> bool:
        return isinstance(input_data, str)
