from typing import Any, Optional
from dataclasses import dataclass, field


@dataclass
class ResolveDependencyCommand:
    tokens: list[Any]
    required: Optional[bool] = field(default=False)
