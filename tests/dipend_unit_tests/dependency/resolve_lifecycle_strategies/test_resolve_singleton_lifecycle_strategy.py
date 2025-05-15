from unittest.mock import MagicMock
import pytest
from dipend.dependency.strategies.resolve_singleton_lifecycle_strategy import (
    ResolveSingletonLifecycleStrategy,
)
from dipend.dependency.strategies.resolve_lifecycle_strategy_input import (
    ResolveLifecycleStrategyInput,
)


class TestResolveSingletonLifecycleStrategy:
    @pytest.fixture
    def singleton_strategy(self):
        return ResolveSingletonLifecycleStrategy()

    def test_execute_creates_instance_if_none(self, singleton_strategy):
        implementation_details = MagicMock(
            instance=None, builder=None, classConstructor=None
        )
        dependency_registry = MagicMock(implementation_details=implementation_details)
        input_data = ResolveLifecycleStrategyInput(dependency_registry, [])

        singleton_strategy._construct = MagicMock(return_value="NewInstance")

        result = singleton_strategy.execute(input_data)

        singleton_strategy._construct.assert_called_once_with(input_data)
        assert result == "NewInstance"
        assert dependency_registry.implementation_details.instance == "NewInstance"

    def test_execute_returns_existing_instance(self, singleton_strategy):
        existing_instance = "ExistingInstance"
        implementation_details = MagicMock(
            instance=existing_instance, builder=None, classConstructor=None
        )
        dependency_registry = MagicMock(implementation_details=implementation_details)
        input_data = ResolveLifecycleStrategyInput(dependency_registry, [])

        singleton_strategy._construct = MagicMock()

        result = singleton_strategy.execute(input_data)

        singleton_strategy._construct.assert_not_called()
        assert result == existing_instance
        assert dependency_registry.implementation_details.instance == existing_instance
