# 09. Schedule inside a change window

## What you'll learn

- The three launch options: **Run now**, **Schedule for later**, and **In the change window**.
- How a workflow declares a ServiceNow change window (`schedule.servicenow`) and which input holds the ticket.
- That **In the change window** needs a working ServiceNow connection. The lab seed creates a fake External Integration named **ServiceNow (demo)** so the setting can be saved, but it does not talk to a real ServiceNow. Use **Schedule for later** in a lab that has no ServiceNow.
- Cancelling a run that is still **Scheduled** or **Pending Approval**.

This workflow never writes to inventory. Before steps (none here) would run when the schedule is created, and a failure would block the booking.

## How to run

1. Run the [lab seed](../README.md#lab-setup) so the **ServiceNow (demo)** integration exists.
2. Choose **Run** on **09. Schedule inside a change window**.
3. Enter ticket `CHG0031245` and a short summary.
4. Under **When should it run?**, choose **Schedule for later**, pick a time a few minutes ahead, and submit.
5. Open **Workflows → Run History**, open the scheduled run, and try **Cancel Run** on a second test booking if you want to see that path.
6. Leave one booking in place and confirm it runs at the scheduled time, then try **Run Again** on the finished run. That opens the launch form with the earlier inputs (`?from_run=<id>`).

**In the change window** will not succeed against the fake ServiceNow URL. Use it only when you have pointed an External Integration at a real instance and enabled the *Sync ServiceNow Scheduled Workflows* job, as described in the plugin's integration guide.

## Next

[10. Maintenance-window change](10-maintenance-window-change.md) is the capstone: table input, pre/post steps, approval, a change window, and an optional apply with a backout note on failure.
