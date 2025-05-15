from typing import Any
from .base_resolve_lifecycle_strategy import BaseResolveLifecycleStrategy
from .resolve_lifecycle_strategy_input import ResolveLifecycleStrategyInput


class ResolveTransientLifecycleStrategy(BaseResolveLifecycleStrategy):
    def execute(self, input_data: ResolveLifecycleStrategyInput) -> Any:
        return self._construct(input_data)
