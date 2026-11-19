"""Plan a maintenance-window change, and apply lab-safe Nautobot updates only when asked."""

PARAMETERS = {
    "location": {"type": "object", "model": "dcim.Location", "required": True},
    "devices": {"type": "list", "required": True},
    "vlans": {"type": "list", "required": True},
    "change_ticket": {"type": "string", "required": True},
    "apply": {"type": "boolean", "required": False, "default": False},
}


def run(params):
    """Plan VLAN work at a location. Create lab VLANs only when apply is true."""
    from scripts.lib.params import as_bool, as_list
    from nautobot.dcim.models import Device, Location
    from nautobot.extras.models import Status
    from nautobot.ipam.models import VLAN

    location = Location.objects.get(pk=params["location"])
    device_ids = as_list(params.get("devices"))
    devices = list(Device.objects.filter(pk__in=device_ids).order_by("name"))
    rows = as_list(params.get("vlans"))
    ticket = str(params.get("change_ticket") or "").strip()
    apply = as_bool(params.get("apply"))
    planned = [{"vid": int(row["vid"]), "name": str(row["name"]).strip()} for row in rows]
    names = [device.name for device in devices]
    print(f"Maintenance {ticket}: planned {len(planned)} VLAN(s) at {location.name} on {names}.")

    created = []
    if apply:
        status = Status.objects.get(name="Active")
        for item in planned:
            vlan, was_created = VLAN.objects.get_or_create(
                vid=item["vid"],
                location=location,
                defaults={"name": item["name"], "status": status},
            )
            created.append({"vid": vlan.vid, "name": vlan.name, "created": was_created})
            print(f"{'Created' if was_created else 'Already present'}: VLAN {vlan.vid} ({vlan.name})")
    else:
        print("Apply was off. Nothing was created in Nautobot.")

    return {
        "location": location.name,
        "devices": names,
        "planned": planned,
        "change_ticket": ticket,
        "applied": apply,
        "created": created,
    }
