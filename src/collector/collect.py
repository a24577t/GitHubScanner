"""Collection flow: authenticate, gather evidence for one organization."""
import json

from collector import transport


class RunFrameError(Exception):
    pass


def run_collect(api_url, org, out_dir, token, run_id=None, max_pages=100):
    identity = transport.get(api_url, "/user", token)
    if identity.status == 401:
        raise RunFrameError("authentication rejected by target (401 on /user)")

    transport.get(api_url, "/meta", token)
    transport.get(api_url, f"/orgs/{org}", token)
    transport.get(api_url, f"/orgs/{org}/repos?per_page=100", token)
    return 0
