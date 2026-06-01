from __future__ import annotations

from typing import Any


class StrMixin:
    def __str__(self) -> str:
        if hasattr(self, "to_list"):
            items = self.to_list()
        elif hasattr(self, "__iter__"):
            items = list(self)
        else:
            items = []
        return f"[{', '.join(str(v) for v in items)}]"

    def display(self, sep: str = " ") -> None:
        items = []
        if hasattr(self, "to_list"):
            items = self.to_list()
        elif hasattr(self, "__iter__"):
            items = list(self)
        print(sep.join(str(v) for v in items))

    def visualize(self, style: str = "ascii") -> str:
        items = []
        if hasattr(self, "to_list"):
            items = self.to_list()
        elif hasattr(self, "__iter__"):
            items = list(self)
        if not items:
            return "(empty)"
        if style == "ascii":
            return " -> ".join(str(v) for v in items)
        if style == "compact":
            return f"[{', '.join(str(v) for v in items)}]"
        return " -> ".join(str(v) for v in items)
