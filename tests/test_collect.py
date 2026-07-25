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


HAPPY_SCRIPT = {
    "/user": [USER_OK],
    "/meta": [META_OK],
    "/orgs/acme": [ORG_OK],
    "/orgs/acme/repos": [response(200, [repo(2), repo(1)])],
}

RUN_ID = "20260724T000000Z"


class SinglePageScaffold(unittest.TestCase):
    def test_scaffold_layout_envelopes_observed_and_reports(self):
        with serve(HAPPY_SCRIPT) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = collect(base, out, ["--run-id", RUN_ID])
            self.assertEqual(result.returncode, 0, result.stderr)

            raw = out / "evidence" / "raw" / RUN_ID
            for name in ("user.json", "meta.json", "org.json", "repos.page-1.json"):
                self.assertTrue((raw / name).exists(), f"missing raw/{name}")

            envelope = json.loads((raw / "org.json").read_text(encoding="utf-8"))["envelope"]
            for field in ("url", "method", "status", "captured_at", "run_id"):
                self.assertIn(field, envelope)
            self.assertEqual(envelope["method"], "GET")
            self.assertEqual(envelope["status"], 200)

            observed_org = json.loads((out / "observed" / "org.json").read_text(encoding="utf-8"))
            self.assertEqual(observed_org["state"], "collected")
            self.assertEqual(observed_org["org"]["login"], "acme")

            observed_repos = json.loads(
                (out / "observed" / "repositories.json").read_text(encoding="utf-8")
            )
            self.assertEqual(observed_repos["state"], "collected")
            self.assertEqual(observed_repos["count"], 2)
            self.assertEqual(
                [r["id"] for r in observed_repos["repositories"]], [1, 2],
                "repositories sorted by stable identity",
            )
            self.assertEqual(
                sorted(observed_repos["repositories"][0]),
                ["archived", "created_at", "default_branch", "fork", "full_name",
                 "id", "name", "visibility"],
            )

            self.assertTrue((out / "reports" / f"{RUN_ID}.json").exists())
            self.assertTrue((out / "reports" / f"{RUN_ID}.md").exists())


if __name__ == "__main__":
    unittest.main()
