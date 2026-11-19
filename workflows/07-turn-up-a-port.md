# 07. Turn up a port

## What you'll learn

- **Before**, **Main**, and **Always run at the end** action groups (`pre_actions`, `actions`, `post_actions`).
- A Before step that must succeed before the main work runs. If a Before step fails, nothing else runs.
- A step condition that reads an earlier result (`results.check_reachable.status` and `return_value.reachable`).
- A post step that runs only when Apply is on and the main step succeeded. Post steps still run after a main failure; this one is skipped by its condition when there is nothing to record.

The reachability check is simulated: it confirms the device exists in Nautobot and always reports reachable. No packets are sent. With Apply off, the main step only plans. With Apply on, it sets the interface description in this lab and, if that succeeds, adds a journal entry.

## How to run

1. Run the [lab seed](../README.md#lab-setup) if you have not already.
2. Choose **Run** on **07. Turn up a port**.
3. Pick **AMS01**, `ams01-acc-sw01`, and `Ethernet1/1`.
4. Enter VLAN `110` and a short description.
5. Leave Apply off, run now, and confirm the Before check, the plan, and that no journal entry was added.
6. Optionally run again with Apply on and inspect the interface description and the device journal.

In the builder, **Preview run** follows these conditions with the values in the launch-form preview. When a condition depends on an earlier step's output, it tells you that the outcome can only be known in a real run.

## Next

[08. Approve a maintenance reboot](08-approve-maintenance-reboot.md) opts the workflow into Nautobot's approval pipeline.
