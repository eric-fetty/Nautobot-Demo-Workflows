# 13. Software upgrade with pre and post checks

## What you'll learn

- A **Before** step that records a baseline. If it fails, nothing else runs.
- Passing that baseline into a later step with `results.precheck.return_value`.
- Branching on a **return value** rather than a status: `close_success` runs when `results.postcheck.return_value.drift == 0`, and `open_backout` runs when it is greater than 0.
- Putting a list from an earlier step into a note: `details: "{{ results.postcheck.return_value.differences }}"`.

| Step | Phase | Runs when | Does |
| --- | --- | --- | --- |
| `precheck` | Before | always | Counts enabled interfaces and cabled neighbors and lists VLANs |
| `upgrade` | Main | always | Simulated upgrade. Nothing contacts the device |
| `postcheck` | Main | `upgrade` succeeded | Collects the same data and compares it with the baseline. Returns `drift` and `differences` |
| `close_success` | Main | `postcheck.return_value.drift == 0` | Notes that the upgrade was verified |
| `open_backout` | Main | `postcheck.return_value.drift > 0` | Notes that backout is needed, listing each difference |

The post-check **succeeds** even when it finds drift: the check itself worked, and what it found is in its return value. So both paths finish with run status **Success**. Compare examples 11 and 12, where the failure path ends **Failed** because a Main step failed.

The checks use what Nautobot knows about the switch. A real workflow would collect the same counts from the device or a monitoring system.

## How to run

1. Run the [lab seed](../README.md#lab-setup). It cables `ams01-acc-sw01 Ethernet1/48` to `ams01-dist-sw01 Ethernet1/48`, so that switch has a neighbor to lose.
2. Choose **Run** on **13. Software upgrade with pre and post checks**.
3. Pick **AMS01** and `ams01-acc-sw01`, and keep the target version.
4. **Clean path:** leave **Simulate drift after the upgrade** off. `close_success` runs and `open_backout` is skipped.
5. **Drift path:** turn **Simulate drift** on. The post-check reports the uplink down, a lost neighbor, and a missing VLAN (when the switch has one), and `open_backout` runs.
6. With **Apply** on, the notes are added to the device's **Notes** tab.

## Next

You have walked the example ladder. In the plugin docs, continue with the tutorial-only topics: Git sync and publish, Preview run, Run Again, run history and cancel, the time-savings dashboard, permissions, and new scripts from the builder.
