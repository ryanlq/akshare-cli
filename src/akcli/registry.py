"""Function introspection registry for akshare."""

from __future__ import annotations

import inspect
import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from akcli.categories import get_category, get_category_label, get_category_tier, get_category_desc

CACHE_DIR = Path.home() / ".akcli"
CACHE_FILE = CACHE_DIR / "registry_cache.json"

# Functions to skip (non-data utility functions)
SKIP_FUNCTIONS = {
    "set_token", "get_token", "pro_api",
}


@dataclass
class ParamInfo:
    name: str
    type_hint: str
    default: Optional[str] = None
    has_default: bool = False
    description: str = ""
    choices: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> ParamInfo:
        return cls(**d)


@dataclass
class FunctionInfo:
    name: str
    category: str
    category_label: str
    description: str
    params: list[ParamInfo]
    docstring: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "category_label": self.category_label,
            "description": self.description,
            "params": [p.to_dict() for p in self.params],
            "docstring": self.docstring,
        }

    @classmethod
    def from_dict(cls, d: dict) -> FunctionInfo:
        d["params"] = [ParamInfo.from_dict(p) for p in d.get("params", [])]
        return cls(**d)


def _parse_param_docs(docstring: str) -> dict[str, str]:
    """Parse :param name: description from docstring."""
    result = {}
    pattern = re.compile(r":param\s+(\w+)\s*:\s*(.+?)(?=\n\s*:param|\n\s*:type|\n\s*:return|\n\s*:rtype|$)", re.DOTALL)
    for m in pattern.finditer(docstring):
        name = m.group(1)
        desc = m.group(2).strip()
        result[name] = desc
    return result


def _extract_choices(text: str) -> list[str]:
    """Extract choices from patterns like: choice of {'daily', 'weekly', 'monthly'}."""
    m = re.search(r"choice\s+of\s*\{([^}]+)\}", text)
    if m:
        items = re.findall(r"'([^']*)'", m.group(1))
        if items:
            return items
        items = re.findall(r'"([^"]*)"', m.group(1))
        if items:
            return items
    return []


def _type_hint_str(annotation: Any) -> str:
    """Convert type annotation to string."""
    if annotation is inspect.Parameter.empty:
        return "str"
    origin = getattr(annotation, "__origin__", None)
    if origin is not None:
        return str(annotation)
    if isinstance(annotation, type):
        return annotation.__name__
    return str(annotation)


def _default_str(value: Any) -> str | None:
    """Convert default value to string representation."""
    if value is inspect.Parameter.empty:
        return None
    if value is None:
        return "None"
    return repr(value)


def _analyze_function(name: str, func: callable) -> FunctionInfo | None:
    """Analyze a single akshare function."""
    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        return None

    doc = inspect.getdoc(func) or ""
    param_docs = _parse_param_docs(doc)
    cat = get_category(name)

    params = []
    for pname, param in sig.parameters.items():
        if pname in ("args", "kwargs"):
            continue
        desc = param_docs.get(pname, "")
        params.append(ParamInfo(
            name=pname,
            type_hint=_type_hint_str(param.annotation),
            default=_default_str(param.default),
            has_default=param.default is not inspect.Parameter.empty,
            description=desc,
            choices=_extract_choices(desc),
        ))

    description = doc.split("\n")[0].strip() if doc else ""

    return FunctionInfo(
        name=name,
        category=cat,
        category_label=get_category_label(cat),
        description=description,
        params=params,
        docstring=doc,
    )


class FunctionRegistry:
    """Registry of all akshare functions with metadata."""

    def __init__(self):
        self._functions: dict[str, FunctionInfo] = {}
        self._categories: dict[str, list[str]] = {}

    @property
    def functions(self) -> dict[str, FunctionInfo]:
        return self._functions

    @property
    def categories(self) -> dict[str, list[str]]:
        return self._categories

    def get(self, name: str) -> FunctionInfo | None:
        return self._functions.get(name)

    def list_functions(
        self,
        category: str | None = None,
        search: str | None = None,
        max_tier: int = 5,
        categories: list[str] | None = None,
    ) -> list[FunctionInfo]:
        results = list(self._functions.values())
        if categories:
            results = [f for f in results if f.category in categories]
        elif category:
            results = [f for f in results if f.category == category]
        else:
            results = [f for f in results if get_category_tier(f.category) <= max_tier]
        if search:
            search_lower = search.lower()
            results = [f for f in results if search_lower in f.name.lower() or search_lower in f.description.lower()]
        return results

    def list_categories(self, max_tier: int = 5) -> list[tuple[str, str, str, int, int]]:
        """Return (category, label, desc, count, tier) sorted by tier then count."""
        result = []
        for cat, funcs in self._categories.items():
            tier = get_category_tier(cat)
            if tier <= max_tier:
                result.append((cat, get_category_label(cat), get_category_desc(cat), len(funcs), tier))
        result.sort(key=lambda x: (x[4], -x[3]))
        return result

    def load(self) -> bool:
        """Load registry. Try cache first, fall back to introspection."""
        if self._load_cache():
            return True
        return self._introspect()

    def _load_cache(self) -> bool:
        """Load from JSON cache file."""
        if not CACHE_FILE.exists():
            return False
        try:
            with open(CACHE_FILE) as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return False
            self._functions = {k: FunctionInfo.from_dict(v) for k, v in data.items()}
            self._rebuild_categories()
            return bool(self._functions)
        except (json.JSONDecodeError, KeyError, TypeError):
            return False

    def save_cache(self):
        """Save registry to JSON cache file."""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {k: v.to_dict() for k, v in self._functions.items()}
        tmp = CACHE_FILE.with_suffix(".tmp")
        with open(tmp, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(CACHE_FILE)

    def _introspect(self) -> bool:
        """Introspect akshare module to build registry."""
        try:
            import akshare as ak
        except ImportError:
            return False

        for name in dir(ak):
            if name.startswith("_") or name in SKIP_FUNCTIONS:
                continue
            obj = getattr(ak, name, None)
            if not callable(obj):
                continue
            info = _analyze_function(name, obj)
            if info is None:
                continue
            self._functions[name] = info

        self._rebuild_categories()
        if self._functions:
            self.save_cache()
        return bool(self._functions)

    def _rebuild_categories(self):
        """Rebuild category index from functions."""
        self._categories = {}
        for info in self._functions.values():
            self._categories.setdefault(info.category, []).append(info.name)

    def clear_cache(self):
        """Delete the cache file."""
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
