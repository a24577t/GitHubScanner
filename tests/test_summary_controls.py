"""Per-control distribution aggregates at the summary seam (Slice 3 T4; V59).

The pure counting function over control-observation documents: the four
count families the specification's Reporting section enumerates -
applicability counts, applicability-reason counts, operational-state
counts, operational-state-reason counts - closed vocabularies only,
observed keys only, never zero-filled. Evidence-plane state and citations
never enter the aggregates (rollup of either plane is rejected by
ADR-0009); size is bounded by the closed vocabularies, never the estate.
"""
import unittest

from collector.serialize import canonical_dumps
from collector.summary import control_aggregates

RUN = "20260101T000000Z"

FAMILIES = ["applicability_counts", "applicability_reason_counts",
            "operational_state_counts", "operational_state_reason_counts"]


def control_document(entries, state="collected"):
    return {"run_id": RUN, "state": state,
            "coverage": {"basis": "eligible-discovered-repositories",
                         "inventory_state": "collected",
                         "eligible_target_count": len(entries)},
            "repositories": entries}


def entry(i, applicability="applicable",
          applicability_reason="public-repository-visibility",
          operational_state="disabled",
          operational_state_reason="affirmative-status-disabled",
          evidence_state="collected", evidence_reason="collected"):
    return {"id": i, "full_name": f"acme/repo-{i}",
            "applicability": applicability,
            "applicability_reason": applicability_reason,
            "operational_state": operational_state,
            "operational_state_reason": operational_state_reason,
            "evidence": {"resource": "security-and-analysis",
                         "state": evidence_state, "reason": evidence_reason}}


class AggregateShape(unittest.TestCase):
    def test_v59_four_count_families_over_mixed_entries(self):
        document = control_document([
            entry(1),
            entry(2, applicability_reason="affirmative-enabled-status",
                  operational_state="enabled",
                  operational_state_reason="affirmative-status-enabled"),
            entry(3, applicability="applicability-unknown",
                  applicability_reason="visibility-not-public",
                  operational_state="unknown",
                  operational_state_reason="status-undetermined"),
            entry(4, applicability="applicability-unknown",
                  applicability_reason="evidence-unavailable",
                  operational_state="inaccessible",
                  operational_state_reason="evidence-inaccessible",
                  evidence_state="inaccessible",
                  evidence_reason="absence-rule-unmatched-404"),
        ])
        block = control_aggregates({"secret-scanning": document})
        self.assertEqual(sorted(block), ["secret-scanning"])
        block = block["secret-scanning"]
        self.assertEqual(sorted(block), FAMILIES)
        self.assertEqual(block["applicability_counts"],
                         {"applicable": 2, "applicability-unknown": 2})
        self.assertEqual(block["applicability_reason_counts"],
                         {"public-repository-visibility": 1,
                          "affirmative-enabled-status": 1,
                          "visibility-not-public": 1,
                          "evidence-unavailable": 1})
        self.assertEqual(block["operational_state_counts"],
                         {"disabled": 1, "enabled": 1, "unknown": 1,
                          "inaccessible": 1})
        self.assertEqual(block["operational_state_reason_counts"],
                         {"affirmative-status-disabled": 1,
                          "affirmative-status-enabled": 1,
                          "status-undetermined": 1,
                          "evidence-inaccessible": 1})

    def test_no_evidence_plane_state_and_no_citations_in_the_block(self):
        # The four families are exhaustive: the document's evidence-plane
        # rollup and the per-entry citations never surface in aggregates.
        block = control_aggregates(
            {"secret-scanning": control_document([entry(1)])})
        self.assertEqual(sorted(block["secret-scanning"]), FAMILIES)

    def test_observed_keys_only_absent_states_never_zero_filled(self):
        document = control_document([entry(1), entry(2)])
        block = control_aggregates({"secret-scanning": document})
        block = block["secret-scanning"]
        self.assertEqual(block["operational_state_counts"], {"disabled": 2})
        self.assertEqual(block["applicability_counts"], {"applicable": 2})

    def test_closed_vocabulary_gating_excluded_states_never_counted(self):
        # `unavailable` (grill condition 2) and `not-applicable` (unreachable
        # this slice) are outside the closed plane vocabularies: never
        # counted, even if a document claimed them. The plane conclusion is
        # emitted as one (state, reason) pair, so an excluded state
        # suppresses its paired reason too - the other plane's conclusion on
        # the same entry still counts.
        document = control_document([
            entry(1, operational_state="unavailable",
                  operational_state_reason="plan-gated"),
            entry(2, applicability="not-applicable",
                  applicability_reason="platform-fact"),
            entry(3),
        ])
        block = control_aggregates({"secret-scanning": document})
        block = block["secret-scanning"]
        self.assertEqual(block["operational_state_counts"], {"disabled": 2})
        self.assertEqual(block["operational_state_reason_counts"],
                         {"affirmative-status-disabled": 2})
        self.assertEqual(block["applicability_counts"], {"applicable": 2})
        self.assertEqual(block["applicability_reason_counts"],
                         {"public-repository-visibility": 2})

    def test_empty_control_set_aggregates_to_empty_mapping(self):
        self.assertEqual(control_aggregates({}), {})

    def test_empty_estate_yields_four_empty_maps(self):
        block = control_aggregates(
            {"secret-scanning": control_document([])})
        self.assertEqual(block["secret-scanning"],
                         {family: {} for family in FAMILIES})

    def test_empty_maps_serialize_as_empty_objects(self):
        block = control_aggregates(
            {"secret-scanning": control_document([])})
        dumped = canonical_dumps(block)
        self.assertEqual(dumped.count("{}"), 4)
        self.assertNotIn('"enabled": 0', dumped)
        self.assertNotIn('"applicable": 0', dumped)


if __name__ == "__main__":
    unittest.main()
