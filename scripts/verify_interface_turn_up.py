"""Verify an interface turn-up. Fails when the interface does not match the plan, or when simulate_failure is on."""

PARAMETERS = {
    "interface": {"type": "object", "model": "dcim.Interface", "required": True},
    "desired": {"type": "string", "required": True, "help": "The desired settings returned by the apply step."},
    "apply": {"type": "boolean", "required": False, "default": False},
    "simulate_failure": {"type": "boolean", "required": False, "default": False},
}


def run(params):
    """Read the interface back and compare it with the plan. Raise to mark this step failed."""
    from nautobot.dcim.models import Interface

    from scripts.lib.interface_state import differences, read_interface
    from scripts.lib.params import as_bool, as_dict

    iface = Interface.objects.select_related("device", "untagged_vlan", "status").get(pk=params["interface"])
    desired = as_dict(params.get("desired"))
    apply = as_bool(params.get("apply"))

    if as_bool(params.get("simulate_failure")):
        raise RuntimeError(
            f"Verification failed on {iface.device.name} {iface.name}: the link stayed down after the change "
            "(simulated). Roll back."
        )

    if not apply:
        print("Apply was off, so there is nothing to read back. The plan passed verification.")
        return {"verified": True, "checked": sorted(desired), "applied": False}

    problems = differences(desired, read_interface(iface))
    if problems:
        raise RuntimeError(f"Verification failed on {iface.name}: " + "; ".join(problems))
    print(f"Verified {iface.device.name} {iface.name}: every planned setting is in place.")
    return {"verified": True, "checked": sorted(desired), "applied": True}
