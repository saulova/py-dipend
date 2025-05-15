import inspect
from typing import Callable


class InspectClassHelper:
    @staticmethod
    def get_constructor_dependencies(class_constructor: Callable):
        class_signature = inspect.signature(class_constructor)

        class_args = [parameter.annotation for parameter in class_signature.parameters.values()]

        return class_args
