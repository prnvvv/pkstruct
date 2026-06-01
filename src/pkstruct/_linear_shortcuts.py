from __future__ import annotations

from typing import Any


class LinearShortcutsMixin:
    def next(self, value: Any) -> Any | None:
        """Return the element that follows *value* in the sequence, or *None*."""
        lst = self._get_items()
        for i, v in enumerate(lst):
            if v == value and i + 1 < len(lst):
                return lst[i + 1]
        return None

    def prev(self, value: Any) -> Any | None:
        """Return the element that precedes *value* in the sequence, or *None*."""
        lst = self._get_items()
        for i, v in enumerate(lst):
            if v == value and i - 1 >= 0:
                return lst[i - 1]
        return None

    def _get_items(self) -> list[Any]:
        if hasattr(self, "to_list"):
            return self.to_list()
        if hasattr(self, "__iter__"):
            return list(self)
        return []
