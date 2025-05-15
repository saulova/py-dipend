from typing import Any, Optional, Callable, overload
from dataclasses import dataclass, field
from .dependency_container_config import DependencyContainerConfig
from .token.token_store import TokenStore
from .dependency.dependency_store import DependencyStore
from .dependency.dependency_resolver import DependencyResolver
from .token.token_type_resolver import TokenTypeResolver
from .token.token_name_resolver import TokenNameResolver
from .exceptions.exception_handler import ExceptionHandler
from .exceptions.base_dependency_container_exception import (
    BaseDependencyContainerException,
)
from .commands.add_dependency_command import AddDependencyCommand
from .commands.add_dependency_command_handler import (
    AddDependencyCommandHandler,
)
from .commands.resolve_dependency_command import (
    ResolveDependencyCommand,
)
from .commands.resolve_dependency_command_handler import (
    ResolveDependencyCommandHandler,
)
from .commands.resolve_specific_lifecycles_command import (
    ResolveSpecificLifecyclesCommand,
)
from .commands.resolve_specific_lifecycles_command_handler import (
    ResolveSpecificLifecyclesCommandHandler,
)
from .enums.lifecycle_enum import LifecycleEnum


@dataclass
class _AddDependencyInput:
    lifecycle: str
    dependency_token: Optional[Any] = field(default=None)
    check_qualifier: Optional[bool] = field(default=False)
    qualifier_tokens: Optional[list[Any]] = field(default_factory=lambda: [])
    class_constructor: Optional[Callable] = field(default=None)
    builder: Optional[Callable] = field(default=None)
    instance: Optional[Any] = field(default=None)


@dataclass
class _RetrieveDependencyInput:
    dependency_token: Optional[Any] = field(default=None)
    check_qualifier: Optional[bool] = field(default=False)
    qualifier_tokens: Optional[list[Any]] = field(default_factory=lambda: [])
    required: Optional[bool] = field(default=False)


