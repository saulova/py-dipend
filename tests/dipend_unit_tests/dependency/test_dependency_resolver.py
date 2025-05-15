from unittest.mock import MagicMock
import pytest
from dipend.exceptions.invalid_lifecycle_exception import (
    InvalidLifecycleException,
)
from dipend.enums.lifecycle_enum import LifecycleEnum
from dipend.dependency.dependency_store import (
    DependencyStore,
)
from dipend.dependency.dependency_resolver import (
    DependencyResolver,
)
from dipend.dependency.strategies.resolve_lifecycle_strategy_input import (
    ResolveLifecycleStrategyInput,
)
from dipend.dependency.strategies.resolve_singleton_lifecycle_strategy import (
    ResolveSingletonLifecycleStrategy,
)
from dipend.dependency.strategies.resolve_transient_lifecycle_strategy import (
    ResolveTransientLifecycleStrategy,
)
from dipend.dependency.strategies.resolve_context_lifecycle_strategy import (
    ResolveContextLifecycleStrategy,
)


class TestDependencyResolver:
    @pytest.fixture
    def setup_resolver(self):
        dependency_store = MagicMock(DependencyStore)
        resolver = DependencyResolver(dependency_store)
        resolver.set_default_resolve_lifecycle_strategies()
        dependency_store.reset_mock()
        return dependency_store, resolver

    def test_set_default_resolve_lifecycle_strategies(self, setup_resolver):
        dependency_store, resolver = setup_resolver
        assert isinstance(
            resolver._strategies.get(LifecycleEnum.SINGLETON),
            ResolveSingletonLifecycleStrategy,
        )
        assert isinstance(
            resolver._strategies.get(LifecycleEnum.TRANSIENT),
            ResolveTransientLifecycleStrategy,
        )
        assert isinstance(
            resolver._strategies.get(LifecycleEnum.CONTEXT),
            ResolveContextLifecycleStrategy,
        )

    def test_add_resolve_lifecycle_strategy(self, setup_resolver):
        dependency_store, resolver = setup_resolver
        mock_strategy = MagicMock()
        resolver.add_resolve_lifecycle_strategy("CUSTOM", mock_strategy)
        assert resolver._strategies.get("CUSTOM") == mock_strategy

    def test_use_lifecycle_strategy_calls_correct_strategy(self, setup_resolver):
        dependency_store, resolver = setup_resolver
        dependency_registry = MagicMock(lifecycle=LifecycleEnum.SINGLETON, dependency_id="dep1")
        resolved_dependencies = ["dep2"]
        singleton_strategy = MagicMock()
        singleton_strategy.execute.return_value = "ResolvedInstance"

        resolver._strategies.set(LifecycleEnum.SINGLETON, singleton_strategy)

        result = resolver._use_lifecycle_strategy(dependency_registry, resolved_dependencies)

        singleton_strategy.execute.assert_called_once_with(ResolveLifecycleStrategyInput(dependency_registry, resolved_dependencies))
        assert result == "ResolvedInstance"

    def test_use_lifecycle_strategy_raises_invalid_lifecycle_exception(self, setup_resolver):
        dependency_store, resolver = setup_resolver
        dependency_registry = MagicMock(lifecycle="INVALID", dependency_id="dep1")

        with pytest.raises(InvalidLifecycleException):
            resolver._use_lifecycle_strategy(dependency_registry, [])

    def test_resolve_return_already_resolved_instance(self, setup_resolver):
        dependency_store, resolver = setup_resolver
        dependency_id = "dep1"
        implementation_details = MagicMock(class_constructor_dependencies_ids=[], instance="ResolvedInstance")
        dependency_registry = MagicMock(lifecycle=LifecycleEnum.SINGLETON, dependency_id=dependency_id, implementation_details=implementation_details)
        resolver._use_lifecycle_strategy = MagicMock(return_value="")

        dependency_store.get_dependency.return_value = dependency_registry

        result = resolver.resolve(dependency_id)

        resolver._use_lifecycle_strategy.assert_not_called()
        assert result == "ResolvedInstance"

    def test_resolve_delegates_to_use_lifecycle_strategy(self, setup_resolver):
        dependency_store, resolver = setup_resolver
        dependency_id = "dep1"
        resolved_dependencies = []
        implementation_details = MagicMock(class_constructor_dependencies_ids=[], instance=None)
        dependency_registry = MagicMock(lifecycle=LifecycleEnum.SINGLETON, dependency_id=dependency_id, implementation_details=implementation_details)
        resolver._use_lifecycle_strategy = MagicMock(return_value="ResolvedInstance")

        dependency_store.get_dependency.return_value = dependency_registry

        result = resolver.resolve(dependency_id)

        resolver._use_lifecycle_strategy.assert_called_once_with(dependency_registry, resolved_dependencies)
        assert result == "ResolvedInstance"

    def test_resolve_delegates_to_use_lifecycle_strategy_and_has_constructor_dependency(self, setup_resolver):
        dependency_store, resolver = setup_resolver
        dependency_id_1 = "dep1"
        dependency_id_2 = "dep2"
        implementation_details_1 = MagicMock(class_constructor_dependencies_ids=["dep2"], instance=None)
        implementation_details_2 = MagicMock(class_constructor_dependencies_ids=[], instance="ResolvedInstance2")
        dependency_registry_1 = MagicMock(lifecycle=LifecycleEnum.SINGLETON, dependency_id=dependency_id_1, implementation_details=implementation_details_1)
        dependency_registry_2 = MagicMock(lifecycle=LifecycleEnum.SINGLETON, dependency_id=dependency_id_2, implementation_details=implementation_details_2)

        resolver._use_lifecycle_strategy = MagicMock(return_value="ResolvedInstance1")

        dependency_store.get_dependency.side_effect = [dependency_registry_1, dependency_registry_2]

        result = resolver.resolve(dependency_id_1)

        resolver._use_lifecycle_strategy.assert_called_once_with(dependency_registry_1, ["ResolvedInstance2"])

        assert result == "ResolvedInstance1"
