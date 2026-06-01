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
            methods.append(
                {
                    "name": name_,
                    "signature": f"{name_}{sig}",
                    "doc": doc.split("\n\n")[0] if doc else "",
                }
            )
    _HELP_REGISTRY[name] = {
        "class": cls,
        "doc": inspect.getdoc(cls) or "",
        "methods": sorted(methods, key=lambda m: m["name"]),
    }


def _sanitize(text: str) -> str:
    return text.encode("ascii", errors="replace").decode("ascii")


def module_help(target: Any = None) -> str:
    if target is None:
        lines = ["Available structures:\n"]
        for name in sorted(_HELP_REGISTRY):
            doc = _HELP_REGISTRY[name]["doc"]
            first_line = doc.split("\n")[0] if doc else ""
            lines.append(f"  {name}")
            if first_line:
                lines[-1] += f"  - {first_line}"
        return "\n".join(lines)

    if isinstance(target, str):
        grouped: dict[str, list[str]] = {}
        for cls_name, info in sorted(_HELP_REGISTRY.items()):
            for m in info["methods"]:
                if m["name"] == target:
                    full_doc = _get_method_full_doc(info["class"], target)
                    entry = f"  {m['signature']}\n  {_sanitize(full_doc)}"
                    grouped.setdefault(cls_name, []).append(entry)
        if grouped:
            parts = [f"Method {target!r} found in:\n"]
            for cls_name in sorted(grouped):
                parts.append(f"[{cls_name}]")
                parts.extend(grouped[cls_name])
                parts.append("")
            return "\n".join(parts).rstrip()
        return f"Method {target!r} not found."

    if isinstance(target, type):
        name = target.__name__
        info = _HELP_REGISTRY.get(name)
        if info is None:
            _register(target)
            info = _HELP_REGISTRY.get(name)
        if info is None:
            return f"No help available for {name}."
        lines = [f"{name}\n{'=' * len(name)}\n"]
        doc = info["doc"]
        if doc:
            lines.append(_sanitize(textwrap.dedent(doc).strip()))
            lines.append("")
        lines.append("Methods:")
        for m in info["methods"]:
            lines.append(f"  {m['signature']}")
            if m["doc"]:
                lines.append(f"    {_sanitize(m['doc'])}")
        return "\n".join(lines)

    return ""


def _get_method_full_doc(cls: type, method_name: str) -> str:
    for cls_ in cls.__mro__:
        if method_name in cls_.__dict__:
            fn = cls_.__dict__[method_name]
            return inspect.getdoc(fn) or ""
    return ""


class HelpMixin:
    def help(self, target: str | None = None) -> str:
        if target is None:
            return module_help(type(self))
        if isinstance(target, str):
            return module_help(target)
        return module_help(target)
