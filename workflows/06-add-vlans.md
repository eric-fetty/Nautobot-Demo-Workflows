# 06. Add VLANs

## What you'll learn

- A table input (`listdict`) with typed columns, unique VLAN IDs, and row limits.
- **Download template** and **Import CSV** on the launch form. The file is read in your browser and is not stored.
- A list of text (extra trunk ports), a whole-number MTU, and a pick-many tags field.
- A several-objects picker for switches at the chosen location.
- An **Apply these changes in Nautobot** switch that defaults to off.

With Apply off, the script only reports the plan. With Apply on, it creates (or reuses) VLANs at the location. That is a lab-safe inventory write. Leave it off unless you intend to change this lab.

## How to run

1. Run the [lab seed](../README.md#lab-setup) if you have not already.
2. Choose **Run** on **06. Add VLANs**.
3. Pick **AMS01** and one or two switches.
4. Add a row with VLAN ID `110` and name `users-floor-2`, or import a small CSV.
5. Leave **Apply these changes in Nautobot** off, run now, and read the plan.
6. Optionally run again with Apply on and confirm the VLANs appear under IPAM.

## Next

[07. Turn up a port](07-turn-up-a-port.md) introduces Before / Main / Always-after steps and conditions that read an earlier result.
