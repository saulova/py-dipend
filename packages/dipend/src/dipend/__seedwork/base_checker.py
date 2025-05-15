from abc import ABC, abstractmethod
from typing import TypeVar, Generic

CheckerInputT = TypeVar("CheckerInputT")


class CheckerInterface(ABC, Generic[CheckerInputT]):
    @abstractmethod
    def execute(self, input_data: CheckerInputT) -> bool:
        raise NotImplementedError
