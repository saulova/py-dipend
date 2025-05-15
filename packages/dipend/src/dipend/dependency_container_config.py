from typing import Any, Optional
from dataclasses import dataclass, field


@dataclass
class DependencyContainerConfig:
    """
    Configuration settings for DependencyContainer.

    Attributes:
        disable_default_resolve_lifecycle_strategies (Optional[bool]):
            Whether to disable default resolve lifecycle strategies.
        disable_default_token_type_checkers (Optional[bool]):
            Whether to disable default token type checkers.
        disable_default_token_name_strategies (Optional[bool]):
            Whether to disable default token name strategies.
        disable_build_required (Optional[bool]):
            Whether to disable build requirement.
        custom_dependency_container_token (Optional[Any]):
            Custom token for dependency container.
    """

    disable_default_resolve_lifecycle_strategies: Optional[bool] = field(default=False)
    disable_default_token_type_checkers: Optional[bool] = field(default=False)
    disable_default_token_name_strategies: Optional[bool] = field(default=False)
    build_singletons_required: Optional[bool] = field(default=False)
    custom_dependency_container_token: Optional[Any] = None
