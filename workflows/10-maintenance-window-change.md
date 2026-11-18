# 10. Maintenance-window change

## What you'll learn

This capstone combines earlier rungs:

- A table of VLANs and a several-objects device picker.
- The shared change-ticket include.
- A Before reachability check, a main plan/apply step, and Always-after steps.
- A journal entry when Apply is on and the main step succeeded.
- A backout note when the main step failed. Always-after steps still run after a failure; this one is selected by a condition on `results.plan_or_apply.status`.
- Nautobot approval and a ServiceNow change-window declaration, like rungs 8 and 9.

With Apply off, nothing is written. With Apply on, lab VLANs are created (or reused) at the location and a journal entry is added to the first device when the main step succeeds. The device is never contacted. The reachability check is simulated.

## How to run

1. Run the [lab seed](../README.md#lab-setup) if you have not already.
2. After Git sync, open **Approvals → Workflow Definitions**, find **Workflow Engine: 10-maintenance-window-change**, and add at least one stage.
3. Choose **Run** on **10. Maintenance-window change**.
4. Pick **AMS01**, one or two active switches, VLAN `120` / `voice-floor-2`, and ticket `CHG0031246`.
5. Leave Apply off. Under **When should it run?**, choose **Schedule for later** (or **Run now** after you are comfortable with approval).
6. Approve the run, then open it and confirm the Before check, the plan, and that the backout step was skipped.
7. Optionally run again with Apply on to create the lab VLANs and a journal entry.

**In the change window** needs a real ServiceNow. In this lab, use **Schedule for later** or **Run now**, as in rung 9.

## Next

You have walked the example ladder. In the plugin docs, continue with the tutorial-only topics: Git sync and publish, Preview run, Run Again, run history and cancel, the time-savings dashboard, permissions, and new scripts from the builder.
