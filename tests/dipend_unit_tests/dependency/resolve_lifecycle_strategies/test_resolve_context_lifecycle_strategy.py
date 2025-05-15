from unittest.mock import MagicMock, patch
import pytest
from dipend.dependency.strategies.resolve_context_lifecycle_strategy import (
    ResolveContextLifecycleStrategy,
)
from dipend.context.context_store import ContextStore


class TestResolveContextLifecycleStrategy:
    @pytest.fixture
    def setup_strategy(self):
        strategy = ResolveContextLifecycleStrategy()

        context_wrapper_mock = MagicMock(spec=ContextStore)
        strategy._context_wrapper = context_wrapper_mock

        registry = MagicMock(dependency_id="test_dependency")
        input_data = MagicMock(dependency_registry=registry)

        return context_wrapper_mock, strategy, input_data

    def test_execute_returns_existing_instance(self, setup_strategy):
        context_wrapper_mock, strategy, input_data = setup_strategy

        existing_instance = MagicMock()
        context_wrapper_mock.get.return_value = existing_instance

        result = strategy.execute(input_data)

        context_wrapper_mock.get.assert_called_once_with("test_dependency")
        assert result == existing_instance

    def test_execute_creates_new_instance(self, setup_strategy):
        context_wrapper_mock, strategy, input_data = setup_strategy

        context_wrapper_mock.get.return_value = None
        new_instance = MagicMock()

        with patch.object(strategy, "_construct", return_value=new_instance) as mock_construct:
            result = strategy.execute(input_data)

        context_wrapper_mock.get.assert_called_once_with("test_dependency")
        mock_construct.assert_called_once_with(input_data)
        context_wrapper_mock.set.assert_called_once_with("test_dependency", new_instance)
        assert result == new_instance

    def test_execute_handles_none_registry_id(self, setup_strategy):
        context_wrapper_mock, strategy, input_data = setup_strategy

        input_data = MagicMock()
        input_data.dependency_registry = None

        with pytest.raises(AttributeError):
            strategy.execute(input_data)

    def test_set_var_is_called_correctly_on_new_instance(self, setup_strategy):
        context_wrapper_mock, strategy, input_data = setup_strategy

        context_wrapper_mock.get.return_value = None
        new_instance = MagicMock()

        with patch.object(strategy, "_construct", return_value=new_instance):
            strategy.execute(input_data)

        context_wrapper_mock.set.assert_called_once_with("test_dependency", new_instance)
