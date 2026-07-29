"""Coverage qualification (V39) and structural conflicts (V34/V35) at the derive seam."""
import tempfile
import unittest
from pathlib import Path

from test_derive_resources import (
    PROTECTION_BODY, page_record, protection, protection_doc, record,
    repo_item, write_tree,
)


class CoverageQualification(unittest.TestCase):
    def test_v39_incomplete_inventory_qualifies_never_converts(self):
        # The capped page is still valid partial evidence: its items remain
        # targets, entry states stay their own, only coverage carries the
        # inventory vocabulary.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(
                out,
                [page_record([repo_item(1)], number=1),
                 page_record([repo_item(2)], number=2, incomplete=True)],
                [protection("1-repo-1", 200, PROTECTION_BODY),
                 protection("2-repo-2", 200, PROTECTION_BODY)],
            )
            doc = protection_doc(out)
            self.assertEqual(doc["coverage"]["inventory_state"], "incomplete")
            self.assertEqual(doc["coverage"]["eligible_target_count"], 2)
            self.assertEqual(
                [(entry["id"], entry["state"]) for entry in doc["repositories"]],
                [(1, "collected"), (2, "collected")],
            )
            self.assertEqual(doc["state"], "collected")

    def test_v39_failed_inventory_page_contributes_no_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(
                out,
                [page_record([repo_item(1)], number=1),
                 record(500, {"message": "boom"}, page=2, item_count=0)],
                [protection("1-repo-1", 200, PROTECTION_BODY)],
            )
            doc = protection_doc(out)
            self.assertEqual(doc["coverage"]["inventory_state"], "failed")
            self.assertEqual(doc["coverage"]["eligible_target_count"], 1)
            self.assertEqual([entry["id"] for entry in doc["repositories"]], [1])
            self.assertEqual(doc["repositories"][0]["state"], "collected")


class StructuralConflicts(unittest.TestCase):
    def test_v34_duplicate_id_directories_select_no_winner(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(
                out,
                [page_record([repo_item(1), repo_item(2)])],
                [protection("1-repo-1", 200, PROTECTION_BODY,
                            repo={"id": 1, "full_name": "acme/repo-1"}),
                 protection("1-other", 200, PROTECTION_BODY,
                            repo={"id": 1, "full_name": "acme/repo-1"}),
                 protection("2-repo-2", 200, PROTECTION_BODY,
                            repo={"id": 2, "full_name": "acme/repo-2"})],
            )
            doc = protection_doc(out)
            by_id = {entry["id"]: entry for entry in doc["repositories"]}
            self.assertEqual((by_id[1]["state"], by_id[1]["reason"]),
                             ("unknown", "structural-conflict"))
            self.assertEqual(by_id[1]["enforce_admins"], "unknown")
            self.assertEqual((by_id[2]["state"], by_id[2]["reason"]),
                             ("collected", "collected"))
            self.assertEqual(doc["state"], "unknown")

    def test_v35_path_envelope_disagreement_is_a_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(
                out,
                [page_record([repo_item(1)])],
                [protection("1-repo-1", 200, PROTECTION_BODY,
                            repo={"id": 9, "full_name": "acme/other"})],
            )
            [entry] = protection_doc(out)["repositories"]
            self.assertEqual((entry["state"], entry["reason"]),
                             ("unknown", "structural-conflict"))

    def test_missing_input_precedes_conflict_and_conflict_precedes_absence(self):
        # V33's no-request rule is evaluated before tree inspection; among
        # inspected targets, a conflict suppresses artifact reads entirely.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(
                out,
                [page_record([repo_item(1, default_branch=""), repo_item(2)])],
                [protection("1-repo-1", 200, PROTECTION_BODY,
                            repo={"id": 1, "full_name": "acme/repo-1"}),
                 protection("1-dup", 200, PROTECTION_BODY,
                            repo={"id": 1, "full_name": "acme/repo-1"}),
                 protection("2-repo-2", 200, PROTECTION_BODY,
                            repo={"id": 2, "full_name": "acme/repo-2"}),
                 ("2-dup", "unrelated.json",
                  record(200, {}, repo={"id": 2, "full_name": "acme/repo-2"}))],
            )
            doc = protection_doc(out)
            by_id = {entry["id"]: entry for entry in doc["repositories"]}
            self.assertEqual((by_id[1]["state"], by_id[1]["reason"]),
                             ("unknown", "missing-required-input"))
            self.assertEqual((by_id[2]["state"], by_id[2]["reason"]),
                             ("unknown", "structural-conflict"))

    def test_unrecognized_directory_is_reporting_never_a_conflict(self):
        # Ratified refinement: names the scanner could not have written are
        # surfaced through reporting; entries are untouched.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(
                out,
                [page_record([repo_item(1)])],
                [protection("1-repo-1", 200, PROTECTION_BODY,
                            repo={"id": 1, "full_name": "acme/repo-1"}),
                 ("stray-notes", "default-branch-protection.json",
                  record(200, PROTECTION_BODY,
                         repo={"id": 1, "full_name": "acme/repo-1"}))],
            )
            [entry] = protection_doc(out)["repositories"]
            self.assertEqual((entry["state"], entry["reason"]),
                             ("collected", "collected"))


if __name__ == "__main__":
    unittest.main()
