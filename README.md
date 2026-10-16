# Nautobot Demo Workflows

Trusted workflow source for [Nautobot Workflow Engine](https://github.com/eric-fetty/Nautobot_Workflow_Engine).
Use this repository to get a syncable PoC running quickly and to capture documentation screenshots.

These examples are non-destructive: they echo values and demonstrate filters/approval.
They do not create or change Nautobot inventory objects.

## Repository layout

```text
workflows/                 # Workflow YAML (workflow_dir)
  echo-hostname.yaml       # Getting-started tutorial
  custom-filter-demo.yaml  # Repo-backed Jinja filters + scripts/lib
  approval-required-demo.yaml
scripts/
  echo_hostname.py
  lib/
    text_helpers.py        # Shared helpers imported by filters/scripts
filters/
  string_filters.py        # Exposes normalize_for_dns
```

## Included workflows

| Workflow | Key | What it shows |
| --- | --- | --- |
| Echo Hostname | `echo-hostname` | Docs getting-started path: form → immediate run → logs/results |
| Custom Filter Demo | `custom-filter-demo` | `normalize_for_dns` filter and `scripts/lib` imports |
| Approval Required Demo | `approval-required-demo` | `approval_required: true` (Nautobot 3.2+) |

## Configure in Nautobot

1. Install and configure [nautobot-workflow-engine](https://github.com/eric-fetty/Nautobot_Workflow_Engine) (`workflow_dir: workflows`, `filters_dir: filters`).
2. Add a **Git Repository** pointing at this repo (or a fork/clone Nautobot can reach).
3. Enable the Workflow Engine content type for that repository and synchronize.
4. Confirm the three **Examples** workflows appear under Workflow Engine.

### Echo Hostname (screenshots / first run)

1. Open **Echo Hostname**.
2. Enter `router.example.com`.
3. Choose immediate execution.
4. Open the run and inspect status, returned hostname, and execution logs.

### Custom Filter Demo

1. Open **Custom Filter Demo**.
2. Enter a value such as `My Router Host` or `bad_name_host`.
3. Run immediately; the action receives the DNS-normalized hostname (spaces → hyphens, lowercased; underscores → hyphens via the filter).

### Approval Required Demo (Nautobot 3.2+)

1. After sync, open **Approvals → Workflow Definitions**.
2. Open **Workflow Engine: approval-required-demo** and add at least one approval stage.
3. Launch the workflow; the run stays **Pending Approval** until approved.

## Authoring reference

See the engine docs:

- [Getting started](https://github.com/eric-fetty/Nautobot_Workflow_Engine/blob/main/docs/user/app_getting_started.md)
- [Workflow authoring](https://github.com/eric-fetty/Nautobot_Workflow_Engine/blob/main/docs/user/app_use_cases.md)
- [Custom filters](https://github.com/eric-fetty/Nautobot_Workflow_Engine/blob/main/docs/dev/extending.md)
