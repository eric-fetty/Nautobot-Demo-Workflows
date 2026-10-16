"""Example action script that returns the hostname it receives."""


def run(params):
    """Return a hostname without modifying inventory."""
    hostname = params["hostname"]
    print(f"Prepared hostname: {hostname}")
    return {"hostname": hostname}
