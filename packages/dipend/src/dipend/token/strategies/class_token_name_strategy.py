from typing import Callable
from ...__seedwork.strategy_interface import StrategyInterface


class ClassTokenNameStrategy(StrategyInterface[Callable, str]):
    def execute(self, input_data: Callable) -> str:
        return input_data.__name__
