from dataclasses import dataclass


@dataclass
class ResolveSpecificLifecyclesCommand:
    lifecycles: list[str]
