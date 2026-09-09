"""Validated, atomic appearance preferences, separate from clipboard data."""

import json
import os
from pathlib import Path
import tempfile

DEFAULTS = {"theme": "system", "backdrop": "acrylic", "panel_density": 80}


def normalize(values):
    values = values if isinstance(values, dict) else {}
    result = DEFAULTS.copy()
    for key, choices in {
        "theme": ("system", "light", "dark"),
        "backdrop": ("off", "mica", "acrylic"),
    }.items():
        if values.get(key) in choices:
            result[key] = values[key]
    density = values.get("panel_density")
    if type(density) is int:
        result["panel_density"] = max(50, min(100, density))
    return result


class AppearanceSettings:
    def __init__(self, path=None):
        base = Path(os.environ.get("APPDATA", Path.home() / ".config"))
        self.path = Path(path) if path else base / "CopyAndPaste" / "appearance.json"
        try:
            self.values = normalize(json.loads(self.path.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            self.values = DEFAULTS.copy()

    def save(self, values):
        values = normalize(values)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.path.parent, delete=False
            ) as handle:
                temporary = handle.name
                json.dump(values, handle, ensure_ascii=False, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
        self.values = values
