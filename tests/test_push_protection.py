"""The shipped push-protection control through the generic engine (T5).

Ticket #71's additive emergence: the second control's observation document,
per-control aggregates, and report row emerge from the control definition
alone — derive, summary, and report carry no push-protection-specific
branch. First-run greens here are expected and disclosed: the T1-T4
machinery realizes the behavior, which is the architectural claim under
test. Reason literals are pinned verbatim from the accepted specification.
"""
import json
import tempfile
import unittest
from pathlib import Path

from collector.derive import derive_observed, run_summary
from collector.report import render_markdown
from test_derive_resources import RUN, page_record, repo_item, write_tree
from test_derive_security import sa_body, sa_file
from test_report_controls import mixed_estate, security_tree, tree_report

DOCUMENT = "secret-scanning-push-protection.json"


def pp_document(out):
    derive_observed(out, run_id=RUN)
    path = out / "observed" / "controls" / DOCUMENT
    return json.loads(path.read_text(encoding="utf-8"))


class DocumentEmergence(unittest.TestCase):
    def test_chain_conclusions_per_target_in_discovery_order(self):
        # Target 1: SS applicable (enabled, public); PP affirmatively
        # disabled — the chain concludes available while the operational
        # plane stays disabled (V46's direction). Target 2: SS
        # applicability-unknown (disabled, private) — the chain stays
        # unestablished (V55). Pages arrive out of id order; entries must
        # inherit the canonical ascending discovery order.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(2), repo_item(1)])],
                       [sa_file(1, 200, sa_body()),
                        sa_file(2, 200,
                                sa_body(status_pair=("disabled", "disabled"),
                                        visibility="private"))])
            doc = pp_document(out)
        self.assertEqual(doc["state"], "collected")
        self.assertEqual(
            [(entry["id"], entry["applicability"],
              entry["applicability_reason"], entry["operational_state"],
              entry["operational_state_reason"])
             for entry in doc["repositories"]],
            [(1, "applicable", "secret-scanning-available",
              "disabled", "affirmative-status-disabled"),
             (2, "applicability-unknown",
              "secret-scanning-availability-unknown",
              "disabled", "affirmative-status-disabled")])
        for entry in doc["repositories"]:
            self.assertEqual(entry["evidence"],
                             {"resource": "security-and-analysis",
                              "state": "collected", "reason": "collected"})

    def test_v56_own_enabled_status_precedes_the_chain(self):
        # PP affirmatively enabled while SS is disabled on a private
        # repository: the chain is unestablished, yet rule 1 self-evidences
        # applicability and the operational plane concludes enabled.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [sa_file(1, 200,
                                sa_body(status_pair=("disabled", "enabled"),
                                        visibility="private"))])
            doc = pp_document(out)
        [entry] = doc["repositories"]
        self.assertEqual((entry["applicability"],
                          entry["applicability_reason"],
                          entry["operational_state"],
                          entry["operational_state_reason"]),
                         ("applicable", "affirmative-enabled-status",
                          "enabled", "affirmative-status-enabled"))


class ReportEmergence(unittest.TestCase):
    def test_v59_four_count_families_over_the_mixed_estate(self):
        # The six-repository V50-V56 estate through the generic aggregation:
        # observed keys only, closed vocabularies, chain reasons counted as
        # emitted.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            mixed_estate(out)
            summary = run_summary(out, RUN)
        self.assertEqual(
            summary["controls"]["secret-scanning-push-protection"], {
                "applicability_counts": {
                    "applicable": 3, "applicability-unknown": 3},
                "applicability_reason_counts": {
                    "secret-scanning-available": 3,
                    "secret-scanning-availability-unknown": 3},
                "operational_state_counts": {
                    "disabled": 4, "inaccessible": 1, "unknown": 1},
                "operational_state_reason_counts": {
                    "affirmative-status-disabled": 4,
                    "evidence-inaccessible": 1,
                    "evidence-unavailable": 1},
            })

    def test_markdown_renders_the_push_protection_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            security_tree(out, 1, [sa_file(1, 200, sa_body())])
            markdown = render_markdown(tree_report(out))
        self.assertIn("## Per-control aggregates", markdown)
        self.assertIn(
            "| secret-scanning-push-protection | applicable: 1 "
            "| secret-scanning-available: 1 | disabled: 1 "
            "| affirmative-status-disabled: 1 |", markdown)


if __name__ == "__main__":
    unittest.main()
