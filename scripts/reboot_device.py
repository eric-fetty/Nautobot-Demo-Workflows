"""Reboot Device

Created in the workflow builder. Edit it in the repository.
"""

# An admin reviews this file and sets ENABLED = True before a workflow step can run it.
ENABLED = False

PARAMETERS = {
    "hostname": {"type": "string", "required": True},
}


def run(params):
    """Do the work for the workflow step. Return a dict for later steps to read."""
    # Placeholder: replace this with the real work.
    # params holds: hostname
    print(f"Placeholder script ran with {sorted(params)}")
    return {"placeholder": True}
