"""Preservation and deterministic rederivation for control documents
(Slice 3 T3: V60 and the ticket's byte-identity and serialization ACs).

Slice-1/2-shaped trees carry no dedicated-request evidence, so control
entries degrade honestly; every pre-existing observed document is
byte-identical with and without control emission (the extension is purely
additive, ADR-0009's consequence); derivation is deterministic from raw
evidence alone through the canonical serializer.
"""
import json
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path

from collector import controls
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
            self.assertNotIn("controls/secret-scanning.json", before_docs)
            self.assertIn("controls/secret-scanning.json", after_docs)
            del after_docs["controls/secret-scanning.json"]
            self.assertEqual(before_docs, after_docs)


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
