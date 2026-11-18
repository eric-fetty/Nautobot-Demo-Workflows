# Nautobot Demo Workflows

Example workflows for [Nautobot Workflow Engine](https://github.com/eric-fetty/Nautobot_Workflow_Engine).

This is the canonical examples repository. Use it to get a lab or proof of concept running quickly, and to learn the plugin one feature at a time. The plugin's [Examples tutorial](https://github.com/eric-fetty/Nautobot_Workflow_Engine/blob/develop/docs/user/examples_tutorial.md) walks the same ladder with screenshots of the UI.

The first five examples never change Nautobot inventory. Examples 6–10 have an **Apply these changes in Nautobot** switch that defaults to off. Leave it off to only plan. Turn it on only in a lab, to make small inventory changes such as creating VLANs or adding a journal entry. None of these examples contact or reboot a live network device, and none of them require AWX.

## The ladder

Work through the examples in order. Each one adds a feature and points to the next.

| # | Workflow | Key | What you'll learn |
| --- | --- | --- | --- |
| 1 | [Echo a hostname](workflows/01-echo-hostname.md) | `01-echo-hostname` | Launch form, Run now, run details and logs |
| 2 | [Reserve a VLAN ID](workflows/02-reserve-vlan-id.md) | `02-reserve-vlan-id` | Whole-number limits, help text, placeholders, regex validation |
| 3 | [Plan an interface description](workflows/03-plan-interface-description.md) | `03-plan-interface-description` | Object pickers, `depends_on`, `show_if`, a step condition |
| 4 | [Normalize a hostname](workflows/04-normalize-hostname.md) | `04-normalize-hostname` | Repo-backed Jinja filters and `scripts/lib` helpers |
| 5 | [Record a planned change](workflows/05-record-planned-change.md) | `05-record-planned-change` | Reusable inputs with `{% include %}` |
| 6 | [Add VLANs](workflows/06-add-vlans.md) | `06-add-vlans` | Table + CSV import, lists, several objects, optional apply |
| 7 | [Turn up a port](workflows/07-turn-up-a-port.md) | `07-turn-up-a-port` | Before / main / always-after steps, conditions on earlier results |
| 8 | [Approve a maintenance reboot](workflows/08-approve-maintenance-reboot.md) | `08-approve-maintenance-reboot` | Nautobot 3.2 approval definitions (plan only, no reboot) |
| 9 | [Schedule inside a change window](workflows/09-schedule-change-window.md) | `09-schedule-change-window` | Schedule for later, ServiceNow change window, cancel, Run Again |
| 10 | [Maintenance-window change](workflows/10-maintenance-window-change.md) | `10-maintenance-window-change` | Capstone: table, pre/post, approval, change window, optional apply and backout |

## Lab setup

You need Nautobot 3.x with [Nautobot Workflow Engine](https://github.com/eric-fetty/Nautobot_Workflow_Engine) installed, and its background workers running. AWX and a real ServiceNow are optional and are not required for this ladder.

### 1. Add this repository in Nautobot

1. Add a **Git Repository** pointing at this repo (or a fork or clone Nautobot can reach), on the branch you want to use.
2. Under **Provides**, enable the Workflow Engine content (workflows). To run the lab seed as a Job, also enable **jobs**.
3. Synchronize the repository.
4. Confirm the ten **Examples** workflows appear on the Workflows list.

If you enable jobs, also add an empty `__init__.py` at the repository root (already present here) so Nautobot can import the Job module. Jobs from Git are disabled until you enable them.

### 2. Seed the lab inventory

Examples 3 and 6–10 need a few locations, devices, interfaces, and prefixes. The seed is idempotent and labeled lab-only. **Do not run it in production.**

It creates:

- Locations **AMS01** and **NYC02**
- Access and distribution switches at each site, with `Management1`, `Ethernet1/1`, `Ethernet1/2`, and `Ethernet1/48`
- Prefixes `10.20.0.0/16` and `10.21.0.0/16`
- A fake External Integration named **ServiceNow (demo)** so example 9 can declare a change window. It does not talk to a real ServiceNow.

**Option A — Job (easiest when Jobs content is enabled)**

1. Enable **jobs** on the Git repository and synchronize.
2. Open **Jobs**, find **Seed Workflow Engine lab data** (grouping *Workflow Engine examples*), and enable it.
3. Run the Job once.

**Option B — nbshell**

After the repository has been synchronized, in `nautobot-server nbshell` or `nautobot-server shell`:

```python
from pathlib import Path
from django.conf import settings

matches = list(Path(settings.GIT_ROOT).glob("*/jobs/seed_lab.py"))
if len(matches) != 1:
    raise SystemExit(f"Expected one seed file, found: {matches}")
namespace = {}
exec(matches[0].read_text(encoding="utf-8"), namespace)
namespace["seed"]()
```

Examples 1, 2, 4, and 5 can be run before you seed.

### 3. Permissions and approvals

Grant operators the ready-made **Workflow Engine: Run workflows** and **Workflow Engine: View runs** permissions. Approving a run is not a Workflow Engine permission: for examples 8 and 10, add at least one stage under **Approvals → Workflow Definitions** for `Workflow Engine: 08-approve-maintenance-reboot` and `Workflow Engine: 10-maintenance-window-change`.

## Repository layout

```text
workflows/                 # Workflow YAML (workflow_dir)
  01-echo-hostname.yaml    # … through 10-maintenance-window-change.yaml
  01-echo-hostname.md      # Short "what you'll learn / how to run / next" notes
  templates/inputs/
    standard_change_inputs.yaml   # Shared change-ticket fragment
scripts/                   # Nautobot action scripts (def run(params))
  lib/text_helpers.py
jobs/                      # Lab-only seed Job
  seed_lab.py
filters/
  string_filters.py        # Exposes normalize_for_dns
```

## Authoring reference

See the engine docs:

- [Examples tutorial](https://github.com/eric-fetty/Nautobot_Workflow_Engine/blob/develop/docs/user/examples_tutorial.md)
- [Getting started](https://github.com/eric-fetty/Nautobot_Workflow_Engine/blob/develop/docs/user/app_getting_started.md)
- [Workflow authoring](https://github.com/eric-fetty/Nautobot_Workflow_Engine/blob/develop/docs/user/app_use_cases.md)
- [Custom filters](https://github.com/eric-fetty/Nautobot_Workflow_Engine/blob/develop/docs/dev/extending.md)
