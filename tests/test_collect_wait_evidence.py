"""Envelope retention of transport wait evidence (Slice 2 T7; E1 refinement).

The ratified refinement: raw envelopes retain `wait_records` (order exactly
as transport produced, allowlisted headers only; legacy absence reads empty)
and `termination_reason` (only when one exists; never synthesized).
"""
import contextlib
import io
import json
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path

from collector import transport
from collector.collect import run_collect
from collector.transport import RATE_LIMIT_HEADERS
from fake_github import response, serve
from test_collect import META_OK, ORG_OK, RUN_ID, USER_OK, repo

PROTECTION = "/repos/acme/repo-1/branches/main/protection"
PROTECTION_BODY = {"enforce_admins": {"enabled": True}}


def org_script(**endpoints):
    return {
        "/user": [USER_OK], "/meta": [META_OK], "/orgs/acme": [ORG_OK],
        "/orgs/acme/repos": [response(200, [repo(1)])],
        **endpoints,
    }


def collect_in_proc(base, out):
    """Run collection in-process with sleeps suppressed (wait records keep
    their requested durations; only real waiting is elided)."""
    with mock.patch.object(transport.SYSTEM_CLOCK, "sleep", lambda s: None), \
            contextlib.redirect_stderr(io.StringIO()):
        return run_collect(base, "acme", out, "tok-inproc", run_id=RUN_ID)


def load_envelope(out, *parts):
    path = Path(out, "evidence", "raw", RUN_ID, *parts)
    return json.loads(path.read_text(encoding="utf-8"))["envelope"]


class WaitRecordRetention(unittest.TestCase):
    def test_waitless_envelopes_retain_empty_records_and_no_reason(self):
        script = org_script(**{PROTECTION: [response(200, PROTECTION_BODY)]})
        with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(collect_in_proc(base, out), 0)
            for parts in (("user.json",), ("org.json",),
                          ("repos.page-1.json",),
                          ("repos", "1-repo-1",
                           "default-branch-protection.json")):
                envelope = load_envelope(out, *parts)
                self.assertEqual(envelope["wait_records"], [], parts)
                self.assertNotIn("termination_reason", envelope, parts)

    def test_records_preserve_transport_order_and_allowlisted_headers(self):
        script = org_script(**{PROTECTION: [
            response(500, {"message": "boom"},
                     headers={"X-Noise": "never-evidence"}),
            response(429, {"message": "slow down"},
                     headers={"Retry-After": "0",
                              "X-RateLimit-Remaining": "0",
                              "X-GitHub-Request-Id": "never-evidence"}),
            response(200, PROTECTION_BODY),
        ]})
        with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(collect_in_proc(base, out), 0)
            envelope = load_envelope(
                out, "repos", "1-repo-1", "default-branch-protection.json")
            self.assertEqual(envelope["status"], 200)
            self.assertEqual(envelope["attempts"], 3)
            self.assertNotIn("termination_reason", envelope)
            records = envelope["wait_records"]
            self.assertEqual([r["category"] for r in records],
                             ["retry", "retry-after"])
            self.assertEqual([r["status"] for r in records], [500, 429])
            self.assertEqual([r["outcome"] for r in records],
                             ["retried", "retried"])
            for record in records:
                self.assertEqual(sorted(record), [
                    "attempt", "category", "elapsed_seconds",
                    "maximum_seconds", "outcome", "rate_limit_headers",
                    "reason", "requested_seconds", "status", "url",
                ])
                self.assertLessEqual(set(record["rate_limit_headers"]),
                                     set(RATE_LIMIT_HEADERS))

    def test_terminal_refusal_retains_refused_record_and_reason(self):
        script = org_script(**{PROTECTION: [
            response(429, {"message": "slow down"},
                     headers={"Retry-After": "9999"}),
        ]})
        with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(collect_in_proc(base, out), 0)
            envelope = load_envelope(
                out, "repos", "1-repo-1", "default-branch-protection.json")
            self.assertEqual(envelope["status"], 429)
            self.assertEqual(envelope["termination_reason"],
                             "retry-after-exceeds-maximum")
            [record] = envelope["wait_records"]
            self.assertEqual(record["category"], "retry-after")
            self.assertEqual(record["outcome"], "retry-after-exceeds-maximum")
            self.assertEqual(record["requested_seconds"], 9999)
            self.assertEqual(record["elapsed_seconds"], 0)


if __name__ == "__main__":
    unittest.main()
