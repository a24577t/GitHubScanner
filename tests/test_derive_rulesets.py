"""Rulesets derivation at the derive seam (Slice 2 T8; V06/V07/V37 derive half).

Crafted raw trees through the shipped descriptor: observed-document shape,
the empty-listing value rule, cap-breach qualification with every valid page
contributing, the pinned no-page-gap-detection behavior (T6 disposition:
scanner-written drains are contiguous by construction; no governed matrix
row requires detection), Slice-1-tree derivability, and byte-identity of
every pre-T8 observed output against the extended table.
"""
import json
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path

from collector import controls, resources
from collector.derive import derive_observed
from test_derive_resources import (
    PROTECTION_BODY, RUN, page_record, protection, record, repo_item,
    write_tree,
)
from test_resources_rulesets import RULESET_ITEM


def rs_page(items, number, repo_id=1, incomplete=False):
    extra = {"page": number, "item_count": len(items),
             "repo": {"id": repo_id, "full_name": f"acme/repo-{repo_id}"},
             "resource": "repository-rulesets"}
    if incomplete:
        extra["incomplete"] = True
    return record(200, items, **extra)


def rs_file(repo_id, number, items, incomplete=False):
    return (f"{repo_id}-repo-{repo_id}",
            f"repository-rulesets.page-{number}.json",
            rs_page(items, number, repo_id=repo_id, incomplete=incomplete))


def rulesets_doc(out):
    derive_observed(out, run_id=RUN)
    path = out / "observed" / "repository-rulesets.json"
    return json.loads(path.read_text(encoding="utf-8"))


class ObservedDocument(unittest.TestCase):
    def test_v06_single_ruleset_entry_collected_with_summary_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [rs_file(1, 1, [RULESET_ITEM])])
            doc = rulesets_doc(out)
            self.assertEqual(sorted(doc),
                             ["coverage", "repositories", "run_id", "state"])
            self.assertEqual(doc["state"], "collected")
            [entry] = doc["repositories"]
            self.assertEqual((entry["state"], entry["reason"]),
                             ("collected", "collected"))
            self.assertEqual(entry["count"], 1)
            self.assertEqual(entry["rulesets"], [
                {"id": 42, "name": "default-protection", "target": "branch",
                 "enforcement": "active",
                 "created_at": "2026-07-01T00:00:00Z"},
            ])

    def test_v07_empty_listing_is_collected_count_zero_never_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [rs_file(1, 1, [])])
            [entry] = rulesets_doc(out)["repositories"]
            self.assertEqual((entry["state"], entry["reason"]),
                             ("collected", "collected"))
            self.assertEqual(entry["count"], 0)
            self.assertEqual(entry["rulesets"], [])

    def test_v37_cap_breach_derives_incomplete_and_valid_pages_contribute(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [rs_file(1, 1, [{**RULESET_ITEM, "id": 9}]),
                        rs_file(1, 2, [{**RULESET_ITEM, "id": 3}],
                                incomplete=True)])
            [entry] = rulesets_doc(out)["repositories"]
            self.assertEqual((entry["state"], entry["reason"]),
                             ("incomplete", "pagination-cap"))
            # Both drained pages remain evidence: items merge and sort by id.
            self.assertEqual(entry["count"], 2)
            self.assertEqual([r["id"] for r in entry["rulesets"]], [3, 9])

    def test_page_gap_is_not_detected_present_pages_derive_as_found(self):
        # Pinned T6 disposition: scanner-written drains are contiguous by
        # construction, so a gap (here page-2 lost to a recorded collection
        # failure) is not a detected condition - present pages classify and
        # project as found, and the gap itself adds nothing.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [rs_file(1, 1, [{**RULESET_ITEM, "id": 9}]),
                        rs_file(1, 3, [{**RULESET_ITEM, "id": 3}])])
            [entry] = rulesets_doc(out)["repositories"]
            self.assertEqual((entry["state"], entry["reason"]),
                             ("collected", "collected"))
            self.assertEqual(entry["count"], 2)
            self.assertEqual([r["id"] for r in entry["rulesets"]], [3, 9])

    def test_slice_1_tree_derives_all_unknown_raw_evidence_absent(self):
        # V40's rule extends to the new descriptor: a tree collected before
        # T8 carries no rulesets evidence and derives unknown, projections
        # included.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1), repo_item(2)])])
            doc = rulesets_doc(out)
            self.assertEqual(doc["state"], "unknown")
            for entry in doc["repositories"]:
                self.assertEqual((entry["state"], entry["reason"]),
                                 ("unknown", "raw-evidence-absent"))
                self.assertEqual(entry["count"], "unknown")
                self.assertEqual(entry["rulesets"], "unknown")

    def test_failed_listing_projects_unknown_never_partial_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [("1-repo-1", "repository-rulesets.page-1.json",
                         record(500, {"message": "boom"}, page=1,
                                item_count=0))])
            [entry] = rulesets_doc(out)["repositories"]
            self.assertEqual((entry["state"], entry["reason"]),
                             ("failed", "transport-failed"))
            self.assertEqual(entry["count"], "unknown")
            self.assertEqual(entry["rulesets"], "unknown")


class ExistingOutputsByteIdentity(unittest.TestCase):
    def test_pre_t8_observed_outputs_are_byte_identical(self):
        # The architectural AC's preservation half: deriving the same tree
        # with the pre-T8 table and with the shipped table produces
        # byte-identical org, repositories, and protection documents; the
        # extension is purely additive.
        def build(out, table):
            write_tree(out, [page_record([repo_item(1), repo_item(2)])],
                       [protection("1-repo-1", 200, PROTECTION_BODY),
                        rs_file(2, 1, [RULESET_ITEM])])
            # The reduced-table world keeps only controls whose evidence
            # descriptor it derives (T3's loud pairing invariant); the pre-T8
            # world therefore has none.
            names = {descriptor["name"] for descriptor in table}
            with mock.patch.object(resources, "DESCRIPTORS", table), \
                    mock.patch.object(controls, "CONTROLS", tuple(
                        c for c in controls.CONTROLS
                        if c["descriptor"] in names)):
                derive_observed(out, run_id=RUN)

        with tempfile.TemporaryDirectory() as tmp:
            before = Path(tmp) / "before"
            after = Path(tmp) / "after"
            build(before, (resources.DEFAULT_BRANCH_PROTECTION,))
            build(after, resources.DESCRIPTORS)
            for name in ("org.json", "repositories.json",
                         "default-branch-protection.json"):
                self.assertEqual(
                    (before / "observed" / name).read_bytes(),
                    (after / "observed" / name).read_bytes(), name)
            self.assertFalse(
                (before / "observed" / "repository-rulesets.json").exists())
            self.assertTrue(
                (after / "observed" / "repository-rulesets.json").exists())


if __name__ == "__main__":
    unittest.main()
