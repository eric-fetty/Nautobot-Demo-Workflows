"""Record a backout plan when a maintenance change did not succeed. Never changes devices."""

PARAMETERS = {
    "change_ticket": {"type": "string", "required": True},
    "location": {"type": "string", "required": False},
    "reason": {"type": "string", "required": False},
}


def run(params):
    """Return a backout note. This script does not revert live network state."""
    from scripts.lib.params import as_text
    ticket = str(params.get("change_ticket") or "").strip()
    location = as_text(params.get("location"))
    reason = as_text(params.get("reason")) or "The main step did not succeed."
    message = f"Backout plan for {ticket} at {location or 'the site'}: leave devices unchanged and re-run after the failure is understood. Reason: {reason}"
    print(message)
    return {"change_ticket": ticket, "message": message, "applied": False}
