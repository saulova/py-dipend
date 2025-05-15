class BaseDependencyContainerException(BaseException):
    def __init__(self, dependency_ids: list[str], message: str):
        super().__init__(message)
        self.dependency_ids = dependency_ids
