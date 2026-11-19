"""Close out a verified turn-up: set the interface Active and add a note. Changes Nautobot only when apply is true."""

PARAMETERS = {
    "interface": {"type": "object", "model": "dcim.Interface", "required": True},
    "message": {"type": "string", "required": True, "help": "Text of the note."},
    "apply": {"type": "boolean", "required": False, "default": False},
}


def run(params):
    """Mark the interface Active and record a note."""
    from nautobot.dcim.models import Interface
    from nautobot.extras.models import Note, Status

    from scripts.lib.params import as_bool, as_text

    iface = Interface.objects.select_related("device").get(pk=params["interface"])
    message = as_text(params.get("message"))
    apply = as_bool(params.get("apply"))
    print(f"Close out {iface.device.name} {iface.name}: set status Active and note {message!r}.")
    if apply:
        iface.status = Status.objects.get(name="Active")
        iface.validated_save()
        Note.objects.create(assigned_object=iface, note=message)
        print("Set the interface Active and added the note.")
    else:
        print("Apply was off. The status and notes were not changed.")
    return {"interface": iface.name, "status": "Active", "note": message, "applied": apply}
