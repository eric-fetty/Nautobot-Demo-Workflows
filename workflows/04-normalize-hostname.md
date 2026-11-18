# 04. Normalize a hostname

## What you'll learn

- A custom Jinja filter shipped in `filters/string_filters.py`.
- How that filter imports a shared helper from `scripts/lib/text_helpers.py`.
- Using a filter both in a step parameter and in a `when` condition.

`normalize_for_dns` lowercases the value, trims it, and turns spaces and underscores into hyphens. This workflow never writes to inventory.

## How to run

1. Choose **Run** on **04. Normalize a hostname**.
2. Enter `My Router Host` or `bad_name_host`.
3. Run now and confirm the action received a DNS-normalized hostname such as `my-router-host` or `bad-name-host`.

You do not need the lab seed for this workflow.

## Next

[05. Record a planned change](05-record-planned-change.md) introduces a reusable input fragment included with Jinja.
