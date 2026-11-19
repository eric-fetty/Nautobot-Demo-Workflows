#!/usr/bin/env python3
"""Check scripts/lib/params.py without Nautobot. Step parameters arrive as rendered text."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.params import as_bool, as_list, as_text  # noqa: E402

assert as_bool("False") is False and as_bool("false") is False and as_bool(False) is False
assert as_bool("True") is True and as_bool(True) is True
assert as_bool("None") is False and as_bool("", default=True) is True and as_bool(None, default=True) is True
assert as_list("['a', 'b']") == ["a", "b"] and as_list("[]") == [] and as_list("None") == [] and as_list(None) == []
assert as_list("[{'vid': 210, 'name': 'users-210'}]") == [{"vid": 210, "name": "users-210"}]
assert as_list("Ethernet1/49\nEthernet1/50") == ["Ethernet1/49", "Ethernet1/50"]
assert as_list(["x"]) == ["x"]
assert as_text("None") == "" and as_text(" core ") == "core" and as_text(None) == ""
print("params helpers OK")
