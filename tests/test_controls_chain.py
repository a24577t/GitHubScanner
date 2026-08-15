"""Chain applicability kind and the derived-entry contract (Slice 3 T2).

The ("chain", <control>) kind shipped with the evaluation layer so T5's
push-protection diff is the control definition alone (ADR-0009 additivity;
the spec's T5 architectural AC) — the chain rules are pinned generically
through a synthetic definition, and the ShippedPushProtection class pins
the real T5 definition through the same unchanged seam (V55/V56, V45/V46
offline analogs). The contract class proves the entries the evaluator
consumes are exactly the entries projections.resource_document emits for
the shipped descriptor.
"""
import tempfile
import unittest
from pathlib import Path

from collector.controls import (
    PUSH_PROTECTION, SECRET_SCANNING, applicability, operational_state,
    validate_controls,
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


class ShippedPushProtection(unittest.TestCase):
    """The real T5 definition through the unchanged evaluation seam.

    Reason literals are pinned verbatim from the accepted specification,
    never derived in the test. First-run greens here are expected and are
    the point: the generic chain machinery already realizes the behavior
    (ticket #71's architectural AC)."""

    def test_v56_own_enabled_status_self_evidences(self):
        # Rule 1 precedes the chain even where visibility is undetermined
        # and the chain is unresolved (the deliberately asymmetric rule).
        probe = pp_entry(push="enabled", visibility="unknown")
        self.assertEqual(applicability(PUSH_PROTECTION, probe),
                         ("applicable", "affirmative-enabled-status"))

    def test_v46_analog_chain_keys_on_availability_never_enablement(self):
        # PP affirmatively disabled while secret-scanning is applicable:
        # the pair stays distinguishable — applicable via the chain, yet
        # operationally disabled.
        probe = pp_entry(push="disabled")
        self.assertEqual(
            applicability(PUSH_PROTECTION, probe,
                          {"secret-scanning": "applicable"}),
            ("applicable", "secret-scanning-available"))
        self.assertEqual(operational_state(PUSH_PROTECTION, probe),
                         ("disabled", "affirmative-status-disabled"))

    def test_v55_unestablished_chain_degrades(self):
        for resolved in (None, {},
                         {"secret-scanning": "applicability-unknown"}):
            with self.subTest(resolved=resolved):
                self.assertEqual(
                    applicability(PUSH_PROTECTION, pp_entry(push="disabled"),
                                  resolved),
                    ("applicability-unknown",
                     "secret-scanning-availability-unknown"))

    def test_v55_operational_state_stays_on_its_own_field(self):
        # Planes independent: the operational conclusion derives from the
        # push-protection status even where applicability is unknown.
        self.assertEqual(
            operational_state(PUSH_PROTECTION, pp_entry(push="disabled")),
            ("disabled", "affirmative-status-disabled"))

    def test_v45_analog_enabled_concludes_on_both_planes(self):
        probe = pp_entry(push="enabled")
        self.assertEqual(operational_state(PUSH_PROTECTION, probe),
                         ("enabled", "affirmative-status-enabled"))
        self.assertEqual(applicability(PUSH_PROTECTION, probe, {}),
                         ("applicable", "affirmative-enabled-status"))

    def test_degraded_evidence_rules_apply_to_the_real_definition(self):
        # The shared first-match rules verbatim: unrecognized status never
        # coerced; inaccessible and unusable evidence degrade honestly.
        self.assertEqual(operational_state(PUSH_PROTECTION, pp_entry(push=5)),
                         ("unknown", "status-undetermined"))
        self.assertEqual(
            operational_state(PUSH_PROTECTION,
                              pp_entry(state="inaccessible",
                                       reason="authorization-denied")),
            ("inaccessible", "evidence-inaccessible"))
        self.assertEqual(
            operational_state(PUSH_PROTECTION,
                              pp_entry(state="unknown",
                                       reason="raw-evidence-absent")),
            ("unknown", "evidence-unavailable"))


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
