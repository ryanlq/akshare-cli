"""Favorites management for akshare functions."""

from __future__ import annotations

import json
from pathlib import Path

FAVORITES_DIR = Path.home() / ".config" / "akcli"
FAVORITES_FILE = FAVORITES_DIR / "favorites.json"


def _ensure_file() -> None:
    FAVORITES_DIR.mkdir(parents=True, exist_ok=True)
    if not FAVORITES_FILE.exists():
        FAVORITES_FILE.write_text("{}", encoding="utf-8")


def load_favorites() -> dict[str, str]:
    """Load favorites. Returns {func_name: note}."""
    _ensure_file()
    try:
        return json.loads(FAVORITES_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_favorites(favs: dict[str, str]) -> None:
    _ensure_file()
    FAVORITES_FILE.write_text(
        json.dumps(favs, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def add_favorite(func_name: str, note: str = "") -> None:
    favs = load_favorites()
    favs[func_name] = note
    save_favorites(favs)


def remove_favorite(func_name: str) -> bool:
    favs = load_favorites()
    if func_name in favs:
        del favs[func_name]
        save_favorites(favs)
        return True
    return False


def is_favorite(func_name: str) -> bool:
    return func_name in load_favorites()
