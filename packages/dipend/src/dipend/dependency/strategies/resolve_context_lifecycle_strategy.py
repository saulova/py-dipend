from typing import Any
from .base_resolve_lifecycle_strategy import BaseResolveLifecycleStrategy
from .resolve_lifecycle_strategy_input import ResolveLifecycleStrategyInput
from ...context.context_store import ContextStore


class ResolveContextLifecycleStrategy(BaseResolveLifecycleStrategy):
    def __init__(self):
        self._context_wrapper = ContextStore()

    def execute(self, input_data: ResolveLifecycleStrategyInput) -> Any:
        instance = self._context_wrapper.get(
            input_data.dependency_registry.dependency_id
        )

        if instance is None:
            instance = self._construct(input_data)

            self._context_wrapper.set(
                input_data.dependency_registry.dependency_id, instance
            )

        return instance
