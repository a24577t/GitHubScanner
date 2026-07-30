"""Execution/wait visibility aggregation from retained evidence (T7; V30).

Every figure derives from the retained tree alone: wait categories and
seconds from retained wait_records, terminations from retained
termination_reason, planned requests from retained inventory via canonical
discovery — planned is never conflated with attempts.
"""
import tempfile
import unittest
from pathlib import Path

from collector.derive import run_summary
from test_derive_resources import (
    PROTECTION_BODY, RUN, page_record, protection, record, repo_item,
    write_tree,
)


def slept(category, requested, attempt=1, outcome="retried"):
    return {
        "category": category, "attempt": attempt, "status": 403,
        "url": "https://api.example/x", "rate_limit_headers": {},
        "requested_seconds": requested, "elapsed_seconds": float(requested),
        "maximum_seconds": 3900, "outcome": outcome, "reason": None,
    }


def refused(category, requested, outcome):
    return {**slept(category, requested), "elapsed_seconds": 0,
            "outcome": outcome}


def execution(out):
    return run_summary(out, RUN)["execution"]


class WaitVisibility(unittest.TestCase):
    def test_categories_seconds_max_and_terminations(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            ok = record(200, PROTECTION_BODY,
                        wait_records=[slept("retry", 1),
                                      slept("retry-after", 30)])
            refused_park = record(
                403, {"message": "limit"},
                headers={"x-ratelimit-remaining": "0"},
                wait_records=[refused("primary-park", 5000,
                                      "rate_limit_reset_exceeds_maximum_park")],
                termination_reason="rate_limit_reset_exceeds_maximum_park")
            renewed = record(
                403, {"message": "limit"},
                headers={"x-ratelimit-remaining": "0"},
                wait_records=[slept("primary-park", 100,
                                    outcome="renewed-exhaustion")],
                termination_reason="rate_limit_renewed_exhaustion")
            write_tree(out, [page_record([repo_item(1), repo_item(2),
                                          repo_item(3)])],
                       [("1-repo-1", "default-branch-protection.json", ok),
                        ("2-repo-2", "default-branch-protection.json",
                         refused_park),
                        ("3-repo-3", "default-branch-protection.json",
                         renewed)])
            waits = execution(out)["waits"]
            self.assertEqual(waits["retry"],
                             {"count": 1, "requested_seconds": 1,
                              "slept_seconds": 1.0})
            self.assertEqual(waits["retry-after"],
                             {"count": 1, "requested_seconds": 30,
                              "slept_seconds": 30.0})
            self.assertEqual(waits["primary-park"],
                             {"count": 1, "requested_seconds": 100,
                              "slept_seconds": 100.0})
            self.assertEqual(waits["refused"], 1)
            self.assertEqual(waits["max_single_wait_seconds"], 100)
            self.assertEqual(waits["total_wait_seconds"], 131)
            self.assertEqual(execution(out)["terminations"], {
                "rate_limit_renewed_exhaustion": 1,
                "rate_limit_reset_exceeds_maximum_park": 1,
            })

    def test_legacy_tree_without_retention_reads_empty(self):
        # V40: pre-refinement envelopes carry no wait_records or
        # termination_reason; readers treat absence as empty, never crash.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [protection("1-repo-1", 200, PROTECTION_BODY)])
            block = execution(out)
            for category in ("primary-park", "retry-after", "retry"):
                self.assertEqual(block["waits"][category],
                                 {"count": 0, "requested_seconds": 0,
                                  "slept_seconds": 0})
            self.assertEqual(block["waits"]["refused"], 0)
            self.assertEqual(block["waits"]["max_single_wait_seconds"], 0)
            self.assertEqual(block["terminations"], {})


class ScanTolerance(unittest.TestCase):
    def test_crafted_junk_types_never_derail_aggregation(self):
        # Scan tolerance is type-deep, not vocabulary-only: junk the scanner
        # could not have written is skipped, never counted, never a crash.
        junk = record(200, PROTECTION_BODY, wait_records=[
            {"category": "retry", "outcome": "retried",
             "requested_seconds": "abc", "elapsed_seconds": None},
            {"category": "retry", "outcome": "retried",
             "requested_seconds": float("inf"),
             "elapsed_seconds": float("nan")},
            "not-a-record",
        ])
        junk["envelope"]["attempts"] = "three"
        junk["envelope"]["captured_at"] = 12345
        not_a_list = record(200, PROTECTION_BODY, wait_records=7)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1), repo_item(2)])],
                       [("1-repo-1", "default-branch-protection.json", junk),
                        ("2-repo-2", "default-branch-protection.json",
                         not_a_list)])
            block = execution(out)
            retry = block["waits"]["retry"]
            self.assertEqual(retry["count"], 2)
            self.assertEqual(retry["requested_seconds"], 0)
            self.assertEqual(retry["slept_seconds"], 0)
            self.assertEqual(block["waits"]["max_single_wait_seconds"], 0)
            self.assertEqual(block["waits"]["total_wait_seconds"], 0)
            self.assertEqual(block["requests"]["attempts"], 5)
            self.assertEqual(block["captured"]["first"],
                             "2026-01-01T00:00:00Z")
            self.assertEqual(block["captured"]["last"],
                             "2026-01-01T00:00:00Z")


