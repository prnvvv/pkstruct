"""
pkstruct.shared.serializers
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Safe, eval-free serialization helpers used by all pkstruct modules.
"""
from __future__ import annotations

import json
from typing import Any

from pkstruct.shared.exceptions import SerializationError


def serialize_to_json(items: list[Any]) -> str:
    """Serialize a list of items to a JSON string.

    Only JSON-safe types (str, int, float, bool, None, list, dict) are supported.
    No ``pickle``, no ``eval``.

    Args:
        items: A flat list of JSON-serializable values.

    Returns:
        A compact JSON string representation.

    Raises:
        SerializationError: If any item is not JSON-serializable.
    """
    try:
        return json.dumps({"items": items}, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise SerializationError(
            f"Cannot serialize items to JSON: {exc}"
        ) from exc


def deserialize_from_json(json_str: str) -> list[Any]:
    """Deserialize a JSON string produced by :func:`serialize_to_json`.

    Args:
        json_str: A JSON string with a top-level ``"items"`` key.

    Returns:
        A list of values.

    Raises:
        SerializationError: If the string is malformed or missing the ``"items"`` key.
    """
    if not isinstance(json_str, str):
        raise SerializationError(
            f"Expected a str for deserialization, got {type(json_str).__name__!r}."
        )
    try:
        payload = json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise SerializationError(f"Invalid JSON: {exc}") from exc

    if not isinstance(payload, dict) or "items" not in payload:
        raise SerializationError(
            "JSON payload must be an object with an 'items' key."
        )
    items = payload["items"]
    if not isinstance(items, list):
        raise SerializationError("'items' in JSON payload must be a list.")
    return items