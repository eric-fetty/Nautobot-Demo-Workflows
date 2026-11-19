"""Find the next free IP in a prefix, and reserve it in Nautobot only when apply is true.

Fails when the prefix is full (or simulate_full is on), so a later step can fall back.
"""

PARAMETERS = {
    "prefix": {"type": "object", "model": "ipam.Prefix", "required": True, "help": "Prefix to take an address from."},
    "device": {"type": "object", "model": "dcim.Device", "required": True, "help": "Device the address is for."},
    "role": {"type": "string", "required": False, "default": "preferred", "help": "preferred or fallback, for logs."},
    "simulate_full": {"type": "boolean", "required": False, "default": False},
    "apply": {"type": "boolean", "required": False, "default": False},
}


def run(params):
    """Return the address found. Raise when there is no free address so this step is marked failed."""
    from nautobot.dcim.models import Device
    from nautobot.extras.models import Status
    from nautobot.ipam.models import IPAddress, Prefix

    from scripts.lib.params import as_bool, as_text

    prefix = Prefix.objects.select_related("namespace").get(pk=params["prefix"])
    device = Device.objects.get(pk=params["device"])
    role = as_text(params.get("role")) or "preferred"
    apply = as_bool(params.get("apply"))

    if as_bool(params.get("simulate_full")):
        raise RuntimeError(f"The {role} prefix {prefix.prefix} has no free addresses (simulated).")
    address = prefix.get_first_available_ip()
    if not address:
        raise RuntimeError(f"The {role} prefix {prefix.prefix} has no free addresses.")
    print(f"Next free address in the {role} prefix {prefix.prefix}: {address} for {device.name}.")

    if apply:
        status = Status.objects.filter(name="Reserved").first() or Status.objects.get(name="Active")
        ip = IPAddress.objects.create(
            address=address,
            namespace=prefix.namespace,
            status=status,
            description=f"Management for {device.name} (reserved by workflow)",
        )
        print(f"Reserved {ip.address} in Nautobot with status {status.name}.")
    else:
        print("Apply was off. The address was not reserved.")
    return {"address": str(address), "prefix": str(prefix.prefix), "role": role, "applied": apply}
