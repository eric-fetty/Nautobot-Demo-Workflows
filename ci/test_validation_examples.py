#!/usr/bin/env python3
"""Check the validation rules in examples 02 and 06 the way the server does (re.search with flags)."""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FLAGS = {"IGNORECASE": re.IGNORECASE, "MULTILINE": re.MULTILINE, "DOTALL": re.DOTALL, "VERBOSE": re.VERBOSE}


def load(name):
    return yaml.safe_load((ROOT / "workflows" / name).read_text(encoding="utf-8"))


def find(items, key):
    return next(item for item in items if item.get("key") == key)


def first_failure(rules, value):
    """The message the launch form shows: the first rule the value does not match, or None."""
    for rule in rules:
        flags = 0
        for name in rule.get("flags") or []:
            flags |= FLAGS[name]
        if re.search(rule["regex"], value, flags) is None:
            return rule.get("message")
    return None


def check(rules, good, bad):
    for value in good:
        assert first_failure(rules, value) is None, f"{value!r} should pass"
    for value, message_part in bad.items():
        message = first_failure(rules, value)
        assert message and message_part in message, f"{value!r} should fail with {message_part!r}, got {message!r}"


reserve = load("02-reserve-vlan-id.yaml")
check(
    find(reserve["inputs"], "name")["validators"],
    ["users-floor-2", "voice", "mgmt-10"],
    {"users floor 2": "1 to 32", "Users_Floor_2": "lowercase", "a" * 33: "1 to 32"},
)
check(
    find(reserve["inputs"], "change_ticket")["validators"],
    ["CHG0012345", "chg0012345"],
    {"CHG12": "change number", "INC0012345": "change number"},
)

vlans = load("06-add-vlans.yaml")
name_column = find(find(vlans["inputs"], "vlans")["columns"], "name")
check(name_column["validators"], ["users-floor-2"], {"Users Floor 2": "1 to 32", "Users.Floor": "lowercase"})
check(
    find(vlans["inputs"], "trunk_ports")["validators"],
    ["Ethernet1/49", "ethernet1/50", "Port-Channel10"],
    {"Ethernet 1/49": "interface name", "Vlan10": "Ethernet or Port-Channel", "1/49": "interface name"},
)
print("validation examples OK")
sys.exit(0)
