from dataclasses import dataclass
from ..__seedwork.dictionary import Dictionary
from .dependency_registry import DependencyRegistry
from ..exceptions.cyclic_dependencies_exception import CyclicDependenciesException
from ..exceptions.missing_dependency_exception import MissingDependencyException


@dataclass
class _GraphAndDegrees:
    graph: dict[str, list[str]]
    input_degree: dict[str, int]


class DependencyStore:
    def __init__(self):
        self._dependencies = Dictionary[str, DependencyRegistry]()
        self._sorted_dependencies_ids_cache_invalidated = False
        self._sorted_dependencies_ids = []

    def add_dependency(self, registry: DependencyRegistry):
        self._sorted_dependencies_ids_cache_invalidated = True
        self._dependencies.set(registry.dependency_id, registry)

    def get_dependency(self, dependency_id: str) -> DependencyRegistry:
        registry = self._dependencies.get(dependency_id)

        if registry is None:
            raise MissingDependencyException([dependency_id])

        return registry

    def delete_dependency(self, dependency_id: str):
        self._dependencies.delete(dependency_id)

    def reset(self):
        self._dependencies.clear()

    def _initialize_graph_and_degrees(self) -> _GraphAndDegrees:
        graph: dict[str, list[str]] = {}
        input_degree: dict[str, int] = {}

        for dependency_id, dependency_registry in self._dependencies.items():
            input_degree[dependency_id] = input_degree.get(dependency_id, 0)

            for class_constructor_dependency_id in dependency_registry.implementation_details.class_constructor_dependencies_ids:
                input_degree[class_constructor_dependency_id] = input_degree.get(class_constructor_dependency_id, 0) + 1

                if dependency_id not in graph.values():
                    graph[dependency_id] = []

                graph[dependency_id].append(class_constructor_dependency_id)

        return _GraphAndDegrees(graph, input_degree)

    def _perform_topological_sort(
        self,
        graph: dict[str, list[str]],
        input_degree: dict[str, int],
    ) -> list[str]:
        queue: list[str] = []

        for dependency_id, degree in input_degree.items():
            if degree == 0:
                queue.append(dependency_id)

        sorted_list: list[str] = []

        while len(queue) > 0:
            current_item = queue.pop(0)
            sorted_list.append(current_item)

            if graph.get(current_item, None) is None:
                continue

            for dependent in graph[current_item]:
                input_degree[dependent] = input_degree[dependent] - 1

                if input_degree[dependent] == 0:
                    queue.append(dependent)

        return sorted_list

    def _detect_and_raise_cyclic_dependencies(
        self,
        graph: dict[str, list[str]],
        input_degree: dict[str, int],
    ):
        unresolved = filter(
            lambda dependency_id: input_degree[dependency_id] > 0 and graph.get(dependency_id, None) is not None,
            list(input_degree.keys()),
        )

        if len(list(unresolved)) > 0:
            raise CyclicDependenciesException(unresolved)

    def get_sorted_dependencies_ids(self) -> list[str]:
        if self._sorted_dependencies_ids_cache_invalidated:
            graph_and_degrees = self._initialize_graph_and_degrees()
            sorted_list = self._perform_topological_sort(graph_and_degrees.graph, graph_and_degrees.input_degree)

            if len(sorted_list) != self._dependencies.len():
                self._detect_and_raise_cyclic_dependencies(graph_and_degrees.graph, graph_and_degrees.input_degree)

            self._sorted_dependencies_ids = list(reversed(sorted_list))
            self._sorted_dependencies_ids_cache_invalidated = False

            return self._sorted_dependencies_ids

        return self._sorted_dependencies_ids
