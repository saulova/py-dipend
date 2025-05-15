from typing import Any
from ..enums.token_type_enum import TokenTypeEnum
from ..__seedwork.strategy_interface import StrategyInterface
from ..__seedwork.dictionary import Dictionary
from .strategies.class_token_name_strategy import ClassTokenNameStrategy
from .strategies.string_token_name_strategy import StringTokenNameStrategy


class TokenNameResolver:
    def __init__(self):
        self._strategies = Dictionary[str, StrategyInterface]()

    def set_default_token_name_strategies(self):
        self._strategies.set(TokenTypeEnum.CLASS_CONSTRUCTOR, ClassTokenNameStrategy())
        self._strategies.set(TokenTypeEnum.STRING, StringTokenNameStrategy())

    def set_token_name_strategy(
        self, token_type: str, token_name_strategy: StrategyInterface
    ):
        self._strategies.set(token_type, token_name_strategy)

    def get_token_name(self, token: Any, token_type: str) -> str:
        strategy = self._strategies.get(token_type)

        if strategy is None:
            return "UNKNOWN"

        return strategy.execute(token)
