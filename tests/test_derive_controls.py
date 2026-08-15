"""Control-observation documents at the derive seam (Slice 3 T3, V57).

ADR-0009 element 3: one latest-only document per control under
observed/controls/, house shape {run_id, state, coverage, repositories},
entries in canonical discovery order, every conclusion citing its retained
descriptor evidence {resource, state, reason} — paths never embedded. The
document consumes derived resource-document entries only; derive.py
orchestrates, controls.py concludes.
"""
import json
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path

from collector import controls
from collector.derive import derive_observed
from test_controls_chain import CHAINED
from test_derive_resources import RUN, page_record, repo_item, write_tree
from test_derive_security import sa_body, sa_file


def control_document(out, name="secret-scanning"):
    derive_observed(out, run_id=RUN)
    path = out / "observed" / "controls" / (name + ".json")
    return json.loads(path.read_text(encoding="utf-8"))


class DocumentShape(unittest.TestCase):
    def build(self, out):
        # Listing pages arrive out of id order; entry order must inherit the
        # canonical ascending discovery order, not page order.
        write_tree(out, [page_record([repo_item(2), repo_item(1)])],
                   [sa_file(1, 200, sa_body()),
                    sa_file(2, 200, sa_body(status_pair=("disabled", "disabled"),
                                            visibility="private"))])

    def test_v57_document_shape_order_citations_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.build(out)
            doc = control_document(out)
            self.assertEqual(doc, {
                "run_id": RUN,
                "state": "collected",
                "coverage": {"basis": "eligible-discovered-repositories",
                             "inventory_state": "collected",
                             "eligible_target_count": 2},
                "repositories": [
                    {"id": 1, "full_name": "acme/repo-1",
                     "applicability": "applicable",
                     "applicability_reason": "affirmative-enabled-status",
                     "operational_state": "enabled",
                     "operational_state_reason": "affirmative-status-enabled",
                     "evidence": {"resource": "security-and-analysis",
                                  "state": "collected",
                                  "reason": "collected"}},
                    {"id": 2, "full_name": "acme/repo-2",
                     "applicability": "applicability-unknown",
                     "applicability_reason": "visibility-not-public",
                     "operational_state": "disabled",
                     "operational_state_reason": "affirmative-status-disabled",
                     "evidence": {"resource": "security-and-analysis",
                                  "state": "collected",
                                  "reason": "collected"}},
                ],
            })

    def test_v57_exact_key_sets_no_rollup_keys_anywhere(self):
        # The closed key sets: no operational-state or applicability rollup
        # can appear at any level (ADR-0009: such a collapse is Conformance
        # territory, out of scope).
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.build(out)
            doc = control_document(out)
            self.assertEqual(sorted(doc),
                             ["coverage", "repositories", "run_id", "state"])
            for entry in doc["repositories"]:
                self.assertEqual(sorted(entry), [
                    "applicability", "applicability_reason", "evidence",
                    "full_name", "id", "operational_state",
                    "operational_state_reason"])
                self.assertEqual(sorted(entry["evidence"]),
                                 ["reason", "resource", "state"])

    def test_v57_coverage_is_the_descriptor_documents_block_verbatim(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.build(out)
            doc = control_document(out)
            descriptor_doc = json.loads(
                (out / "observed" / "security-and-analysis.json")
                .read_text(encoding="utf-8"))
            self.assertEqual(doc["coverage"], descriptor_doc["coverage"])

    def test_one_document_per_shipped_control_latest_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.build(out)
            derive_observed(out, run_id=RUN)
            controls_dir = out / "observed" / "controls"
            names = ["secret-scanning-push-protection.json",
                     "secret-scanning.json"]
            self.assertEqual([p.name for p in sorted(controls_dir.iterdir())],
                             names)
            first = {name: (controls_dir / name).read_bytes()
                     for name in names}
            derive_observed(out, run_id=RUN)
            for name in names:
                self.assertEqual((controls_dir / name).read_bytes(),
                                 first[name], name)


class RollupAndDegradation(unittest.TestCase):
    """V58: the top-level state is the Slice 1 listing rule over the cited
    evidence states — the evidence-plane rollup only. V53: unusable evidence
    degrades both planes with the recorded-failure citation preserved."""

    def test_v58_rollup_is_the_listing_rule_over_cited_evidence_states(self):
        # Mixed tree: collected + 403 + absent artifact. The rollup takes the
        # first non-collected cited state. It coincides with the descriptor
        # document's state by construction (citations carry the same states),
        # so this pins the value; the computed-from-citations path is code
        # inspection, per the spec's wording (S10 record).
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out,
                       [page_record([repo_item(1), repo_item(2), repo_item(3)])],
                       [sa_file(1, 200, sa_body()),
                        sa_file(2, 403, {"message": "Forbidden"})])
            doc = control_document(out)
            cited = [entry["evidence"]["state"]
                     for entry in doc["repositories"]]
            self.assertEqual(cited, ["collected", "inaccessible", "unknown"])
            self.assertEqual(doc["state"], "inaccessible")

    def test_v53_absent_artifact_degrades_both_planes_with_citation(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])])
            doc = control_document(out)
            self.assertEqual(doc["state"], "unknown")
            [entry] = doc["repositories"]
            self.assertEqual(entry["operational_state"], "unknown")
            self.assertEqual(entry["operational_state_reason"],
                             "evidence-unavailable")
            self.assertEqual(entry["applicability"], "applicability-unknown")
            self.assertEqual(entry["applicability_reason"],
                             "evidence-unavailable")
            self.assertEqual(entry["evidence"],
                             {"resource": "security-and-analysis",
                              "state": "unknown",
                              "reason": "raw-evidence-absent"})

    def test_v52_v54_inaccessible_citations_carry_their_exact_reasons(self):
        # The citation preserves the taxonomy's deterministic reason — the
        # 401/403 and anchor-less-404 classes stay distinguishable in the
        # document even though both planes degrade identically.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1), repo_item(2)])],
                       [sa_file(1, 403, {"message": "Forbidden"}),
                        sa_file(2, 404, {"message": "Not Found"})])
            doc = control_document(out)
            reasons = [(entry["evidence"]["reason"],
                        entry["operational_state"],
                        entry["applicability"])
                       for entry in doc["repositories"]]
            self.assertEqual(reasons, [
                ("authorization-denied", "inaccessible",
                 "applicability-unknown"),
                ("absence-rule-unmatched-404", "inaccessible",
                 "applicability-unknown"),
            ])

    def test_empty_estate_rolls_up_unknown_with_zero_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([])])
            doc = control_document(out)
            self.assertEqual(doc["state"], "unknown")
            self.assertEqual(doc["repositories"], [])
            self.assertEqual(doc["coverage"]["eligible_target_count"], 0)


