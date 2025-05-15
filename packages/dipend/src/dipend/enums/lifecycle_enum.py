from enum import Enum


class LifecycleEnum(Enum):
    SINGLETON = "SINGLETON"
    TRANSIENT = "TRANSIENT"
    CONTEXT = "CONTEXT"
