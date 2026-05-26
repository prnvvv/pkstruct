"""
pkstruct.shared
~~~~~~~~~~~~~~~
Reusable infrastructure layer shared across all pkstruct modules.

Sub-packages
------------
exceptions   — Base exception hierarchy
validators   — Input validation helpers
serializers  — Safe JSON serialization
threading    — StructureLock (RLock wrapper)
debugging    — DebugTracer for step-tracing
benchmarking — timeit / compare helpers
visualization— Visualizable protocol
"""
from pkstruct.shared.benchmarking import compare, timeit
from pkstruct.shared.debugging import DebugTracer
from pkstruct.shared.exceptions import (
    ConcurrencyError,
    EmptyStructureError,
    IndexOutOfRangeError,
    InvalidRangeError,
    PkstructError,
    SerializationError,
    ValidationError,
    ValueNotFoundError,
)
from pkstruct.shared.serializers import deserialize_from_json, serialize_to_json
from pkstruct.shared.threading import StructureLock
from pkstruct.shared.validators import (
    validate_index,
    validate_non_empty_list,
    validate_non_negative_int,
    validate_positive_int,
    validate_range,
)
from pkstruct.shared.visualization import Visualizable

__all__ = [
    # exceptions
    "PkstructError",
    "ValidationError",
    "IndexOutOfRangeError",
    "ValueNotFoundError",
    "EmptyStructureError",
    "SerializationError",
    "ConcurrencyError",
    "InvalidRangeError",
    # validators
    "validate_index",
    "validate_range",
    "validate_non_empty_list",
    "validate_positive_int",
    "validate_non_negative_int",
    # serializers
    "serialize_to_json",
    "deserialize_from_json",
    # threading
    "StructureLock",
    # debugging
    "DebugTracer",
    # benchmarking
    "timeit",
    "compare",
    # visualization
    "Visualizable",
]