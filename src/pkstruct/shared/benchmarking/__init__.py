"""
pkstruct.shared.benchmarking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Micro-benchmarking utilities for pkstruct structures.
"""
from __future__ import annotations

import statistics
import time
from collections.abc import Callable
from typing import Any


def timeit(
    fn: Callable[..., Any],
    *args: Any,
    iterations: int = 1000,
    **kwargs: Any,
) -> dict[str, float]:
    """Time *fn* over *iterations* calls and return statistics (in seconds).

    Args:
        fn:         The callable to benchmark.
        *args:      Positional arguments forwarded to *fn*.
        iterations: Number of repetitions.
        **kwargs:   Keyword arguments forwarded to *fn*.

    Returns:
        A dict with keys ``min``, ``max``, ``mean``, ``median``, ``stdev``,
        ``total``, and ``iterations``.
    """
    times: list[float] = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        fn(*args, **kwargs)
        times.append(time.perf_counter() - t0)

    return {
        "min": min(times),
        "max": max(times),
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.pstdev(times),
        "total": sum(times),
        "iterations": iterations,
    }


def compare(
    label_a: str,
    fn_a: Callable[..., Any],
    label_b: str,
    fn_b: Callable[..., Any],
    *,
    iterations: int = 1000,
) -> dict[str, Any]:
    """Compare two callables head-to-head.

    Args:
        label_a: Name for the first callable.
        fn_a:    First callable (no-arg).
        label_b: Name for the second callable.
        fn_b:    Second callable (no-arg).
        iterations: Repetitions per callable.

    Returns:
        Dict with per-callable stats and a ``"winner"`` key.
    """
    stats_a = timeit(fn_a, iterations=iterations)
    stats_b = timeit(fn_b, iterations=iterations)
    winner = label_a if stats_a["median"] <= stats_b["median"] else label_b
    return {
        label_a: stats_a,
        label_b: stats_b,
        "winner": winner,
        "speedup": max(stats_a["median"], stats_b["median"])
        / max(min(stats_a["median"], stats_b["median"]), 1e-12),
    }