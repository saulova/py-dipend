from abc import ABC
from typing import TypeVar, Generic, Optional, ValuesView, ItemsView, KeysView

DictKeyT = TypeVar("DictKeyT")
DictValueT = TypeVar("DictValueT")


class Dictionary(ABC, Generic[DictKeyT, DictValueT]):
    def __init__(self):
        self._dictionary: dict[DictKeyT, DictValueT] = {}

    def set(self, key: DictKeyT, value: DictValueT):
        self._dictionary[key] = value

    def get(self, key: DictKeyT) -> Optional[DictValueT]:
        return self._dictionary.get(key, None)

    def get_many(self, keys: list[DictKeyT]) -> list[Optional[DictValueT]]:
        values: list[Optional[DictValueT]] = []

        for key in keys:
            values.append(self._dictionary.get(key, None))

        return values

    def keys(self) -> KeysView[DictKeyT]:
        return self._dictionary.keys()

    def items(self) -> ItemsView[DictKeyT, DictValueT]:
        return self._dictionary.items()

    def values(
        self,
    ) -> ValuesView[DictValueT]:
        return self._dictionary.values()

    def delete(self, key: str):
        self._dictionary.pop(key, None)

    def clear(self):
        self._dictionary.clear()

    def len(self):
        return len(self._dictionary)