class DependencyContainer:
    """
    A dependency injection container for managing lifecycles and dependencies.
    """

    def __init__(self, config: Optional[DependencyContainerConfig] = None):
        """
        Initializes a DependencyContainer

        Args:
            config (Optional[DependencyContainerConfig]): Configuration for the container.
        """
        self._token_store = TokenStore()
        self._dependency_store = DependencyStore()
        self._dependency_resolver = DependencyResolver(self._dependency_store)
        self._token_type_resolver = TokenTypeResolver()
        self._token_name_resolver = TokenNameResolver()
        self._exception_handler = ExceptionHandler(
            self._token_store,
            self._token_type_resolver,
            self._token_name_resolver,
        )
        self._add_dependency_command_handler = AddDependencyCommandHandler(
            self._token_store,
            self._dependency_store,
            self._dependency_resolver,
        )
        self._resolve_dependency_command_handler = ResolveDependencyCommandHandler(
            self._token_store,
            self._dependency_resolver,
        )
        self._resolve_specific_lifecycles_command_handler = ResolveSpecificLifecyclesCommandHandler(
            self._dependency_store,
            self._dependency_resolver,
        )

        self._is_singletons_built = False
        self._is_build_singletons_required = False
        self._dependency_container_token: Any = DependencyContainer

        if config is None:
            config = DependencyContainerConfig()

        self._load_configs(config)

    def _load_configs(self, config: DependencyContainerConfig):
        if config.disable_default_resolve_lifecycle_strategies is False:
            self._dependency_resolver.set_default_resolve_lifecycle_strategies()

        if config.disable_default_token_type_checkers is False:
            self._token_type_resolver.set_default_token_type_checkers()

        if config.disable_default_token_name_strategies is False:
            self._token_name_resolver.set_default_token_name_strategies()

        self._is_build_singletons_required = config.build_singletons_required

        if config.custom_dependency_container_token is not None:
            self._dependency_container_token = config.custom_dependency_container_token

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=self._dependency_container_token,
            instance=self,
        )

        self._add_dependency(add_dependency_input)

    def _exception_handler_wrapper(self, callback: Callable):
        try:
            return callback()
        except BaseDependencyContainerException as err:
            return self._exception_handler.handle(err)

    def _resolve_lifecycles(self, lifecycles: list[str]):
        resolve_specific_lifecycles_command = ResolveSpecificLifecyclesCommand(lifecycles)

        self._exception_handler_wrapper(lambda: self._resolve_specific_lifecycles_command_handler.handle(resolve_specific_lifecycles_command))

    def build_singletons(self):
        """
        Builds resolving singleton lifecycle dependencies.

        Returns:
            DependencyContainer: The built dependency container.
        """
        self._resolve_lifecycles([LifecycleEnum.SINGLETON])

        self._is_singletons_built = True

        return self

    def build_context(self):
        """
        Builds the container, resolving singleton and per context lifecycle dependencies.

        Returns:
            DependencyContainer: The built dependency container.
        """
        lifecycles = [LifecycleEnum.CONTEXT]

        self._resolve_lifecycles(lifecycles)

        return self

    def _add_dependency(self, input_data: _AddDependencyInput):
        dependency_token = input_data.dependency_token or input_data.class_constructor

        if dependency_token is None:
            raise ValueError("Missing dependency token.")

        if input_data.check_qualifier is True and len(input_data.qualifier_tokens) == 0:
            raise ValueError("Missing qualifier tokens.")

        add_dependency_command_input = AddDependencyCommand(
            [dependency_token, *input_data.qualifier_tokens],
            input_data.lifecycle,
            input_data.class_constructor,
            input_data.builder,
            input_data.instance,
        )

        self._exception_handler_wrapper(lambda: self._add_dependency_command_handler.handle(add_dependency_command_input))

    def _retrieve_dependency(self, input_data: _RetrieveDependencyInput):
        if input_data.dependency_token is None:
            raise ValueError("Missing dependency token.")

        if input_data.check_qualifier is True and len(input_data.qualifier_tokens) == 0:
            raise ValueError("Missing qualifier tokens.")

        if self._is_singletons_built is False and self._is_build_singletons_required is True:
            raise ValueError(
                "Dependency container singletons not initialized. Please call the 'build_singletons()' method before attempting to retrieve dependencies.",
            )

        resolve_dependency_command_input = ResolveDependencyCommand(
            tokens=[input_data.dependency_token, *input_data.qualifier_tokens],
            required=input_data.required,
        )

        dependency_instance = self._exception_handler_wrapper(
            lambda: self._resolve_dependency_command_handler.handle(
                resolve_dependency_command_input,
            ),
        )

        return dependency_instance

    def delete_dependency(
        self,
        dependency_token: Any,
        qualifier_token: Optional[Any] = None,
    ):
        """
        Deletes a registered dependency.

        Args:
            dependency_token (Any): The dependency token to remove.
            qualifier_token (Optional[Any]): A token used to distinguish different constructors of the same dependency.
        """
        dependency_id = self._token_store.retrieve_or_create_dependency_id_by_tokens([dependency_token, qualifier_token])

        self._dependency_store.delete_dependency(dependency_id)

        for token in [dependency_token, qualifier_token]:
            self._token_store.delete_token(token)

    def reset(self):
        """
        Resets the dependency container, clearing all stored dependencies.
        """
        self._token_store.reset()
        self._dependency_store.reset()
        self._is_singletons_built = False

    def add_singleton_builder(self, dependency_token: Any, builder: Callable):
        """
        Registers a singleton dependency using a builder function.

        Args:
            dependency_token (Any): The token representing the dependency.
            builder (Callable): A function that builds the dependency instance.

        Raises:
            ValueError: If the builder function is not provided.
        """
        if builder is None:
            raise ValueError("Missing builder function.")

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            builder=builder,
        )

        self._add_dependency(add_dependency_input)

    def add_mapped_singleton_builder(self, dependency_token: Any, qualifier_token: Any, builder: Callable):
        """
        Registers a mapped singleton dependency using a builder function.

        Args:
            dependency_token (Any): The token representing the dependency.
            qualifier_token (Any): A token used to distinguish different constructors of the same dependency.
            builder (Callable): A function that builds the dependency instance.
        """
        if builder is None:
            raise ValueError("Missing builder function.")

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            builder=builder,
        )

        self._add_dependency(add_dependency_input)

    def add_singleton_instance(
        self,
        dependency_token: Any,
        instance: Any,
    ):
        """
        Registers a singleton instance for a dependency.

        Args:
            dependency_token (Any): The token representing the dependency.
            instance (Any): The actual instance to register.

        Raises:
            ValueError: If the instance is not provided.
        """
        if instance is None:
            raise ValueError("Missing instance.")

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            instance=instance,
        )

        self._add_dependency(add_dependency_input)

    def add_mapped_singleton_instance(
        self,
        dependency_token: Any,
        qualifier_token: Any,
        instance: Any,
    ):
        """
        Registers a mapped singleton instance for a dependency.

        Args:
            dependency_token (Any): The token representing the dependency.
            qualifier_token (Any): A token used to distinguish different constructors of the same dependency.
            instance (Any): The actual instance to register.

        Raises:
            ValueError: If the instance is not provided.
        """
        if instance is None:
            raise ValueError("Missing instance.")

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            instance=instance,
        )

        self._add_dependency(add_dependency_input)

    @overload
    def add_singleton(self, dependency_token: Callable):
        pass

    @overload
    def add_singleton(self, dependency_token: Any, class_constructor: Callable):
        pass

    def add_singleton(self, dependency_token: Any, class_constructor: Optional[Callable] = None):
        """
        Registers a singleton dependency in the container.

        This method supports two overloads:
        1. When only `dependency_token` is provided, it is assumed to be a callable that acts as the constructor.
        2. When both `dependency_token` and `class_constructor` are provided, `class_constructor` is used to create instances.

        Args:
            dependency_token (Any): The token representing the dependency.
            class_constructor (Optional[Callable]):
                A callable class constructor used to instantiate the dependency. If not provided,
                `dependency_token` is used as the constructor.
        """
        if class_constructor is None:
            class_constructor = dependency_token

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            class_constructor=class_constructor,
        )

        self._add_dependency(add_dependency_input)

    def add_mapped_singleton(
        self,
        dependency_token: Any,
        qualifier_token: Any,
        class_constructor: Optional[Callable] = None,
    ):
        """
        Registers a mapped singleton dependency in the container.

        Args:
            dependency_token (Any): The token representing the dependency.
            qualifier_token (Any): A token used to distinguish different constructors of the same dependency.
            class_constructor (Callable): A callable class constructor used to instantiate the dependency.
        """
        if class_constructor is None:
            class_constructor = dependency_token

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.SINGLETON,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            class_constructor=class_constructor,
        )

        self._add_dependency(add_dependency_input)

    def add_transient_builder(self, dependency_token: Any, builder: Callable):
        """
        Registers a transient dependency using a builder function.

        Args:
            dependency_token (Any): The token representing the dependency.
            builder (Callable): A function that builds and returns a new instance.

        Raises:
            ValueError: If the builder function is not provided.
        """
        if builder is None:
            raise ValueError("Missing builder function.")

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.TRANSIENT,
            dependency_token=dependency_token,
            builder=builder,
        )

        self._add_dependency(add_dependency_input)

    def add_mapped_transient_builder(self, dependency_token: Any, qualifier_token: Any, builder: Callable):
        """
        Registers a mapped transient dependency using a builder function.

        Args:
            dependency_token (Any): The token representing the dependency.
            qualifier_token (Any): A token used to distinguish different instances of the same dependency.
            builder (Callable): A function that builds and returns a new instance.

        Raises:
            ValueError: If the builder function is not provided.
        """
        if builder is None:
            raise ValueError("Missing builder function.")

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.TRANSIENT,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            builder=builder,
        )

        self._add_dependency(add_dependency_input)

    @overload
    def add_transient(self, dependency_token: Callable):
        pass

    @overload
    def add_transient(self, dependency_token: Any, class_constructor: Callable):
        pass

    def add_transient(self, dependency_token: Any, class_constructor: Optional[Callable] = None):
        """
        Registers a transient dependency in the container.

        This method supports two overloads:
        1. When only `dependency_token` is provided, it is assumed to be a callable that acts as the constructor.
        2. When both `dependency_token` and `class_constructor` are provided, `class_constructor` is used to create instances.

        Args:
            dependency_token (Any): The token representing the dependency.
            class_constructor (Optional[Callable]):
                A callable class constructor used to instantiate the dependency. If not provided,
                `dependency_token` is used as the constructor.
        """
        if class_constructor is None:
            class_constructor = dependency_token

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.TRANSIENT,
            dependency_token=dependency_token,
            class_constructor=class_constructor,
        )

        self._add_dependency(add_dependency_input)

    def add_mapped_transient(
        self,
        dependency_token: Any,
        qualifier_token: Any,
        class_constructor: Optional[Callable] = None,
    ):
        """
        Registers a mapped transient dependency in the container.

        Args:
            dependency_token (Any): The token representing the dependency.
            qualifier_token (Any): The qualifier associated with the dependency.
            class_constructor (Callable): A callable class constructor used to instantiate the dependency.
        """
        if class_constructor is None:
            class_constructor = dependency_token

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.TRANSIENT,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            class_constructor=class_constructor,
        )

        self._add_dependency(add_dependency_input)

    def add_per_context_builder(self, dependency_token: Any, builder: Callable):
        """
        Registers a per-context dependency using a builder function.

        Args:
            dependency_token (Any): The token representing the dependency.
            builder (Callable): A function that builds and returns a new instance per context.

        Raises:
            ValueError: If the builder function is not provided.
        """
        if builder is None:
            raise ValueError("Missing builder function.")

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.CONTEXT,
            dependency_token=dependency_token,
            builder=builder,
        )

        self._add_dependency(add_dependency_input)

    def add_mapped_per_context_builder(self, dependency_token: Any, qualifier_token: Any, builder: Callable):
        """
        Registers a mapped per-context dependency using a builder function.

        Args:
            dependency_token (Any): The token representing the dependency.
            qualifier_token (Any): A token used to distinguish different constructors of the same dependency.
            builder (Callable): A function that builds and returns a new instance per context.

        Raises:
            ValueError: If the builder function is not provided.
        """
        if builder is None:
            raise ValueError("Missing builder function.")

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.CONTEXT,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            builder=builder,
        )

        self._add_dependency(add_dependency_input)

    @overload
    def add_per_context(self, dependency_token: Callable):
        pass

    @overload
    def add_per_context(self, dependency_token: Any, class_constructor: Callable):
        pass

    def add_per_context(self, dependency_token: Any, class_constructor: Optional[Callable] = None):
        """
        Registers a per-context dependency in the container.

        This method supports two overloads:
        1. When only `dependency_token` is provided, it is assumed to be a callable that acts as the constructor.
        2. When both `dependency_token` and `class_constructor` are provided, `class_constructor` is used to create instances.

        Args:
            dependency_token (Any): The token representing the dependency.
            class_constructor (Optional[Callable]):
                A callable class constructor used to instantiate the dependency. If not provided,
                `dependency_token` is used as the constructor.
        """
        if class_constructor is None:
            class_constructor = dependency_token

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.CONTEXT,
            dependency_token=dependency_token,
            class_constructor=class_constructor,
        )

        self._add_dependency(add_dependency_input)

    def add_mapped_per_context(
        self,
        dependency_token: Any,
        qualifier_token: Any,
        class_constructor: Optional[Callable] = None,
    ):
        """
        Registers a mapped per-context dependency in the container.

        Args:
            dependency_token (Any): The token representing the dependency.
            qualifier_token (Any): A token used to distinguish different constructors of the same dependency.
            class_constructor (Callable): A callable class constructor used to instantiate the dependency.
        """
        if class_constructor is None:
            class_constructor = dependency_token

        add_dependency_input = _AddDependencyInput(
            lifecycle=LifecycleEnum.CONTEXT,
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            class_constructor=class_constructor,
        )

        self._add_dependency(add_dependency_input)

    def get_dependency(self, dependency_token: Any):
        """
        Retrieves a dependency from the container.

        Args:
            dependency_token (Any): The token representing the dependency.

        Returns:
            Any: The resolved dependency instance.
        """
        retrieve_dependency_input = _RetrieveDependencyInput(
            dependency_token=dependency_token,
        )

        return self._retrieve_dependency(retrieve_dependency_input)

    def get_required_dependency(self, dependency_token: Any):
        """
        Retrieves a required dependency from the container. Raises an error if not found.

        Args:
            dependency_token (Any): The token representing the dependency.

        Returns:
            Any: The resolved dependency instance.

        Raises:
            KeyError: If the dependency is not found.
        """
        retrieve_dependency_input = _RetrieveDependencyInput(dependency_token=dependency_token, required=True)

        return self._retrieve_dependency(retrieve_dependency_input)

    def get_mapped_dependency(self, dependency_token: Any, qualifier_token: Any):
        """
        Retrieves a mapped dependency.

        Args:
            dependency_token (Any): The token representing the dependency.
            qualifier_token (Any): A token used to distinguish different constructors of the same dependency.

        Returns:
            Any: The resolved dependency instance.
        """
        retrieve_dependency_input = _RetrieveDependencyInput(
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
        )

        return self._retrieve_dependency(retrieve_dependency_input)

    def get_required_mapped_dependency(self, dependency_token: Any, qualifier_token: Any):
        """
        Retrieves a required mapped dependency.

        Args:
            dependency_token (Any): The token representing the dependency.
            qualifier_token (Any): A token used to distinguish different constructors of the same dependency.

        Returns:
            Any: The resolved dependency instance.

        Raises:
            KeyError: If the dependency is not found.
        """
        retrieve_dependency_input = _RetrieveDependencyInput(
            dependency_token=dependency_token,
            check_qualifier=True,
            qualifier_tokens=[qualifier_token],
            required=True,
        )

        return self._retrieve_dependency(retrieve_dependency_input)
