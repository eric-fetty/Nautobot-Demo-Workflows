"""Example action script that returns the comments it receives."""


def run(params):
    """Return the commentsfor demonstration purposes."""
    commment = params["comments"]
    print(f"Comments: {commment}")
    return {"comments": commment}