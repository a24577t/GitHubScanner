"""Report control aggregates (Slice 3 T4; V59 at the summary/report seams).

Orchestration: run_summary carries a per-control aggregate block computed
from the same in-memory control-observation documents derive emits - no
raw-evidence reread for control planes, no plane evaluation outside
controls.py, no control-specific branching. Rendering: the report's
controls section is bounded by the closed vocabularies and additive over
every existing section.
"""
import json
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path

from collector import controls
from collector.derive import derive_observed, run_summary
from collector.summary import control_aggregates
from test_derive_resources import RUN, page_record, repo_item, write_tree
from test_derive_security import sa_body, sa_file


def security_tree(out, count, files):
    write_tree(out, [page_record([repo_item(i) for i in
                                  range(1, count + 1)])], files)


def mixed_estate(out):
    """Six repositories spanning the V50-V56 evidence classes: affirmative
    enabled, affirmative disabled (public and private), unrecognized status,
    404, and absent artifact."""
    security_tree(out, 6, [
        sa_file(1, 200, sa_body()),
        sa_file(2, 200, sa_body(status_pair=("disabled", "disabled"))),
        sa_file(3, 200, sa_body(status_pair=("disabled", "disabled"),
                                visibility="private")),
        sa_file(4, 200, sa_body(status_pair=("paused", "disabled"))),
        sa_file(5, 404, {"message": "Not Found"}),
    ])


MIXED_BLOCK = {
    "applicability_counts": {"applicable": 3, "applicability-unknown": 3},
    "applicability_reason_counts": {
        "affirmative-enabled-status": 1, "public-repository-visibility": 2,
        "visibility-not-public": 1, "evidence-unavailable": 2},
    "operational_state_counts": {
        "enabled": 1, "disabled": 2, "unknown": 2, "inaccessible": 1},
    "operational_state_reason_counts": {
        "affirmative-status-enabled": 1, "affirmative-status-disabled": 2,
        "status-undetermined": 1, "evidence-unavailable": 1,
        "evidence-inaccessible": 1},
}


class SummaryOrchestration(unittest.TestCase):
    def test_v59_summary_carries_per_control_distribution_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            mixed_estate(out)
            summary = run_summary(out, RUN)
        self.assertEqual(sorted(summary["controls"]), ["secret-scanning"])
        self.assertEqual(summary["controls"]["secret-scanning"], MIXED_BLOCK)

    def test_legacy_tree_aggregates_evidence_unavailable_only(self):
        # T3-compatibility trees (no dedicated-request evidence anywhere)
        # count every entry as unknown / applicability-unknown ·
        # evidence-unavailable - never a crash, never disablement.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            security_tree(out, 2, [])
            summary = run_summary(out, RUN)
        self.assertEqual(summary["controls"]["secret-scanning"], {
            "applicability_counts": {"applicability-unknown": 2},
            "applicability_reason_counts": {"evidence-unavailable": 2},
            "operational_state_counts": {"unknown": 2},
            "operational_state_reason_counts": {"evidence-unavailable": 2},
        })

    def test_summary_block_equals_aggregation_of_the_emitted_document(self):
        # The block is exactly control_aggregates over the control-observation
        # document derive emits: the same in-memory document seam, no other
        # source, no reinterpretation.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            mixed_estate(out)
            derive_observed(out, run_id=RUN)
            emitted = json.loads(
                (out / "observed" / "controls" / "secret-scanning.json")
                .read_text(encoding="utf-8"))
            summary = run_summary(out, RUN)
        self.assertEqual(summary["controls"],
                         control_aggregates({"secret-scanning": emitted}))

    def test_controls_block_follows_the_control_table(self):
        # Table-driven, never name-driven: an empty control table yields an
        # empty block from the identical tree.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            security_tree(out, 1, [sa_file(1, 200, sa_body())])
            with mock.patch.object(controls, "CONTROLS", ()):
                summary = run_summary(out, RUN)
        self.assertEqual(summary["controls"], {})


if __name__ == "__main__":
    unittest.main()
