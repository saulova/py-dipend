from unittest.mock import MagicMock
import pytest
from dipend.dependency.dependency_registry import (
    DependencyRegistry,
)
from dipend.dependency.implementation_details import (
    ImplementationDetails,
)
from dipend.dependency.dependency_store import DependencyStore
from dipend.dependency.dependency_resolver import (
    DependencyResolver,
)
from dipend.enums.lifecycle_enum import LifecycleEnum
from dipend.exceptions.missing_dependency_exception import (
    MissingDependencyException,
)
from dipend.commands.resolve_specific_lifecycles_command import (
    ResolveSpecificLifecyclesCommand,
)
from dipend.commands.resolve_specific_lifecycles_command_handler import (
    ResolveSpecificLifecyclesCommandHandler,
)


class TestResolveSingletonsCommandHandler:
    @pytest.fixture
    def setup_handler(self):
        dependency_store = MagicMock(spec=DependencyStore)
        resolver = MagicMock(spec=DependencyResolver)
        handler = ResolveSpecificLifecyclesCommandHandler(dependency_store, resolver)
        return dependency_store, resolver, handler

    def test_handle_resolves_singleton_dependencies_in_order(self, setup_handler):
        dependency_store, resolver, handler = setup_handler

        dependency1 = DependencyRegistry(
            dependency_id="dep1",
            lifecycle=LifecycleEnum.SINGLETON,
            implementation_details=MagicMock(
                spec=ImplementationDetails,
                class_constructor_dependencies_ids=["dep2"],
            ),
        )
        dependency2 = DependencyRegistry(
            dependency_id="dep2",
            lifecycle=LifecycleEnum.SINGLETON,
            implementation_details=MagicMock(
                spec=ImplementationDetails,
                class_constructor_dependencies_ids=[],
            ),
        )

        dependency_store.get_sorted_dependencies_ids.return_value = ["dep2", "dep1"]
        dependency_store.get_dependency.side_effect = lambda id_: {
            "dep1": dependency1,
            "dep2": dependency2,
        }.get(id_)

        command = ResolveSpecificLifecyclesCommand([LifecycleEnum.SINGLETON])
        handler.handle(command)

        dependency_store.get_sorted_dependencies_ids.assert_called_once()
        dependency_store.get_dependency.assert_any_call("dep1")
        dependency_store.get_dependency.assert_any_call("dep2")

        assert resolver.resolve.call_count == 2

    def test_handle_skips_non_singleton_dependencies(self, setup_handler):
        dependency_store, resolver, handler = setup_handler

        dependency1 = DependencyRegistry(
            dependency_id="dep1",
            lifecycle=LifecycleEnum.TRANSIENT,
            implementation_details=MagicMock(
                spec=ImplementationDetails,
                class_constructor_dependencies_ids=[],
            ),
        )
        dependency_store.get_sorted_dependencies_ids.return_value = ["dep1"]
        dependency_store.get_dependency.return_value = dependency1

        command = ResolveSpecificLifecyclesCommand([LifecycleEnum.SINGLETON])
        handler.handle(command)

        dependency_store.get_sorted_dependencies_ids.assert_called_once()
        dependency_store.get_dependency.assert_called_once_with("dep1")
        resolver.resolve.assert_not_called()

    def test_handle_raises_exception_for_missing_dependency(self, setup_handler):
        dependency_store, resolver, handler = setup_handler
        dependency_store.get_sorted_dependencies_ids.side_effect = MissingDependencyException(["dep1"])

        command = ResolveSpecificLifecyclesCommand([LifecycleEnum.SINGLETON])

        with pytest.raises(MissingDependencyException):
            handler.handle(command)
