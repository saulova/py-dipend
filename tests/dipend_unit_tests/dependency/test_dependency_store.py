from unittest.mock import MagicMock
import pytest
from dipend.exceptions.cyclic_dependencies_exception import (
    CyclicDependenciesException,
)
from dipend.exceptions.missing_dependency_exception import (
    MissingDependencyException,
)
from dipend.dependency.dependency_store import DependencyStore


class TestDependencyStore:
    @pytest.fixture
    def dependency_store(self):
        return DependencyStore()

    def test_add_and_get_dependency(self, dependency_store):
        mock_registry = MagicMock(dependency_id="dep1")
        dependency_store.add_dependency(mock_registry)

        result = dependency_store.get_dependency("dep1")

        assert result == mock_registry

    def test_get_dependency_return_none_for_missing_dependency(self, dependency_store):
        with pytest.raises(MissingDependencyException):
            dependency_store.get_dependency("non_existent")

    def test_initialize_graph_and_degrees(self, dependency_store):
        mock_registry_1 = MagicMock(
            dependency_id="dep1",
            implementation_details=MagicMock(class_constructor_dependencies_ids=["dep2"]),
        )
        mock_registry_2 = MagicMock(
            dependency_id="dep2",
            implementation_details=MagicMock(class_constructor_dependencies_ids=[]),
        )

        dependency_store.add_dependency(mock_registry_1)
        dependency_store.add_dependency(mock_registry_2)

        result = dependency_store._initialize_graph_and_degrees()

        expected_graph = {"dep1": ["dep2"]}
        expected_input_degree = {"dep1": 0, "dep2": 1}

        assert result.graph == expected_graph
        assert result.input_degree == expected_input_degree

    def test_perform_topological_sort(self, dependency_store):
        graph = {"dep1": ["dep2"]}
        input_degree = {"dep1": 0, "dep2": 1}

        result = dependency_store._perform_topological_sort(graph, input_degree)

        assert result == ["dep1", "dep2"]

    def test_detect_and_raise_cyclic_dependencies(self, dependency_store):
        graph = {"dep1": ["dep2"], "dep2": ["dep1"]}
        input_degree = {"dep1": 1, "dep2": 1}

        with pytest.raises(CyclicDependenciesException):
            dependency_store._detect_and_raise_cyclic_dependencies(graph, input_degree)

    def test_get_sorted_dependencies_ids(self, dependency_store):
        mock_registry_1 = MagicMock(
            dependency_id="dep1",
            implementation_details=MagicMock(class_constructor_dependencies_ids=["dep2"]),
        )
        mock_registry_2 = MagicMock(
            dependency_id="dep2",
            implementation_details=MagicMock(class_constructor_dependencies_ids=[]),
        )

        dependency_store.add_dependency(mock_registry_1)
        dependency_store.add_dependency(mock_registry_2)

        result = dependency_store.get_sorted_dependencies_ids()

        assert result == ["dep2", "dep1"]

    def test_cache_sorted_dependencies_ids(self, dependency_store):
        mock_registry_1 = MagicMock(
            dependency_id="dep1",
            implementation_details=MagicMock(class_constructor_dependencies_ids=["dep2"]),
        )
        mock_registry_2 = MagicMock(
            dependency_id="dep2",
            implementation_details=MagicMock(class_constructor_dependencies_ids=[]),
        )

        dependency_store.add_dependency(mock_registry_1)
        dependency_store.add_dependency(mock_registry_2)

        dependency_store._initialize_graph_and_degrees = MagicMock(wraps=dependency_store._initialize_graph_and_degrees)

        result = dependency_store.get_sorted_dependencies_ids()
        result = dependency_store.get_sorted_dependencies_ids()

        dependency_store._initialize_graph_and_degrees.assert_called_once()

        assert result == ["dep2", "dep1"]

    def test_get_sorted_dependencies_ids_raises_cyclic_dependencies_exception(self, dependency_store):
        mock_registry_1 = MagicMock(
            dependency_id="dep1",
            implementation_details=MagicMock(class_constructor_dependencies_ids=["dep2"]),
        )
        mock_registry_2 = MagicMock(
            dependency_id="dep2",
            implementation_details=MagicMock(class_constructor_dependencies_ids=["dep1"]),
        )

        dependency_store.add_dependency(mock_registry_1)
        dependency_store.add_dependency(mock_registry_2)

        with pytest.raises(CyclicDependenciesException):
            dependency_store.get_sorted_dependencies_ids()

    def test_delete_token_removes_token_registry(self, dependency_store):
        dependency_id = "dep1"
        mock_registry = MagicMock(
            dependency_id=dependency_id,
            implementation_details=MagicMock(class_constructor_dependencies_ids=[]),
        )

        dependency_store.add_dependency(mock_registry)

        dependency_store.delete_dependency(dependency_id)

        with pytest.raises(MissingDependencyException):
            dependency_store.get_dependency(dependency_id)

    def test_reset_clears_all_tokens(self, dependency_store):
        dependency_id = "dep1"
        mock_registry = MagicMock(
            dependency_id=dependency_id,
            implementation_details=MagicMock(class_constructor_dependencies_ids=[]),
        )

        dependency_store.add_dependency(mock_registry)

        dependency_store.reset()

        with pytest.raises(MissingDependencyException):
            dependency_store.get_dependency(dependency_id)
