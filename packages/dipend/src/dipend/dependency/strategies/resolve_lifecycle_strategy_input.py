from typing import Any
from dataclasses import dataclass
from ...dependency.dependency_registry import DependencyRegistry


@dataclass
class ResolveLifecycleStrategyInput:
    dependency_registry: DependencyRegistry
    resolved_class_constructor_dependencies: list[Any]
