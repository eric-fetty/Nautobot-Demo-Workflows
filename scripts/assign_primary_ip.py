"""Assign an address to a device interface and make it the primary IPv4. Changes Nautobot only when apply is true."""

PARAMETERS = {
    "device": {"type": "object", "model": "dcim.Device", "required": True},
    "interface": {"type": "object", "model": "dcim.Interface", "required": True},
    "address": {"type": "string", "required": True, "help": "Address chosen by an earlier step, like 10.20.254.1/24."},
    "source": {"type": "string", "required": False, "help": "Which step supplied the address."},
    "apply": {"type": "boolean", "required": False, "default": False},
}


def run(params):
    """Attach the address to the interface and set it as the device's primary IPv4."""
    from nautobot.dcim.models import Device, Interface
    from nautobot.extras.models import Status
    from nautobot.ipam.models import IPAddress

    from scripts.lib.params import as_bool, as_text

    device = Device.objects.get(pk=params["device"])
    iface = Interface.objects.get(pk=params["interface"], device=device)
    address = as_text(params.get("address"))
    source = as_text(params.get("source")) or "an earlier step"
    apply = as_bool(params.get("apply"))
    if not address:
        raise ValueError("No address was passed in. Neither reservation step succeeded.")
    previous = str(device.primary_ip4.address) if device.primary_ip4_id else None
    print(f"Assign {address} (from {source}) to {device.name} {iface.name} as primary IPv4. Previous: {previous}.")

    if apply:
        host = address.split("/")[0]
        ip = IPAddress.objects.filter(host=host, mask_length=int(address.split("/")[1])).first()
        if ip is None:
            raise ValueError(f"{address} is not in Nautobot. The reservation step should have created it.")
        ip.status = Status.objects.get(name="Active")
        ip.validated_save()
        iface.add_ip_addresses(ip)
        device.primary_ip4 = ip
        device.validated_save()
        print(f"{device.name} primary IPv4 is now {ip.address}.")
    else:
        print("Apply was off. The device was not changed.")
    return {"device": device.name, "address": address, "source": source, "previous": previous, "applied": apply}
