# 08. Approve a maintenance reboot

## What you'll learn

- `approval_required: true` and Nautobot 3.2 Approval Workflow Definitions.
- That approving a run is configured in Nautobot (**Approvals → Workflow Definitions**), not in a Workflow Engine permission.
- Reusing the shared change-ticket include from rung 5.
- A `show_if` confirmation that only appears for a hard power cycle.

This workflow never reboots a device and never writes inventory. It only records the plan after approval.

## How to run

1. Run the [lab seed](../README.md#lab-setup) if you have not already.
2. After Git sync, open **Approvals → Workflow Definitions**.
3. Open **Workflow Engine: 08-approve-maintenance-reboot** and add at least one stage (an approver group and the minimum number of approvers). Until a stage exists, launches stay **Pending Approval**.
4. Launch the workflow for an AMS01 device with ticket `CHG0031245` and a soft reload.
5. Approve the run in **Approvals → Approval Dashboard**.
6. Open the run and confirm it planned the reboot without contacting the device.

If you do not have Nautobot 3.2, the approval setting is kept and has no effect; the run starts like any other workflow.

## Next

[09. Schedule inside a change window](09-schedule-change-window.md) ties a run to a ServiceNow change window, or to **Schedule for later** if you have no ServiceNow.
