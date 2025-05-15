from unittest.mock import MagicMock
import pytest
from dipend.dependency_container import (
    DependencyContainer,
    _AddDependencyInput,
    _RetrieveDependencyInput,
)

from dipend.dependency_container_config import DependencyContainerConfig
from dipend.token.token_store import (
    TokenStore,
)
from dipend.dependency.dependency_store import DependencyStore
from dipend.dependency.dependency_resolver import (
    DependencyResolver,
)
from dipend.token.token_type_resolver import (
    TokenTypeResolver,
)
from dipend.token.token_name_resolver import (
    TokenNameResolver,
)
from dipend.exceptions.exception_handler import ExceptionHandler
from dipend.exceptions.base_dependency_container_exception import (
    BaseDependencyContainerException,
)
from dipend.commands.add_dependency_command_handler import (
    AddDependencyCommandHandler,
)
from dipend.commands.add_dependency_command import (
    AddDependencyCommand,
)
from dipend.commands.resolve_dependency_command_handler import (
    ResolveDependencyCommandHandler,
)
from dipend.commands.resolve_dependency_command import (
    ResolveDependencyCommand,
)
from dipend.commands.resolve_specific_lifecycles_command_handler import (
    ResolveSpecificLifecyclesCommandHandler,
)
from dipend.commands.resolve_specific_lifecycles_command import (
    ResolveSpecificLifecyclesCommand,
)
from dipend.enums.lifecycle_enum import LifecycleEnum


