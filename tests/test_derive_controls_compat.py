"""Preservation and deterministic rederivation for control documents
(Slice 3 T3: V60 and the ticket's byte-identity and serialization ACs).

Slice-1/2-shaped trees carry no dedicated-request evidence, so control
entries degrade honestly; every pre-existing observed document is
byte-identical with and without control emission (the extension is purely
additive, ADR-0009's consequence); derivation is deterministic from raw
evidence alone through the canonical serializer.
"""
import json
import shutil
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path

from collector import controls, resources
from collector.derive import derive_observed
from test_derive_resources import (
    PROTECTION_BODY, RUN, page_record, protection, repo_item, write_tree,
)
from test_derive_rulesets import rs_file
from test_derive_security import sa_body, sa_file
from test_resources_rulesets import RULESET_ITEM


def slice2_tree(out):
    """A committed Slice-2-shaped run: listing + protection + rulesets
    evidence, no dedicated-request artifacts."""
    write_tree(out, [page_record([repo_item(1), repo_item(2)])],
               [protection("1-repo-1", 200, PROTECTION_BODY),
                rs_file(2, 1, [RULESET_ITEM])])


def observed_bytes(out):
    return {path.relative_to(out / "observed").as_posix(): path.read_bytes()
            for path in sorted((out / "observed").rglob("*.json"))}


class SliceTreeCompatibility(unittest.TestCase):
    def test_v60_slice2_tree_derives_evidence_unavailable_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            slice2_tree(out)
            derive_observed(out, run_id=RUN)
            doc = json.loads(
                (out / "observed" / "controls" / "secret-scanning.json")
                .read_text(encoding="utf-8"))
            self.assertEqual(doc["state"], "unknown")
            for entry in doc["repositories"]:
                self.assertEqual(
                    (entry["operational_state"],
                     entry["operational_state_reason"],
                     entry["applicability"], entry["applicability_reason"]),
                    ("unknown", "evidence-unavailable",
                     "applicability-unknown", "evidence-unavailable"))
                self.assertEqual(entry["evidence"],
                                 {"resource": "security-and-analysis",
                                  "state": "unknown",
                                  "reason": "raw-evidence-absent"})

    def test_v60_existing_observed_documents_are_byte_identical(self):
        # The T1/T8 preservation pattern: deriving the same tree with control
        # emission mocked away and with the shipped table produces
        # byte-identical pre-existing documents; controls/ is purely additive.
        def build(out, table):
            slice2_tree(out)
            with mock.patch.object(controls, "CONTROLS", table):
                derive_observed(out, run_id=RUN)

        with tempfile.TemporaryDirectory() as tmp:
            before = Path(tmp) / "before"
            after = Path(tmp) / "after"
            build(before, ())
            build(after, controls.CONTROLS)
            before_docs = observed_bytes(before)
            after_docs = observed_bytes(after)
            added = ("controls/secret-scanning.json",
                     "controls/secret-scanning-push-protection.json")
            for name in added:
                self.assertNotIn(name, before_docs)
                self.assertIn(name, after_docs)
                del after_docs[name]
            self.assertEqual(before_docs, after_docs)


