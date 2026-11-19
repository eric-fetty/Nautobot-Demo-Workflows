"""Plan a VLAN reservation. Never writes to Nautobot inventory."""

PARAMETERS = {
    "vid": {"type": "integer", "required": True, "help": "VLAN ID to reserve."},
    "name": {"type": "string", "required": True, "help": "VLAN name."},
}


def run(params):
    """Return the planned VLAN ID and name. This script does not create a VLAN."""
    vid = int(params["vid"])
    name = str(params["name"]).strip()
    print(f"Planned VLAN {vid} ({name}). Nothing was created in Nautobot.")
    return {"vid": vid, "name": name, "applied": False}
