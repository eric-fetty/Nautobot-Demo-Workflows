"""Jobs shipped with the Workflow Engine examples repository."""

from nautobot.apps.jobs import register_jobs

from .seed_lab import SeedWorkflowEngineLab

register_jobs(SeedWorkflowEngineLab)
