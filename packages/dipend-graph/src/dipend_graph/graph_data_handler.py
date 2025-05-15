from typing import Any


class GraphDataHandler:
    def __init__(
        self,
        dependency_container: Any,
    ):
        self._dependency_container = dependency_container

    def _get_node_name(self, dependency_id: str):
        tokens = self._dependency_container._token_store.get_tokens(dependency_id)

        token_names: list[str] = []

        for token in tokens:
            token_type = self._dependency_container._token_type_resolver.get_token_type(token)
            token_name = self._dependency_container._token_name_resolver.get_token_name(token, token_type)
            token_names.append(token_name)

        return ":".join(token_names)

    def _get_node_type(self, dependency_id: str):
        dependency_registry = self._dependency_container._dependency_store._dependencies.get(dependency_id)

        return str(dependency_registry.lifecycle.value).upper()

    def _get_node(self, dependency_id: str):
        return {
            "node": self._get_node_name(dependency_id),
            "type": self._get_node_type(dependency_id),
        }

    def _get_types(self):
        return [
            {
                "type": "SINGLETON",
                "color": "#03C800",
            },
            {
                "type": "TRANSIENT",
                "color": "#FF5733",
            },
            {"type": "CONTEXT", "color": "#007FE9"},
        ]

    def _get_dependency_graph_data(self):
        dependency_ids = self._dependency_container._dependency_store.get_sorted_dependencies_ids()

        graph_and_degrees = self._dependency_container._dependency_store._initialize_graph_and_degrees()

        nodes: list[dict[str, str]] = []

        for dependency_id in dependency_ids:
            nodes.append(self._get_node(dependency_id))

        links: list[dict[str, str]] = []

        for source, targets in graph_and_degrees.graph.items():
            for target in targets:
                links.append(
                    {
                        "source": self._get_node_name(source),
                        "target": self._get_node_name(target),
                    }
                )

        return {
            "nodes": nodes,
            "links": links,
            "types": self._get_types(),
        }

    def handle(self):
        return self._get_dependency_graph_data()
