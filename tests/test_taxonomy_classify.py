"""Classification contract: taxonomy states + deterministic reasons (rows V13-V20)."""
import json
import unittest

from collector import resources
from collector.taxonomy import REASONS, classify

PROTECTION_ABSENCE = resources.DEFAULT_BRANCH_PROTECTION["absence_message"]


def record(status, body=None, body_text=None, **envelope):
    text = body_text if body_text is not None else json.dumps(body)
    return {"envelope": {"status": status, **envelope}, "body_text": text}


class ClassifyContract(unittest.TestCase):
    def test_collected_object(self):
        self.assertEqual(
            classify(record(200, {"id": 1}), shape="object"),
            ("collected", "collected"),
        )

    def test_collected_object_array(self):
        self.assertEqual(
            classify(record(200, [{"id": 1}]), shape="object_array"),
            ("collected", "collected"),
        )

    def test_descriptor_anchored_absence_match(self):
        result = classify(
            record(404, {"message": "Branch not protected"}),
            shape="object",
            absence_message=PROTECTION_ABSENCE,
        )
        self.assertEqual(result, ("absent", "absence-message-matched"))

    def test_missing_record_is_unknown_without_reason(self):
        self.assertEqual(classify(None), ("unknown", None))


class Unmatched404(unittest.TestCase):
    """Rows V13-V18: every 404 that misses the anchor is inaccessible."""

    VARIANTS = {
        "V13 case variation": record(404, {"message": "branch not protected"}),
        "V14 text variation": record(404, {"message": "Branch is not protected"}),
        "V15 missing message field": record(404, {"documentation_url": "d"}),
        "V16 non-string message": record(404, {"message": 404}),
        "V17 malformed JSON": record(404, body_text="{not-json"),
        "V18 shape-valid unrecognized": record(404, {"message": "Not Found"}),
    }

    def test_unmatched_404_variants_share_one_deterministic_reason(self):
        for row, rec in self.VARIANTS.items():
            with self.subTest(row=row):
                self.assertEqual(
                    classify(rec, shape="object",
                             absence_message=PROTECTION_ABSENCE),
                    ("inaccessible", "absence-rule-unmatched-404"),
                )

    def test_exact_message_without_anchor_never_matches(self):
        rec = record(404, {"message": "Branch not protected"})
        self.assertEqual(
            classify(rec, shape="object"),
            ("inaccessible", "absence-rule-unmatched-404"),
        )

    def test_optional_endpoint_unmatched_404_is_unsupported(self):
        rec = record(404, {"message": "Not Found"}, endpoint_optional=True)
        self.assertEqual(classify(rec, shape="object"), ("unsupported", None))

    def test_anchored_absence_wins_over_optional_endpoint(self):
        rec = record(404, {"message": "Branch not protected"},
                     endpoint_optional=True)
        self.assertEqual(
            classify(rec, shape="object", absence_message=PROTECTION_ABSENCE),
            ("absent", "absence-message-matched"),
        )


class DenialsAndFailures(unittest.TestCase):
    """Rows V19-V20 plus the remaining deterministic reasons."""

    def test_explicit_denial_statuses_are_authorization_denied(self):
        for status in (401, 403):
            with self.subTest(status=status):
                self.assertEqual(
                    classify(record(status, {"message": "Must authenticate"}),
                             shape="object"),
                    ("inaccessible", "authorization-denied"),
                )

    def test_denial_wins_even_when_body_carries_the_absence_message(self):
        rec = record(403, {"message": "Branch not protected"})
        self.assertEqual(
            classify(rec, shape="object", absence_message=PROTECTION_ABSENCE),
            ("inaccessible", "authorization-denied"),
        )

    def test_malformed_2xx_bodies_are_failed_shape_invalid(self):
        cases = {
            "not JSON": record(200, body_text="{not-json"),
            "object where array expected": record(200, {"m": "x"}),
            "non-object array entries": record(200, [{"id": 1}, 2, "s"]),
        }
        shapes = {"not JSON": "object",
                  "object where array expected": "object_array",
                  "non-object array entries": "object_array"}
        for label, rec in cases.items():
            with self.subTest(case=label):
                self.assertEqual(
                    classify(rec, shape=shapes[label]),
                    ("failed", "shape-invalid"),
                )

    def test_incomplete_listing_is_pagination_cap_before_any_status(self):
        rec = record(200, [{"id": 1}], incomplete=True)
        self.assertEqual(classify(rec, shape="object_array"),
                         ("incomplete", "pagination-cap"))

    def test_persistent_server_errors_are_transport_failed(self):
        for status in (500, 502, 503):
            with self.subTest(status=status):
                self.assertEqual(
                    classify(record(status, {"message": "boom"}),
                             shape="object"),
                    ("failed", "transport-failed"),
                )

    def test_reason_vocabulary_is_the_exact_closed_set(self):
        # raw-evidence-absent joined by ratified refinement (E1, 2026-07-29).
        self.assertEqual(
            REASONS,
            frozenset({
                "collected", "absence-message-matched",
                "absence-rule-unmatched-404", "authorization-denied",
                "shape-invalid", "transport-failed", "pagination-cap",
                "missing-required-input", "structural-conflict",
                "raw-evidence-absent",
                "rate_limit_reset_exceeds_maximum_park",
                "retry-after-exceeds-maximum", "unusable-rate-limit-reset",
            }),
        )

    def test_every_emitted_reason_is_in_the_closed_set(self):
        emitted = {
            classify(record(200, {"id": 1}), shape="object")[1],
            classify(record(200, body_text="]["), shape="object")[1],
            classify(record(404, {"message": "Branch not protected"},),
                     absence_message=PROTECTION_ABSENCE)[1],
            classify(record(404, {"message": "Not Found"}))[1],
            classify(record(403, {"message": "denied"}))[1],
            classify(record(500, {"message": "boom"}))[1],
            classify(record(200, [{"id": 1}], incomplete=True),
                     shape="object_array")[1],
        }
        self.assertTrue(emitted <= REASONS, emitted - REASONS)


if __name__ == "__main__":
    unittest.main()
