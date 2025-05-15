from typing import Any
from unittest.mock import MagicMock
import pytest
from dipend.exceptions.can_not_construct_dependency_exception import (
    CanNotConstructDependencyException,
)
from dipend.dependency.strategies.base_resolve_lifecycle_strategy import (
    BaseResolveLifecycleStrategy,
)
from dipend.dependency.strategies.resolve_lifecycle_strategy_input import (
    ResolveLifecycleStrategyInput,
)


class TestBaseResolveLifecycleStrategy:
    class MockStrategy(BaseResolveLifecycleStrategy):
        def execute(self, input_data: ResolveLifecycleStrategyInput) -> Any:
            return "Executed"

    @pytest.fixture
    def mock_strategy(self):
        return self.MockStrategy()

    def test_construct_returns_instance_if_present(self, mock_strategy):
        implementation_details = MagicMock(instance="InstanceObject", builder=None, class_constructor=None)
        dependency_registry = MagicMock(implementation_details=implementation_details)
        input_data = ResolveLifecycleStrategyInput(dependency_registry, [])

        result = mock_strategy._construct(input_data)

        assert result == "InstanceObject"

    def test_construct_uses_builder_when_instance_is_none(self, mock_strategy):
        implementation_details = MagicMock(instance=None, builder=lambda: "BuiltObject", class_constructor=None)
        dependency_registry = MagicMock(implementation_details=implementation_details)
        input_data = ResolveLifecycleStrategyInput(dependency_registry, [])

        result = mock_strategy._construct(input_data)

        assert result == "BuiltObject"

    def test_construct_raises_exception_when_instance_builder_and_class_constructor_is_none(self, mock_strategy):
        implementation_details = MagicMock(instance=None, builder=None, class_constructor=None)
        dependency_registry = MagicMock(implementation_details=implementation_details)
        input_data = ResolveLifecycleStrategyInput(dependency_registry, [])

        with pytest.raises(CanNotConstructDependencyException) as excinfo:
            mock_strategy._construct(input_data)

        assert str(excinfo.value) == "Can not construct dependency"

    def test_construct_uses_class_constructor_with_resolved_dependencies(self, mock_strategy):
        class_constructor = MagicMock(return_value="ConstructedObject")
        implementation_details = MagicMock(instance=None, builder=None, class_constructor=class_constructor)
        dependency_registry = MagicMock(implementation_details=implementation_details)
        implementation_details.class_constructor = class_constructor
        resolved_dependencies = ["dep1", "dep2"]

        input_data = ResolveLifecycleStrategyInput(
            dependency_registry,
            resolved_dependencies,
        )

        result = mock_strategy._construct(input_data)

        class_constructor.assert_called_once_with("dep1", "dep2")
        assert result == "ConstructedObject"

    def test_execute_do_not_raises_not_implemented_error(self, mock_strategy):
        input_data = MagicMock()

        assert mock_strategy.execute(input_data) == "Executed"
