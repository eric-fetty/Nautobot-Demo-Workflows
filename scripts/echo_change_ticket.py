"""Echo a change ticket and summary. Never writes to Nautobot inventory."""

PARAMETERS = {
    "change_ticket": {"type": "string", "required": True},
    "summary": {"type": "string", "required": True},
}


def run(params):
    """Return the ticket and summary that were entered."""
    ticket = str(params.get("change_ticket") or "").strip()
    summary = str(params.get("summary") or "").strip()
    print(f"Change {ticket}: {summary}")
    print("Nothing was changed in Nautobot.")
    return {"change_ticket": ticket, "summary": summary, "applied": False}
