from __future__ import annotations
from typing import Any, Callable

class Task:
    def __init__(self, name: str, description: str = "", action: Callable[..., Any] | None = None) -> None:
        self.name = name
        self.description = description
        self.action = action

    def run(self, *args: Any, **kwargs: Any) -> Any:
        if self.action is None:
            raise RuntimeError(f"No action defined for task '{self.name}'")
        return self.action(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<Task name={self.name!r} description={self.description!r}>"
