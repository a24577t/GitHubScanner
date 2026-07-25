"""Taxonomy behavior through the CLI seam: degradation, 404s, malformed bodies."""
import json
import tempfile
import unittest
from pathlib import Path

from fake_github import response, serve
from test_collect import HAPPY_SCRIPT, ORG_OK, RUN_ID, collect, paged_script, repo

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

    def test_403_with_mixed_case_ratelimit_header_retries_and_records_wait(self):
        script = dict(HAPPY_SCRIPT)
        script["/orgs/acme"] = [
            response(403, {"message": "API rate limit exceeded"},
                     {"X-RateLimit-Remaining": "0"}),
            ORG_OK,
        ]
        with tempfile.TemporaryDirectory() as tmp:
            report = self._report(script, tmp)
            self.assertEqual(report["resource_states"]["org"], "collected")
            self.assertEqual(report["rate_limit"]["occurrences"], 1)

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


class MalformedResponses(unittest.TestCase):
    def _run(self, script, tmp):
        out = Path(tmp) / "out"
        with serve(script) as (base, _):
            result = collect(base, out, ["--run-id", RUN_ID])
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(
            (out / "reports" / f"{RUN_ID}.json").read_text(encoding="utf-8")
        )
        return out, report

    def test_malformed_2xx_org_body_is_failed_and_derives_no_values(self):
        script = dict(HAPPY_SCRIPT)
        script["/orgs/acme"] = [response(200, None)]
        script["/orgs/acme"][0]["body"] = "{not-json"
        with tempfile.TemporaryDirectory() as tmp:
            out, report = self._run(script, tmp)
            self.assertEqual(report["resource_states"]["org"], "failed")
            observed = json.loads(
                (out / "observed" / "org.json").read_text(encoding="utf-8")
            )
            self.assertEqual(observed["state"], "failed")
            self.assertIsNone(observed["org"])

    def test_malformed_2xx_listing_page_is_failed(self):
        script = dict(HAPPY_SCRIPT)
        script["/orgs/acme/repos"] = [response(200, None)]
        script["/orgs/acme/repos"][0]["body"] = "]broken["
        with tempfile.TemporaryDirectory() as tmp:
            out, report = self._run(script, tmp)
            self.assertEqual(report["resource_states"]["repositories"], "failed")
            observed = json.loads(
                (out / "observed" / "repositories.json").read_text(encoding="utf-8")
            )
            self.assertEqual(observed["state"], "failed")
            self.assertEqual(observed["count"], 0)

    def test_2xx_org_with_valid_non_object_json_is_failed(self):
        script = dict(HAPPY_SCRIPT)
        script["/orgs/acme"] = [response(200, [1, 2, 3])]
        with tempfile.TemporaryDirectory() as tmp:
            out, report = self._run(script, tmp)
            self.assertEqual(report["resource_states"]["org"], "failed")
            observed = json.loads(
                (out / "observed" / "org.json").read_text(encoding="utf-8")
            )
            self.assertEqual(observed["state"], "failed")
            self.assertIsNone(observed["org"])
            raw = out / "evidence" / "raw" / RUN_ID / "org.json"
            self.assertIn("[1, 2, 3]", raw.read_text(encoding="utf-8"))

    def test_2xx_listing_page_with_valid_non_array_json_is_failed(self):
        script = dict(HAPPY_SCRIPT)
        script["/orgs/acme/repos"] = [response(200, {"message": "unexpected"})]
        with tempfile.TemporaryDirectory() as tmp:
            out, report = self._run(script, tmp)
            self.assertEqual(report["resource_states"]["repositories"], "failed")
            observed = json.loads(
                (out / "observed" / "repositories.json").read_text(encoding="utf-8")
            )
            self.assertEqual(observed["state"], "failed")
            self.assertEqual(observed["count"], 0)

    def test_non_object_array_entries_never_become_repository_entities(self):
        script = dict(HAPPY_SCRIPT)
        script["/orgs/acme/repos"] = [response(200, [repo(1), 123, "str"])]
        with tempfile.TemporaryDirectory() as tmp:
            out, report = self._run(script, tmp)
            self.assertEqual(report["resource_states"]["repositories"], "failed")
            observed = json.loads(
                (out / "observed" / "repositories.json").read_text(encoding="utf-8")
            )
            self.assertEqual(observed["state"], "failed")
            self.assertEqual(observed["repositories"], [])

    def test_non_2xx_later_page_preserves_earlier_pages_and_reports_incomplete(self):
        script = paged_script([[repo(1)], [repo(2)]])
        # page 2 fails persistently (survives the bounded retry policy)
        script["/orgs/acme/repos"][1] = response(500, {"message": "boom"})
        script["/orgs/acme/repos"].append(response(500, {"message": "boom"}))
        with tempfile.TemporaryDirectory() as tmp:
            out, report = self._run(script, tmp)
            raw = out / "evidence" / "raw" / RUN_ID
            self.assertTrue((raw / "repos.page-1.json").exists())
            self.assertTrue((raw / "repos.page-2.json").exists())
            self.assertEqual(report["listings"]["repositories"]["complete"], False)
            self.assertEqual(report["resource_states"]["repositories"], "failed")
            observed = json.loads(
                (out / "observed" / "repositories.json").read_text(encoding="utf-8")
            )
            self.assertEqual(observed["state"], "failed")
            self.assertEqual([r["id"] for r in observed["repositories"]], [1])


if __name__ == "__main__":
    unittest.main()