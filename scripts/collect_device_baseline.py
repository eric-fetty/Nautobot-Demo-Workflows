"""Record a device's baseline before a change: enabled interfaces, cabled neighbors, and VLANs. Read-only."""

PARAMETERS = {
    "device": {"type": "object", "model": "dcim.Device", "required": True},
}


def run(params):
    """Return the baseline. Later steps read it as results.precheck.return_value."""
    from nautobot.dcim.models import Device

    from scripts.lib.device_state import collect_baseline

    device = Device.objects.get(pk=params["device"])
    baseline = collect_baseline(device)
    print(
        f"Baseline for {device.name}: {baseline['interfaces_enabled']} enabled interface(s), "
        f"{baseline['interfaces_cabled']} cabled neighbor(s), VLANs {baseline['vlans'] or 'none'}."
    )
    return baseline
