"""Chain applicability kind and the derived-entry contract (Slice 3 T2).

The ("chain", <control>) kind ships with the evaluation layer so T5's
push-protection diff is the control definition alone (ADR-0009 additivity;
the spec's T5 architectural AC) — the chain rules are pinned here through a
synthetic definition; the shipped table still carries secret-scanning only.
The contract class proves the entries the evaluator consumes are exactly
the entries projections.resource_document emits for the shipped descriptor.
"""
import tempfile
import unittest
from pathlib import Path

from collector.controls import (
    SECRET_SCANNING, applicability, operational_state, validate_controls,
)
from test_controls_operational import entry
from test_derive_resources import page_record, repo_item, write_tree
from test_derive_security import sa_body, sa_doc, sa_file

CHAINED = {
    "name": "chained-probe",
    "descriptor": "security-and-analysis",
    "status_path": (
        "security_and_analysis", "secret_scanning_push_protection", "status"),
    "applicability": ("chain", "secret-scanning"),
}


def pp_entry(push="disabled", **overrides):
    probe = entry(**overrides)
    probe["security_and_analysis"]["secret_scanning_push_protection"] = {
        "status": push}
    return probe


class ChainRules(unittest.TestCase):
    def test_chain_definition_validates_against_the_shipped_table(self):
        self.assertIsNone(validate_controls((SECRET_SCANNING, CHAINED)))

    def test_v56_own_enabled_status_precedes_the_chain(self):
        # Rule 1 self-evidences even where the chain is unresolved and the
        # visibility is undetermined (the asymmetric rule's precedence).
        probe = pp_entry(push="enabled", visibility="unknown")
        self.assertEqual(applicability(CHAINED, probe),
                         ("applicable", "affirmative-enabled-status"))

    def test_chained_applicable_derives_available(self):
        # V46's direction: the chain keys on availability, never enablement,
        # and the reason names the chained control.
        probe = pp_entry(push="disabled")
        self.assertEqual(
            applicability(CHAINED, probe, {"secret-scanning": "applicable"}),
            ("applicable", "secret-scanning-available"))

    def test_v55_unestablished_chain_degrades(self):
        for resolved in (None, {}, {"secret-scanning": "applicability-unknown"},
                         {"other-control": "applicable"}):
            with self.subTest(resolved=resolved):
                self.assertEqual(
                    applicability(CHAINED, pp_entry(push="disabled"),
                                  resolved),
                    ("applicability-unknown",
                     "secret-scanning-availability-unknown"))

    def test_chain_state_is_matched_exactly(self):
        for state in ("Applicable", True, 1, ""):
            with self.subTest(state=state):
                self.assertEqual(
                    applicability(CHAINED, pp_entry(push="disabled"),
                                  {"secret-scanning": state}),
                    ("applicability-unknown",
                     "secret-scanning-availability-unknown"))

    def test_v55_planes_stay_independent(self):
        # Operational state derives from the control's own field even where
        # its applicability is unknown.
        probe = pp_entry(push="enabled")
        self.assertEqual(applicability(CHAINED, pp_entry(push="disabled"), {}),
                         ("applicability-unknown",
                          "secret-scanning-availability-unknown"))
        self.assertEqual(operational_state(CHAINED, probe),
                         ("enabled", "affirmative-status-enabled"))

    def test_rule_two_keys_on_the_resolved_chain_state_only(self):
        # The rule as specified carries no entry-state precondition; on the
        # shared surface the inputs cannot actually diverge (the chained
        # conclusion derives from the same entry), so this pins verbatim
        # rule shape, not a reachable live path.
        probe = pp_entry(state="failed", reason="shape-invalid")
        self.assertEqual(
            applicability(CHAINED, probe, {"secret-scanning": "applicable"}),
            ("applicable", "secret-scanning-available"))

    def test_visibility_kind_ignores_the_resolved_mapping(self):
        self.assertEqual(
            applicability(SECRET_SCANNING, entry(scanning="disabled"),
                          {"secret-scanning": "applicable"}),
            ("applicable", "public-repository-visibility"))


class DerivedEntryContract(unittest.TestCase):
    """The evaluator consumes exactly what the generic engine derives."""

    def conclusions(self, files):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])], files)
            [derived] = sa_doc(out)["repositories"]
        return (operational_state(SECRET_SCANNING, derived),
                applicability(SECRET_SCANNING, derived))

    def test_collected_enabled_entry_concludes_on_both_planes(self):
        operational, applic = self.conclusions(
            [sa_file(1, 200, sa_body())])
        self.assertEqual(operational, ("enabled", "affirmative-status-enabled"))
        self.assertEqual(applic, ("applicable", "affirmative-enabled-status"))

    def test_v50_absent_surface_stays_undetermined_through_the_seam(self):
        body = {key: value for key, value in sa_body().items()
                if key != "security_and_analysis"}
        operational, applic = self.conclusions([sa_file(1, 200, body)])
        self.assertEqual(operational, ("unknown", "status-undetermined"))
        self.assertEqual(applic, ("applicable", "public-repository-visibility"))

    def test_v52_authorization_denied_degrades_both_planes(self):
        operational, applic = self.conclusions(
            [sa_file(1, 403, {"message": "Forbidden"})])
        self.assertEqual(operational,
                         ("inaccessible", "evidence-inaccessible"))
        self.assertEqual(applic,
                         ("applicability-unknown", "evidence-unavailable"))

    def test_v54_dedicated_request_404_degrades_both_planes(self):
        operational, applic = self.conclusions(
            [sa_file(1, 404, {"message": "Not Found"})])
        self.assertEqual(operational,
                         ("inaccessible", "evidence-inaccessible"))
        self.assertEqual(applic,
                         ("applicability-unknown", "evidence-unavailable"))

    def test_v53_absent_artifact_degrades_both_planes(self):
        operational, applic = self.conclusions([])
        self.assertEqual(operational, ("unknown", "evidence-unavailable"))
        self.assertEqual(applic,
                         ("applicability-unknown", "evidence-unavailable"))


if __name__ == "__main__":
    unittest.main()
