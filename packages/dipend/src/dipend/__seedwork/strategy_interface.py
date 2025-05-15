from abc import ABC, abstractmethod
from typing import TypeVar, Generic

StrategyInputT = TypeVar("StrategyInputT")
StrategyOutputT = TypeVar("StrategyOutputT")


class StrategyInterface(ABC, Generic[StrategyInputT, StrategyOutputT]):
    @abstractmethod
    def execute(self, input_data: StrategyInputT) -> StrategyOutputT:
        raise NotImplementedError
