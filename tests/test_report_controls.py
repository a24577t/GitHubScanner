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
from collector.report import build_report, render_markdown
from collector.serialize import canonical_dumps
from collector.summary import control_aggregates
from test_derive_resources import RUN, page_record, repo_item, write_tree
from test_derive_security import sa_body, sa_file

# A deliberately meaningless second control on the shared surface: proves
# report additivity for any future definition without shipping one (the
# T2/T3 synthetic-definition device; carries no push-protection semantics).
SYNTHETIC = {"name": "synthetic-control",
             "descriptor": "security-and-analysis",
             "status_path": ("security_and_analysis", "synthetic_surface",
                             "status"),
             "applicability": "visibility"}


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


def tree_report(out):
    return build_report("https://api.example", "acme", RUN, "op",
                        run_summary(out, RUN))


def uniform_report(count):
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        security_tree(out, count,
                      [sa_file(i, 200, sa_body())
                       for i in range(1, count + 1)])
        return tree_report(out)


class ReportRendering(unittest.TestCase):
    def test_v59_report_json_carries_the_controls_block_verbatim(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            mixed_estate(out)
            summary = run_summary(out, RUN)
            report = build_report("https://api.example", "acme", RUN, "op",
                                  summary)
        self.assertEqual(report["controls"], summary["controls"])
        self.assertEqual(report["controls"]["secret-scanning"], MIXED_BLOCK)

    def test_markdown_renders_one_bounded_row_per_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            security_tree(out, 1, [sa_file(1, 200, sa_body())])
            markdown = render_markdown(tree_report(out))
        self.assertIn("## Per-control aggregates", markdown)
        self.assertIn(
            "| secret-scanning | applicable: 1 "
            "| affirmative-enabled-status: 1 | enabled: 1 "
            "| affirmative-status-enabled: 1 |", markdown)

    def test_report_size_independent_of_estate_size(self):
        small, large = uniform_report(2), uniform_report(12)
        self.assertEqual(canonical_dumps(small).count("\n"),
                         canonical_dumps(large).count("\n"))
        self.assertEqual(render_markdown(small).count("\n"),
                         render_markdown(large).count("\n"))

    def test_repeated_generation_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            mixed_estate(out)
            first, second = tree_report(out), tree_report(out)
        self.assertEqual(canonical_dumps(first), canonical_dumps(second))
        self.assertEqual(render_markdown(first), render_markdown(second))


class ExistingSectionPreservation(unittest.TestCase):
    def build_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            mixed_estate(out)
            with mock.patch.object(controls, "CONTROLS", ()):
                reduced = tree_report(out)
            return reduced, tree_report(out)

    def test_every_existing_json_section_is_byte_identical(self):
        reduced, shipped = self.build_pair()
        self.assertEqual(sorted(shipped),
                         sorted(list(reduced)))
        for key in reduced:
            if key == "controls":
                continue
            self.assertEqual(canonical_dumps(reduced[key]),
                             canonical_dumps(shipped[key]), key)
        self.assertEqual(reduced["controls"], {})

    def test_every_existing_markdown_line_is_preserved_verbatim(self):
        reduced, shipped = self.build_pair()
        reduced_lines = render_markdown(reduced).splitlines()
        shipped_lines = render_markdown(shipped).splitlines()
        for line in reduced_lines:
            self.assertIn(line, shipped_lines)
        self.assertEqual(
            [line for line in shipped_lines if line not in reduced_lines],
            ["| secret-scanning | applicability-unknown: 3, applicable: 3 "
             "| affirmative-enabled-status: 1, evidence-unavailable: 2, "
             "public-repository-visibility: 2, visibility-not-public: 1 "
             "| disabled: 2, enabled: 1, inaccessible: 1, unknown: 2 "
             "| affirmative-status-disabled: 2, affirmative-status-enabled: 1, "
             "evidence-inaccessible: 1, evidence-unavailable: 1, "
             "status-undetermined: 1 |"])


class SyntheticSecondControlAdditivity(unittest.TestCase):
    def test_second_control_is_purely_additive_at_the_report_seam(self):
        # T5's definition-only additivity proven forward at this seam: a
        # second definition on the shared surface adds one aggregate block
        # and one markdown row; the first control's bytes never move.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            mixed_estate(out)
            baseline = tree_report(out)
            with mock.patch.object(controls, "CONTROLS",
                                   controls.CONTROLS + (SYNTHETIC,)):
                extended = tree_report(out)
        self.assertEqual(sorted(extended["controls"]),
                         ["secret-scanning", "synthetic-control"])
        self.assertEqual(
            canonical_dumps(baseline["controls"]["secret-scanning"]),
            canonical_dumps(extended["controls"]["secret-scanning"]))
        baseline_lines = render_markdown(baseline).splitlines()
        extended_lines = render_markdown(extended).splitlines()
        for line in baseline_lines:
            self.assertIn(line, extended_lines)
        added = [line for line in extended_lines
                 if line not in baseline_lines]
        self.assertEqual(len(added), 1)
        self.assertTrue(added[0].startswith("| synthetic-control | "))
        # Sorted rendering: the synthetic row follows the shipped row.
        self.assertGreater(
            extended_lines.index(added[0]),
            extended_lines.index(next(
                line for line in extended_lines
                if line.startswith(
                    "| secret-scanning | applicability-unknown: 3"))))


if __name__ == "__main__":
    unittest.main()
