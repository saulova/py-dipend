from .base_dependency_container_exception import BaseDependencyContainerException


class InvalidLifecycleException(BaseDependencyContainerException):
    def __init__(self, dependency_ids: list[str], lifecycle_policy: str):
        super().__init__(dependency_ids, "Invalid lifecycle: " + lifecycle_policy)
