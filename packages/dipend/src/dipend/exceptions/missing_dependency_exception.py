from .base_dependency_container_exception import BaseDependencyContainerException


class MissingDependencyException(BaseDependencyContainerException):
    def __init__(self, dependency_ids: list[str]):
        super().__init__(dependency_ids, "Missing dependency")
