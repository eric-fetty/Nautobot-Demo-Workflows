"""Read, compare, and restore an interface's turn-up settings.

The comparison helpers are plain Python so CI can test them without Nautobot.
The read and restore helpers import Nautobot only when they are called.
"""

FIELDS = ("description", "enabled", "mode", "untagged_vlan", "tagged_vlans", "status")


def read_interface(iface):
    """Return the settings a turn-up changes, as plain JSON-safe values."""
    return {
        "device": iface.device.name if iface.device_id else None,
        "interface": iface.name,
        "description": iface.description or "",
        "enabled": bool(iface.enabled),
        "mode": iface.mode or "",
        "untagged_vlan": iface.untagged_vlan.vid if iface.untagged_vlan_id else None,
        "tagged_vlans": sorted(iface.tagged_vlans.values_list("vid", flat=True)),
        "status": iface.status.name if iface.status_id else None,
    }


def differences(expected, actual, fields=FIELDS):
    """List each field where actual differs from expected. Fields missing from expected are ignored."""
    found = []
    for field in fields:
        if field not in expected:
            continue
        want, have = expected[field], actual.get(field)
        if field == "tagged_vlans":
            want, have = sorted(want or []), sorted(have or [])
        if want != have:
            found.append(f"{field}: expected {want!r}, found {have!r}")
    return found


def find_vlan(vid, location):
    """Return the VLAN with this ID at the location, or a global one. None when there is no match."""
    from django.db.models import Q
    from nautobot.ipam.models import VLAN

    if vid in (None, ""):
        return None
    matches = VLAN.objects.filter(vid=int(vid))
    return matches.filter(Q(locations=location) | Q(locations__isnull=True)).distinct().first()


def write_interface(iface, settings):
    """Set the interface to the given settings and save it with Nautobot validation."""
    from nautobot.extras.models import Status

    location = iface.device.location
    if "description" in settings:
        iface.description = settings["description"] or ""
    if "enabled" in settings:
        iface.enabled = bool(settings["enabled"])
    if "mode" in settings:
        iface.mode = settings["mode"] or ""
    if "untagged_vlan" in settings:
        vid = settings["untagged_vlan"]
        vlan = find_vlan(vid, location)
        if vid not in (None, "") and vlan is None:
            raise ValueError(f"VLAN {vid} does not exist at {location.name} or globally.")
        iface.untagged_vlan = vlan
    if settings.get("status"):
        iface.status = Status.objects.get(name=settings["status"])
    iface.validated_save()
    if "tagged_vlans" in settings:
        vlans = [find_vlan(vid, location) for vid in settings["tagged_vlans"] or []]
        iface.tagged_vlans.set([vlan for vlan in vlans if vlan is not None])
    return iface
