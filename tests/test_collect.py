"""Collection behavior through the CLI seam against a scripted fake GitHub."""
import json
import tempfile
import unittest
from pathlib import Path

from fake_github import response, serve
from helpers import run_cli

TOKEN = "tok-secret-0123456789abcdef"

USER_OK = response(200, {"login": "operator", "id": 7})
META_OK = response(200, {"installed_version": "3.17.0"})
ORG_OK = response(200, {"login": "acme", "id": 42, "created_at": "2020-01-02T03:04:05Z"})


def repo(i):
    return {
        "id": i,
        "name": f"repo-{i}",
        "full_name": f"acme/repo-{i}",
        "visibility": "private",
        "fork": False,
        "archived": False,
        "created_at": "2021-06-07T08:09:10Z",
        "default_branch": "main",
    }


def collect(base_url, out, extra=None):
    return run_cli(
        ["collect", "--api-url", base_url, "--org", "acme", "--out", str(out)]
        + (extra or []),
        env={"GITHUB_TOKEN": TOKEN, "COLLECTOR_INSECURE_ALLOW_HTTP": "1"},
    )


class IdentityGate(unittest.TestCase):
    def test_401_on_identity_fails_run_frame_without_scaffold(self):
        script = {"/user": [response(401, {"message": "Bad credentials"})]}
        with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = collect(base, out)
            self.assertEqual(result.returncode, 2)
            self.assertIn("authentication", result.stderr.lower())
            self.assertFalse(out.exists())

    def test_authenticated_run_exits_orderly(self):
        script = {
            "/user": [USER_OK],
            "/meta": [META_OK],
            "/orgs/acme": [ORG_OK],
            "/orgs/acme/repos": [response(200, [repo(1)])],
        }
        with serve(script) as (base, recorder), tempfile.TemporaryDirectory() as tmp:
            result = collect(base, Path(tmp) / "out")
            self.assertEqual(result.returncode, 0, result.stderr)
            methods = {r["method"] for r in recorder.requests}
            self.assertEqual(methods, {"GET"}, "observation-only: GET requests exclusively")


if __name__ == "__main__":
    unittest.main()
