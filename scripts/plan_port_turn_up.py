"""Plan a port turn-up, and set the interface description only when apply is true."""

PARAMETERS = {
    "device": {"type": "object", "model": "dcim.Device", "required": True},
    "interface": {"type": "object", "model": "dcim.Interface", "required": True},
    "description": {"type": "string", "required": True},
    "vlan_id": {"type": "integer", "required": True},
    "apply": {"type": "boolean", "required": False, "default": False},
}


def run(params):
    """Return the planned port change. Update the interface description only when apply is true."""
    from scripts.lib.params import as_bool
    from nautobot.dcim.models import Device, Interface

    device = Device.objects.get(pk=params["device"])
    iface = Interface.objects.get(pk=params["interface"])
    description = str(params.get("description") or "").strip()
    vlan_id = int(params["vlan_id"])
    apply = as_bool(params.get("apply"))
    print(f"Planned turn-up of {device.name} {iface.name} as access VLAN {vlan_id}: {description}")

    previous = iface.description or ""
    if apply:
        iface.description = description
        iface.save()
        print(f"Applied lab change: set {iface.name} description to {description!r}.")
    else:
        print("Apply was off. The interface was not changed.")

    return {
        "device": device.name,
        "interface": iface.name,
        "description": description,
        "vlan_id": vlan_id,
        "previous_description": previous,
        "applied": apply,
    }
