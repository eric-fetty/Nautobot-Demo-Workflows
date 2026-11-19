"""Pretend to check that a device is reachable. Never contacts the live device."""

PARAMETERS = {
    "device": {"type": "object", "model": "dcim.Device", "required": True, "help": "Device to check."},
    "attempts": {"type": "integer", "required": False, "default": 3, "help": "Checks to report."},
}


def run(params):
    """Return reachable=True after confirming the device exists in Nautobot. No packets are sent."""
    from nautobot.dcim.models import Device

    device = Device.objects.get(pk=params["device"])
    attempts = int(params.get("attempts") or 3)
    print(f"Lab reachability check for {device.name} ({attempts} attempt(s)): reachable (simulated).")
    return {"device": device.name, "reachable": True, "attempts": attempts, "simulated": True}
