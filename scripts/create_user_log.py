"""Create User Log

Created in the workflow builder. Edit it in the repository.
"""

PARAMETERS = {
    "comments": {"type": "string", "required": True, "help": "Comments"},
}


def run(params):
    """Do the work for the workflow step. Return a dict for later steps to read."""
    # Replace this with your logic.
    print(f"comments: {params.get('comments')!r}")
    return {"received": sorted(params)}
