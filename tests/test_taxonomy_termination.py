"""Transport-termination mapping at the derive seam (E1-Q3, ratified 2026-07-29).

Deterministic from retained evidence only: envelope status, allowlisted
rate-limit headers, and captured_at — no clock, no persisted wait records.
"""
import calendar
import time
import unittest

from collector.resources import DEFAULT_BRANCH_PROTECTION
from collector.taxonomy import classify_resource
from test_derive_resources import record

CAPTURED = "2026-01-01T00:00:00Z"
CAPTURED_EPOCH = calendar.timegm(time.strptime(CAPTURED, "%Y-%m-%dT%H:%M:%SZ"))


def classified(status, headers):
    rate_limited = record(status, {"message": "limited"}, headers=headers,
                          captured=CAPTURED)
    return classify_resource(rate_limited, DEFAULT_BRANCH_PROTECTION)


class RetryAfterMapping(unittest.TestCase):
    def test_retry_after_beyond_maximum_maps_to_its_reason(self):
        self.assertEqual(classified(403, {"retry-after": "61"}),
                         ("failed", "retry-after-exceeds-maximum"))

    def test_retry_after_within_maximum_is_bounded_transport_failure(self):
        self.assertEqual(classified(403, {"retry-after": "60"}),
                         ("failed", "transport-failed"))


class PrimaryParkMapping(unittest.TestCase):
    def test_reset_beyond_maximum_park_maps_to_its_reason(self):
        headers = {"x-ratelimit-remaining": "0",
                   "x-ratelimit-reset": str(CAPTURED_EPOCH + 3896)}
        self.assertEqual(classified(403, headers),
                         ("failed", "rate_limit_reset_exceeds_maximum_park"))

    def test_reset_within_maximum_park_is_bounded_transport_failure(self):
        headers = {"x-ratelimit-remaining": "0",
                   "x-ratelimit-reset": str(CAPTURED_EPOCH + 3895)}
        self.assertEqual(classified(403, headers),
                         ("failed", "transport-failed"))

    def test_reset_in_the_past_is_within_bounds(self):
        headers = {"x-ratelimit-remaining": "0",
                   "x-ratelimit-reset": str(CAPTURED_EPOCH - 100)}
        self.assertEqual(classified(403, headers),
                         ("failed", "transport-failed"))

    def test_missing_reset_is_unusable(self):
        self.assertEqual(classified(403, {"x-ratelimit-remaining": "0"}),
                         ("failed", "unusable-rate-limit-reset"))

    def test_unparseable_reset_is_unusable(self):
        headers = {"x-ratelimit-remaining": "0", "x-ratelimit-reset": "soon"}
        self.assertEqual(classified(403, headers),
                         ("failed", "unusable-rate-limit-reset"))


class MarkerPrecedence(unittest.TestCase):
    def test_excessive_retry_after_precedes_reset_evidence(self):
        headers = {"retry-after": "61", "x-ratelimit-remaining": "0",
                   "x-ratelimit-reset": str(CAPTURED_EPOCH + 10)}
        self.assertEqual(classified(403, headers),
                         ("failed", "retry-after-exceeds-maximum"))

    def test_bounded_retry_after_still_exposes_reset_evidence(self):
        # Ratified branch order: reasons describe evidence conditions, not
        # transport history — the far reset is affirmatively present.
        headers = {"retry-after": "30", "x-ratelimit-remaining": "0",
                   "x-ratelimit-reset": str(CAPTURED_EPOCH + 999999)}
        self.assertEqual(classified(403, headers),
                         ("failed", "rate_limit_reset_exceeds_maximum_park"))

    def test_429_is_a_marker_without_remaining_zero(self):
        self.assertEqual(classified(429, {}), ("failed", "transport-failed"))


class UnmarkedRecordsUnchanged(unittest.TestCase):
    def test_markerless_403_remains_authorization_denied(self):
        self.assertEqual(classified(403, {}),
                         ("inaccessible", "authorization-denied"))

    def test_markerless_401_remains_authorization_denied(self):
        self.assertEqual(classified(401, {}),
                         ("inaccessible", "authorization-denied"))

    def test_5xx_remains_transport_failed(self):
        self.assertEqual(classified(500, {}), ("failed", "transport-failed"))


if __name__ == "__main__":
    unittest.main()
