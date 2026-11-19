#!/usr/bin/env python3
"""Validate every workflow YAML against the Workflow Engine schema and semantic checks.

The plugin package imports Nautobot at import time. This script loads the
schema, normalize, and validate modules from a source checkout without
importing nautobot_workflow_engine/__init__.py, and stubs
get_jinja_environment so template checks can run without Django.

Set PLUGIN_SRC to the plugin repository root (the directory that contains
nautobot_workflow_engine/). GitHub Actions checks out
eric-fetty/Nautobot_Workflow_Engine at develop by default.
"""

from __future__ import annotations

import os
import re
import sys
import types
from pathlib import Path

import yaml

INCLUDE_PATTERN = re.compile(r"""^\s*\{%\s*include\s+["'](?P<path>[\w/.\-]+)["']\s*%}""")
REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = REPO_ROOT / "workflows"


def process_includes(path: Path) -> str:
    """Replace {% include %} lines the same way the plugin Git sync does."""
    content = path.read_text(encoding="utf-8")
    for line in content.splitlines():
        match = INCLUDE_PATTERN.search(line)
        if not match:
            continue
        template_file = path.parent / match.group("path")
        if not template_file.is_file():
            raise FileNotFoundError(f"{path}: include not found: {template_file}")
        content = content.replace(line, template_file.read_text(encoding="utf-8"))
    return content


def load_plugin(plugin_src: Path):
    """Import schema.normalize and schema.validate without importing Nautobot."""
    package_dir = plugin_src / "nautobot_workflow_engine"
    if not package_dir.is_dir():
        raise SystemExit(f"PLUGIN_SRC does not look like the plugin repo: {plugin_src}")

    package = types.ModuleType("nautobot_workflow_engine")
    package.__path__ = [str(package_dir)]
    package.__file__ = str(package_dir / "__init__.py")
    package.__package__ = "nautobot_workflow_engine"
    sys.modules["nautobot_workflow_engine"] = package

    from jinja2 import Undefined
    from jinja2.sandbox import ImmutableSandboxedEnvironment

    executors = types.ModuleType("nautobot_workflow_engine.executors")

    def get_jinja_environment(repo=None, *, strict=False):
        return ImmutableSandboxedEnvironment(undefined=Undefined)

    executors.get_jinja_environment = get_jinja_environment
    sys.modules["nautobot_workflow_engine.executors"] = executors

    from nautobot_workflow_engine.schema.normalize import normalize
    from nautobot_workflow_engine.schema.validate import reserved_key_errors, validate

    return normalize, reserved_key_errors, validate


def script_exists(script: str) -> bool:
    if not script:
        return False
    return (REPO_ROOT / script).is_file()


def main() -> int:
    plugin_src = Path(os.environ.get("PLUGIN_SRC", "")).expanduser()
    if not plugin_src.parts:
        plugin_src = Path(os.environ.get("GITHUB_WORKSPACE", "/tmp")) / "plugin"
    normalize, reserved_key_errors, validate = load_plugin(plugin_src)

    paths = sorted(p for p in WORKFLOWS_DIR.glob("*.yaml") if p.is_file())
    if not paths:
        print(f"No workflow YAML files in {WORKFLOWS_DIR}", file=sys.stderr)
        return 1

    failed = 0
    for path in paths:
        rel = path.relative_to(REPO_ROOT)
        try:
            raw = process_includes(path)
            definition = yaml.safe_load(raw)
        except Exception as exc:
            print(f"FAIL {rel}: could not load YAML: {exc}")
            failed += 1
            continue
        if not isinstance(definition, dict):
            print(f"FAIL {rel}: workflow must be a mapping")
            failed += 1
            continue
        errors = [str(err) for err in reserved_key_errors(definition)]
        canonical = normalize(definition)
        errors.extend(str(err) for err in validate(canonical, enforce_policy=False, check_scripts=False))
        for action in (
            list(canonical.get("pre_actions") or [])
            + list(canonical.get("actions") or [])
            + list(canonical.get("post_actions") or [])
        ):
            if action.get("type") == "nautobot":
                script = action.get("script") or ""
                if not script_exists(script):
                    errors.append(f"script file missing: {script}")
        if errors:
            print(f"FAIL {rel}:")
            for error in errors:
                print(f"  - {error}")
            failed += 1
        else:
            print(f"OK   {rel} ({canonical.get('key')})")

    if failed:
        print(f"{failed} workflow(s) failed validation", file=sys.stderr)
        return 1
    print(f"{len(paths)} workflow(s) validated against the plugin schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
