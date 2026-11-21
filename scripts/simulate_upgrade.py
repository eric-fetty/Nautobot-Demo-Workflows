"""Pretend to upgrade device software. Never contacts the device."""

PARAMETERS = {
    "device": {"type": "object", "model": "dcim.Device", "required": True},
    "target_version": {"type": "string", "required": True},
    "apply": {"type": "boolean", "required": False, "default": False},
}


def run(params):
    """Report the upgrade that would run. With apply on, record a note that the (simulated) upgrade started."""
    from nautobot.dcim.models import Device
    from nautobot.extras.models import Note

    from scripts.lib.params import as_bool, as_text

    device = Device.objects.get(pk=params["device"])
    target = as_text(params.get("target_version"))
    current = getattr(device, "software_version", None)
    print(f"Upgrade {device.name} from {current or 'unknown'} to {target} (simulated, no device contact).")
    if as_bool(params.get("apply")):
        Note.objects.create(assigned_object=device, note=f"Software upgrade to {target} started (lab simulation).")
        print("Added a note that the upgrade started.")
    return {"device": device.name, "from": str(current) if current else None, "to": target, "simulated": True}
