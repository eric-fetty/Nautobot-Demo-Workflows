"""Add a note to a device about how a change ended. Writes only when apply is true."""

PARAMETERS = {
    "device": {"type": "object", "model": "dcim.Device", "required": True},
    "message": {"type": "string", "required": True},
    "details": {"type": "list", "required": False, "help": "Extra lines, such as the differences a post-check found."},
    "apply": {"type": "boolean", "required": False, "default": False},
}


def build_note(message, details):
    """Return the note text: the message and one bullet per detail. Plain Python so CI can test it."""
    lines = [message.strip()]
    lines.extend(f"- {item}" for item in details if str(item).strip())
    return "\n".join(lines)


def run(params):
    """Record the note, or print it when apply is off."""
    from nautobot.dcim.models import Device
    from nautobot.extras.models import Note

    from scripts.lib.params import as_bool, as_list, as_text

    device = Device.objects.get(pk=params["device"])
    note = build_note(as_text(params.get("message")), as_list(params.get("details")))
    apply = as_bool(params.get("apply"))
    print(f"Note for {device.name}:\n{note}")
    if apply:
        Note.objects.create(assigned_object=device, note=note)
        print("Added the note in Nautobot.")
    else:
        print("Apply was off. The note was not added.")
    return {"device": device.name, "note": note, "applied": apply}
