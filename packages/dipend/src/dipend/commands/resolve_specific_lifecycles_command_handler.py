from ..__seedwork.handler_interface import HandlerInterface
from .resolve_specific_lifecycles_command import ResolveSpecificLifecyclesCommand
from ..dependency.dependency_store import DependencyStore
from ..dependency.dependency_resolver import DependencyResolver


class ResolveSpecificLifecyclesCommandHandler(HandlerInterface[ResolveSpecificLifecyclesCommand, None]):
    def __init__(
        self,
        dependency_store: DependencyStore,
        dependency_resolver: DependencyResolver,
    ):
        self._dependency_store = dependency_store
        self._dependency_resolver = dependency_resolver

    def handle(self, input_data: ResolveSpecificLifecyclesCommand):
        sorted_dependencies = self._dependency_store.get_sorted_dependencies_ids()

        for dependency_id in sorted_dependencies:
            dependency_registry = self._dependency_store.get_dependency(dependency_id)

            if dependency_registry.lifecycle in input_data.lifecycles:
                self._dependency_resolver.resolve(dependency_id)
