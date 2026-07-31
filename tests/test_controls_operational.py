"""Operational-state plane rules at the controls seam (Slice 3 T2).

The spec's five first-match-wins rules over the derived descriptor entry:
affirmative enabled/disabled from the exact projected status string (V43/V44
offline analogs), everything else undetermined and never coerced (V50/V51),
inaccessible evidence degrading to inaccessible (V52/V54), and every other
evidence state degrading to unknown · evidence-unavailable (V53 and the
failed/incomplete/conflict trees). Exactly one state and one reason per
entry; ambiguity degrades, never concludes (ADR-0008).
"""
import unittest

from collector.controls import (
    OPERATIONAL_STATES, SECRET_SCANNING, operational_state,
)


def entry(state="collected", reason="collected", scanning="enabled",
          visibility="public"):
    """A derived security-and-analysis document entry (the exact shape
    projections.resource_document emits for this descriptor)."""
    return {
        "id": 1, "full_name": "acme/repo-1", "state": state, "reason": reason,
        "visibility": visibility,
        "security_and_analysis": {
            "secret_scanning": {"status": scanning},
            "secret_scanning_push_protection": {"status": "disabled"},
        },
    }


class AffirmativeStatuses(unittest.TestCase):
    def test_v44_enabled_status_derives_enabled(self):
        self.assertEqual(operational_state(SECRET_SCANNING, entry()),
                         ("enabled", "affirmative-status-enabled"))

    def test_v43_disabled_status_derives_disabled(self):
        self.assertEqual(
            operational_state(SECRET_SCANNING, entry(scanning="disabled")),
            ("disabled", "affirmative-status-disabled"))

    def test_own_field_only_never_the_sibling_control(self):
        # SS disabled while the sibling push-protection status is enabled:
        # the definition's status_path must select secret_scanning — a
        # sibling leak would derive enabled.
        probe = entry(scanning="disabled")
        probe["security_and_analysis"]["secret_scanning_push_protection"] = {
            "status": "enabled"}
        self.assertEqual(operational_state(SECRET_SCANNING, probe),
                         ("disabled", "affirmative-status-disabled"))


class UndeterminedStatuses(unittest.TestCase):
    def test_v50_projected_unknown_derives_status_undetermined(self):
        # An absent surface projects the leaf "unknown" (T1); the control
        # plane reads that as undetermined, never as disablement (ADR-0008).
        self.assertEqual(
            operational_state(SECRET_SCANNING, entry(scanning="unknown")),
            ("unknown", "status-undetermined"))

    def test_v51_unrecognized_and_nonstring_statuses_never_coerce(self):
        for status in ("paused", 5, True, False, 1, 0, None, "ENABLED",
                       "Enabled", " enabled", ["enabled"], {"enabled": True}):
            with self.subTest(status=status):
                self.assertEqual(
                    operational_state(SECRET_SCANNING,
                                      entry(scanning=status)),
                    ("unknown", "status-undetermined"))

    def test_malformed_surface_shapes_are_undetermined_under_collected(self):
        # Path traversal over a non-dict never raises and never concludes.
        for surface in ("unknown", 5, None, True, ["secret_scanning"],
                        {"secret_scanning": "enabled"},
                        {"secret_scanning": {"no_status": 1}}):
            with self.subTest(surface=surface):
                probe = entry()
                probe["security_and_analysis"] = surface
                self.assertEqual(operational_state(SECRET_SCANNING, probe),
                                 ("unknown", "status-undetermined"))

    def test_missing_surface_key_is_undetermined_under_collected(self):
        probe = entry()
        del probe["security_and_analysis"]
        self.assertEqual(operational_state(SECRET_SCANNING, probe),
                         ("unknown", "status-undetermined"))


class InaccessibleEvidence(unittest.TestCase):
    def test_v52_authorization_denied_degrades_to_inaccessible(self):
        self.assertEqual(
            operational_state(SECRET_SCANNING,
                              entry(state="inaccessible",
                                    reason="authorization-denied",
                                    scanning="unknown")),
            ("inaccessible", "evidence-inaccessible"))

    def test_v54_absence_rule_unmatched_404_degrades_to_inaccessible(self):
        # No absence anchor exists: the 404 is inaccessible evidence, never
        # absence, never disablement.
        self.assertEqual(
            operational_state(SECRET_SCANNING,
                              entry(state="inaccessible",
                                    reason="absence-rule-unmatched-404",
                                    scanning="unknown")),
            ("inaccessible", "evidence-inaccessible"))


class UnavailableEvidence(unittest.TestCase):
    def test_v53_and_every_other_evidence_state_degrades_to_unknown(self):
        # Rule 5's tree: failed, unknown (raw-evidence-absent,
        # missing-required-input, structural-conflict), incomplete — and any
        # unrecognized state string — all derive unknown ·
        # evidence-unavailable; enablement values in the projection never
        # rescue unusable evidence.
        pairs = [("unknown", "raw-evidence-absent"),
                 ("unknown", "missing-required-input"),
                 ("unknown", "structural-conflict"),
                 ("failed", "shape-invalid"),
                 ("failed", "transport-failed"),
                 ("incomplete", "pagination-cap"),
                 ("absent", "absence-message-matched"),
                 ("no-such-state", "no-such-reason")]
        for state, reason in pairs:
            with self.subTest(state=state):
                self.assertEqual(
                    operational_state(SECRET_SCANNING,
                                      entry(state=state, reason=reason)),
                    ("unknown", "evidence-unavailable"))

    def test_entry_state_is_matched_exactly_never_coerced(self):
        for state in ("Collected", "COLLECTED", True, 1, None):
            with self.subTest(state=state):
                self.assertEqual(
                    operational_state(SECRET_SCANNING, entry(state=state)),
                    ("unknown", "evidence-unavailable"))


class VocabularyMembership(unittest.TestCase):
    def test_every_returned_state_is_in_the_closed_vocabulary(self):
        # Pins the exported vocabulary to the rules' actual outputs so the
        # two cannot drift apart (S10 run-1 strengthening).
        probes = [entry(), entry(scanning="disabled"),
                  entry(scanning="paused"), entry(scanning="unknown"),
                  entry(state="inaccessible", reason="authorization-denied"),
                  entry(state="failed", reason="transport-failed"),
                  entry(state="unknown", reason="raw-evidence-absent")]
        for probe in probes:
            state, _ = operational_state(SECRET_SCANNING, probe)
            self.assertIn(state, OPERATIONAL_STATES)


if __name__ == "__main__":
    unittest.main()
