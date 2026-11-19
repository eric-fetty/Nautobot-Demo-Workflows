"""Plan a maintenance reboot. Never reboots a device and never writes inventory."""

PARAMETERS = {
    "device": {"type": "object", "model": "dcim.Device", "required": True},
    "reboot_type": {"type": "string", "required": True},
    "change_ticket": {"type": "string", "required": True},
    "wait_for_recovery": {"type": "boolean", "required": False, "default": True},
}


def run(params):
    """Return the planned reboot. This script does not contact or reboot the device."""
    from scripts.lib.params import as_bool
    from nautobot.dcim.models import Device

    device = Device.objects.get(pk=params["device"])
    reboot_type = params.get("reboot_type") or "soft"
    ticket = str(params.get("change_ticket") or "").strip()
    wait = as_bool(params.get("wait_for_recovery"), default=True)
    print(f"Planned {reboot_type} reboot of {device.name} under {ticket}.")
    print("This is a plan only. The device was not contacted or rebooted.")
    if wait:
        print("A real change would wait for the device to come back online.")
    return {
        "device": device.name,
        "reboot_type": reboot_type,
        "change_ticket": ticket,
        "wait_for_recovery": wait,
        "applied": False,
    }
