"""Turn rendered step parameters back into Python values.

The Workflow Engine renders every ``with:`` value through Jinja, so a script
receives text: ``"False"``, ``"['id-1', 'id-2']"``, or ``"None"``. A plain
``bool("False")`` is True, so always read flags and lists through these helpers.
"""

import ast

_TRUE = {"true", "1", "yes", "y", "on"}
_EMPTY = {"", "none", "null"}


def as_bool(value, default=False):
    """Return True only for a real True or a true-looking string such as "True"."""
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in _EMPTY:
        return default
    return text in _TRUE


def as_list(value):
    """Return a list from a list, a rendered Python or JSON list, or one item per line."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    text = str(value).strip()
    if text.lower() in _EMPTY:
        return []
    try:
        parsed = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return [line.strip() for line in text.splitlines() if line.strip()]
    if isinstance(parsed, (list, tuple)):
        return list(parsed)
    return [parsed]


def as_text(value, default=""):
    """Return stripped text, treating None and "None" as empty."""
    if value is None:
        return default
    text = str(value).strip()
    return default if text.lower() in ("none", "null") else text


def as_dict(value):
    """Return a dict from a dict or a rendered Python or JSON mapping, such as an earlier step's return_value."""
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    text = str(value).strip()
    if text.lower() in _EMPTY:
        return {}
    try:
        parsed = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        import json

        try:
            parsed = json.loads(text)
        except ValueError as exc:
            raise ValueError(f"Expected a mapping, got: {text[:80]!r}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"Expected a mapping, got {type(parsed).__name__}")
    return parsed


def as_int(value, default=None):
    """Return an int from an int or rendered text, or default for empty values."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    text = as_text(value)
    if not text:
        return default
    return int(float(text))
