"""Bounded execution waits at the transport seam (ADR-0007; rows V21-V29)."""
import unittest

from collector import transport
from fake_github import response, serve

WALL = 1_000_000.0
TOKEN = "test-token"

WAIT_RECORD_FIELDS = {
    "category", "attempt", "status", "rate_limit_headers",
    "requested_seconds", "elapsed_seconds", "maximum_seconds", "outcome",
    "reason",
}


class FakeClock:
    """Deterministic clock: sleeping advances wall and monotonic time."""

    def __init__(self, wall=WALL):
        self.wall = wall
        self.mono = 500.0
        self.sleeps = []

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.wall += seconds
        self.mono += seconds

    def epoch(self):
        return self.wall

    def monotonic(self):
        return self.mono


def exhausted(reset, extra=None):
    headers = {"X-RateLimit-Remaining": "0"}
    if reset is not None:
        headers["X-RateLimit-Reset"] = str(reset)
    headers.update(extra or {})
    return response(403, {"message": "API rate limit exceeded"}, headers)


def fetch(script, path, clock):
    with serve(script) as (base, _):
        return transport.get(base, path, TOKEN, clock=clock)


class PrimaryPark(unittest.TestCase):
    def test_v21_park_then_success_records_one_park(self):
        clock = FakeClock()
        script = {"/park": [exhausted(int(WALL) + 100), response(200, {"ok": 1})]}
        result = fetch(script, "/park", clock)
        self.assertEqual(result.status, 200)
        self.assertEqual(clock.sleeps, [105])
        self.assertEqual(result.waits, [105])
        self.assertIsNone(result.termination_reason)
        self.assertEqual(len(result.wait_records), 1)
        park = result.wait_records[0]
        self.assertEqual(park["category"], "primary-park")
        self.assertEqual(park["attempt"], 1)
        self.assertEqual(park["status"], 403)
        self.assertEqual(park["requested_seconds"], 105)
        self.assertEqual(park["elapsed_seconds"], 105)
        self.assertEqual(park["maximum_seconds"], 3900)
        self.assertEqual(park["outcome"], "retried")
        self.assertEqual(
            park["rate_limit_headers"]["x-ratelimit-remaining"], "0"
        )
        self.assertEqual(
            park["rate_limit_headers"]["x-ratelimit-reset"],
            str(int(WALL) + 100),
        )

    def test_v21_every_wait_record_carries_the_full_evidence_schema(self):
        clock = FakeClock()
        script = {"/park": [exhausted(int(WALL) + 30), response(200, {"ok": 1})]}
        result = fetch(script, "/park", clock)
        for record in result.wait_records:
            self.assertEqual(set(record), WAIT_RECORD_FIELDS)

    def test_v21_past_reset_parks_slack_only_never_negative(self):
        clock = FakeClock()
        script = {"/park": [exhausted(int(WALL) - 50), response(200, {"ok": 1})]}
        result = fetch(script, "/park", clock)
        self.assertEqual(result.status, 200)
        self.assertEqual(clock.sleeps, [5])


class ParkBounds(unittest.TestCase):
    def test_v22_renewed_exhaustion_after_park_terminates_without_second_park(self):
        clock = FakeClock()
        script = {"/park": [exhausted(int(WALL) + 100),
                            exhausted(int(WALL) + 300)]}
        with serve(script) as (base, recorder):
            result = transport.get(base, "/park", TOKEN, clock=clock)
        self.assertEqual(result.status, 403)
        self.assertEqual(len(clock.sleeps), 1)
        self.assertEqual(len(recorder.requests), 2)
        self.assertEqual(result.termination_reason,
                         "rate_limit_renewed_exhaustion")
        self.assertEqual(len(result.wait_records), 1)
        self.assertEqual(result.wait_records[0]["category"], "primary-park")
        self.assertEqual(result.wait_records[0]["outcome"],
                         "renewed-exhaustion")

    def test_v23_reset_beyond_maximum_park_is_refused_not_clamped(self):
        clock = FakeClock()
        script = {"/park": [exhausted(int(WALL) + 4000),
                            response(200, {"ok": 1})]}
        with serve(script) as (base, recorder):
            result = transport.get(base, "/park", TOKEN, clock=clock)
        self.assertEqual(result.status, 403)
        self.assertEqual(clock.sleeps, [])
        self.assertEqual(result.waits, [])
        self.assertEqual(len(recorder.requests), 1)
        self.assertEqual(result.termination_reason,
                         "rate_limit_reset_exceeds_maximum_park")
        self.assertEqual(len(result.wait_records), 1)
        refused = result.wait_records[0]
        self.assertEqual(refused["category"], "primary-park")
        self.assertEqual(refused["requested_seconds"], 4005)
        self.assertEqual(refused["elapsed_seconds"], 0)
        self.assertEqual(refused["maximum_seconds"], 3900)
        self.assertEqual(refused["outcome"],
                         "rate_limit_reset_exceeds_maximum_park")