class TableOrderOrchestration(unittest.TestCase):
    """The orchestration is generic over the control table: controls evaluate
    in table order with a fresh per-target resolved mapping, a chained
    control receives its predecessor's conclusion, and a future chained
    definition therefore needs no derive change (T5's architectural AC).
    Synthetic table only — the shipped CONTROLS stays secret-scanning."""

    def chained_documents(self, out):
        with mock.patch.object(controls, "CONTROLS",
                               (controls.SECRET_SCANNING, CHAINED)):
            derive_observed(out, run_id=RUN)
        controls_dir = out / "observed" / "controls"
        return ([path.name for path in sorted(controls_dir.iterdir())],
                json.loads((controls_dir / "chained-probe.json")
                           .read_text(encoding="utf-8")))

    def test_dependent_receives_its_predecessors_conclusion_per_target(self):
        # Target 1: SS applicable (enabled, public) -> the chained probe
        # concludes available. Target 2: SS applicability-unknown (disabled,
        # private) -> the chain stays unestablished. The per-target resolved
        # mapping is fresh - target 1's conclusion never leaks to target 2.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1), repo_item(2)])],
                       [sa_file(1, 200, sa_body()),
                        sa_file(2, 200,
                                sa_body(status_pair=("disabled", "disabled"),
                                        visibility="private"))])
            names, doc = self.chained_documents(out)
            self.assertEqual(names,
                             ["chained-probe.json", "secret-scanning.json"])
            chain_conclusions = [
                (entry["applicability"], entry["applicability_reason"],
                 entry["operational_state"])
                for entry in doc["repositories"]]
            self.assertEqual(chain_conclusions, [
                ("applicable", "secret-scanning-available", "disabled"),
                ("applicability-unknown",
                 "secret-scanning-availability-unknown", "disabled"),
            ])

    def test_own_enabled_status_precedes_the_chain_in_the_document(self):
        # V56's direction at the document seam: the probe's own affirmative
        # status self-evidences even where the predecessor is unknown.
        body = sa_body(status_pair=("disabled", "enabled"),
                       visibility="private")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [sa_file(1, 200, body)])
            _, doc = self.chained_documents(out)
            [entry] = doc["repositories"]
            self.assertEqual((entry["applicability"],
                              entry["applicability_reason"]),
                             ("applicable", "affirmative-enabled-status"))
            self.assertEqual(entry["operational_state"], "enabled")


if __name__ == "__main__":
    unittest.main()
