"""Evidence classification: taxonomy states + deterministic reasons (ADR-0002/0006)."""
import json

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
