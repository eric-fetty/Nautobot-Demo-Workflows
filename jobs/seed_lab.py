"""Lab-only inventory seed for the Workflow Engine examples.

Idempotent and safe to run again. Creates demo locations, devices, interfaces,
prefixes, and a fake ServiceNow External Integration named "ServiceNow (demo)".

This module does not run any seed work on import. Nautobot imports Job modules
when a Git repository is synchronized, so the work starts only when you run the
Job or call seed() from nbshell.

Do not run this in production.
"""

from django.contrib.contenttypes.models import ContentType
from nautobot.apps.jobs import Job
from nautobot.dcim.models import Device, DeviceType, Interface, Location, LocationType, Manufacturer, Platform
from nautobot.extras.models import ExternalIntegration, Role, Status
from nautobot.ipam.models import IPAddress, Namespace, Prefix, VLANGroup


LAB_ONLY = True
SERVICENOW_INTEGRATION_NAME = "ServiceNow (demo)"


def _log(log, message):
    """Write to the Job logger when present, otherwise print."""
    if log is not None:
        log.info(message)
    else:
        print(message)


def seed(log=None):
    """Create or reuse the lab inventory. Return a summary dict. Safe to run again."""
    active = Status.objects.get(name="Active")
    device_ct = ContentType.objects.get_for_model(Device)
    interface_ct = ContentType.objects.get_for_model(Interface)
    vlan_ct = ContentType.objects.get(app_label="ipam", model="vlan")
    prefix_ct = ContentType.objects.get(app_label="ipam", model="prefix")
    ip_ct = ContentType.objects.get(app_label="ipam", model="ipaddress")

    for name in ("Active", "Planned", "Staged", "Offline"):
        status = Status.objects.filter(name=name).first()
        if status is not None:
            status.content_types.add(device_ct, interface_ct, vlan_ct, prefix_ct, ip_ct)

    integration, integration_created = ExternalIntegration.objects.get_or_create(
        name=SERVICENOW_INTEGRATION_NAME,
        defaults={"remote_url": "https://example.service-now.com", "timeout": 30},
    )
    _log(log, f"{'Created' if integration_created else 'Reused'} External Integration {integration.name}")

    site_type, _ = LocationType.objects.get_or_create(name="Site")
    site_type.content_types.add(device_ct, vlan_ct, prefix_ct)

    locations = {}
    for name, description in (("AMS01", "Amsterdam DC 1"), ("NYC02", "New York HQ")):
        location, created = Location.objects.get_or_create(
            name=name, defaults={"location_type": site_type, "status": active, "description": description}
        )
        locations[name] = location
        _log(log, f"{'Created' if created else 'Reused'} location {name}")

    arista, _ = Manufacturer.objects.get_or_create(name="Arista")
    cisco, _ = Manufacturer.objects.get_or_create(name="Cisco")
    types = {
        "eos": DeviceType.objects.get_or_create(model="DCS-7050SX3", defaults={"manufacturer": arista})[0],
        "ios": DeviceType.objects.get_or_create(model="C9300-48P", defaults={"manufacturer": cisco})[0],
    }
    platforms = {
        "eos": Platform.objects.get_or_create(name="Arista EOS", defaults={"manufacturer": arista})[0],
        "ios": Platform.objects.get_or_create(name="Cisco IOS-XE", defaults={"manufacturer": cisco})[0],
    }
    roles = {}
    for name in ("Access switch", "Distribution switch"):
        roles[name], _ = Role.objects.get_or_create(name=name)
        roles[name].content_types.add(device_ct)

    namespace = Namespace.objects.get(name="Global")
    statuses = ["Active", "Active", "Active", "Staged", "Offline", "Active"]
    device_count = 0
    for site_index, (code, location) in enumerate(locations.items()):
        prefix, prefix_created = Prefix.objects.get_or_create(
            prefix=f"10.{20 + site_index}.0.0/16", namespace=namespace, defaults={"status": active}
        )
        _log(log, f"{'Created' if prefix_created else 'Reused'} prefix {prefix}")
        try:
            VLANGroup.objects.get_or_create(name=f"{code} lab VLANs", defaults={"location": location})
        except Exception as exc:  # Model fields vary slightly across Nautobot 3.x releases.
            _log(log, f"Skipped VLAN group for {code}: {exc}")

        plan = [("Access switch", "acc-sw", 6 if code == "AMS01" else 4), ("Distribution switch", "dist-sw", 2)]
        for role_name, abbr, count in plan:
            for number in range(1, count + 1):
                kind = "eos" if (number + site_index) % 2 else "ios"
                name = f"{code.lower()}-{abbr}{number:02d}"
                status_name = statuses[(number - 1) % len(statuses)] if role_name == "Access switch" else "Active"
                device, created = Device.objects.get_or_create(
                    name=name,
                    defaults={
                        "location": location,
                        "device_type": types[kind],
                        "platform": platforms[kind],
                        "role": roles[role_name],
                        "status": Status.objects.get(name=status_name),
                        "serial": f"SN{site_index}{number:03d}{len(abbr)}",
                    },
                )
                device_count += 1
                mgmt, _ = Interface.objects.get_or_create(
                    device=device, name="Management1", defaults={"type": "1000base-t", "status": active}
                )
                for if_name in ("Ethernet1/1", "Ethernet1/2", "Ethernet1/48"):
                    Interface.objects.get_or_create(
                        device=device, name=if_name, defaults={"type": "10gbase-x-sfpp", "status": active}
                    )
                if not device.primary_ip4_id:
                    third = 0 if role_name == "Access switch" else 1
                    address, _ = IPAddress.objects.get_or_create(
                        address=f"10.{20 + site_index}.{third}.{10 + number}/16",
                        namespace=namespace,
                        defaults={"status": active},
                    )
                    mgmt.add_ip_addresses(address)
                    device.primary_ip4 = address
                    device.save()
                _log(log, f"{'Created' if created else 'Reused'} device {device.name}")

    summary = {
        "locations": sorted(locations),
        "devices": device_count,
        "servicenow_integration": integration.name,
        "vlan_groups": [f"{code} lab VLANs" for code in locations],
        "lab_only": True,
    }
    _log(log, f"Lab seed complete: {summary}")
    return summary


class SeedWorkflowEngineLab(Job):
    """Create the lab inventory used by the example workflows."""

    class Meta:
        name = "Seed Workflow Engine lab data"
        description = (
            "LAB ONLY. Creates demo locations, devices, interfaces, prefixes, "
            "VLAN groups, and a fake ServiceNow (demo) External Integration. "
            "Safe to run again. Do not run this in production."
        )
        grouping = "Workflow Engine examples"

    def run(self):
        """Seed the lab inventory."""
        return seed(log=self.logger)
