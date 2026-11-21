# 11. Turn up a port with verify and rollback

## What you'll learn

- Several **Main** steps that each read earlier results through `results.<step>`.
- A step that runs **only when an earlier step failed**: `rollback` restores the port when `verify` (or `apply_change`) has `status == 'failed'`.
- A step that runs **only when an earlier step succeeded**: `close_out` runs when `verify` has `status == 'success'`.
- Passing a whole return value forward: `rollback` gets `results.snapshot.return_value`, the settings the first step saved.

This is the change pattern most engineers already follow by hand: save the running state, make the change, check it, and either put it back or close it out.

| Step | Runs when | Does |
| --- | --- | --- |
| `snapshot` | always | Saves the port's description, enabled, mode, VLANs, and status |
| `apply_change` | `snapshot` succeeded | Checks the VLAN exists at the site, then sets the port as an access port in **Planned** status |
| `verify` | `apply_change` succeeded | Reads the port back and compares it with the plan. Fails on any mismatch, or when **Simulate a failed verification** is on |
| `rollback` | `verify` failed, or `apply_change` failed | Restores every setting from `results.snapshot.return_value` and adds a note |
| `close_out` | `verify` succeeded | Sets the port **Active** and adds a note |

Exactly one of `rollback` and `close_out` runs; the other shows as **skipped**.

## Why a rolled-back run still shows Failed

Main steps keep going after a failure, which is what lets `rollback` run. The run's final status is still **Failed** whenever a Main step failed, even when the rollback worked. That is deliberate: the change did not land, and the run history should say so. The step list shows that the rollback succeeded.

## How to run

1. Run the [lab seed](../README.md#lab-setup). It creates VLANs 110 and 120 at each site.
2. Choose **Run** on **11. Turn up a port with verify and rollback**.
3. Pick **AMS01**, `ams01-acc-sw02`, and `Ethernet1/2`. Keep VLAN `110` and enter a description.
4. **Success path:** leave **Simulate a failed verification** off. `rollback` is skipped and `close_out` runs.
5. **Failure path:** turn **Simulate a failed verification** on. `verify` fails, `rollback` runs, and `close_out` is skipped.
6. With **Apply** off, every step only reports what it would do. With **Apply** on, the failure path really changes the port and then restores it; open the interface and its **Notes** tab to see both.

The device is never contacted. "Verify" reads Nautobot back, which stands in for checking the device.

## Next

[12. Next free management IP with a fallback prefix](12-next-free-ip-with-fallback.md) uses a failure to choose a different path instead of undoing one.
