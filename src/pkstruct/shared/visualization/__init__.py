"""
pkstruct.shared.visualization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Base visualization protocol and colour/style constants for all pkstruct modules.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Visualizable(Protocol):
    """Protocol implemented by any pkstruct structure that supports visualization."""

    def visualize(self, style: str = "ascii") -> str:
        """Return a string representation of the structure."""
        ...

    def debug(self) -> dict[str, object]:
        """Return a dictionary of internal debug metadata."""
        ...