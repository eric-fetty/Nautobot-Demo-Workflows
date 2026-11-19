"""Record an interface's current settings so a later step can roll back to them. Read-only."""

PARAMETERS = {
    "interface": {"type": "object", "model": "dcim.Interface", "required": True, "help": "Interface to snapshot."},
}


def run(params):
    """Return description, enabled, mode, VLANs, and status. Later steps read this as results.snapshot.return_value."""
    from nautobot.dcim.models import Interface

    from scripts.lib.interface_state import read_interface

    iface = Interface.objects.select_related("device", "untagged_vlan", "status").get(pk=params["interface"])
    snapshot = read_interface(iface)
    print(f"Snapshot of {snapshot['device']} {snapshot['interface']} before the change: {snapshot}")
    return snapshot
