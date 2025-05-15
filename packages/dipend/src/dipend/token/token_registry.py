from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class TokenRegistry:
    token: Any
    id: str = field(default_factory=lambda: str(uuid4()))
