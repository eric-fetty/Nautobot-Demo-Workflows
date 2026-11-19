# 01. Echo a hostname

## What you'll learn

- How to open a workflow, fill in a text input, and choose **Run now**.
- Where to read the run status, the returned hostname, and the execution log.
- How `manual_duration_minutes` feeds the time-savings dashboard after a successful run.

This workflow never writes to Nautobot inventory.

## How to run

1. On the Workflows list, choose **Run** on **01. Echo a hostname**.
2. Enter `router.example.com`.
3. Leave **When should it run?** on **Run now** and submit.
4. Open the run and confirm the status, the returned hostname, and the log line `Prepared hostname: router.example.com`.

You do not need the lab seed for this workflow.

## Next

[02. Reserve a VLAN ID](02-reserve-vlan-id.md) adds validation rules and a whole-number input.
