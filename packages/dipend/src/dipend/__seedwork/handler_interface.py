from abc import ABC, abstractmethod
from typing import TypeVar, Generic

HandlerInputT = TypeVar("HandlerInputT")
HandlerOutputT = TypeVar("HandlerOutputT")


class HandlerInterface(ABC, Generic[HandlerInputT, HandlerOutputT]):
    @abstractmethod
    def handle(self, input_data: HandlerInputT) -> HandlerOutputT:
        raise NotImplementedError
