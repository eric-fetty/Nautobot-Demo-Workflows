# 02. Reserve a VLAN ID

## What you'll learn

- Whole-number inputs with a minimum and a maximum (VLAN ID 1–4094).
- Help text and a placeholder on a field.
- Validation rules. The VLAN name has two: the builder's **VLAN name** preset, then a stricter site convention (lowercase and dashes). The form shows the message of the first rule a value fails.
- An optional field with a rule. **Change ticket** uses the **ServiceNow change number** preset with the `IGNORECASE` flag, and an empty value is not checked.
- That a planned result can be useful even when nothing is written to inventory.

This workflow never writes to Nautobot inventory. Try an ID outside 1–4094, the name `users floor 2` (fails the preset), the name `Users_Floor_2` (passes the preset, fails the convention), or the ticket `CHG12`, and watch the form reject each one before you submit. The server checks the same rules again when the form is sent.

To build the same rules without YAML, open the input in the builder, open **Validation**, and choose **Insert preset**. **Try a value** shows which rules a sample passes. See [Validation rules](https://github.com/eric-fetty/Nautobot_Workflow_Engine/blob/develop/docs/user/inputs.md#validation-rules).

## How to run

1. Choose **Run** on **02. Reserve a VLAN ID**.
2. Enter VLAN ID `110`, name `users-floor-2`, and optionally change ticket `CHG0012345`.
3. Run now, then open the run and confirm the planned VLAN in the results.

You do not need the lab seed for this workflow.

## Next

[03. Plan an interface description](03-plan-interface-description.md) introduces Nautobot object pickers, dependent fields, and conditional visibility. Run the lab seed first.