class CommittedRunTrees(unittest.TestCase):
    """V60 against the actually committed validation-run trees: deriving
    them with the T3 engine leaves every committed observed document
    byte-identical and adds only honest evidence-unavailable control
    conclusions (no dedicated-request evidence exists in either run)."""

    RUNS = Path(__file__).resolve().parent.parent / "docs" / "validation" / "runs"

    def rederive(self, run_name):
        committed = self.RUNS / run_name
        run_id = next((committed / "evidence" / "raw").iterdir()).name
        original = {path.name: path.read_bytes()
                    for path in sorted((committed / "observed").glob("*.json"))}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            shutil.copytree(committed / "evidence", out / "evidence")
            derive_observed(out, run_id=run_id)
            rederived = {path.name: path.read_bytes()
                         for path in sorted((out / "observed").glob("*.json"))}
            doc = json.loads(
                (out / "observed" / "controls" / "secret-scanning.json")
                .read_text(encoding="utf-8"))
        return original, rederived, doc

    def assert_v60(self, run_name):
        original, rederived, doc = self.rederive(run_name)
        for name, content in original.items():
            self.assertEqual(rederived[name], content, name)
        self.assertTrue(doc["repositories"])
        for entry in doc["repositories"]:
            self.assertEqual(
                (entry["operational_state"], entry["operational_state_reason"],
                 entry["applicability"], entry["applicability_reason"],
                 entry["evidence"]["reason"]),
                ("unknown", "evidence-unavailable", "applicability-unknown",
                 "evidence-unavailable", "raw-evidence-absent"))

    def test_v60_committed_slice1_run_tree(self):
        self.assert_v60("20260725-GHScannerLab")

    def test_v60_committed_slice2_run_tree(self):
        self.assert_v60("20260730-GHScannerLab")


class DegradedCoverage(unittest.TestCase):
    def test_non_collected_inventory_state_carried_verbatim(self):
        # Coverage qualifies, never converts: a capped listing's
        # "incomplete" inventory state reaches the control document
        # untouched while the usable page's targets still count.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)], incomplete=True)],
                       [sa_file(1, 200, sa_body())])
            derive_observed(out, run_id=RUN)
            doc = json.loads(
                (out / "observed" / "controls" / "secret-scanning.json")
                .read_text(encoding="utf-8"))
            self.assertEqual(doc["coverage"],
                             {"basis": "eligible-discovered-repositories",
                              "inventory_state": "incomplete",
                              "eligible_target_count": 1})


class PairingInvariant(unittest.TestCase):
    def test_control_without_derived_descriptor_fails_loudly(self):
        # S10 adjudication of the cycle-4 guard: a control whose evidence
        # descriptor was not derived is an invariant violation (unreachable
        # when the shipped tables agree - import-time validation pins them),
        # surfaced as a loud ValueError, never a silent omission.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            slice2_tree(out)
            with mock.patch.object(
                    resources, "DESCRIPTORS",
                    (resources.DEFAULT_BRANCH_PROTECTION,)):
                with self.assertRaises(ValueError) as ctx:
                    derive_observed(out, run_id=RUN)
        self.assertIn("security-and-analysis", str(ctx.exception))
        self.assertIn("secret-scanning", str(ctx.exception))


class DeterministicRederivation(unittest.TestCase):
    def full_tree(self, out):
        write_tree(out, [page_record([repo_item(1), repo_item(2)])],
                   [protection("1-repo-1", 200, PROTECTION_BODY),
                    rs_file(2, 1, [RULESET_ITEM]),
                    sa_file(1, 200, sa_body()),
                    sa_file(2, 403, {"message": "Forbidden"})])

    def test_destructive_rederivation_from_raw_alone_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.full_tree(out)
            derive_observed(out, run_id=RUN)
            first = observed_bytes(out)
            for path in sorted((out / "observed").rglob("*.json")):
                path.unlink()
            derive_observed(out, run_id=RUN)
            self.assertEqual(observed_bytes(out), first)

    def test_serialization_rules_through_the_canonical_serializer(self):
        # UTF-8, LF only, trailing newline, sorted keys at every level; the
        # only timestamp-shaped value is the run id.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.full_tree(out)
            derive_observed(out, run_id=RUN)
            raw = (out / "observed" / "controls" / "secret-scanning.json"
                   ).read_bytes()
            self.assertNotIn(b"\r", raw)
            self.assertTrue(raw.endswith(b"\n"))
            text = raw.decode("utf-8")
            document = json.loads(text)
            self.assertEqual(
                text,
                json.dumps(document, sort_keys=True, indent=2,
                           ensure_ascii=False) + "\n")


if __name__ == "__main__":
    unittest.main()
