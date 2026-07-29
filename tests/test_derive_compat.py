"""V40 Slice-1-tree compatibility, the generic drain seam, and summary growth."""
import tempfile
import unittest
from pathlib import Path

from collector.derive import run_summary
from collector.projections import resource_document
from collector.serialize import canonical_dumps
from test_derive_resources import (
    PROTECTION_BODY, RUN, page_record, protection, protection_doc, record,
    repo_item, write_tree,
)

# A synthetic drain descriptor exercised at the pure seam only: the engine
# must already be descriptor-generic so T8's second descriptor touches only
# resources.py, tests, and fixtures (ADR-0004's falsifiable claim).
SYNTHETIC_DRAIN = {
    "name": "synthetic-listing",
    "path_template": "/repos/{full_name}/synthetic",
    "shape": "object_array",
    "required_inputs": (),
    "absence_message": None,
    "projection": (("count", ("count", "items")),),
}


def drain_page(items, number, incomplete=False):
    extra = {"page": number, "item_count": len(items),
             "repo": {"id": 1, "full_name": "acme/repo-1"},
             "resource": "synthetic-listing"}
    if incomplete:
        extra["incomplete"] = True
    return record(200, items, **extra)


class Slice1TreeCompatibility(unittest.TestCase):
    def test_v40_new_projection_derives_all_unknown_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1), repo_item(2)])])
            doc = protection_doc(out)
            self.assertEqual(doc["coverage"]["eligible_target_count"], 2)
            self.assertEqual(doc["state"], "unknown")
            for entry in doc["repositories"]:
                self.assertEqual((entry["state"], entry["reason"]),
                                 ("unknown", "raw-evidence-absent"))
                self.assertEqual(entry["enforce_admins"], "unknown")

    def test_v40_org_artifacts_stay_byte_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])])
            protection_doc(out)
            expected_org = canonical_dumps({
                "org": {"created_at": "2020-01-02T03:04:05Z", "id": 42,
                        "login": "acme"},
                "run_id": RUN, "state": "collected",
            }).encode("utf-8")
            self.assertEqual((out / "observed" / "org.json").read_bytes(),
                             expected_org)
            expected_repos = canonical_dumps({
                "count": 1,
                "repositories": [{
                    "archived": False, "created_at": "2021-01-01T00:00:00Z",
                    "default_branch": "main", "fork": False, "full_name":
                    "acme/repo-1", "id": 1, "name": "repo-1", "state":
                    "collected", "visibility": "public",
                }],
                "run_id": RUN, "state": "collected",
            }).encode("utf-8")
            self.assertEqual(
                (out / "observed" / "repositories.json").read_bytes(),
                expected_repos)


class GenericDrainSeam(unittest.TestCase):
    def _document(self, out, resources):
        write_tree(out, [page_record([repo_item(1)])], resources)
        raw_dir = out / "evidence" / "raw" / RUN
        pages = [page_record([repo_item(1)])]
        return resource_document(RUN, raw_dir, SYNTHETIC_DRAIN, pages,
                                 "collected")

    def test_multi_page_drain_derives_collected(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            doc = self._document(out, [
                ("1-repo-1", "synthetic-listing.page-1.json",
                 drain_page([{"a": 1}], 1)),
                ("1-repo-1", "synthetic-listing.page-2.json",
                 drain_page([{"a": 2}], 2)),
            ])
            [entry] = doc["repositories"]
            self.assertEqual((entry["state"], entry["reason"]),
                             ("collected", "collected"))

    def test_capped_drain_derives_incomplete_pagination_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            doc = self._document(out, [
                ("1-repo-1", "synthetic-listing.page-1.json",
                 drain_page([{"a": 1}], 1, incomplete=True)),
            ])
            [entry] = doc["repositories"]
            self.assertEqual((entry["state"], entry["reason"]),
                             ("incomplete", "pagination-cap"))

    def test_absent_listing_is_raw_evidence_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            doc = self._document(out, [])
            [entry] = doc["repositories"]
            self.assertEqual((entry["state"], entry["reason"]),
                             ("unknown", "raw-evidence-absent"))


class SummaryGeneralization(unittest.TestCase):
    def test_per_resource_rollup_counts_and_waits(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            failed = record(500, {"message": "boom"},
                            repo={"id": 1, "full_name": "acme/repo-1"},
                            resource="default-branch-protection")
            failed["envelope"]["waits_seconds"] = [1, 1]
            write_tree(out, [page_record([repo_item(1), repo_item(2)])],
                       [("1-repo-1", "default-branch-protection.json", failed),
                        protection("2-repo-2", 200, PROTECTION_BODY,
                                   repo={"id": 2, "full_name": "acme/repo-2"},
                                   resource="default-branch-protection")])
            summary = run_summary(out, RUN)
            resource = summary["resources"]["default-branch-protection"]
            self.assertEqual(resource["state"], "failed")
            self.assertEqual(resource["state_counts"],
                             {"failed": 1, "collected": 1})
            self.assertEqual(resource["reason_counts"],
                             {"transport-failed": 1, "collected": 1})
            self.assertEqual(resource["waits_seconds"], [1, 1])

    def test_structural_facts_and_report_shape_are_stable(self):
        from collector.report import build_report

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [protection("1-repo-1", 200, PROTECTION_BODY,
                                   repo={"id": 1, "full_name": "acme/repo-1"}),
                        ("stray-notes", "default-branch-protection.json",
                         record(200, PROTECTION_BODY))])
            summary = run_summary(out, RUN)
            self.assertEqual(summary["structural"]["unrecognized_directories"],
                             ["stray-notes"])
            self.assertEqual(summary["structural"]["conflicted_directories"], [])
            # Slice-1 report assembly is untouched this ticket: the same four
            # summary keys feed it and no new top-level report key appears.
            report = build_report("https://api.example", "acme", RUN, "op",
                                  summary)
            self.assertEqual(sorted(report), [
                "api_url", "failures", "identity_login", "listings", "org",
                "rate_limit", "resource_states", "run_id", "state_counts",
            ])
            self.assertEqual(sorted(summary["resource_states"]),
                             ["meta", "org", "repositories", "user"])


if __name__ == "__main__":
    unittest.main()
