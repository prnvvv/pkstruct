from __future__ import annotations

from typing import Any


class TreeShortcutsMixin:
    def root(self) -> Any:
        """Return the root node of the tree, or *None* if empty."""
        return self._root

    def parent(self, key: Any) -> Any | None:
        """Return the parent node of the node identified by *key*, or *None*."""
        node = self._find_key_node(key)
        if node is None:
            return None
        return node.parent

    def children(self, key: Any) -> list[Any]:
        """Return a list of child nodes for the node identified by *key*."""
        node = self._find_key_node(key)
        if node is None:
            return []
        result = []
        if hasattr(node, "left") and node.left is not None:
            result.append(node.left)
        if hasattr(node, "right") and node.right is not None:
            result.append(node.right)
        if hasattr(node, "children"):
            result.extend(node.children)
        return result

    def left(self, key: Any) -> Any | None:
        """Return the left child of the node identified by *key*, or *None*."""
        node = self._find_key_node(key)
        if node is None:
            return None
        return getattr(node, "left", None)

    def right(self, key: Any) -> Any | None:
        """Return the right child of the node identified by *key*, or *None*."""
        node = self._find_key_node(key)
        if node is None:
            return None
        return getattr(node, "right", None)

    def sibling(self, key: Any) -> Any | None:
        """Return the sibling node of the node identified by *key*, or *None*."""
        node = self._find_key_node(key)
        if node is None:
            return None
        if hasattr(node, "sibling"):
            return node.sibling()
        if node.parent is None:
            return None
        if hasattr(node.parent, "left") and node.parent.left is node:
            return getattr(node.parent, "right", None)
        if hasattr(node.parent, "right") and node.parent.right is node:
            return getattr(node.parent, "left", None)
        return None

    def _find_key_node(self, key: Any) -> Any | None:
        if hasattr(self, "_find"):
            return self._find(self._root, key)
        if hasattr(self, "search"):
            return self._find_node_by_key(key)
        return None

    def _find_node_by_key(self, key: Any) -> Any | None:
        if self._root is None:
            return None
        is_nil = getattr(self, "_is_nil", lambda n: False)
        if is_nil(self._root):
            return None
        stack = [self._root]
        while stack:
            node = stack.pop()
            if node is None or is_nil(node):
                continue
            if hasattr(node, "keys"):
                if key in node.keys:
                    return node
                for child in node.children:
                    stack.append(child)
            elif hasattr(node, "key"):
                if node.key == key:
                    return node
                if hasattr(node, "left"):
                    stack.append(node.left)
                if hasattr(node, "right"):
                    stack.append(node.right)
        return None
