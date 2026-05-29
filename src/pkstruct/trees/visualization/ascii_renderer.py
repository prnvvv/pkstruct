"""
pkstruct.trees.visualization.ascii_renderer
============================================
Low-level ASCII rendering engine for binary trees.

Provides static methods that render a binary tree as a clean ASCII string.
Works with any node type that exposes ``.key``, ``.left``, and ``.right``
attributes (``TreeNode``, ``AVLNode``, ``RBNode``, ``IntervalNode``, etc.).
"""

from __future__ import annotations

from collections import deque
from typing import Any, Callable, Optional


class AsciiRenderer:
    """Static methods for rendering binary trees as ASCII art strings."""

    _SPACE: str = " "
    _FORWARD_SLASH: str = "/"
    _BACKSLASH: str = "\\"

    @staticmethod
    def render(
        root: Any,
        key_repr: Callable[[Any], str] = str,
    ) -> str:
        """
        Render a binary tree as an ASCII art string.

        The output uses slashes to connect parent nodes to their children::

                10
               /  \\
              5   15
             / \\
            3   7

        Parameters
        ----------
        root:
            Root node of the tree.  Must have ``.key``, ``.left``, and
            ``.right`` attributes.
        key_repr:
            Callable that converts a node's key to its string representation.
            Defaults to ``str``.

        Returns
        -------
        str
            ASCII art representation, or ``"(empty)"`` if *root* is *None*.
        """
        if root is None:
            return "(empty)"

        height = AsciiRenderer._height(root)
        if height == 0:
            return key_repr(root.key)

        tree_lines: list[str] = []
        level: list[Optional[Any]] = [root]
        level_num = 0

        while level and level_num <= height:
            next_level: list[Optional[Any]] = []
            for node in level:
                if node is not None:
                    next_level.append(node.left)
                    next_level.append(node.right)
                else:
                    next_level.append(None)
                    next_level.append(None)

            indent = 2 ** (height - level_num) - 1
            between = 2 ** (height - level_num + 1) - 1

            line: list[str] = []
            for node in level:
                if node is None:
                    line.append(" " * (max(1, indent + 1)))
                else:
                    rep = key_repr(node.key)
                    padding = max(0, indent - len(rep) + 1)
                    line.append(" " * padding + rep + " " * (indent - padding))

            tree_lines.append("".join(line).rstrip())

            if level_num < height:
                connector_line: list[str] = []
                for i, node in enumerate(level):
                    if node is None:
                        connector_line.append(" " * (indent + between // 2 + 1))
                    else:
                        left_char = AsciiRenderer._FORWARD_SLASH if node.left else " "
                        right_char = AsciiRenderer._BACKSLASH if node.right else " "
                        left_pad = indent - 1
                        mid_pad = between - 2
                        if left_pad < 0:
                            left_pad = 0
                        if mid_pad < 0:
                            mid_pad = 0
                        segment = (
                            " " * left_pad
                            + left_char
                            + " " * max(0, mid_pad)
                            + right_char
                            + " " * (indent)
                        )
                        connector_line.append(segment)
                tree_lines.append("".join(connector_line).rstrip())

            level = next_level
            level_num += 1

        return "\n".join(tree_lines)

    @staticmethod
    def render_compact(
        root: Any,
        key_repr: Callable[[Any], str] = str,
    ) -> str:
        """
        Render a compact single-line representation of the tree.

        Produces output like: ``10 (5 (3, 7), 15)``.

        Parameters
        ----------
        root:
            Root node of the tree.
        key_repr:
            Callable that converts a node's key to a string.

        Returns
        -------
        str
            Compact representation, or ``"(empty)"`` if *root* is *None*.
        """
        if root is None:
            return "(empty)"

        def _build(node: Optional[Any]) -> str:
            if node is None:
                return ""
            left_str = _build(node.left)
            right_str = _build(node.right)
            rep = key_repr(node.key)
            if left_str or right_str:
                parts = []
                if left_str:
                    parts.append(left_str)
                if right_str:
                    parts.append(right_str)
                return f"{rep} ({', '.join(parts)})"
            return rep

        return _build(root)

    @staticmethod
    def render_levels(
        root: Any,
        key_repr: Callable[[Any], str] = str,
    ) -> str:
        """
        Render the tree level by level, one line per level.

        Produces output like::

            Level 0: 10
            Level 1: 5 15
            Level 2: 3 7

        Parameters
        ----------
        root:
            Root node of the tree.
        key_repr:
            Callable that converts a node's key to a string.

        Returns
        -------
        str
            Level-by-level representation.
        """
        if root is None:
            return "(empty)"

        lines: list[str] = []
        queue: deque = deque([(root, 0)])
        current_level = 0
        level_nodes: list[str] = []

        while queue:
            node, level = queue.popleft()
            if level != current_level:
                lines.append(f"Level {current_level}: {' '.join(level_nodes)}")
                level_nodes = []
                current_level = level
            level_nodes.append(key_repr(node.key))
            if node.left:
                queue.append((node.left, level + 1))
            if node.right:
                queue.append((node.right, level + 1))

        if level_nodes:
            lines.append(f"Level {current_level}: {' '.join(level_nodes)}")

        return "\n".join(lines)

    @staticmethod
    def _height(node: Optional[Any]) -> int:
        """Compute the height of the tree rooted at *node*."""
        if node is None:
            return -1
        return 1 + max(
            AsciiRenderer._height(node.left),
            AsciiRenderer._height(node.right),
        )
