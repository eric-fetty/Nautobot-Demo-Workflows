"""Plan a VLAN reservation. Never writes to Nautobot inventory."""

PARAMETERS = {
    "vid": {"type": "integer", "required": True, "help": "VLAN ID to reserve."},
    "name": {"type": "string", "required": True, "help": "VLAN name."},
    "change_ticket": {"type": "string", "required": False, "help": "ServiceNow change number, if any."},
}


def run(params):
    """Return the planned VLAN ID and name. This script does not create a VLAN."""
    from scripts.lib.params import as_text

    vid = int(params["vid"])
    name = str(params["name"]).strip()
    ticket = as_text(params.get("change_ticket")).upper()
    print(f"Planned VLAN {vid} ({name}){f' under {ticket}' if ticket else ''}. Nothing was created in Nautobot.")
    return {"vid": vid, "name": name, "change_ticket": ticket, "applied": False}
