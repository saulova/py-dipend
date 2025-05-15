from unittest.mock import MagicMock, call
import pytest
from dipend.token.token_store import (
    TokenStore,
)
from dipend.enums.lifecycle_enum import LifecycleEnum
from dipend.dependency.dependency_store import DependencyStore
from dipend.dependency.dependency_resolver import (
    DependencyResolver,
)
from dipend.commands.add_dependency_command import (
    AddDependencyCommand,
)
from dipend.commands.add_dependency_command_handler import (
    AddDependencyCommandHandler,
)
from dipend.decorators.inject_mapped_dependency import (
    inject_mapped_dependency,
)
from dipend.exceptions.can_not_construct_dependency_exception import (
    CanNotConstructDependencyException,
)


class MyClass1:
    def __init__(self):
        self.test = "test-value"


class MyClass2:
    def __init__(self, my_class1: MyClass1):
        self.my_class1 = my_class1


@inject_mapped_dependency(0, [MyClass2])
class MyClass3:
    def __init__(self, my_class1: MyClass1):
        self.my_class1 = my_class1


class MyClass4:
    def __init__(self, my_str):
        self.my_str = my_str


class TestAddDependencyCommandHandler:
    @pytest.fixture
    def setup_handler(self):
        token_store = MagicMock(TokenStore)
        dependency_store = MagicMock(DependencyStore)
        dependency_resolver = MagicMock(DependencyResolver)

        handler = AddDependencyCommandHandler(
            token_store,
            dependency_store,
            dependency_resolver,
        )

        return handler, token_store, dependency_store, dependency_resolver

    def test_handle_creates_dependency_registry(self, setup_handler):
        handler, token_store, dependency_store, _ = setup_handler

        command = AddDependencyCommand(
            tokens=[MyClass1],
            lifecycle=LifecycleEnum.SINGLETON,
            class_constructor=MyClass1,
        )

        token_store.retrieve_or_create_dependency_id_by_tokens.return_value = "dependency_id"

        handler.handle(command)

        token_store.retrieve_or_create_dependency_id_by_tokens.assert_called_once_with(command.tokens)
        dependency_store.add_dependency.assert_called_once()

    def test_handle_with_class_constructor_dependencies(self, setup_handler):
        handler, token_store, dependency_store, _ = setup_handler

        command = AddDependencyCommand(
            tokens=[MyClass2],
            lifecycle=LifecycleEnum.SINGLETON,
            class_constructor=MyClass2,
        )

        token_store.retrieve_or_create_dependency_id_by_tokens.return_value = "dependency_id"

        handler.handle(command)

        token_store.retrieve_or_create_dependency_id_by_tokens.assert_has_calls([call([MyClass2]), call([MyClass1])])
        dependency_store.add_dependency.assert_called_once()

    def test_handle_with_no_class_constructor(self, setup_handler):
        handler, token_store, dependency_store, _ = setup_handler

        command = AddDependencyCommand(
            tokens=[MyClass1],
            lifecycle=LifecycleEnum.TRANSIENT,
            builder=lambda x: MyClass1(),
        )

        token_store.retrieve_or_create_dependency_id_by_tokens.return_value = "dependency_id"

        handler.handle(command)

        token_store.retrieve_or_create_dependency_id_by_tokens.assert_called_once()
        dependency_store.add_dependency.assert_called_once()

    def test_handle_with_mapped_dependency_class_constructor_dependencies(self, setup_handler):
        handler, token_store, dependency_store, _ = setup_handler

        command = AddDependencyCommand(
            tokens=[MyClass3],
            lifecycle=LifecycleEnum.SINGLETON,
            class_constructor=MyClass3,
        )

        token_store.retrieve_or_create_dependency_id_by_tokens.return_value = "dependency_id"

        handler.handle(command)

        token_store.retrieve_or_create_dependency_id_by_tokens.assert_has_calls([call([MyClass3]), call([MyClass1, MyClass2])])
        dependency_store.add_dependency.assert_called_once()

    def test_handle_with_invalid_class_constructor(self, setup_handler):
        handler, token_store, dependency_store, _ = setup_handler

        command = AddDependencyCommand(
            tokens=[MyClass4],
            lifecycle=LifecycleEnum.TRANSIENT,
            class_constructor=MyClass4,
        )

        token_store.retrieve_or_create_dependency_id_by_tokens.return_value = "dependency_id"

        with pytest.raises(CanNotConstructDependencyException):
            handler.handle(command)

        token_store.retrieve_or_create_dependency_id_by_tokens.assert_called_once()
        dependency_store.add_dependency.assert_not_called()
