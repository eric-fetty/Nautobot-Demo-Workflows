# 05. Record a planned change

## What you'll learn

- How YAML can include a shared fragment with `{% include "templates/inputs/standard_change_inputs.yaml" %}`.
- That include paths are resolved relative to the workflow file, and the fragment must use the indentation expected at the insertion point.
- Reusing a validated change-ticket field in later examples (rungs 8–10).

The include adds a required **Change ticket** field that must match `CHG` plus seven digits, for example `CHG0031245`. This workflow never writes to inventory.

## How to run

1. Choose **Run** on **05. Record a planned change**.
2. Enter ticket `CHG0031245` and a short summary.
3. Try a ticket that does not match the pattern and confirm the form rejects it.
4. Run now and confirm the ticket and summary in the results.

You do not need the lab seed for this workflow. Open `workflows/templates/inputs/standard_change_inputs.yaml` to see the fragment.

## Next

[06. Add VLANs](06-add-vlans.md) introduces a table input with CSV import, a list, and several objects. From here on, an **Apply these changes in Nautobot** switch is available and defaults to off.
