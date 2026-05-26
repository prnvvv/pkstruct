"""Benchmarking utilities for pkstruct linked list classes."""
from __future__ import annotations

import time
import collections
from typing import Any


def _timeit(fn, *args, **kwargs) -> float:
    """Run *fn* once and return elapsed seconds."""
    start = time.perf_counter()
    fn(*args, **kwargs)
    return time.perf_counter() - start


def benchmark_operations(
    list_class: type,
    sizes: list[int] | None = None,
    n: int | None = None,
) -> dict[str, Any]:
    """Time insert / delete / get / search operations for *list_class*.

    Args:
        list_class: A pkstruct linked list class to benchmark.
        sizes: List of element counts to test against.
            Defaults to ``[100, 1000, 10000]``.
        n: If provided, sets sizes to [n].

    Returns:
        Nested dict::

            {
                size: {
                    "insert_head": float,   # seconds
                    "insert_tail": float,
                    "delete_head": float,
                    "delete_tail": float,
                    "get_middle": float,
                    "search": float,
                },
                ...
            }
    """
    if n is not None:
        sizes = [n]
    if sizes is None:
        sizes = [100, 1000, 10000]

    results: dict[str, Any] = {}

    for n in sizes:
        data = list(range(n))
        stats: dict[str, float] = {}

        # --- insert head (position 0) ---
        lst = list_class()
        start = time.perf_counter()
        for v in data:
            lst.insert(v, position=0)
        stats["insert_head"] = time.perf_counter() - start

        # --- insert tail (position=None appends) ---
        lst2 = list_class()
        start = time.perf_counter()
        for v in data:
            lst2.insert(v)  # position=None appends at tail
        stats["insert_tail"] = time.perf_counter() - start

        # Build a fresh list for deletion / access tests
        lst3 = list_class.from_list(data)

        # --- get middle ---
        mid = n // 2
        start = time.perf_counter()
        _ = lst3.get(mid)
        stats["get_middle"] = time.perf_counter() - start

        # --- search using index() ---
        target = data[mid]
        start = time.perf_counter()
        _ = lst3.index(target)
        stats["search"] = time.perf_counter() - start

        # --- delete head (position 0) ---
        lst4 = list_class.from_list(data)
        start = time.perf_counter()
        for _ in range(min(100, n)):
            lst4.delete(position=0)
        stats["delete_head"] = time.perf_counter() - start

        # --- delete tail (position = size-1) ---
        lst5 = list_class.from_list(data)
        start = time.perf_counter()
        for _ in range(min(100, n)):
            lst5.delete(position=lst5.size() - 1)
        stats["delete_tail"] = time.perf_counter() - start

        results[str(n)] = stats

    return results


def compare_with_builtins(sizes: list[int] | None = None, n: int | None = None) -> dict[str, Any]:
    """Compare all pkstruct list types against Python ``list`` and ``deque``.

    Args:
        sizes: List of element counts to test. Defaults to ``[100, 1000]``.
        n: If provided, sets sizes to [n].

    Returns:
        Nested dict::

            {
                size: {
                    class_name: {operation: seconds, ...},
                    ...
                },
                ...
            }
    """
    if n is not None:
        sizes = [n]
    if sizes is None:
        sizes = [100, 1000]

    from pkstruct.linear.linked_lists.singly_linked_list import SinglyLinkedList
    from pkstruct.linear.linked_lists.doubly_linked_list import DoublyLinkedList
    from pkstruct.linear.linked_lists.circular_linked_list import CircularLinkedList

    pkstruct_classes = [SinglyLinkedList, DoublyLinkedList, CircularLinkedList]

    results: dict[str, Any] = {}

    for n in sizes:
        data = list(range(n))
        size_results: dict[str, dict[str, float]] = {}

        # --- pkstruct classes ---
        for cls in pkstruct_classes:
            name = cls.__name__
            stats: dict[str, float] = {}

            # Insert tail
            lst = cls()
            start = time.perf_counter()
            for v in data:
                lst.insert(v)  # position=None appends
            stats["insert_tail"] = time.perf_counter() - start

            # Search using index
            start = time.perf_counter()
            _ = lst.index(data[n // 2])
            stats["search"] = time.perf_counter() - start

            # Delete head
            stats["delete_head"] = _timeit(lst.delete, position=0)

            size_results[name] = stats

        # --- Python list ---
        py_stats: dict[str, float] = {}
        py_list: list[int] = []
        
        # Insert tail
        start = time.perf_counter()
        for v in data:
            py_list.append(v)
        py_stats["insert_tail"] = time.perf_counter() - start

        # Search
        start = time.perf_counter()
        _ = (data[n // 2] in py_list)
        py_stats["search"] = time.perf_counter() - start

        # Delete head
        start = time.perf_counter()
        if py_list:
            py_list.pop(0)
        py_stats["delete_head"] = time.perf_counter() - start

        size_results["list"] = py_stats

        # --- collections.deque ---
        dq_stats: dict[str, float] = {}
        dq: collections.deque[int] = collections.deque()
        
        # Insert tail
        start = time.perf_counter()
        for v in data:
            dq.append(v)
        dq_stats["insert_tail"] = time.perf_counter() - start

        # Search (deque requires iteration, so convert to list or use 'in')
        start = time.perf_counter()
        _ = (data[n // 2] in dq)
        dq_stats["search"] = time.perf_counter() - start

        # Delete head
        start = time.perf_counter()
        if dq:
            dq.popleft()
        dq_stats["delete_head"] = time.perf_counter() - start

        size_results["deque"] = dq_stats

        results[str(n)] = size_results

    return results


def run_full_benchmark() -> dict[str, Any]:
    """Run complete benchmark suite and return results."""
    print("Running pkstruct benchmarks...")
    
    print("\n--- Benchmark: SinglyLinkedList ---")
    singly_results = benchmark_operations(
        SinglyLinkedList,
        sizes=[100, 1000, 5000]
    )
    
    print("\n--- Benchmark: DoublyLinkedList ---")
    doubly_results = benchmark_operations(
        DoublyLinkedList,
        sizes=[100, 1000, 5000]
    )
    
    print("\n--- Benchmark: CircularLinkedList ---")
    circular_results = benchmark_operations(
        CircularLinkedList,
        sizes=[100, 1000, 5000]
    )
    
    print("\n--- Comparison with Built-ins ---")
    comparison = compare_with_builtins(sizes=[100, 500])
    
    return {
        "singly": singly_results,
        "doubly": doubly_results,
        "circular": circular_results,
        "vs_builtins": comparison,
    }


if __name__ == "__main__":
    # Run benchmarks when script executed directly
    results = run_full_benchmark()
    
    # Pretty print results
    import json
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(json.dumps(results, indent=2, default=str))