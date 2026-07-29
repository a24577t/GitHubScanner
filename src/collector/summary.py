"""Execution/wait visibility aggregates from retained evidence only (V30).

Pure aggregation over the raw tree as found: wait categories and seconds
from retained wait_records, terminations from retained termination_reason,
planned requests from retained inventory via canonical discovery. Legacy
trees without the E1 retention fields read as empty — never repaired.
"""
from collector import resources, targets
from collector.projections import scan_envelope
from collector.transport import rate_limited

WAIT_CATEGORIES = ("primary-park", "retry-after", "retry")
SLEPT_OUTCOMES = frozenset({"retried", "renewed-exhaustion"})
SINGLE_ARTIFACTS = ("user.json", "meta.json", "org.json")


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
    rate-limit-marked final response. Anything else is a definitive answer."""
    status = envelope.get("status", 0)
    headers = envelope.get("response_headers", {})
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
    failed = sum(1 for envelope in envelopes if _transport_failed(envelope))
    waits = {category: {"count": 0, "requested_seconds": 0,
                        "slept_seconds": 0} for category in WAIT_CATEGORIES}
    refused, singles_max = 0, 0
    terminations = {}
    for envelope in envelopes:
        reason = envelope.get("termination_reason")
        if reason is not None:
            terminations[reason] = terminations.get(reason, 0) + 1
        for record in envelope.get("wait_records", []):
            if record.get("outcome") not in SLEPT_OUTCOMES:
                refused += 1
                continue
            bucket = waits.get(record.get("category"))
            if bucket is None:
                continue
            requested = record.get("requested_seconds") or 0
            bucket["count"] += 1
            bucket["requested_seconds"] += requested
            bucket["slept_seconds"] += record.get("elapsed_seconds") or 0
            singles_max = max(singles_max, requested)
    captured = sorted(envelope["captured_at"] for envelope in envelopes
                      if envelope.get("captured_at"))
    return {
        "requests": {
            "planned_singles": planned_singles,
            "planned_drains": planned_drains,
            "missing_input": missing_input,
            "retained_records": len(envelopes),
            "attempts": sum(e.get("attempts", 0) for e in envelopes),
            "completed": len(envelopes) - failed,
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
