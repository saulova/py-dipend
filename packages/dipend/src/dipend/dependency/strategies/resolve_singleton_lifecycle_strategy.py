from typing import Any
from .base_resolve_lifecycle_strategy import BaseResolveLifecycleStrategy
from .resolve_lifecycle_strategy_input import ResolveLifecycleStrategyInput


class ResolveSingletonLifecycleStrategy(BaseResolveLifecycleStrategy):
    def execute(self, input_data: ResolveLifecycleStrategyInput) -> Any:
        if input_data.dependency_registry.implementation_details.instance is None:
            instance = self._construct(input_data)
            input_data.dependency_registry.implementation_details.instance = instance

        return input_data.dependency_registry.implementation_details.instance
