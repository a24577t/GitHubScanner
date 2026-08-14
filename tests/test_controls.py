"""The control-definition table and its import-time validation (Slice 3 T2).

ADR-0009's control-definition layer: controls are reviewed in-code
declarative data validated at import time exactly as the descriptor table
is. The shipped table carries both slice controls — secret-scanning and its
chained dependent secret-scanning-push-protection (T5's definition-only
diff, ticket #71). Malformed definitions are rejected loudly (ticket #68
AC).
"""
import unittest

from collector import controls


def control(**overrides):
    """A structurally valid control definition to mutate per probe."""
    base = {
        "name": "probe-control",
        "descriptor": "security-and-analysis",
        "status_path": ("security_and_analysis", "secret_scanning", "status"),
        "applicability": "visibility",
    }
    base.update(overrides)
    return base


class ShippedTable(unittest.TestCase):
    def test_table_ships_both_slice_controls_in_chain_order(self):
        # T5 adds the push-protection definition (spec Tasks: T5; ticket
        # #71). Table order is load-bearing: a chain target must precede its
        # dependent (single deterministic evaluation pass).
        self.assertEqual(
            [entry["name"] for entry in controls.CONTROLS],
            ["secret-scanning", "secret-scanning-push-protection"])

    def test_secret_scanning_definition_is_pinned_field_by_field(self):
        [definition, _] = controls.CONTROLS
        self.assertEqual(definition, {
            "name": "secret-scanning",
            "descriptor": "security-and-analysis",
            "status_path": (
                "security_and_analysis", "secret_scanning", "status"),
            "applicability": "visibility",
        })

    def test_push_protection_definition_is_pinned_field_by_field(self):
        # Spec Control definitions: own status field on the shared
        # security-and-analysis surface (no descriptor change, no new
        # request); applicability chains on secret-scanning availability.
        [_, definition] = controls.CONTROLS
        self.assertEqual(definition, {
            "name": "secret-scanning-push-protection",
            "descriptor": "security-and-analysis",
            "status_path": (
                "security_and_analysis", "secret_scanning_push_protection",
                "status"),
            "applicability": ("chain", "secret-scanning"),
        })

    def test_shipped_table_passes_its_own_validation(self):
        self.assertIsNone(controls.validate_controls(controls.CONTROLS))

    def test_closed_plane_vocabularies_are_pinned(self):
        # Operational subset excludes `unavailable` (grill condition 2) and
        # the configuration triple (boolean-enablement controls).
        self.assertEqual(controls.OPERATIONAL_STATES,
                         frozenset({"enabled", "disabled", "inaccessible",
                                    "unknown"}))
        self.assertEqual(controls.APPLICABILITY_STATES,
                         frozenset({"applicable", "applicability-unknown"}))


class TableValidation(unittest.TestCase):
    def assert_rejects(self, table, fragment):
        with self.assertRaises(ValueError) as ctx:
            controls.validate_controls(table)
        self.assertIn(fragment, str(ctx.exception))

    def test_empty_table_is_rejected(self):
        self.assert_rejects((), "control table is empty")

    def test_malformed_names_are_rejected(self):
        for name in ("", "Probe", "probe_control", "-probe", "probe-", 5,
                     None):
            with self.subTest(name=name):
                self.assert_rejects((control(name=name),),
                                    "malformed control name")

    def test_duplicate_names_are_rejected(self):
        self.assert_rejects((control(), control()), "duplicate control name")

    def test_unknown_descriptor_is_rejected(self):
        # Each control names its evidence descriptor (ADR-0009); a name
        # outside the descriptor table cannot identify retained evidence.
        for descriptor in ("no-such-descriptor", "", None, 7):
            with self.subTest(descriptor=descriptor):
                self.assert_rejects((control(descriptor=descriptor),),
                                    "unknown evidence descriptor")

    def test_malformed_status_paths_are_rejected(self):
        for path in ((), ("",), ("ok", 5), "security_and_analysis", None,
                     ["security_and_analysis"]):
            with self.subTest(path=path):
                self.assert_rejects((control(status_path=path),),
                                    "status_path")

    def test_unknown_applicability_kind_is_rejected(self):
        for kind in ("chained", "", None, 5, ("visibility",)):
            with self.subTest(kind=kind):
                self.assert_rejects((control(applicability=kind),),
                                    "applicability")

    def test_chain_to_unknown_control_is_rejected(self):
        self.assert_rejects(
            (control(applicability=("chain", "no-such-control")),),
            "chains on unknown control")

    def test_chain_forward_reference_is_rejected(self):
        # A chain target must be declared earlier in the table: evaluation is
        # a single deterministic pass in table order.
        first = control(name="first", applicability=("chain", "second"))
        second = control(name="second")
        self.assert_rejects((first, second), "chains on unknown control")

    def test_chain_to_self_is_rejected(self):
        self.assert_rejects(
            (control(applicability=("chain", "probe-control")),),
            "chains on unknown control")

    def test_malformed_chain_forms_are_rejected(self):
        for kind in (("chain",), ("chain", ""), ("chain", 5),
                     ("chain", "a", "b")):
            with self.subTest(kind=kind):
                self.assert_rejects(
                    (control(name="target"), control(applicability=kind)),
                    "applicability")


if __name__ == "__main__":
    unittest.main()
