#!/usr/bin/env python3
"""Check examples 11-13 without Nautobot.

1. Unit tests for the plain-Python helpers the new scripts use.
2. Branch tests: walk each workflow's steps the way the engine does (Before steps
   stop at the first failure, Main and After steps keep going), render every
   ``when`` with Jinja against fake step results, and check which steps run,
   which are skipped, and the run's final status.
"""

import importlib.util
import sys
from pathlib import Path

import yaml
from jinja2 import Undefined
from jinja2.sandbox import ImmutableSandboxedEnvironment

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.lib.device_state import compare_baselines, simulate_drift  # noqa: E402
from scripts.lib.interface_state import differences  # noqa: E402
from scripts.lib.params import as_dict, as_int, as_list  # noqa: E402


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --- helpers -------------------------------------------------------------------------------------------------
snapshot = {"description": "", "enabled": False, "mode": "", "untagged_vlan": None, "tagged_vlans": [], "status": "Active"}
assert as_dict(str(snapshot)) == snapshot, "a rendered return_value must parse back to the same dict"
assert as_dict('{"drift": 0, "ok": true}') == {"drift": 0, "ok": True}
assert as_dict("None") == {} and as_dict(None) == {} and as_dict({"a": 1}) == {"a": 1}
assert as_int("110") == 110 and as_int("") is None and as_int(" 7 ") == 7
try:
    as_dict("['not', 'a', 'dict']")
    raise AssertionError("as_dict should refuse a list")
except ValueError:
    pass

desired = load_script("apply_interface_turn_up").desired_settings("110", "user access floor 3")
assert desired["mode"] == "access" and desired["untagged_vlan"] == 110 and desired["enabled"] is True
assert desired["status"] == "Planned"
actual = dict(desired, tagged_vlans=[])
assert differences(desired, actual) == []
assert differences(desired, dict(actual, enabled=False)) == ["enabled: expected True, found False"]
assert differences({"tagged_vlans": [20, 10]}, {"tagged_vlans": [10, 20]}) == []
assert differences({"description": "x"}, {"description": "x", "mode": "tagged"}) == [], "only expected fields count"

baseline = {
    "interfaces_enabled": 4,
    "enabled_interfaces": ["Ethernet1/1", "Ethernet1/2", "Ethernet1/48", "Management1"],
    "interfaces_cabled": 1,
    "vlans": [110, 120],
}
assert compare_baselines(baseline, dict(baseline)) == []
drifted = simulate_drift(baseline)
assert "Ethernet1/48" not in drifted["enabled_interfaces"] and "Management1" in drifted["enabled_interfaces"]
found = compare_baselines(baseline, drifted)
assert len(found) == 4, found
assert "interfaces no longer up: Ethernet1/48" in found and "VLANs missing: 120" in found
assert compare_baselines({"vlans": [10]}, {"vlans": [10, 20]}) == ["VLANs added: 20"]
assert simulate_drift(baseline) is not baseline and baseline["interfaces_enabled"] == 4

note = load_script("record_change_note").build_note("Needs backout.", as_list("['a down', 'b missing']"))
assert note == "Needs backout.\n- a down\n- b missing"
print("helpers OK")


# --- branch tests --------------------------------------------------------------------------------------------
INCLUDE = "{% include"
env = ImmutableSandboxedEnvironment(undefined=Undefined)


def load_workflow(name):
    text = (ROOT / "workflows" / name).read_text(encoding="utf-8")
    assert INCLUDE not in text, "branch tests do not expand includes"
    return yaml.safe_load(text)


def walk(workflow, inputs, outcomes):
    """Return ({step: status}, run_status). outcomes maps a step name to its result when it runs."""
    results, statuses = {}, {}
    ctx = {"inputs": inputs, "results": results}
    run_failed = False
    for phase in ("pre_actions", "actions", "post_actions"):
        phase_failed = False
        for action in workflow.get(phase) or []:
            name = action["name"]
            should = env.from_string(action.get("when") or "true").render(ctx).strip().lower()
            if should not in ("true", "1", "yes", "on", "y"):
                results[name] = {"status": "skipped", "return_value": None}
            else:
                # The engine renders "with" only for steps that run, so a bad reference fails there.
                for value in (action.get("with") or {}).values():
                    env.from_string(str(value)).render(ctx)
                results[name] = outcomes[name]
            statuses[name] = results[name]["status"]
            if results[name]["status"] == "failed":
                phase_failed = True
                if phase == "pre_actions":
                    return statuses, "failed"
        if phase == "actions":
            run_failed = phase_failed
    return statuses, "failed" if run_failed else "success"


