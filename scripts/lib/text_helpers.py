"""Shared helpers imported by filters and action scripts."""


def normalize_hostname(value):
    """Strip, lowercase, and replace spaces for hostname-style strings."""
    return str(value).strip().lower().replace(" ", "-")
