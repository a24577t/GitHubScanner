"""The shipped push-protection control through the generic engine (T5).

Ticket #71's additive emergence: the second control's observation document,
per-control aggregates, and report row emerge from the control definition
alone — derive, summary, and report carry no push-protection-specific
branch. First-run greens here are expected and disclosed: the T1-T4
machinery realizes the behavior, which is the architectural claim under
test. Reason literals are pinned verbatim from the accepted specification.
"""
import json
import shutil
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path

from collector import controls
from collector.derive import derive_observed, run_summary
from collector.report import render_markdown
from collector.serialize import canonical_dumps
from test_derive_controls_compat import observed_bytes
from test_derive_resources import (
    PROTECTION_BODY, RUN, page_record, protection, repo_item, write_tree,
)
from test_derive_rulesets import rs_file
from test_derive_security import sa_body, sa_file
from test_report_controls import mixed_estate, security_tree, tree_report
from test_resources_rulesets import RULESET_ITEM

DOCUMENT = "secret-scanning-push-protection.json"
PRE_T5 = (controls.SECRET_SCANNING,)


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


class TwoWorldAdditivity(unittest.TestCase):
    """Pre-T5 control table vs the shipped table over identical trees: the
    only difference anywhere is the additive push-protection output. Any
    other delta is a failure to investigate, never an expected consequence
    (ticket #71's architectural AC; ADR-0009's byte-identity consequence).
    """

    def full_tree(self, out):
        # Every descriptor exercised, security evidence spanning collected,
        # denied, and absent classes.
        write_tree(out, [page_record([repo_item(1), repo_item(2),
                                      repo_item(3)])],
                   [protection("1-repo-1", 200, PROTECTION_BODY),
                    rs_file(2, 1, [RULESET_ITEM]),
                    sa_file(1, 200, sa_body()),
                    sa_file(2, 403, {"message": "Forbidden"})])

    def test_only_new_observed_output_is_the_push_protection_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            worlds = {}
            for name, table in (("before", PRE_T5),
                                ("after", controls.CONTROLS)):
                out = Path(tmp) / name
                self.full_tree(out)
                with mock.patch.object(controls, "CONTROLS", table):
                    derive_observed(out, run_id=RUN)
                worlds[name] = observed_bytes(out)
        added = "controls/" + DOCUMENT
        self.assertIn(added, worlds["after"])
        self.assertNotIn(added, worlds["before"])
        del worlds["after"][added]
        # Byte-for-byte: every pre-T5 document including the secret-scanning
        # control document is untouched by the second control.
        self.assertEqual(worlds["before"], worlds["after"])

    def world_report(self, out, table):
        with mock.patch.object(controls, "CONTROLS", table):
            return tree_report(out)

    def test_report_gains_only_the_push_protection_representation(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            mixed_estate(out)
            before = self.world_report(out, PRE_T5)
            after = self.world_report(out, controls.CONTROLS)
        self.assertEqual(sorted(before), sorted(after))
        for key in before:
            if key != "controls":
                # Includes execution: planned request counts identical —
                # the second control introduces no request.
                self.assertEqual(canonical_dumps(before[key]),
                                 canonical_dumps(after[key]), key)
        self.assertEqual(sorted(after["controls"]),
                         ["secret-scanning", "secret-scanning-push-protection"])
        self.assertEqual(
            canonical_dumps(before["controls"]["secret-scanning"]),
            canonical_dumps(after["controls"]["secret-scanning"]))
        before_lines = render_markdown(before).splitlines()
        after_lines = render_markdown(after).splitlines()
        for line in before_lines:
            self.assertIn(line, after_lines)
        added = [line for line in after_lines if line not in before_lines]
        self.assertEqual(len(added), 1)
        self.assertTrue(
            added[0].startswith("| secret-scanning-push-protection | "))


class CommittedTreeCompatibility(unittest.TestCase):
    """V60 extended to the second control: on the committed Slice-1/2
    validation-run trees (no dedicated-request evidence exists) every
    push-protection conclusion degrades honestly — never disablement, the
    chain never established, the recorded-failure citation preserved."""

    RUNS = Path(__file__).resolve().parent.parent / "docs" / "validation" / "runs"

    def assert_degrades(self, run_name):
        committed = self.RUNS / run_name
        run_id = next((committed / "evidence" / "raw").iterdir()).name
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            shutil.copytree(committed / "evidence", out / "evidence")
            derive_observed(out, run_id=run_id)
            doc = json.loads((out / "observed" / "controls" / DOCUMENT)
                             .read_text(encoding="utf-8"))
        self.assertTrue(doc["repositories"])
        for entry in doc["repositories"]:
            self.assertEqual(
                (entry["operational_state"],
                 entry["operational_state_reason"],
                 entry["applicability"], entry["applicability_reason"],
                 entry["evidence"]["reason"]),
                ("unknown", "evidence-unavailable", "applicability-unknown",
                 "secret-scanning-availability-unknown",
                 "raw-evidence-absent"))

    def test_committed_slice1_run_tree(self):
        self.assert_degrades("20260725-GHScannerLab")

    def test_committed_slice2_run_tree(self):
        self.assert_degrades("20260730-GHScannerLab")


if __name__ == "__main__":
    unittest.main()
