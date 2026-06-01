from __future__ import annotations

from typing import Any


def display(ds: Any, sep: str = " ") -> None:
    items = []
    if hasattr(ds, "to_list"):
        items = ds.to_list()
    elif hasattr(ds, "__iter__"):
        items = list(ds)
    print(sep.join(str(v) for v in items))
