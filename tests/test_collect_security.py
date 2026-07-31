"""Dedicated-request collection at the fan-out seam (Slice 3 T1; V41's offline half).

The engine is descriptor-generic (ADR-0004), so these tests pin its behavior
through the shipped security-and-analysis descriptor: the dedicated
repository GET (ADR-0009; the issue #27 dedicated-request decision), the
object envelope extensions without the input-derived branch field, the
verbatim body, and the 404-as-evidence rule that feeds V54's inaccessible ·
absence-rule-unmatched-404 derivation.
"""
import json
import tempfile
import unittest
from pathlib import Path

from fake_github import response, serve
from test_collect import RUN_ID, collect, repo
from test_collect_fanout import (
    org_script, protection_path, rulesets_empty, security_body, security_path,
    security_ok,
)


def load(out, repo_dir):
    return json.loads(
        (out / "evidence" / "raw" / RUN_ID / "repos" / repo_dir /
         "security-and-analysis.json").read_text(encoding="utf-8"))


class RequestContract(unittest.TestCase):
    def test_dedicated_get_issued_once_per_repo_ascending_by_id(self):
        script = org_script([repo(9), repo(4)], **security_ok(4, 9),
                            **rulesets_empty(4, 9))
        with serve(script) as (base, recorder), \
                tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = collect(base, out, ["--run-id", RUN_ID])
            self.assertEqual(result.returncode, 0, result.stderr)
            dedicated = [r["path"] for r in recorder.requests
                         if r["path"] in (security_path(4), security_path(9))]
            # One bare dedicated GET per repository - no query string, no
            # pagination - in canonical ascending-id order.
            self.assertEqual(dedicated, [security_path(4), security_path(9)])

    def test_object_envelope_extensions_without_branch_or_list_fields(self):
        script = org_script([repo(1)], **security_ok(1))
        with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(collect(base, out, ["--run-id", RUN_ID]).returncode, 0)
            record = load(out, "1-repo-1")
            envelope = record["envelope"]
            self.assertEqual(envelope["repo"],
                             {"id": 1, "full_name": "acme/repo-1"})
            self.assertEqual(envelope["resource"], "security-and-analysis")
            self.assertTrue(envelope["url"].endswith(security_path(1)))
            # No required per-repository input, so the input-derived branch
            # extension never appears; object requests carry no list fields.
            for absent in ("branch", "page", "item_count", "incomplete"):
                self.assertNotIn(absent, envelope)
            self.assertEqual(json.loads(record["body_text"]),
                             security_body(1))

    def test_404_metadata_response_is_persisted_verbatim_evidence(self):
        # V54's collection half: no absence anchor exists, so the 404 is
        # partial evidence persisted verbatim - never a fabricated absence.
        script = org_script(
            [repo(1)],
            **{security_path(1): [response(404, {"message": "Not Found"})]},
        )
        with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(collect(base, out, ["--run-id", RUN_ID]).returncode, 0)
            record = load(out, "1-repo-1")
            self.assertEqual(record["envelope"]["status"], 404)
            self.assertEqual(json.loads(record["body_text"]),
                             {"message": "Not Found"})


if __name__ == "__main__":
    unittest.main()
