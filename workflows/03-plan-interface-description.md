# 03. Plan an interface description

## What you'll learn

- Nautobot object inputs for a location, a device, and an interface.
- `depends_on` and a filter so each picker waits for the one before it.
- A choice that shows or hides later fields with `show_if`.
- A yes/no field and a step condition (`when`) based on an input.

This workflow never writes to the interface. It only returns the description that would be used.

## How to run

1. Run the [lab seed](../README.md#lab-setup) if you have not already, so locations and devices exist.
2. Choose **Run** on **03. Plan an interface description**.
3. Pick **AMS01**, a switch such as `ams01-acc-sw01`, and `Ethernet1/1`.
4. Leave the style on the built-in option, run now, and read the planned description.
5. Run it again, choose the custom style, and confirm the custom description field appears.

This is also a good time to try **Preview run** in the builder: it shows which steps would run without executing them.

## Next

[04. Normalize a hostname](04-normalize-hostname.md) introduces a repo-backed Jinja filter and shared Python helpers.
