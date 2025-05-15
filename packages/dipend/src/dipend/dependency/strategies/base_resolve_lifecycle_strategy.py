from typing import Any
from dipend.__seedwork.strategy_interface import StrategyInterface
from dipend.exceptions.can_not_construct_dependency_exception import (
    CanNotConstructDependencyException,
)
from .resolve_lifecycle_strategy_input import ResolveLifecycleStrategyInput


class BaseResolveLifecycleStrategy(
    StrategyInterface[ResolveLifecycleStrategyInput, Any]
):
    def _construct(self, input_data: ResolveLifecycleStrategyInput) -> Any:
        implementation_details = input_data.dependency_registry.implementation_details

        if implementation_details.instance is not None:
            return implementation_details.instance

        if implementation_details.builder is not None:
            return implementation_details.builder()

        if implementation_details.class_constructor is None:
            raise CanNotConstructDependencyException(
                [input_data.dependency_registry.dependency_id]
            )

        return implementation_details.class_constructor(
            *input_data.resolved_class_constructor_dependencies
        )
