"""
pkstruct.trees.visualization.tree_printer
==========================================
High-level tree visualizer that dispatches to AsciiRenderer based on tree type.

Provides a unified ``TreeVisualizer`` class with ``visualize()`` and
``debug_view()`` methods, mirroring the architecture of
``pkstruct.linear.visualization.linked_list_visualizer``.
"""

from __future__ import annotations

from typing import Any

from .ascii_renderer import AsciiRenderer


class TreeVisualizer:
    """Provides ASCII visualization and debug views for any pkstruct tree."""

    # Lazy imports to avoid circular dependencies at module load time.
    @staticmethod
    def _tree_types() -> tuple[type, ...]:
        from pkstruct.trees.avl import AVLTree
        from pkstruct.trees.bst import BinarySearchTree
        from pkstruct.trees.interval_tree import IntervalTree
        from pkstruct.trees.red_black import RedBlackTree

        return (BinarySearchTree, AVLTree, RedBlackTree, IntervalTree)

    def visualize(
        self,
        tree_instance: Any,
        style: str = "ascii",
        key_repr: Any = None,
    ) -> str:
        """
        Return a string representation of *tree_instance*.

        Parameters
        ----------
        tree_instance:
            A supported tree instance (BST, AVL, RedBlack, IntervalTree).
        style:
            Rendering style.  One of ``"ascii"``, ``"compact"``, or
            ``"levels"``.  Defaults to ``"ascii"``.
        key_repr:
            Optional callable to convert a node's key to a string.
            Defaults to ``str``.

        Returns
        -------
        str
            ASCII art string describing the tree.

        Raises
        ------
        TypeError
            If *tree_instance* is not a recognised tree type.
        ValueError
            If *style* is not supported.
        """
        if key_repr is None:
            key_repr = str

        styles = {"ascii", "compact", "levels"}
        if style not in styles:
            raise ValueError(
                f"Unsupported visualisation style {style!r}. "
                f"Use one of: {sorted(styles)}."
            )

        tree_types = self._tree_types()
        if not isinstance(tree_instance, tree_types):
            raise TypeError(
                f"Unsupported tree type: {type(tree_instance).__name__}. "
                f"Expected one of: {[t.__name__ for t in tree_types]}."
            )

        root = getattr(tree_instance, "_root", None)

        if style == "ascii":
            return AsciiRenderer.render(root, key_repr=key_repr)
        if style == "compact":
            return AsciiRenderer.render_compact(root, key_repr=key_repr)
        return AsciiRenderer.render_levels(root, key_repr=key_repr)

    def debug_view(self, tree_instance: Any) -> dict[str, Any]:
        """
        Return a diagnostic dictionary for *tree_instance*.

        The returned dict always contains:

            - ``type``: class name string
            - ``size``: integer node count
            - ``height``: integer tree height
            - ``is_empty``: boolean
            - ``is_valid``: boolean (calls the tree's ``validate()``)
            - ``keys``: list of all keys in in-order

        Parameters
        ----------
        tree_instance:
            Any supported tree instance.

        Returns
        -------
        dict
            Dictionary with debugging information.

        Raises
        ------
        TypeError
            If *tree_instance* is not a recognised tree type.
        """
        tree_types = self._tree_types()
        if not isinstance(tree_instance, tree_types):
            raise TypeError(
                f"Unsupported tree type: {type(tree_instance).__name__}."
            )

        return {
            "type": type(tree_instance).__name__,
            "size": tree_instance.size(),
            "height": tree_instance.height(),
            "is_empty": tree_instance.is_empty(),
            "is_valid": tree_instance.validate(),
            "keys": list(tree_instance),
        }
