from dataclasses import dataclass
from .implementation_details import ImplementationDetails


@dataclass
class DependencyRegistry:
    dependency_id: str
    lifecycle: str
    implementation_details: ImplementationDetails
