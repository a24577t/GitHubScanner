"""Evidence classification: taxonomy states + deterministic reasons (ADR-0002/0006)."""
import calendar
import json
import time

from collector.transport import (
    MAX_PARK_SECONDS, PARK_SLACK_SECONDS, RETRY_AFTER_MAX_SECONDS,
    parse_nonnegative_int, rate_limited,
)

# Closed deterministic-reason set for this slice (spec: taxonomy application).
REASONS = frozenset({
    "collected", "absence-message-matched", "absence-rule-unmatched-404",
    "authorization-denied", "shape-invalid", "transport-failed",
    "pagination-cap", "missing-required-input", "structural-conflict",
    "rate_limit_reset_exceeds_maximum_park", "retry-after-exceeds-maximum",
    "unusable-rate-limit-reset",
})


def body_of(record):
    try:
        return json.loads(record["body_text"])
    except (json.JSONDecodeError, TypeError):
        return None


def shape_ok(body, shape):
    if body is None:
        return False
    if shape == "object":
        return isinstance(body, dict)
    if shape == "object_array":
        return isinstance(body, list) and all(isinstance(item, dict) for item in body)
    return True


def usable_page(record):
    """A shape-valid 2xx listing page — the only kind whose items feed
    discovery and projection (ADR-0005); capped pages remain usable."""
    return (record is not None
            and 200 <= record["envelope"]["status"] < 300
            and shape_ok(body_of(record), "object_array"))


def classify(record, shape=None, absence_message=None):
    """Classify a raw record per ADR-0002; absence anchored per ADR-0006."""
    if record is None:
        return "unknown", None
    status = record["envelope"]["status"]
    if record["envelope"].get("incomplete"):
        return "incomplete", "pagination-cap"
    if 200 <= status < 300:
        # A 2xx whose body is not the expected JSON shape is a failed
        # collection, never a collected one; no values are derived from it.
        if shape_ok(body_of(record), shape):
            return "collected", "collected"
        return "failed", "shape-invalid"
    if status in (401, 403):
        return "inaccessible", "authorization-denied"
    if status == 404:
        body = body_of(record)
        message = body.get("message") if isinstance(body, dict) else None
        if absence_message is not None and message == absence_message:
            return "absent", "absence-message-matched"
        if record["envelope"].get("endpoint_optional"):
            # Slice 1 optional-endpoint rule; outside the closed reason set —
            # no repo-resource descriptor is endpoint-optional this slice.
            return "unsupported", None
        return "inaccessible", "absence-rule-unmatched-404"
    return "failed", "transport-failed"


def _termination_reason(envelope):
    """E1-Q3 mapping, evidence conditions in ADR-0007 precedence order.

    Reasons describe retained evidence, never transport history: the park
    duration is recomputed from the reset header and the envelope's own
    captured_at — no clock, no persisted wait records.
    """
    headers = envelope["response_headers"]
    retry_after = parse_nonnegative_int(headers.get("retry-after"))
    if retry_after is not None and retry_after > RETRY_AFTER_MAX_SECONDS:
        return "retry-after-exceeds-maximum"
    if parse_nonnegative_int(headers.get("x-ratelimit-remaining")) == 0:
        reset = parse_nonnegative_int(headers.get("x-ratelimit-reset"))
        if reset is None:
            return "unusable-rate-limit-reset"
        captured_epoch = calendar.timegm(
            time.strptime(envelope["captured_at"], "%Y-%m-%dT%H:%M:%SZ"))
        if max(0, reset - captured_epoch) + PARK_SLACK_SECONDS > MAX_PARK_SECONDS:
            return "rate_limit_reset_exceeds_maximum_park"
    return "transport-failed"


def classify_resource(record, descriptor):
    """Classify a repo-resource record against its descriptor (ADR-0006).

    Absence anchors to the descriptor's pinned message; repo-resource records
    are never endpoint-optional this slice, so Slice 1 org-resource behavior
    is untouched. A final record carrying affirmative rate-limit markers is a
    bounded transport failure, never an authorization denial (E1-Q3).
    """
    envelope = record["envelope"]
    if (not envelope.get("incomplete")
            and not 200 <= envelope["status"] < 300
            and rate_limited(envelope["status"], envelope["response_headers"])):
        return "failed", _termination_reason(envelope)
    return classify(record, shape=descriptor["shape"],
                    absence_message=descriptor.get("absence_message"))