class HugeIntegers(unittest.TestCase):
    def test_arbitrary_precision_integers_never_crash(self):
        # json.loads parses 400-digit integers; they are finite numbers and
        # read as found — never a float conversion, never an OverflowError.
        huge = 10 ** 400
        crafted = record(200, PROTECTION_BODY, wait_records=[
            {"category": "retry", "outcome": "retried",
             "requested_seconds": huge, "elapsed_seconds": 0},
        ])
        crafted["envelope"]["attempts"] = huge
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [("1-repo-1", "default-branch-protection.json",
                         crafted)])
            block = execution(out)
            self.assertEqual(block["waits"]["retry"]["requested_seconds"],
                             huge)
            self.assertEqual(block["waits"]["max_single_wait_seconds"], huge)
            self.assertEqual(block["requests"]["attempts"], huge + 4)


class PlannedVersusAttempts(unittest.TestCase):
    def test_planned_attempts_completed_failed_evidence_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            failing = record(500, {"message": "boom"}, attempts=3)
            # repo-2's protection artifact is deliberately absent: the
            # recorded-collection-failure trace keeps planned != attempts.
            write_tree(out, [page_record([repo_item(1), repo_item(2)])],
                       [("1-repo-1", "default-branch-protection.json",
                         failing)])
            requests = execution(out)["requests"]
            self.assertEqual(requests["planned_singles"], 5)
            self.assertEqual(requests["planned_drains"], 1)
            self.assertEqual(requests["missing_input"], 0)
            self.assertEqual(requests["retained_records"], 5)
            self.assertEqual(requests["attempts"], 7)
            self.assertEqual(requests["completed"], 4)
            self.assertEqual(requests["failed"], 1)
            self.assertEqual(requests["evidence_absent"], 1)

    def test_missing_input_receives_no_planned_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1,
                                                    default_branch=None)])])
            requests = execution(out)["requests"]
            self.assertEqual(requests["planned_singles"], 3)
            self.assertEqual(requests["missing_input"], 1)
            self.assertEqual(requests["evidence_absent"], 0)

    def test_rate_limit_marked_final_record_counts_failed(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            marked = record(429, {"message": "limit"},
                            headers={"retry-after": "9999"},
                            termination_reason="retry-after-exceeds-maximum")
            write_tree(out, [page_record([repo_item(1)])],
                       [("1-repo-1", "default-branch-protection.json",
                         marked)])
            requests = execution(out)["requests"]
            self.assertEqual(requests["failed"], 1)
            self.assertEqual(requests["completed"], 4)


class CaptureWindow(unittest.TestCase):
    def test_first_and_last_capture_timestamps(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            early = record(200, PROTECTION_BODY,
                           captured="2026-01-01T00:00:01Z")
            late = record(200, PROTECTION_BODY,
                          captured="2026-01-01T09:00:00Z")
            write_tree(out, [page_record([repo_item(1), repo_item(2)])],
                       [("1-repo-1", "default-branch-protection.json", early),
                        ("2-repo-2", "default-branch-protection.json", late)])
            captured = execution(out)["captured"]
            self.assertEqual(captured["first"], "2026-01-01T00:00:00Z")
            self.assertEqual(captured["last"], "2026-01-01T09:00:00Z")


if __name__ == "__main__":
    unittest.main()
