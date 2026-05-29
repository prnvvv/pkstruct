"""
pkstruct.trees.utils.complexity_helpers
========================================
Benchmarking utilities for pkstruct tree classes.

All functions use only the standard library.  They operate on tree instances
duck-typed through a minimal public API (insert, search, delete, size, etc.)
so they work with any tree class supported by ``pkstruct.trees``.
"""

from __future__ import annotations

import time
from typing import Any, Callable


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _timeit(fn: Callable, *args: Any, **kwargs: Any) -> float:
    """Run *fn* once and return elapsed seconds."""
    start = time.perf_counter()
    fn(*args, **kwargs)
    return time.perf_counter() - start


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def measure_execution_time(
    fn: Callable,
    *args: Any,
    iterations: int = 1,
    **kwargs: Any,
) -> float:
    """
    Measure the average execution time of *fn* over *iterations* runs.

    Parameters
    ----------
    fn:
        Function to time.
    *args:
        Positional arguments forwarded to *fn*.
    iterations:
        Number of times to repeat the measurement.  Defaults to 1.
    **kwargs:
        Keyword arguments forwarded to *fn*.

    Returns
    -------
    float
        Average execution time in seconds.
    """
    total: float = 0.0
    for _ in range(iterations):
        total += _timeit(fn, *args, **kwargs)
    return total / iterations


def benchmark_insert(
    tree_class: type,
    n: int = 1000,
    value_factory: Callable[[int], Any] = lambda i: i,
) -> float:
    """
    Benchmark insertion of *n* elements into a tree.

    Parameters
    ----------
    tree_class:
        A pkstruct tree class (e.g. ``BinarySearchTree``, ``AVLTree``).
    n:
        Number of elements to insert.  Defaults to 1000.
    value_factory:
        Callable ``f(i) -> value`` that generates the i-th key (0-indexed).

    Returns
    -------
    float
        Total time in seconds for all *n* insertions.
    """
    tree = tree_class()
    start = time.perf_counter()
    for i in range(n):
        tree.insert(value_factory(i))
    return time.perf_counter() - start


def benchmark_search(
    tree_class: type,
    n: int = 1000,
    value_factory: Callable[[int], Any] = lambda i: i,
) -> tuple[float, float]:
    """
    Benchmark search (found + not-found) in a tree of size *n*.

    Parameters
    ----------
    tree_class:
        A pkstruct tree class.
    n:
        Number of elements to pre-populate and search.
    value_factory:
        Callable ``f(i) -> key``.

    Returns
    -------
    tuple[float, float]
        ``(found_time, not_found_time)`` in seconds.

        - ``found_time``: time to search for each of the *n* keys.
        - ``not_found_time``: time to search for *n* keys that are
          guaranteed absent.
    """
    tree = tree_class()
    keys = [value_factory(i) for i in range(n)]
    for k in keys:
        tree.insert(k)

    # Found searches
    start = time.perf_counter()
    for k in keys:
        tree.search(k)
    found_time = time.perf_counter() - start

    # Not-found searches
    not_found_keys = [value_factory(i + n) for i in range(n)]
    start = time.perf_counter()
    for k in not_found_keys:
        tree.search(k)
    not_found_time = time.perf_counter() - start

    return found_time, not_found_time


def benchmark_delete(
    tree_class: type,
    n: int = 1000,
    value_factory: Callable[[int], Any] = lambda i: i,
) -> float:
    """
    Benchmark deletion of *n* elements from a tree.

    Parameters
    ----------
    tree_class:
        A pkstruct tree class.
    n:
        Number of elements to insert and then delete.
    value_factory:
        Callable ``f(i) -> key``.

    Returns
    -------
    float
        Total time in seconds for all *n* deletions.
    """
    tree = tree_class()
    keys = [value_factory(i) for i in range(n)]
    for k in keys:
        tree.insert(k)

    start = time.perf_counter()
    for k in keys:
        tree.delete(k)
    return time.perf_counter() - start


def compare_operations(
    tree_classes: list[type],
    sizes: list[int] | None = None,
) -> dict[str, Any]:
    """
    Compare insert / search / delete performance across multiple tree classes.

    Parameters
    ----------
    tree_classes:
        List of tree classes to benchmark.
    sizes:
        List of element counts to test.  Defaults to ``[100, 1000, 10000]``.

    Returns
    -------
    dict
        Nested dictionary::

            {
                class_name: {
                    size: {
                        "insert": float,
                        "search_found": float,
                        "search_not_found": float,
                        "delete": float,
                    },
                    ...
                },
                ...
            }

        Times are in seconds.
    """
    if sizes is None:
        sizes = [100, 1000, 10000]

    results: dict[str, Any] = {}

    for cls in tree_classes:
        name = cls.__name__
        class_results: dict[str, Any] = {}

        for n in sizes:
            insert_time = benchmark_insert(cls, n=n)
            search_found, search_not_found = benchmark_search(cls, n=n)
            delete_time = benchmark_delete(cls, n=n)

            class_results[str(n)] = {
                "insert": insert_time,
                "search_found": search_found,
                "search_not_found": search_not_found,
                "delete": delete_time,
            }

        results[name] = class_results

    return results
