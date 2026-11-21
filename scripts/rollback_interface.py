"""Put an interface back to an earlier snapshot. Restores only when apply is true."""

PARAMETERS = {
    "interface": {"type": "object", "model": "dcim.Interface", "required": True},
    "snapshot": {"type": "string", "required": True, "help": "results.snapshot.return_value from the snapshot step."},
    "reason": {"type": "string", "required": False},
    "apply": {"type": "boolean", "required": False, "default": False},
}


def run(params):
    """Restore description, enabled, mode, VLANs, and status from the snapshot."""
    from nautobot.dcim.models import Interface
    from nautobot.extras.models import Note

    from scripts.lib.interface_state import FIELDS, differences, read_interface, write_interface
    from scripts.lib.params import as_bool, as_dict, as_text

    iface = Interface.objects.select_related("device__location", "untagged_vlan", "status").get(pk=params["interface"])
    snapshot = as_dict(params.get("snapshot"))
    if not snapshot:
        raise ValueError("No snapshot to roll back to.")
    restore = {field: snapshot[field] for field in FIELDS if field in snapshot}
    reason = as_text(params.get("reason")) or "the change did not verify"
    undo = differences(restore, read_interface(iface))
    print(f"Rollback of {iface.device.name} {iface.name} because {reason}.")
    print(f"Settings to restore: {undo or 'none, the interface already matches the snapshot'}")

    if as_bool(params.get("apply")):
        write_interface(iface, restore)
        Note.objects.create(assigned_object=iface, note=f"Rolled back by workflow: {reason}. Restored {restore}.")
        print("Restored the interface and added a note.")
    else:
        print("Apply was off. Nothing was changed, so there is nothing to undo.")
    return {"interface": iface.name, "restored": restore, "undone": undo, "applied": as_bool(params.get("apply"))}
