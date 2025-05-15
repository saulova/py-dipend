from unittest.mock import MagicMock
import pytest
from dipend.dependency.strategies.resolve_transient_lifecycle_strategy import (
    ResolveTransientLifecycleStrategy,
)
from dipend.dependency.strategies.resolve_lifecycle_strategy_input import (
    ResolveLifecycleStrategyInput,
)


class TestResolveTransientLifecycleStrategy:
    @pytest.fixture
    def transient_strategy(self):
        return ResolveTransientLifecycleStrategy()

    def test_execute_calls_construct(self, transient_strategy):
        implementation_details = MagicMock(
            instance=None, builder=None, classConstructor=None
        )
        dependency_registry = MagicMock(implementation_details=implementation_details)
        input_data = ResolveLifecycleStrategyInput(dependency_registry, [])

        transient_strategy._construct = MagicMock(return_value="TransientInstance")

        result = transient_strategy.execute(input_data)

        transient_strategy._construct.assert_called_once_with(input_data)
        assert result == "TransientInstance"
