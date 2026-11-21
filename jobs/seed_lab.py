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
from nautobot.dcim.models import Cable, Device, DeviceType, Interface, Location, LocationType, Manufacturer, Platform
from nautobot.extras.models import ExternalIntegration, Role, Status
from nautobot.ipam.models import VLAN, IPAddress, Namespace, Prefix, VLANGroup


# Nautobot groups Jobs by the module-level ``name``; Meta.grouping is not used.
name = "Workflow Engine examples"

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
            group, group_created = VLANGroup.objects.get_or_create(name=f"{code} lab VLANs", defaults={"location": location})
            _log(log, f"{'Created' if group_created else 'Reused'} VLAN group {group.name}")
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

    extras = _seed_conditional_examples(locations, namespace, active, log)

    summary = {
        "locations": sorted(locations),
        "devices": device_count,
        "servicenow_integration": integration.name,
        "vlan_groups": [f"{code} lab VLANs" for code in locations],
        **extras,
        "lab_only": True,
    }
    _log(log, f"Lab seed complete: {summary}")
    return summary


def _seed_conditional_examples(locations, namespace, active, log):
    """Add the VLANs, management prefixes, and uplink cables that examples 11-13 use."""
    vlans, prefixes, cables = [], [], []
    for site_index, (code, location) in enumerate(locations.items()):
        group = VLANGroup.objects.filter(name=f"{code} lab VLANs").first()
        for vid, vlan_name in ((110, "users-110"), (120, "voice-120")):
            # Example 6 can create the same VLAN IDs at a location; reuse those.
            vlan = VLAN.objects.filter(vid=vid, locations=location).first()
            if vlan is None:
                vlan = VLAN.objects.create(
                    vid=vid, name=vlan_name, status=active, location=location, vlan_group=group
                )
                _log(log, f"Created VLAN {vid} at {code}")
            vlans.append(f"{code} {vlan.vid}")

        # A /29 has six usable addresses. Fill them all so example 12's preferred prefix is full.
        full, _ = Prefix.objects.get_or_create(
            prefix=f"10.{20 + site_index}.255.0/29",
            namespace=namespace,
            defaults={"status": active, "description": f"{code} mgmt (lab: full on purpose)"},
        )
        for host in range(1, 7):
            IPAddress.objects.get_or_create(
                address=f"10.{20 + site_index}.255.{host}/29",
                namespace=namespace,
                defaults={"status": active, "description": "Lab filler so this prefix is full"},
            )
        fallback, _ = Prefix.objects.get_or_create(
            prefix=f"10.{20 + site_index}.254.0/24",
            namespace=namespace,
            defaults={"status": active, "description": f"{code} mgmt fallback (lab)"},
        )
        prefixes.extend([str(full.prefix), str(fallback.prefix)])

        # Cable the first access switch's uplink to the first distribution switch, for example 13's neighbor count.
        access = Interface.objects.filter(device__name=f"{code.lower()}-acc-sw01", name="Ethernet1/48").first()
        dist = Interface.objects.filter(device__name=f"{code.lower()}-dist-sw01", name="Ethernet1/48").first()
        if access and dist and not access.cable_id and not dist.cable_id:
            try:
                connected = Status.objects.get(name="Connected")
                Cable.objects.create(termination_a=access, termination_b=dist, status=connected)
                _log(log, f"Cabled {access.device.name} {access.name} to {dist.device.name} {dist.name}")
            except Exception as exc:  # Cable statuses vary by install; the examples still run without it.
                _log(log, f"Skipped uplink cable at {code}: {exc}")
        if access and access.cable_id:
            cables.append(f"{access.device.name} {access.name}")
    return {"example_vlans": vlans, "example_prefixes": prefixes, "example_cables": cables}


class SeedWorkflowEngineLab(Job):
    """Create the lab inventory used by the example workflows."""

    class Meta:
        name = "Seed Workflow Engine lab data"
        description = (
            "LAB ONLY. Creates demo locations, devices, interfaces, prefixes, "
            "VLAN groups, VLANs 110 and 120, an uplink cable per site, and a fake "
            "ServiceNow (demo) External Integration. "
            "Safe to run again. Do not run this in production."
        )

    def run(self):
        """Seed the lab inventory."""
        return seed(log=self.logger)
