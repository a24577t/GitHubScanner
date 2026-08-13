"""Per-control distribution aggregates at the summary seam (Slice 3 T4; V59).

The pure counting function over control-observation documents: the four
count families the specification's Reporting section enumerates -
applicability counts, applicability-reason counts, operational-state
counts, operational-state-reason counts - closed vocabularies only,
observed keys only, never zero-filled. Evidence-plane state and citations
never enter the aggregates (rollup of either plane is rejected by
ADR-0009); state figures gate on the closed plane vocabularies, reason
vocabularies are the emitting control layer's guarantee, and on
scanner-written documents size never tracks the estate.
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


EMPTY = {family: {} for family in FAMILIES}


class TypeDeepTolerance(unittest.TestCase):
    # The T7 lesson at this seam: malformed control-document inputs never
    # crash aggregation, junk contributes nothing, and valid conclusions
    # aggregate identically with junk present or absent.

    def test_malformed_documents_never_crash_and_count_nothing(self):
        for junk in (None, [], "junk", 5, True, {}, {"repositories": None},
                     {"repositories": {}}, {"repositories": "x"},
                     {"repositories": 7}):
            with self.subTest(document=junk):
                self.assertEqual(control_aggregates({"secret-scanning": junk}),
                                 {"secret-scanning": EMPTY})

    def test_non_dict_entries_are_skipped(self):
        document = control_document(
            [None, 7, "entry", [], True, entry(1)])
        block = control_aggregates({"secret-scanning": document})
        self.assertEqual(block["secret-scanning"]["operational_state_counts"],
                         {"disabled": 1})

    def test_entries_missing_conclusion_fields_contribute_nothing(self):
        document = control_document(
            [{"id": 1, "full_name": "acme/repo-1"}, entry(2)])
        block = control_aggregates({"secret-scanning": document})
        self.assertEqual(block["secret-scanning"]["applicability_counts"],
                         {"applicable": 1})

    def test_invalid_state_types_suppress_the_pair(self):
        # Unhashable and non-string states can never enter a closed
        # vocabulary: the whole (state, reason) pair is discarded.
        junk_states = ({}, ["applicable"], None, True, 5)
        document = control_document(
            [entry(i, applicability=junk, operational_state=junk)
             for i, junk in enumerate(junk_states, start=1)] + [entry(9)])
        block = control_aggregates({"secret-scanning": document})
        self.assertEqual(block["secret-scanning"],
                         {"applicability_counts": {"applicable": 1},
                          "applicability_reason_counts":
                              {"public-repository-visibility": 1},
                          "operational_state_counts": {"disabled": 1},
                          "operational_state_reason_counts":
                              {"affirmative-status-disabled": 1}})

    def test_invalid_reason_types_count_the_state_only(self):
        # A valid state whose paired reason is junk still counts as a state
        # figure; the junk reason never becomes a count key.
        junk_reasons = ({}, [], None, True, 5)
        document = control_document(
            [entry(i, applicability_reason=junk, operational_state_reason=junk)
             for i, junk in enumerate(junk_reasons, start=1)])
        block = control_aggregates({"secret-scanning": document})
        self.assertEqual(block["secret-scanning"],
                         {"applicability_counts": {"applicable": 5},
                          "applicability_reason_counts": {},
                          "operational_state_counts": {"disabled": 5},
                          "operational_state_reason_counts": {}})

    def test_non_string_control_names_are_skipped(self):
        aggregates = control_aggregates(
            {5: control_document([entry(1)]),
             "secret-scanning": control_document([entry(2)])})
        self.assertEqual(sorted(aggregates), ["secret-scanning"])

    def test_junk_never_contaminates_valid_aggregates(self):
        valid = [entry(1), entry(2, operational_state="enabled",
                                 operational_state_reason=
                                 "affirmative-status-enabled")]
        junk = [None, "x", {"applicability": {}, "operational_state": []},
                entry(3, applicability="not-applicable",
                      operational_state="unavailable"),
                entry(4, applicability_reason=7, operational_state_reason={})]
        clean = control_aggregates(
            {"secret-scanning": control_document(list(valid))})
        polluted = control_aggregates(
            {"secret-scanning": control_document(valid + junk)})
        # Entry 4's valid states still count; every junk figure vanishes.
        expected = {family: dict(counts) for family, counts in
                    clean["secret-scanning"].items()}
        expected["applicability_counts"]["applicable"] += 1
        expected["operational_state_counts"]["disabled"] += 1
        self.assertEqual(polluted["secret-scanning"], expected)
        self.assertEqual(canonical_dumps(clean),
                         canonical_dumps(control_aggregates(
                             {"secret-scanning": control_document(valid)})))


if __name__ == "__main__":
    unittest.main()
