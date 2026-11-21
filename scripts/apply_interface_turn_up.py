"""Plan an access-port turn-up, and apply it in Nautobot only when apply is true.

When applied, the interface is left in Planned status until a verify step passes.
"""

PARAMETERS = {
    "interface": {"type": "object", "model": "dcim.Interface", "required": True},
    "vlan_id": {"type": "integer", "required": True, "help": "Access VLAN. It must exist at the device's location."},
    "description": {"type": "string", "required": True},
    "apply": {"type": "boolean", "required": False, "default": False},
}


def desired_settings(vlan_id, description):
    """Return the interface settings this turn-up wants. Plain Python so CI can test it."""
    return {
        "description": description,
        "enabled": True,
        "mode": "access",
        "untagged_vlan": int(vlan_id),
        "tagged_vlans": [],
        "status": "Planned",
    }


def run(params):
    """Check the VLAN exists, then set the interface (apply on) or report the plan (apply off)."""
    from nautobot.dcim.models import Interface

    from scripts.lib.interface_state import find_vlan, write_interface
    from scripts.lib.params import as_bool, as_int, as_text

    iface = Interface.objects.select_related("device__location").get(pk=params["interface"])
    location = iface.device.location
    vlan_id = as_int(params.get("vlan_id"))
    apply = as_bool(params.get("apply"))
    desired = desired_settings(vlan_id, as_text(params.get("description")))

    if find_vlan(vlan_id, location) is None:
        raise ValueError(
            f"VLAN {vlan_id} does not exist at {location.name}. Run the lab seed or example 06 to create it."
        )
    print(f"Planned turn-up of {iface.device.name} {iface.name}: {desired}")

    if apply:
        write_interface(iface, desired)
        print(f"Applied lab change to {iface.name}. It stays Planned until verification passes.")
    else:
        print("Apply was off. The interface was not changed.")
    return {"interface": iface.name, "desired": desired, "applied": apply}
