from typing import Any
from ..__seedwork.dictionary import Dictionary
from ..enums.lifecycle_enum import LifecycleEnum
from ..exceptions.invalid_lifecycle_exception import InvalidLifecycleException
from .strategies.resolve_lifecycle_strategy_input import (
    ResolveLifecycleStrategyInput,
)
from .strategies.base_resolve_lifecycle_strategy import (
    BaseResolveLifecycleStrategy,
)
from .strategies.resolve_singleton_lifecycle_strategy import (
    ResolveSingletonLifecycleStrategy,
)
from .strategies.resolve_transient_lifecycle_strategy import (
    ResolveTransientLifecycleStrategy,
)
from .strategies.resolve_context_lifecycle_strategy import (
    ResolveContextLifecycleStrategy,
)
from ..dependency.dependency_store import DependencyRegistry
from ..dependency.dependency_store import DependencyStore


class DependencyResolver:
    def __init__(self, dependency_store: DependencyStore):
        self._strategies = Dictionary[str, BaseResolveLifecycleStrategy]()
        self._dependency_store = dependency_store

    def set_default_resolve_lifecycle_strategies(self):
        self._strategies.set(LifecycleEnum.SINGLETON, ResolveSingletonLifecycleStrategy())
        self._strategies.set(LifecycleEnum.TRANSIENT, ResolveTransientLifecycleStrategy())
        self._strategies.set(LifecycleEnum.CONTEXT, ResolveContextLifecycleStrategy())

    def add_resolve_lifecycle_strategy(
        self,
        lifecycle: str,
        strategy: BaseResolveLifecycleStrategy,
    ):
        self._strategies.set(lifecycle, strategy)

    def _use_lifecycle_strategy(
        self,
        dependency_registry: DependencyRegistry,
        resolved_class_constructor_dependencies: list[Any],
    ):
        strategy = self._strategies.get(dependency_registry.lifecycle)

        if strategy is None:
            raise InvalidLifecycleException(
                [dependency_registry.dependency_id],
                getattr(dependency_registry.lifecycle, "value", None) or dependency_registry.lifecycle,
            )

        strategy_input = ResolveLifecycleStrategyInput(dependency_registry, resolved_class_constructor_dependencies)

        return strategy.execute(strategy_input)

    def _resolved_instance(self, dependency_registry: DependencyRegistry):
        return dependency_registry.implementation_details.instance

    def resolve(self, dependency_id: str):
        dependency_registry = self._dependency_store.get_dependency(dependency_id)
        resolved_instance = self._resolved_instance(dependency_registry)

        if resolved_instance is not None:
            return resolved_instance

        class_constructor_dependencies_ids = dependency_registry.implementation_details.class_constructor_dependencies_ids

        resolved_class_constructor_dependencies = []

        for constructor_dependency_id in class_constructor_dependencies_ids:
            resolved_class_constructor_dependencies.append(self.resolve(constructor_dependency_id))

        return self._use_lifecycle_strategy(
            dependency_registry,
            resolved_class_constructor_dependencies,
        )