def ok(value=None):
    return {"status": "success", "return_value": value}


def failed(error):
    return {"status": "failed", "return_value": None, "error": error}


snap = ok(snapshot)
applied = ok({"desired": desired})
wf11 = load_workflow("11-turn-up-with-rollback.yaml")
inputs11 = {"interface": {"id": "i1", "name": "Ethernet1/2"}, "vlan_id": 110, "description": "x", "apply": True}
steps, status = walk(
    wf11, inputs11, {"snapshot": snap, "apply_change": applied, "verify": ok({"verified": True}), "close_out": ok()}
)
assert steps == {
    "snapshot": "success", "apply_change": "success", "verify": "success", "rollback": "skipped", "close_out": "success"
}, steps
assert status == "success"
steps, status = walk(
    wf11, inputs11, {"snapshot": snap, "apply_change": applied, "verify": failed("link down"), "rollback": ok()}
)
assert steps["rollback"] == "success" and steps["close_out"] == "skipped", steps
assert status == "failed", "a recovered run is still failed: the change did not land"
steps, status = walk(wf11, inputs11, {"snapshot": snap, "apply_change": failed("no VLAN"), "rollback": ok()})
assert steps["verify"] == "skipped" and steps["rollback"] == "success" and steps["close_out"] == "skipped", steps
steps, status = walk(wf11, inputs11, {"snapshot": failed("gone")})
assert set(steps.values()) == {"failed", "skipped"} and steps["rollback"] == "skipped", "no snapshot, no rollback"

wf12 = load_workflow("12-next-free-ip-with-fallback.yaml")
inputs12 = {
    "device": {"id": "d1"}, "interface": {"id": "i1"}, "preferred_prefix": {"id": "p1"},
    "fallback_prefix": {"id": "p2"}, "simulate_preferred_full": False, "apply": False,
}
steps, status = walk(wf12, inputs12, {"reserve_primary": ok({"address": "10.20.255.1/29"}), "assign_ip": ok()})
assert steps == {"reserve_primary": "success", "reserve_fallback": "skipped", "assign_ip": "success"}, steps
assert status == "success"
rendered = env.from_string(wf12["actions"][2]["with"]["address"]).render(
    {"results": {"reserve_primary": failed("full"), "reserve_fallback": ok({"address": "10.20.254.7/24"})}}
)
assert rendered == "10.20.254.7/24", rendered
steps, status = walk(
    wf12, inputs12,
    {"reserve_primary": failed("full"), "reserve_fallback": ok({"address": "10.20.254.7/24"}), "assign_ip": ok()},
)
assert steps == {"reserve_primary": "failed", "reserve_fallback": "success", "assign_ip": "success"}, steps
assert status == "failed"
steps, status = walk(wf12, inputs12, {"reserve_primary": failed("full"), "reserve_fallback": failed("full too")})
assert steps["assign_ip"] == "skipped", steps

wf13 = load_workflow("13-upgrade-with-pre-post-checks.yaml")
inputs13 = {"device": {"id": "d1"}, "target_version": "4.32.2F", "simulate_drift": False, "apply": False}
base = ok(baseline)
steps, status = walk(
    wf13, inputs13,
    {"precheck": base, "upgrade": ok(), "postcheck": ok({"drift": 0, "differences": []}), "close_success": ok()},
)
assert steps["close_success"] == "success" and steps["open_backout"] == "skipped", steps
assert status == "success"
steps, status = walk(
    wf13, inputs13,
    {"precheck": base, "upgrade": ok(), "postcheck": ok({"drift": 2, "differences": ["a", "b"]}), "open_backout": ok()},
)
assert steps["close_success"] == "skipped" and steps["open_backout"] == "success", steps
assert status == "success", "drift is a value the post-check returns, not a failed step"
steps, status = walk(wf13, inputs13, {"precheck": failed("device not found")})
assert steps == {"precheck": "failed"} and status == "failed", "a failed Before step stops the run"
print("branch tests OK")
