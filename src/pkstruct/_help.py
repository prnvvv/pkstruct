from __future__ import annotations

import inspect
import textwrap
from typing import Any

_HELP_REGISTRY: dict[str, dict[str, Any]] = {}


def _register(cls: type) -> None:
    name = cls.__name__
    methods = []
    for name_ in dir(cls):
        if name_.startswith("_"):
            continue
        obj = getattr(cls, name_)
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            sig = inspect.signature(obj)
            doc = inspect.getdoc(obj) or ""
            first_line = doc.split("\n\n")[0] if doc else ""
            methods.append(
                {
                    "name": name_,
                    "signature": f"{name_}{sig}",
                    "doc": doc,
                    "summary": first_line,
                }
            )
    _HELP_REGISTRY[name] = {
        "class": cls,
        "doc": inspect.getdoc(cls) or "",
        "methods": sorted(methods, key=lambda m: m["name"]),
    }


def _sanitize(text: str) -> str:
    return text.encode("ascii", errors="replace").decode("ascii")


def _structure_list() -> str:
    lines = ["─── Available Structures ───\n"]
    for name in sorted(_HELP_REGISTRY):
        lines.append(f"  {name}")
    return "\n".join(lines)


def _structure_help(cls: type) -> str:
    name = cls.__name__
    info = _HELP_REGISTRY.get(name)
    if info is None:
        _register(cls)
        info = _HELP_REGISTRY.get(name)
    if info is None:
        return f"No help available for {name}."

    lines = [f"\n{name}\n{'=' * len(name)}\n"]
    doc = info["doc"]
    if doc:
        lines.append(_sanitize(textwrap.dedent(doc).strip()))
        lines.append("")
    lines.append("Methods:")
    for m in info["methods"]:
        lines.append(f"  {m['signature']}")
        if m["summary"]:
            lines.append(f"    {_sanitize(m['summary'])}")
    return "\n".join(lines)


def _method_help(method_name: str) -> str:
    grouped: dict[str, list[str]] = {}
    for cls_name, info in sorted(_HELP_REGISTRY.items()):
        for m in info["methods"]:
            if m["name"] == method_name:
                full_doc = _get_method_full_doc(info["class"], method_name)
                entry = f"  {m['signature']}\n  {_sanitize(full_doc)}"
                grouped.setdefault(cls_name, []).append(entry)
    if grouped:
        parts = [f"Method {method_name!r} found in:\n"]
        for cls_name in sorted(grouped):
            parts.append(f"[{cls_name}]")
            parts.extend(grouped[cls_name])
            parts.append("")
        return "\n".join(parts).rstrip()
    return f"Method {method_name!r} not found."


def module_help(target: Any = None) -> str:
    if target is None:
        return _structure_list()
    if isinstance(target, str):
        return _method_help(target)
    if isinstance(target, type):
        return _structure_help(target)
    raise ValueError(
        f"Invalid help target: {target!r}. Expected a string (method name), "
        f"a type (class), or None."
    )


def _get_method_full_doc(cls: type, method_name: str) -> str:
    for cls_ in cls.__mro__:
        if method_name in cls_.__dict__:
            fn = cls_.__dict__[method_name]
            return inspect.getdoc(fn) or ""
    return ""


class HelpMixin:
    def help(self, target: str | type | None = None) -> str:
        if target is None:
            return module_help(None)
        if isinstance(target, str):
            return module_help(target)
        if isinstance(target, type):
            return module_help(target)
        return module_help(type(target))
