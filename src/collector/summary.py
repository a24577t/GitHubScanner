"""Execution/wait visibility aggregates from retained evidence only (V30).

Read-only aggregation over the raw tree as found — no network, no wall
clock, no writes: wait categories and seconds from retained wait_records,
terminations from retained termination_reason, planned requests from
retained inventory via canonical discovery. Legacy trees without the E1
retention fields read as empty — never repaired.
"""
import math

from collector import resources, targets
from collector.projections import scan_envelope
from collector.transport import rate_limited

WAIT_CATEGORIES = ("primary-park", "retry-after", "retry")
SLEPT_OUTCOMES = frozenset({"retried", "renewed-exhaustion"})
REFUSED_OUTCOMES = frozenset({"retry-after-exceeds-maximum",
                              "rate_limit_reset_exceeds_maximum_park"})
SINGLE_ARTIFACTS = ("user.json", "meta.json", "org.json")


def _number(value):
    """A retained numeric figure, or 0 — scan tolerance is type-deep: junk
    values contribute nothing and never derail derivation. Integers are
    always finite (isfinite would overflow converting huge ones to float);
    only floats need the NaN/Infinity gate."""
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    return 0


def _tree_envelopes(raw_dir):
    """Envelopes of the run as found (scan tolerance, per T6 scan rules)."""
    artifacts = [raw_dir / name for name in SINGLE_ARTIFACTS]
    artifacts += sorted(raw_dir.glob("repos.page-*.json"))
    repos_root = raw_dir / "repos"
    if repos_root.is_dir():
        artifacts += sorted(repos_root.rglob("*.json"))
    return [envelope for artifact in artifacts
            if (envelope := scan_envelope(artifact)) is not None]


def _transport_failed(envelope):
    """The bounded-transport-failure class, from the final retained record:
    unreachable (status 0), attempts-exhausting 5xx, or an affirmatively
    rate-limit-marked final response. Anything else is a definitive answer.
    Malformed scan input (non-int status, non-dict headers) returns None —
    the record contributes to neither figure, per the scan-tolerance rule.

    Aggregate visibility only — taxonomy's E1-Q3 mapping remains the sole
    authority for derived states and reasons; both build on the shared
    rate_limited predicate."""
    status = envelope.get("status")
    headers = envelope.get("response_headers")
    if (isinstance(status, bool) or not isinstance(status, int)
            or not isinstance(headers, dict)):
        return None
    return status == 0 or status >= 500 or bool(rate_limited(status, headers))


def _planned(raw_dir, page_records):
    singles, drains, missing_input, absent = len(SINGLE_ARTIFACTS), 1, 0, 0
    for name in SINGLE_ARTIFACTS:
        absent += 0 if (raw_dir / name).exists() else 1
    if not page_records:
        absent += 1
    for target in targets.discover_targets(page_records):
        directory = raw_dir / "repos" / targets.directory_key(
            target["id"], target["name"])
        for descriptor in resources.DESCRIPTORS:
            _, missing = targets.descriptor_inputs(target, descriptor)
            if missing:
                missing_input += 1
            elif descriptor["shape"] == "object_array":
                drains += 1
                if not list(directory.glob(descriptor["name"] + ".page-*.json")):
                    absent += 1
            else:
                singles += 1
                if not (directory / (descriptor["name"] + ".json")).exists():
                    absent += 1
    return singles, drains, missing_input, absent


def execution_summary(raw_dir, page_records):
    """The report-visibility block: planned never conflated with attempts."""
    envelopes = _tree_envelopes(raw_dir)
    planned_singles, planned_drains, missing_input, absent = _planned(
        raw_dir, page_records)
    verdicts = [_transport_failed(envelope) for envelope in envelopes]
    failed = sum(1 for verdict in verdicts if verdict is True)
    completed = sum(1 for verdict in verdicts if verdict is False)
    waits = {category: {"count": 0, "requested_seconds": 0,
                        "slept_seconds": 0} for category in WAIT_CATEGORIES}
    refused, singles_max = 0, 0
    terminations = {}
    for envelope in envelopes:
        reason = envelope.get("termination_reason")
        # Only strings are valid retained reasons; anything else is malformed
        # scan input, discarded before aggregation — never repaired.
        if isinstance(reason, str):
            terminations[reason] = terminations.get(reason, 0) + 1
        records = envelope.get("wait_records")
        for record in (records if isinstance(records, list) else []):
            # Closed ratified vocabularies gate every figure; anything else
            # is junk the scanner could not have written and is skipped per
            # the T6 scan-tolerance rule — never counted, never a crash.
            if not isinstance(record, dict):
                continue
            if record.get("outcome") in REFUSED_OUTCOMES:
                refused += 1
                continue
            bucket = waits.get(record.get("category"))
            if record.get("outcome") not in SLEPT_OUTCOMES or bucket is None:
                continue
            requested = _number(record.get("requested_seconds"))
            bucket["count"] += 1
            bucket["requested_seconds"] += requested
            bucket["slept_seconds"] += _number(record.get("elapsed_seconds"))
            singles_max = max(singles_max, requested)
    captured = sorted(envelope.get("captured_at") for envelope in envelopes
                      if isinstance(envelope.get("captured_at"), str))
    return {
        "requests": {
            "planned_singles": planned_singles,
            "planned_drains": planned_drains,
            "missing_input": missing_input,
            "retained_records": len(envelopes),
            "attempts": sum(_number(e.get("attempts")) for e in envelopes),
            "completed": completed,
            "failed": failed,
            "evidence_absent": absent,
        },
        "waits": {
            **waits,
            "refused": refused,
            "max_single_wait_seconds": singles_max,
            "total_wait_seconds": sum(
                waits[c]["requested_seconds"] for c in WAIT_CATEGORIES),
        },
        "terminations": terminations,
        "captured": {"first": captured[0] if captured else None,
                     "last": captured[-1] if captured else None},
    }
