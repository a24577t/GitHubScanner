"""Security-and-analysis derivation at the derive seam (Slice 3 T1).

Crafted raw trees through the shipped descriptor: the observed document the
generic engine emits, V50/V51 carried through derivation (projected unknowns
and uncoerced values in the entry), V54's derive half (404 with no absence
anchor), the raw-evidence-absent rule for pre-T1 trees (V60's direction; T3
owns control documents), and byte-identity of every pre-T1 observed output
against the extended table (T8's preservation pattern).
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
from test_derive_rulesets import rs_file
from test_resources_rulesets import RULESET_ITEM


def sa_body(status_pair=("enabled", "disabled"), visibility="public"):
    scanning, push = status_pair
    return {
        "id": 1, "name": "repo-1", "full_name": "acme/repo-1",
        "visibility": visibility,
        "security_and_analysis": {
            "secret_scanning": {"status": scanning},
            "secret_scanning_push_protection": {"status": push},
            "dependabot_security_updates": {"status": "disabled"},
        },
    }


def sa_file(repo_id, status, body):
    return (f"{repo_id}-repo-{repo_id}", "security-and-analysis.json",
            record(status, body,
                   repo={"id": repo_id, "full_name": f"acme/repo-{repo_id}"},
                   resource="security-and-analysis"))


def sa_doc(out):
    derive_observed(out, run_id=RUN)
    path = out / "observed" / "security-and-analysis.json"
    return json.loads(path.read_text(encoding="utf-8"))


class ObservedDocument(unittest.TestCase):
    def test_v41_collected_entry_carries_the_exact_projected_surface(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [sa_file(1, 200, sa_body())])
            doc = sa_doc(out)
            self.assertEqual(sorted(doc),
                             ["coverage", "repositories", "run_id", "state"])
            self.assertEqual(doc["state"], "collected")
            self.assertEqual(doc["repositories"], [{
                "id": 1, "full_name": "acme/repo-1",
                "state": "collected", "reason": "collected",
                "visibility": "public",
                "security_and_analysis": {
                    "secret_scanning": {"status": "enabled"},
                    "secret_scanning_push_protection": {"status": "disabled"},
                },
            }])

    def test_v50_absent_surface_survives_derivation_as_unknown(self):
        body = {key: value for key, value in sa_body().items()
                if key != "security_and_analysis"}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [sa_file(1, 200, body)])
            [entry] = sa_doc(out)["repositories"]
            self.assertEqual((entry["state"], entry["reason"]),
                             ("collected", "collected"))
            self.assertEqual(entry["security_and_analysis"], {
                "secret_scanning": {"status": "unknown"},
                "secret_scanning_push_protection": {"status": "unknown"},
            })

    def test_v51_unrecognized_statuses_survive_derivation_uncoerced(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [sa_file(1, 200, sa_body(status_pair=("paused", 5)))])
            [entry] = sa_doc(out)["repositories"]
            surface = entry["security_and_analysis"]
            self.assertEqual(surface["secret_scanning"]["status"], "paused")
            self.assertEqual(
                surface["secret_scanning_push_protection"]["status"], 5)

    def test_v54_404_derives_inaccessible_absence_rule_unmatched(self):
        # No absence anchor exists for repository metadata: the 404 never
        # joins the absence set and never suggests disablement.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [sa_file(1, 404, {"message": "Not Found"})])
            [entry] = sa_doc(out)["repositories"]
            self.assertEqual((entry["state"], entry["reason"]),
                             ("inaccessible", "absence-rule-unmatched-404"))
            self.assertEqual(entry["security_and_analysis"], {
                "secret_scanning": {"status": "unknown"},
                "secret_scanning_push_protection": {"status": "unknown"},
            })

    def test_pre_t1_tree_derives_unknown_raw_evidence_absent(self):
        # V60's direction at this seam: a tree collected before T1 carries no
        # dedicated-request evidence and derives unknown, projections included.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1), repo_item(2)])])
            doc = sa_doc(out)
            self.assertEqual(doc["state"], "unknown")
            for entry in doc["repositories"]:
                self.assertEqual((entry["state"], entry["reason"]),
                                 ("unknown", "raw-evidence-absent"))
                self.assertEqual(entry["visibility"], "unknown")
                self.assertEqual(entry["security_and_analysis"], {
                    "secret_scanning": {"status": "unknown"},
                    "secret_scanning_push_protection": {"status": "unknown"},
                })


class ExistingOutputsByteIdentity(unittest.TestCase):
    def test_pre_t1_observed_outputs_are_byte_identical(self):
        # The ticket's preservation AC (T8 pattern): deriving the same tree
        # with the pre-T1 table and with the shipped table produces
        # byte-identical org, repositories, protection, and rulesets
        # documents; the extension is purely additive.
        def build(out, table):
            write_tree(out, [page_record([repo_item(1), repo_item(2)])],
                       [protection("1-repo-1", 200, PROTECTION_BODY),
                        rs_file(2, 1, [RULESET_ITEM]),
                        sa_file(1, 200, sa_body())])
            # The reduced-table world keeps only controls whose evidence
            # descriptor it derives (T3's loud pairing invariant); the pre-T1
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
            build(before, (resources.DEFAULT_BRANCH_PROTECTION,
                           resources.REPOSITORY_RULESETS))
            build(after, resources.DESCRIPTORS)
            for name in ("org.json", "repositories.json",
                         "default-branch-protection.json",
                         "repository-rulesets.json"):
                self.assertEqual(
                    (before / "observed" / name).read_bytes(),
                    (after / "observed" / name).read_bytes(), name)
            self.assertFalse(
                (before / "observed" / "security-and-analysis.json").exists())
            self.assertTrue(
                (after / "observed" / "security-and-analysis.json").exists())


if __name__ == "__main__":
    unittest.main()
