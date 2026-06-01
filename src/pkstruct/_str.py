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
        return " ".join(str(v) for v in items)