class TestDependencyContainer:
    @pytest.fixture
    def dependency_container(self):
        container = DependencyContainer()

        container._token_store = MagicMock(spec=TokenStore)
        container._dependency_store = MagicMock(spec=DependencyStore)
        container._dependency_resolver = MagicMock(spec=DependencyResolver)
        container._token_type_resolver = MagicMock(spec=TokenTypeResolver)
        container._token_name_resolver = MagicMock(spec=TokenNameResolver)
        container._exception_handler = MagicMock(spec=ExceptionHandler)
        container._add_dependency_command_handler = MagicMock(spec=AddDependencyCommandHandler)
        container._resolve_dependency_command_handler = MagicMock(spec=ResolveDependencyCommandHandler)
        container._resolve_specific_lifecycles_command_handler = MagicMock(spec=ResolveSpecificLifecyclesCommandHandler)

        return container

    def test_load_configs_when_use_default_configs(self, dependency_container):
        configs = DependencyContainerConfig()
        dependency_container._add_dependency = MagicMock()

        dependency_container._load_configs(configs)

        dependency_container._dependency_resolver.set_default_resolve_lifecycle_strategies.assert_called_once()
        dependency_container._token_type_resolver.set_default_token_type_checkers.assert_called_once()
        dependency_container._token_name_resolver.set_default_token_name_strategies.assert_called_once()
        dependency_container._add_dependency.assert_called_once()
        assert not dependency_container._is_build_singletons_required
        assert dependency_container._dependency_container_token == DependencyContainer

    def test_load_configs_when_set_configs(self, dependency_container):
        configs = DependencyContainerConfig(
            disable_default_resolve_lifecycle_strategies=True,
            disable_default_token_type_checkers=True,
            disable_default_token_name_strategies=True,
            build_singletons_required=False,
            custom_dependency_container_token=object(),
        )
        dependency_container._add_dependency = MagicMock()

        dependency_container._load_configs(configs)

        dependency_container._dependency_resolver.set_default_resolve_lifecycle_strategies.assert_not_called()
        dependency_container._token_type_resolver.set_default_token_type_checkers.assert_not_called()
        dependency_container._token_name_resolver.set_default_token_name_strategies.assert_not_called()
        dependency_container._add_dependency.assert_called_once()
        assert not dependency_container._is_build_singletons_required
        assert dependency_container._dependency_container_token != DependencyContainer

    def test_exception_handler_wrapper(self, dependency_container):
        assert dependency_container._exception_handler_wrapper(lambda: "ok") == "ok"
        dependency_container._exception_handler.handle.assert_not_called()

    def test_exception_handler_wrapper_when_callback_raise(self, dependency_container):
        class TestException(BaseDependencyContainerException):
            pass

        test_exception = TestException(["dependency_id"], "test")

        def callback():
            raise test_exception

        def handle_error():
            raise Exception("test")

        dependency_container._exception_handler.handle.side_effect = handle_error

        with pytest.raises(Exception, match="test"):
            dependency_container._exception_handler_wrapper(callback)

        dependency_container._exception_handler.handle.assert_called_once()

    def test_resolve_lifecycles(self, dependency_container):
        lifecycles = ["TEST"]

        dependency_container._exception_handler_wrapper = MagicMock(wraps=dependency_container._exception_handler_wrapper)

        dependency_container._resolve_lifecycles(lifecycles)

        dependency_container._exception_handler_wrapper.assert_called_once()
        dependency_container._resolve_specific_lifecycles_command_handler.handle.assert_called_once_with(ResolveSpecificLifecyclesCommand(lifecycles))

    def test_build_singletons(self, dependency_container):
        dependency_container._resolve_lifecycles = MagicMock()

        assert not dependency_container._is_singletons_built

        result = dependency_container.build_singletons()

        assert result == dependency_container
        assert dependency_container._is_singletons_built
        dependency_container._resolve_lifecycles.assert_called_once_with([LifecycleEnum.SINGLETON])

    def test_build_context(self, dependency_container):
        dependency_container._resolve_lifecycles = MagicMock()

        result = dependency_container.build_context()

        assert result == dependency_container
        dependency_container._resolve_lifecycles.assert_called_once_with([LifecycleEnum.CONTEXT])

    def test_build_context_when_container_is_built(self, dependency_container):
        dependency_container._resolve_lifecycles = MagicMock()

        dependency_container._is_singletons_built = True

        result = dependency_container.build_context()

        assert result == dependency_container
        assert dependency_container._is_singletons_built
        dependency_container._resolve_lifecycles.assert_called_once_with([LifecycleEnum.CONTEXT])

    def test_add_dependency(self, dependency_container):
        dependency_token = "token"
        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            builder=lambda: "dependency-instance",
        )

        dependency_container._exception_handler_wrapper = MagicMock(wraps=dependency_container._exception_handler_wrapper)

        dependency_container._add_dependency(add_dependency_input)

        add_dependency_command = AddDependencyCommand(
            [
                add_dependency_input.dependency_token,
                *add_dependency_input.qualifier_tokens,
            ],
            add_dependency_input.lifecycle,
            add_dependency_input.class_constructor,
            add_dependency_input.builder,
            add_dependency_input.instance,
        )

        dependency_container._exception_handler_wrapper.assert_called_once()
        dependency_container._add_dependency_command_handler.handle.assert_called_once_with(add_dependency_command)

    def test_add_dependency_with_qualifier_tokens(self, dependency_container):
        dependency_token = "token"
        qualifier_token = "qualifier-token"
        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            builder=lambda: "dependency-instance",
        )

        dependency_container._exception_handler_wrapper = MagicMock(wraps=dependency_container._exception_handler_wrapper)

        dependency_container._add_dependency(add_dependency_input)

        add_dependency_command = AddDependencyCommand(
            [
                add_dependency_input.dependency_token,
                *add_dependency_input.qualifier_tokens,
            ],
            add_dependency_input.lifecycle,
            add_dependency_input.class_constructor,
            add_dependency_input.builder,
            add_dependency_input.instance,
        )

        dependency_container._exception_handler_wrapper.assert_called_once()
        dependency_container._add_dependency_command_handler.handle.assert_called_once_with(add_dependency_command)

    def test_add_dependency_use_class_constructor_as_dependency_token(self, dependency_container):
        class TestClass:
            pass

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=None,
            class_constructor=TestClass,
        )

        dependency_container._exception_handler_wrapper = MagicMock(wraps=dependency_container._exception_handler_wrapper)

        dependency_container._add_dependency(add_dependency_input)

        add_dependency_command = AddDependencyCommand(
            [
                add_dependency_input.class_constructor,
                *add_dependency_input.qualifier_tokens,
            ],
            add_dependency_input.lifecycle,
            add_dependency_input.class_constructor,
            add_dependency_input.builder,
            add_dependency_input.instance,
        )

        dependency_container._exception_handler_wrapper.assert_called_once()
        dependency_container._add_dependency_command_handler.handle.assert_called_once_with(add_dependency_command)

    def test_add_dependency_raise_with_missing_dependency_token(self, dependency_container):
        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=None,
            builder=lambda: "dependency-instance",
        )

        dependency_container._exception_handler_wrapper = MagicMock(wraps=dependency_container._exception_handler_wrapper)

        with pytest.raises(ValueError, match="Missing dependency token\\."):
            dependency_container._add_dependency(add_dependency_input)

        dependency_container._exception_handler_wrapper.assert_not_called()
        dependency_container._add_dependency_command_handler.handle.assert_not_called()

    def test_add_dependency_raise_with_check_qualifier_tokens_and_they_are_missing(self, dependency_container):
        dependency_token = "token"
        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            check_qualifier=True,
            builder=lambda: "dependency-instance",
        )

        dependency_container._exception_handler_wrapper = MagicMock(wraps=dependency_container._exception_handler_wrapper)

        with pytest.raises(ValueError, match="Missing qualifier tokens\\."):
            dependency_container._add_dependency(add_dependency_input)

        dependency_container._exception_handler_wrapper.assert_not_called()
        dependency_container._add_dependency_command_handler.handle.assert_not_called()

    def test_retrieve_dependency(self, dependency_container):
        dependency_token = "token"
        dependency_instance = "dependency_instance"

        dependency_container._exception_handler_wrapper = MagicMock(wraps=dependency_container._exception_handler_wrapper)
        dependency_container._is_singletons_built = True
        dependency_container._resolve_dependency_command_handler.handle.return_value = dependency_instance

        retrieve_dependency_input = _RetrieveDependencyInput(dependency_token=dependency_token)

        result = dependency_container._retrieve_dependency(retrieve_dependency_input)

        resolve_dependency_command = ResolveDependencyCommand([retrieve_dependency_input.dependency_token])

        assert result == dependency_instance
        dependency_container._exception_handler_wrapper.assert_called_once()
        dependency_container._resolve_dependency_command_handler.handle.assert_called_once_with(resolve_dependency_command)

    def test_retrieve_dependency_with_qualifier_token(self, dependency_container):
        dependency_token = "token"
        qualifier_token = "qualifier_token"
        dependency_instance = "dependency_instance"

        dependency_container._exception_handler_wrapper = MagicMock(wraps=dependency_container._exception_handler_wrapper)
        dependency_container._is_singletons_built = True
        dependency_container._resolve_dependency_command_handler.handle.return_value = dependency_instance

        retrieve_dependency_input = _RetrieveDependencyInput(
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
        )

        result = dependency_container._retrieve_dependency(retrieve_dependency_input)

        resolve_dependency_command = ResolveDependencyCommand(
            [
                retrieve_dependency_input.dependency_token,
                *retrieve_dependency_input.qualifier_tokens,
            ]
        )

        assert result == dependency_instance
        dependency_container._exception_handler_wrapper.assert_called_once()
        dependency_container._resolve_dependency_command_handler.handle.assert_called_once_with(resolve_dependency_command)

    def test_retrieve_dependency_raise_when_dependency_token_is_missing(self, dependency_container):
        dependency_instance = "dependency_instance"

        dependency_container._exception_handler_wrapper = MagicMock(wraps=dependency_container._exception_handler_wrapper)
        dependency_container._is_singletons_built = True
        dependency_container._resolve_dependency_command_handler.handle.return_value = dependency_instance

        retrieve_dependency_input = _RetrieveDependencyInput(dependency_token=None)

        with pytest.raises(ValueError, match="Missing dependency token\\."):
            dependency_container._retrieve_dependency(retrieve_dependency_input)

        dependency_container._exception_handler_wrapper.assert_not_called()
        dependency_container._resolve_dependency_command_handler.handle.assert_not_called()

    def test_retrieve_dependency_raise_with_check_qualifier_tokens_and_they_are_missing(self, dependency_container):
        dependency_token = "token"
        dependency_instance = "dependency_instance"

        dependency_container._exception_handler_wrapper = MagicMock(wraps=dependency_container._exception_handler_wrapper)
        dependency_container._is_singletons_built = True
        dependency_container._resolve_dependency_command_handler.handle.return_value = dependency_instance

        retrieve_dependency_input = _RetrieveDependencyInput(dependency_token=dependency_token, check_qualifier=True)

        with pytest.raises(ValueError, match="Missing qualifier tokens\\."):
            dependency_container._retrieve_dependency(retrieve_dependency_input)

        dependency_container._exception_handler_wrapper.assert_not_called()
        dependency_container._resolve_dependency_command_handler.handle.assert_not_called()

    def test_retrieve_dependency_raise_when_use_and_container_is_not_built(self, dependency_container):
        dependency_token = "token"
        dependency_instance = "dependency_instance"

        dependency_container._exception_handler_wrapper = MagicMock(wraps=dependency_container._exception_handler_wrapper)
        dependency_container._resolve_dependency_command_handler.handle.return_value = dependency_instance
        dependency_container._is_build_singletons_required = True

        retrieve_dependency_input = _RetrieveDependencyInput(dependency_token=dependency_token)

        with pytest.raises(
            ValueError,
            match="Dependency container singletons not initialized\\. Please call the \\'build_singletons\\(\\)\\' method before attempting to retrieve dependencies\\.",
        ):
            dependency_container._retrieve_dependency(retrieve_dependency_input)

        dependency_container._exception_handler_wrapper.assert_not_called()
        dependency_container._resolve_dependency_command_handler.handle.assert_not_called()

    def test_delete_dependency(self, dependency_container):
        dependency_token = "token"
        dependency_id = "dependency_id"
        dependency_container._token_store.retrieve_or_create_dependency_id_by_tokens.return_value = dependency_id

        dependency_container.delete_dependency(dependency_token)

        dependency_container._token_store.retrieve_or_create_dependency_id_by_tokens.assert_called_once_with([dependency_token, None])
        dependency_container._dependency_store.delete_dependency.assert_called_once_with(dependency_id)

    def test_delete_dependency_with_qualifier_token(self, dependency_container):
        dependency_token = "token"
        qualifier_token = "qualifier_token"
        dependency_id = "dependency_id"
        dependency_container._token_store.retrieve_or_create_dependency_id_by_tokens.return_value = dependency_id

        dependency_container.delete_dependency(dependency_token, qualifier_token)

        dependency_container._token_store.retrieve_or_create_dependency_id_by_tokens.assert_called_once_with([dependency_token, qualifier_token])
        dependency_container._dependency_store.delete_dependency.assert_called_once_with(dependency_id)

    def test_reset(self, dependency_container):
        dependency_container.reset()
        dependency_container._token_store.reset.assert_called_once()
        dependency_container._dependency_store.reset.assert_called_once()

    def test_add_singleton_builder(self, dependency_container):
        dependency_token = "token"

        dependency_container._add_dependency = MagicMock()

        def builder():
            return "dependency-instance"

        dependency_container.add_singleton_builder(dependency_token=dependency_token, builder=builder)

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            builder=builder,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_singleton_builder_raise_with_missing_builder(self, dependency_container):
        dependency_token = "token"

        dependency_container._add_dependency = MagicMock()

        with pytest.raises(ValueError, match="Missing builder function\\."):
            dependency_container.add_singleton_builder(dependency_token=dependency_token, builder=None)

        dependency_container._add_dependency.assert_not_called()

    def test_add_mapped_singleton_builder(self, dependency_container):
        dependency_token = "token"
        qualifier_token = "qualifier-token"

        dependency_container._add_dependency = MagicMock()

        def builder():
            return "dependency-instance"

        dependency_container.add_mapped_singleton_builder(
            dependency_token=dependency_token,
            qualifier_token=qualifier_token,
            builder=builder,
        )

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            builder=builder,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_mapped_singleton_builder_raise_with_missing_builder(self, dependency_container):
        dependency_token = "token"
        qualifier_token = "qualifier-token"

        dependency_container._add_dependency = MagicMock()

        with pytest.raises(ValueError, match="Missing builder function\\."):
            dependency_container.add_mapped_singleton_builder(
                dependency_token=dependency_token,
                qualifier_token=qualifier_token,
                builder=None,
            )

        dependency_container._add_dependency.assert_not_called()

    def test_add_singleton_instance(self, dependency_container):
        dependency_token = "token"

        dependency_container._add_dependency = MagicMock()

        instance = "dependency-instance"

        dependency_container.add_singleton_instance(
            dependency_token=dependency_token,
            instance=instance,
        )

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            instance=instance,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_singleton_instance_raise_with_missing_instance(self, dependency_container):
        dependency_token = "token"

        dependency_container._add_dependency = MagicMock()

        with pytest.raises(ValueError, match="Missing instance\\."):
            dependency_container.add_singleton_instance(
                dependency_token=dependency_token,
                instance=None,
            )

        dependency_container._add_dependency.assert_not_called()

    def test_add_mapped_singleton_instance(self, dependency_container):
        dependency_token = "token"
        qualifier_token = "qualifier-token"

        dependency_container._add_dependency = MagicMock()

        instance = "dependency-instance"

        dependency_container.add_mapped_singleton_instance(
            dependency_token=dependency_token,
            qualifier_token=qualifier_token,
            instance=instance,
        )

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            instance=instance,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_mapped_singleton_instance_raise_with_missing_instance(self, dependency_container):
        dependency_token = "token"
        qualifier_token = "qualifier-token"

        dependency_container._add_dependency = MagicMock()

        with pytest.raises(ValueError, match="Missing instance\\."):
            dependency_container.add_mapped_singleton_instance(
                dependency_token=dependency_token,
                qualifier_token=qualifier_token,
                instance=None,
            )

        dependency_container._add_dependency.assert_not_called()

    def test_add_singleton_with_dependency_token_as_constructor(self, dependency_container):
        class MyClass:
            pass

        dependency_token = MyClass

        dependency_container._add_dependency = MagicMock()

        dependency_container.add_singleton(dependency_token=dependency_token)

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            class_constructor=dependency_token,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_singleton_with_dependency_token_and_constructor(self, dependency_container):
        class MyClassInterface:
            pass

        class MyClassConcrete(MyClassInterface):
            pass

        dependency_token = MyClassInterface
        class_constructor = MyClassConcrete

        dependency_container._add_dependency = MagicMock()

        dependency_container.add_singleton(dependency_token=dependency_token, class_constructor=class_constructor)

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            class_constructor=class_constructor,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_mapped_singleton_with_dependency_token_as_constructor(self, dependency_container):
        class MyClass:
            pass

        dependency_token = MyClass
        qualifier_token = "qualifier-token"

        dependency_container._add_dependency = MagicMock()

        dependency_container.add_mapped_singleton(dependency_token=dependency_token, qualifier_token=qualifier_token)

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            class_constructor=dependency_token,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_mapped_singleton_with_dependency_token_and_constructor(self, dependency_container):
        class MyClassInterface:
            pass

        class MyClassConcrete(MyClassInterface):
            pass

        dependency_token = MyClassInterface
        class_constructor = MyClassConcrete
        qualifier_token = "qualifier-token"

        dependency_container._add_dependency = MagicMock()

        dependency_container.add_mapped_singleton(
            dependency_token=dependency_token,
            qualifier_token=qualifier_token,
            class_constructor=class_constructor,
        )

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            class_constructor=class_constructor,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_transient_builder(self, dependency_container):
        dependency_token = "token"

        dependency_container._add_dependency = MagicMock()

        def builder():
            return "dependency-instance"

        dependency_container.add_transient_builder(dependency_token=dependency_token, builder=builder)

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.TRANSIENT,
            dependency_token=dependency_token,
            builder=builder,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_transient_builder_raise_with_missing_builder(self, dependency_container):
        dependency_token = "token"

        dependency_container._add_dependency = MagicMock()

        with pytest.raises(ValueError, match="Missing builder function\\."):
            dependency_container.add_transient_builder(dependency_token=dependency_token, builder=None)

        dependency_container._add_dependency.assert_not_called()

    def test_add_mapped_transient_builder(self, dependency_container):
        dependency_token = "token"
        qualifier_token = "qualifier-token"

        dependency_container._add_dependency = MagicMock()

        def builder():
            return "dependency-instance"

        dependency_container.add_mapped_transient_builder(
            dependency_token=dependency_token,
            qualifier_token=qualifier_token,
            builder=builder,
        )

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.TRANSIENT,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            builder=builder,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_mapped_transient_builder_raise_with_missing_builder(self, dependency_container):
        dependency_token = "token"
        qualifier_token = "qualifier-token"

        dependency_container._add_dependency = MagicMock()

        with pytest.raises(ValueError, match="Missing builder function\\."):
            dependency_container.add_mapped_transient_builder(
                dependency_token=dependency_token,
                qualifier_token=qualifier_token,
                builder=None,
            )

        dependency_container._add_dependency.assert_not_called()

    def test_add_transient_with_dependency_token_as_constructor(self, dependency_container):
        class MyClass:
            pass

        dependency_token = MyClass

        dependency_container._add_dependency = MagicMock()

        dependency_container.add_transient(dependency_token=dependency_token)

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.TRANSIENT,
            dependency_token=dependency_token,
            class_constructor=dependency_token,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_transient_with_dependency_token_and_constructor(self, dependency_container):
        class MyClassInterface:
            pass

        class MyClassConcrete(MyClassInterface):
            pass

        dependency_token = MyClassInterface
        class_constructor = MyClassConcrete

        dependency_container._add_dependency = MagicMock()

        dependency_container.add_transient(dependency_token=dependency_token, class_constructor=class_constructor)

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.TRANSIENT,
            dependency_token=dependency_token,
            class_constructor=class_constructor,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_mapped_transient_with_dependency_token_as_constructor(self, dependency_container):
        class MyClass:
            pass

        dependency_token = MyClass
        qualifier_token = "qualifier-token"

        dependency_container._add_dependency = MagicMock()

        dependency_container.add_mapped_transient(dependency_token=dependency_token, qualifier_token=qualifier_token)

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.TRANSIENT,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            class_constructor=dependency_token,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_mapped_transient_with_dependency_token_and_constructor(self, dependency_container):
        class MyClassInterface:
            pass

        class MyClassConcrete(MyClassInterface):
            pass

        dependency_token = MyClassInterface
        class_constructor = MyClassConcrete
        qualifier_token = "qualifier-token"

        dependency_container._add_dependency = MagicMock()

        dependency_container.add_mapped_transient(
            dependency_token=dependency_token,
            qualifier_token=qualifier_token,
            class_constructor=class_constructor,
        )

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.TRANSIENT,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            class_constructor=class_constructor,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_per_context_builder(self, dependency_container):
        dependency_token = "token"

        dependency_container._add_dependency = MagicMock()

        def builder():
            return "dependency-instance"

        dependency_container.add_per_context_builder(dependency_token=dependency_token, builder=builder)

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.CONTEXT,
            dependency_token=dependency_token,
            builder=builder,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_per_context_builder_raise_with_missing_builder(self, dependency_container):
        dependency_token = "token"

        dependency_container._add_dependency = MagicMock()

        with pytest.raises(ValueError, match="Missing builder function\\."):
            dependency_container.add_per_context_builder(dependency_token=dependency_token, builder=None)

        dependency_container._add_dependency.assert_not_called()

    def test_add_mapped_per_context_builder(self, dependency_container):
        dependency_token = "token"
        qualifier_token = "qualifier-token"

        dependency_container._add_dependency = MagicMock()

        def builder():
            return "dependency-instance"

        dependency_container.add_mapped_per_context_builder(
            dependency_token=dependency_token,
            qualifier_token=qualifier_token,
            builder=builder,
        )

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.CONTEXT,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            builder=builder,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_mapped_per_context_builder_raise_with_missing_builder(self, dependency_container):
        dependency_token = "token"
        qualifier_token = "qualifier-token"

        dependency_container._add_dependency = MagicMock()

        with pytest.raises(ValueError, match="Missing builder function\\."):
            dependency_container.add_mapped_per_context_builder(
                dependency_token=dependency_token,
                qualifier_token=qualifier_token,
                builder=None,
            )

        dependency_container._add_dependency.assert_not_called()

    def test_add_per_context_with_dependency_token_as_constructor(self, dependency_container):
        class MyClass:
            pass

        dependency_token = MyClass

        dependency_container._add_dependency = MagicMock()

        dependency_container.add_per_context(dependency_token=dependency_token)

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.CONTEXT,
            dependency_token=dependency_token,
            class_constructor=dependency_token,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_per_context_with_dependency_token_and_constructor(self, dependency_container):
        class MyClassInterface:
            pass

        class MyClassConcrete(MyClassInterface):
            pass

        dependency_token = MyClassInterface
        class_constructor = MyClassConcrete

        dependency_container._add_dependency = MagicMock()

        dependency_container.add_per_context(dependency_token=dependency_token, class_constructor=class_constructor)

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.CONTEXT,
            dependency_token=dependency_token,
            class_constructor=class_constructor,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_mapped_per_context_with_dependency_token_as_constructor(self, dependency_container):
        class MyClass:
            pass

        dependency_token = MyClass
        qualifier_token = "qualifier-token"

        dependency_container._add_dependency = MagicMock()

        dependency_container.add_mapped_per_context(dependency_token=dependency_token, qualifier_token=qualifier_token)

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.CONTEXT,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            class_constructor=dependency_token,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_add_mapped_per_context_with_dependency_token_and_constructor(self, dependency_container):
        class MyClassInterface:
            pass

        class MyClassConcrete(MyClassInterface):
            pass

        dependency_token = MyClassInterface
        class_constructor = MyClassConcrete
        qualifier_token = "qualifier-token"

        dependency_container._add_dependency = MagicMock()

        dependency_container.add_mapped_per_context(
            dependency_token=dependency_token,
            qualifier_token=qualifier_token,
            class_constructor=class_constructor,
        )

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.CONTEXT,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            class_constructor=class_constructor,
        )

        dependency_container._add_dependency.assert_called_once_with(add_dependency_input)

    def test_get_dependency(self, dependency_container: DependencyContainer):
        dependency_token = "token"

        dependency_container._retrieve_dependency = MagicMock()

        dependency_container.get_dependency(dependency_token)

        retrieve_dependency_input = _RetrieveDependencyInput(
            dependency_token=dependency_token,
        )

        dependency_container._retrieve_dependency.assert_called_once_with(retrieve_dependency_input)

    def test_get_required_dependency(self, dependency_container: DependencyContainer):
        dependency_token = "token"

        dependency_container._retrieve_dependency = MagicMock()

        dependency_container.get_required_dependency(dependency_token)

        retrieve_dependency_input = _RetrieveDependencyInput(dependency_token=dependency_token, required=True)

        dependency_container._retrieve_dependency.assert_called_once_with(retrieve_dependency_input)

    def test_get_mapped_dependency(self, dependency_container: DependencyContainer):
        dependency_token = "token"
        qualifier_token = "qualifier-token"

        dependency_container._retrieve_dependency = MagicMock()

        dependency_container.get_mapped_dependency(dependency_token, qualifier_token)

        retrieve_dependency_input = _RetrieveDependencyInput(
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
        )

        dependency_container._retrieve_dependency.assert_called_once_with(retrieve_dependency_input)

    def test_get_required_mapped_dependency(self, dependency_container: DependencyContainer):
        dependency_token = "token"
        qualifier_token = "qualifier-token"

        dependency_container._retrieve_dependency = MagicMock()

        dependency_container.get_required_mapped_dependency(dependency_token, qualifier_token)

        retrieve_dependency_input = _RetrieveDependencyInput(
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            required=True,
        )

        dependency_container._retrieve_dependency.assert_called_once_with(retrieve_dependency_input)
