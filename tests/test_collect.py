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


def paged_script(pages):
    """Repos listing served page-by-page with Link rel=next headers."""
    responses = []
    for index, items in enumerate(pages, start=1):
        headers = {}
        if index < len(pages):
            headers["Link"] = f'<http://x/orgs/acme/repos?page={index + 1}>; rel="next"'
        responses.append(response(200, items, headers))
    return {
        "/user": [USER_OK],
        "/meta": [META_OK],
        "/orgs/acme": [ORG_OK],
        "/orgs/acme/repos": responses,
    }


class Pagination(unittest.TestCase):
    def test_multi_page_drain_states_pages_and_items_as_fact(self):
        script = paged_script([[repo(3), repo(1)], [repo(2)], [repo(4)]])
        with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = collect(base, out, ["--run-id", RUN_ID])
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(
                (out / "reports" / f"{RUN_ID}.json").read_text(encoding="utf-8")
            )
            self.assertEqual(report["listings"]["repositories"],
                             {"pages": 3, "items": 4, "complete": True})
            observed = json.loads(
                (out / "observed" / "repositories.json").read_text(encoding="utf-8")
            )
            self.assertEqual([r["id"] for r in observed["repositories"]], [1, 2, 3, 4])
            self.assertEqual(observed["state"], "collected")

    def test_max_pages_breach_preserves_partial_evidence_and_reports_incomplete(self):
        script = paged_script([[repo(1)], [repo(2)], [repo(3)]])
        with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = collect(base, out, ["--run-id", RUN_ID, "--max-pages", "2"])
            self.assertEqual(result.returncode, 0, result.stderr)
            raw = out / "evidence" / "raw" / RUN_ID
            self.assertTrue((raw / "repos.page-1.json").exists())
            self.assertTrue((raw / "repos.page-2.json").exists())
            self.assertFalse((raw / "repos.page-3.json").exists())
            report = json.loads(
                (out / "reports" / f"{RUN_ID}.json").read_text(encoding="utf-8")
            )
            self.assertEqual(report["listings"]["repositories"]["complete"], False)
            self.assertEqual(report["resource_states"]["repositories"], "incomplete")
            observed = json.loads(
                (out / "observed" / "repositories.json").read_text(encoding="utf-8")
            )
            self.assertEqual(observed["state"], "incomplete")
            self.assertEqual(observed["count"], 2)


class AppendOnlyRawEvidence(unittest.TestCase):
    def test_existing_run_id_rejected_without_touching_any_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            with serve(HAPPY_SCRIPT) as (base, _):
                self.assertEqual(collect(base, out, ["--run-id", RUN_ID]).returncode, 0)
            before = {p: p.read_bytes() for p in out.rglob("*") if p.is_file()}
            with serve(HAPPY_SCRIPT) as (base, _):
                result = collect(base, out, ["--run-id", RUN_ID])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(RUN_ID, result.stderr)
            after = {p: p.read_bytes() for p in out.rglob("*") if p.is_file()}
            self.assertEqual(before, after, "existing evidence must remain byte-identical")


class Degradation(unittest.TestCase):
    def _report(self, script, tmp):
        with serve(script) as (base, _):
            out = Path(tmp) / "out"
            result = collect(base, out, ["--run-id", RUN_ID])
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(
                (out / "reports" / f"{RUN_ID}.json").read_text(encoding="utf-8")
            )

    def test_403_on_meta_is_inaccessible_and_run_continues(self):
        script = dict(HAPPY_SCRIPT)
        script["/meta"] = [response(403, {"message": "Must have admin rights"})]
        with tempfile.TemporaryDirectory() as tmp:
            report = self._report(script, tmp)
            self.assertEqual(report["resource_states"]["meta"], "inaccessible")
            self.assertEqual(report["resource_states"]["repositories"], "collected")

    def test_ambiguous_404_is_inaccessible_never_absent(self):
        script = dict(HAPPY_SCRIPT)
        script["/orgs/acme"] = [response(404, {"message": "Not Found"})]
        with tempfile.TemporaryDirectory() as tmp:
            report = self._report(script, tmp)
            self.assertEqual(report["resource_states"]["org"], "inaccessible")

    def test_affirmative_absence_body_is_absent(self):
        script = dict(HAPPY_SCRIPT)
        script["/orgs/acme"] = [response(404, {"message": "Branch not protected"})]
        with tempfile.TemporaryDirectory() as tmp:
            report = self._report(script, tmp)
            self.assertEqual(report["resource_states"]["org"], "absent")

    def test_rate_limit_retry_is_recorded(self):
        script = dict(HAPPY_SCRIPT)
        script["/orgs/acme"] = [
            response(429, {"message": "rate limited"}, {"Retry-After": "0"}),
            ORG_OK,
        ]
        with tempfile.TemporaryDirectory() as tmp:
            report = self._report(script, tmp)
            self.assertEqual(report["resource_states"]["org"], "collected")
            self.assertEqual(report["rate_limit"]["occurrences"], 1)


if __name__ == "__main__":
    unittest.main()
