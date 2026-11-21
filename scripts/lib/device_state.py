"""Collect and compare a device's operational baseline from Nautobot data.

A real pre/post check would read the device. These examples use what Nautobot
already knows (interfaces, cables, VLANs) so they run in a lab with no devices.
compare_baselines() and simulate_drift() are plain Python so CI can test them.
"""

COUNT_FIELDS = (
    ("interfaces_enabled", "enabled interfaces"),
    ("interfaces_cabled", "cabled interfaces (neighbors)"),
)


def collect_baseline(device):
    """Return interface, cable, and VLAN counts for a device as JSON-safe values."""
    from nautobot.dcim.models import Interface

    interfaces = Interface.objects.filter(device=device)
    vids = set(interfaces.exclude(untagged_vlan__isnull=True).values_list("untagged_vlan__vid", flat=True))
    vids.update(interfaces.exclude(tagged_vlans__isnull=True).values_list("tagged_vlans__vid", flat=True))
    software = getattr(device, "software_version", None)
    return {
        "device": device.name,
        "software_version": str(software) if software else None,
        "interfaces_total": interfaces.count(),
        "interfaces_enabled": interfaces.filter(enabled=True).count(),
        "enabled_interfaces": sorted(interfaces.filter(enabled=True).values_list("name", flat=True)),
        "interfaces_cabled": interfaces.filter(cable__isnull=False).count(),
        "vlans": sorted(vid for vid in vids if vid is not None),
    }


def simulate_drift(baseline):
    """Return a copy of baseline as if one interface stayed down, one cable lost its neighbor, and one VLAN went missing.

    A device with no enabled interfaces, cables, or VLANs has nothing to lose, so it shows no drift.
    """
    after = dict(baseline)
    enabled = list(baseline.get("enabled_interfaces") or [])
    if enabled:
        # Prefer a data port such as the Ethernet1/48 uplink over the management interface.
        data_ports = [name for name in enabled if not name.lower().startswith("management")] or enabled
        after["enabled_interfaces"] = [name for name in enabled if name != data_ports[-1]]
    after["interfaces_enabled"] = max(int(baseline.get("interfaces_enabled") or 0) - 1, 0)
    if int(baseline.get("interfaces_cabled") or 0) > 0:
        after["interfaces_cabled"] = int(baseline["interfaces_cabled"]) - 1
    vlans = list(baseline.get("vlans") or [])
    after["vlans"] = vlans[:-1]
    return after


def compare_baselines(before, after):
    """Return a list of human-readable differences between two baselines. Empty means no drift."""
    found = []
    for key, label in COUNT_FIELDS:
        was, now = int(before.get(key) or 0), int(after.get(key) or 0)
        if was != now:
            found.append(f"{label}: {was} before, {now} after")
    went_down = sorted(set(before.get("enabled_interfaces") or []) - set(after.get("enabled_interfaces") or []))
    if went_down:
        found.append(f"interfaces no longer up: {', '.join(went_down)}")
    missing = sorted(set(before.get("vlans") or []) - set(after.get("vlans") or []))
    if missing:
        found.append(f"VLANs missing: {', '.join(str(vid) for vid in missing)}")
    added = sorted(set(after.get("vlans") or []) - set(before.get("vlans") or []))
    if added:
        found.append(f"VLANs added: {', '.join(str(vid) for vid in added)}")
    return found
