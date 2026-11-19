"""Plan VLAN rows, and create them in Nautobot only when apply is true."""

PARAMETERS = {
    "location": {"type": "object", "model": "dcim.Location", "required": True},
    "switches": {"type": "list", "required": False},
    "vlans": {"type": "list", "required": True},
    "status": {"type": "string", "required": False, "default": "active"},
    "tags": {"type": "list", "required": False},
    "trunk_ports": {"type": "list", "required": False},
    "mtu": {"type": "integer", "required": False, "default": 1500},
    "apply": {"type": "boolean", "required": False, "default": False},
}


def run(params):
    """Return a plan for each VLAN row. Create lab VLANs only when apply is true."""
    from scripts.lib.params import as_bool, as_list, as_text
    from nautobot.dcim.models import Device, Location
    from nautobot.extras.models import Status, Tag
    from nautobot.ipam.models import VLAN

    location = Location.objects.get(pk=params["location"])
    rows = as_list(params.get("vlans"))
    apply = as_bool(params.get("apply"))
    status_name = as_text(params.get("status")) or "active"
    tag_names = as_list(params.get("tags"))
    trunk_ports = as_list(params.get("trunk_ports"))
    mtu = int(params.get("mtu") or 1500)
    switch_ids = as_list(params.get("switches"))
    switch_names = []
    if switch_ids:
        switch_names = list(Device.objects.filter(pk__in=switch_ids).values_list("name", flat=True))

    planned = [{"vid": int(row["vid"]), "name": str(row["name"]).strip(), "role": row.get("role")} for row in rows]
    print(f"Planned {len(planned)} VLAN(s) at {location.name} for switches {switch_names or '(none)'}.")
    print(f"Trunk ports: {trunk_ports or '(uplinks only)'}; MTU {mtu}; tags {tag_names or '(none)'}.")

    created = []
    if apply:
        status = Status.objects.get(name__iexact=status_name)
        tag_objects = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
        for item in planned:
            vlan, was_created = VLAN.objects.get_or_create(
                vid=item["vid"],
                location=location,
                defaults={"name": item["name"], "status": status},
            )
            if tag_objects:
                vlan.tags.add(*tag_objects)
            created.append({"vid": vlan.vid, "name": vlan.name, "created": was_created})
            print(f"{'Created' if was_created else 'Already present'}: VLAN {vlan.vid} ({vlan.name})")
    else:
        print("Apply was off. Nothing was created in Nautobot.")

    return {
        "location": location.name,
        "planned": planned,
        "switches": switch_names,
        "trunk_ports": trunk_ports,
        "mtu": mtu,
        "applied": apply,
        "created": created,
    }
