"""Return the hostname it receives without changing inventory."""


def run(params):
    """Return a hostname without modifying inventory."""
    hostname = params["hostname"]
    print(f"Prepared hostname: {hostname}")
    return {"hostname": hostname}
