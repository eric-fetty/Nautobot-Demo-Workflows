"""Write a journal entry on a device. Used only by opt-in apply steps."""

PARAMETERS = {
    "device": {"type": "object", "model": "dcim.Device", "required": True, "help": "Device that gets the note."},
    "message": {"type": "string", "required": True, "help": "Text of the journal entry."},
}


def run(params):
    """Add a Nautobot journal entry to the device."""
    from nautobot.dcim.models import Device
    from nautobot.extras.models import JournalEntry

    device = Device.objects.get(pk=params["device"])
    message = str(params.get("message") or "").strip()
    JournalEntry.objects.create(assigned_object=device, comments=message)
    print(f"Added journal entry on {device.name}: {message}")
    return {"device": device.name, "message": message}
