"""Applicability plane rules at the controls seam (Slice 3 T2).

The spec's secret-scanning rules, first match wins: an affirmatively
enabled control self-evidences applicability (deliberately asymmetric —
disabled establishes nothing); public visibility applies (V47, resting on
the platform fact the V44 enablement obligation proves); private/internal
is plan-gated and never guessed; undetermined visibility degrades; unusable
evidence degrades on this plane exactly as on the operational plane.
Exactly one state and one reason per entry.
"""
import unittest

from collector.controls import (
    APPLICABILITY_STATES, SECRET_SCANNING, applicability,
)
from test_controls_operational import entry


class SelfEvidencingRule(unittest.TestCase):
    def test_v44_enabled_status_self_evidences_applicability(self):
        self.assertEqual(applicability(SECRET_SCANNING, entry()),
                         ("applicable", "affirmative-enabled-status"))

    def test_rule_one_precedes_every_visibility_rule(self):
        # First match wins: enabled + private never reaches the plan-gated
        # rule; enabled + undetermined visibility never degrades.
        for visibility in ("private", "internal", "unknown", 5, None):
            with self.subTest(visibility=visibility):
                self.assertEqual(
                    applicability(SECRET_SCANNING,
                                  entry(visibility=visibility)),
                    ("applicable", "affirmative-enabled-status"))

    def test_disabled_establishes_nothing_about_applicability(self):
        # The asymmetry: disabled falls through to the visibility rules
        # rather than concluding anything on this plane.
        self.assertEqual(
            applicability(SECRET_SCANNING,
                          entry(scanning="disabled", visibility="private")),
            ("applicability-unknown", "visibility-not-public"))


class VisibilityRules(unittest.TestCase):
    def test_v47_public_visibility_applies(self):
        self.assertEqual(
            applicability(SECRET_SCANNING, entry(scanning="disabled")),
            ("applicable", "public-repository-visibility"))

    def test_v47_public_applies_under_undetermined_status_too(self):
        self.assertEqual(
            applicability(SECRET_SCANNING, entry(scanning="unknown")),
            ("applicable", "public-repository-visibility"))

    def test_private_and_internal_are_plan_gated_never_guessed(self):
        for visibility in ("private", "internal"):
            with self.subTest(visibility=visibility):
                self.assertEqual(
                    applicability(SECRET_SCANNING,
                                  entry(scanning="disabled",
                                        visibility=visibility)),
                    ("applicability-unknown", "visibility-not-public"))

    def test_undetermined_visibility_degrades_uncoerced(self):
        # Projected "unknown", unrecognized strings, and non-string values
        # all degrade; exact string matching, never coercion.
        for visibility in ("unknown", "Public", "PUBLIC", " public", "", 5,
                           True, None, ["public"]):
            with self.subTest(visibility=visibility):
                self.assertEqual(
                    applicability(SECRET_SCANNING,
                                  entry(scanning="disabled",
                                        visibility=visibility)),
                    ("applicability-unknown", "visibility-undetermined"))

    def test_missing_visibility_key_degrades(self):
        probe = entry(scanning="disabled")
        del probe["visibility"]
        self.assertEqual(applicability(SECRET_SCANNING, probe),
                         ("applicability-unknown", "visibility-undetermined"))


class UnusableEvidence(unittest.TestCase):
    def test_every_non_collected_state_degrades_on_this_plane(self):
        # V52/V53/V54's applicability half: the plane never concludes from
        # unusable evidence, whatever the projection carries.
        pairs = [("inaccessible", "authorization-denied"),
                 ("inaccessible", "absence-rule-unmatched-404"),
                 ("unknown", "raw-evidence-absent"),
                 ("unknown", "structural-conflict"),
                 ("failed", "transport-failed"),
                 ("incomplete", "pagination-cap"),
                 ("no-such-state", "no-such-reason")]
        for state, reason in pairs:
            with self.subTest(state=state):
                self.assertEqual(
                    applicability(SECRET_SCANNING,
                                  entry(state=state, reason=reason)),
                    ("applicability-unknown", "evidence-unavailable"))

    def test_enabled_projection_never_rescues_unusable_evidence(self):
        # Rule 1 requires collected evidence: an "enabled" value inside a
        # failed entry's projection establishes nothing.
        self.assertEqual(
            applicability(SECRET_SCANNING,
                          entry(state="failed", reason="shape-invalid")),
            ("applicability-unknown", "evidence-unavailable"))


class VocabularyMembership(unittest.TestCase):
    def test_every_returned_state_is_in_the_closed_vocabulary(self):
        # Pins the exported vocabulary to the rules' actual outputs so the
        # two cannot drift apart (S10 run-1 strengthening).
        probes = [entry(), entry(scanning="disabled"),
                  entry(scanning="disabled", visibility="private"),
                  entry(scanning="disabled", visibility="unknown"),
                  entry(state="inaccessible", reason="authorization-denied"),
                  entry(state="unknown", reason="raw-evidence-absent")]
        for probe in probes:
            state, _ = applicability(SECRET_SCANNING, probe)
            self.assertIn(state, APPLICABILITY_STATES)


if __name__ == "__main__":
    unittest.main()
