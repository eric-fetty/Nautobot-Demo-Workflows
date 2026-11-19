"""Compare a device with its pre-change baseline. Succeeds either way and reports the drift in its return value."""

PARAMETERS = {
    "device": {"type": "object", "model": "dcim.Device", "required": True},
    "baseline": {"type": "string", "required": True, "help": "results.precheck.return_value from the precheck step."},
    "simulate_drift": {"type": "boolean", "required": False, "default": False},
}


def run(params):
    """Return drift (a count) and differences (a list). Later steps branch on these values, not on status."""
    from nautobot.dcim.models import Device

    from scripts.lib.device_state import collect_baseline, compare_baselines, simulate_drift
    from scripts.lib.params import as_bool, as_dict

    device = Device.objects.get(pk=params["device"])
    before = as_dict(params.get("baseline"))
    after = collect_baseline(device)
    simulated = as_bool(params.get("simulate_drift"))
    if simulated:
        after = simulate_drift(before)
        print("Simulating drift: one uplink stayed down, a neighbor was lost, and a VLAN went missing.")
    differences = compare_baselines(before, after)
    if differences:
        print(f"Post-check found {len(differences)} difference(s) on {device.name}: " + "; ".join(differences))
    else:
        print(f"Post-check matches the baseline on {device.name}.")
    return {"device": device.name, "drift": len(differences), "differences": differences, "simulated": simulated}
