# 02. Reserve a VLAN ID

## What you'll learn

- Whole-number inputs with a minimum and a maximum (VLAN ID 1–4094).
- Help text and a placeholder on a field.
- Regex validation, including an optional `IGNORECASE` flag.
- That a planned result can be useful even when nothing is written to inventory.

This workflow never writes to Nautobot inventory. Try an invalid name or an ID outside 1–4094 and watch the form reject it before you submit.

## How to run

1. Choose **Run** on **02. Reserve a VLAN ID**.
2. Enter VLAN ID `110` and name `users-floor-2`.
3. Run now, then open the run and confirm the planned VLAN in the results.

You do not need the lab seed for this workflow.

## Next

[03. Plan an interface description](03-plan-interface-description.md) introduces Nautobot object pickers, dependent fields, and conditional visibility. Run the lab seed first.