class RetryAfterPrecedence(unittest.TestCase):
    def test_v26_retry_after_wins_over_primary_exhaustion(self):
        clock = FakeClock()
        script = {"/r": [exhausted(int(WALL) + 1000, {"Retry-After": "7"}),
                         response(200, {"ok": 1})]}
        result = fetch(script, "/r", clock)
        self.assertEqual(result.status, 200)
        self.assertEqual(clock.sleeps, [7])
        self.assertIsNone(result.termination_reason)
        self.assertEqual(
            [r["category"] for r in result.wait_records], ["retry-after"]
        )
        record = result.wait_records[0]
        self.assertEqual(record["requested_seconds"], 7)
        self.assertEqual(record["maximum_seconds"], 60)
        self.assertEqual(record["outcome"], "retried")

    def test_v27_retry_after_beyond_maximum_is_refused_not_clamped(self):
        clock = FakeClock()
        script = {"/r": [response(429, {"message": "slow down"},
                                  {"Retry-After": "61"}),
                         response(200, {"ok": 1})]}
        with serve(script) as (base, recorder):
            result = transport.get(base, "/r", TOKEN, clock=clock)
        self.assertEqual(result.status, 429)
        self.assertEqual(clock.sleeps, [])
        self.assertEqual(len(recorder.requests), 1)
        self.assertEqual(result.termination_reason,
                         "retry-after-exceeds-maximum")
        refused = result.wait_records[0]
        self.assertEqual(refused["category"], "retry-after")
        self.assertEqual(refused["requested_seconds"], 61)
        self.assertEqual(refused["elapsed_seconds"], 0)
        self.assertEqual(refused["maximum_seconds"], 60)
        self.assertEqual(refused["outcome"], "retry-after-exceeds-maximum")


class UnusableReset(unittest.TestCase):
    def test_v24_missing_reset_falls_back_with_reason_preserved(self):
        clock = FakeClock()
        script = {"/r": [exhausted(None), response(200, {"ok": 1})]}
        result = fetch(script, "/r", clock)
        self.assertEqual(result.status, 200)
        self.assertEqual(clock.sleeps, [1])
        record = result.wait_records[0]
        self.assertEqual(record["category"], "retry")
        self.assertEqual(record["reason"], "unusable-rate-limit-reset")
        self.assertEqual(record["outcome"], "retried")

    def test_v25_unparseable_reset_falls_back_with_reason_preserved(self):
        clock = FakeClock()
        script = {"/r": [exhausted(None, {"X-RateLimit-Reset": "soon"}),
                         response(200, {"ok": 1})]}
        result = fetch(script, "/r", clock)
        self.assertEqual(clock.sleeps, [1])
        self.assertEqual(result.wait_records[0]["reason"],
                         "unusable-rate-limit-reset")

    def test_v24_valid_retry_after_with_unusable_reset_takes_retry_after(self):
        clock = FakeClock()
        script = {"/r": [exhausted(None, {"Retry-After": "3"}),
                         response(200, {"ok": 1})]}
        result = fetch(script, "/r", clock)
        self.assertEqual(clock.sleeps, [3])
        record = result.wait_records[0]
        self.assertEqual(record["category"], "retry-after")
        self.assertEqual(record["reason"], "unusable-rate-limit-reset")


class NonRateLimitPaths(unittest.TestCase):
    def test_v28_markerless_403_reaches_taxonomy_with_no_wait(self):
        clock = FakeClock()
        script = {"/r": [response(403, {"message": "Must have admin rights"})]}
        with serve(script) as (base, recorder):
            result = transport.get(base, "/r", TOKEN, clock=clock)
        self.assertEqual(result.status, 403)
        self.assertEqual(len(recorder.requests), 1)
        self.assertEqual(clock.sleeps, [])
        self.assertEqual(result.waits, [])
        self.assertEqual(result.wait_records, [])
        self.assertIsNone(result.termination_reason)
        self.assertEqual(result.attempts, 1)

    def test_v29_attempts_exhaust_on_5xx_at_max_attempts(self):
        clock = FakeClock()
        script = {"/r": [response(500, {"message": "boom"})]}
        with serve(script) as (base, recorder):
            result = transport.get(base, "/r", TOKEN, clock=clock)
        self.assertEqual(result.status, 500)
        self.assertEqual(result.attempts, transport.MAX_ATTEMPTS)
        self.assertEqual(len(recorder.requests), 3)
        self.assertEqual(clock.sleeps, [1, 1])
        self.assertEqual(result.waits, [1, 1])
        self.assertIsNone(result.termination_reason)
        self.assertEqual(
            [(r["category"], r["outcome"]) for r in result.wait_records],
            [("retry", "retried"), ("retry", "retried")],
        )


if __name__ == "__main__":
    unittest.main()
