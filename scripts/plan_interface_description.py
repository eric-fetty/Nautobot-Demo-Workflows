"""Build a planned interface description. Never writes to Nautobot inventory."""

PARAMETERS = {
    "device": {"type": "object", "model": "dcim.Device", "required": True},
    "interface": {"type": "object", "model": "dcim.Interface", "required": True},
    "style": {"type": "string", "required": True},
    "custom_description": {"type": "string", "required": False},
    "include_role": {"type": "boolean", "required": False, "default": True},
}


def run(params):
    """Return the description that would be applied. This script does not change the interface."""
    from scripts.lib.params import as_bool, as_text
    from nautobot.dcim.models import Device, Interface

    device = Device.objects.get(pk=params["device"])
    iface = Interface.objects.get(pk=params["interface"])
    style = params.get("style") or "standard"
    if style == "custom":
        description = as_text(params.get("custom_description"))
    else:
        parts = [device.location.name if device.location_id else "lab", device.name, iface.name]
        if as_bool(params.get("include_role"), default=True) and getattr(device, "role", None):
            parts.append(str(device.role))
        description = " | ".join(str(part) for part in parts if part)
    print(f"Planned description for {device.name} {iface.name}: {description}")
    print("Nothing was changed in Nautobot.")
    return {
        "device": device.name,
        "interface": iface.name,
        "description": description,
        "applied": False,
    }
