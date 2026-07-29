"""Per-resource observed documents: entries, coverage, rollup (ADR-0004/0005/0006)."""
import json

from collector import targets
from collector.resources import project
from collector.taxonomy import body_of, classify_resource

COVERAGE_BASIS = "eligible-discovered-repositories"


def listing_state(states):
    """Slice 1 listing rule: first non-collected state; unknown when empty."""
    if not states:
        return "unknown"
    return next((state for state in states if state != "collected"), "collected")


def _entry(target, descriptor, state, reason, body, inputs):
    projected = project(descriptor, body, inputs)
    return {"id": target["id"], "full_name": target["full_name"],
            "state": state, "reason": reason, **projected}


def _classify_target(raw_dir, target, descriptor):
    """(state, reason, body) for one target's expected artifact.

    An absent artifact is the durable trace of a recorded collection failure
    (E1) — or a pre-fan-out tree — and derives unknown; nothing is fabricated.
    """
    directory = raw_dir / "repos" / targets.directory_key(
        target["id"], target["name"])
    path = directory / (descriptor["name"] + ".json")
    if not path.exists():
        return "unknown", "raw-evidence-absent", None
    record = json.loads(path.read_text(encoding="utf-8"))
    state, reason = classify_resource(record, descriptor)
    return state, reason, body_of(record) if state == "collected" else None


def resource_document(run_id, raw_dir, descriptor, page_records,
                      inventory_state):
    """The latest-only observed document for one descriptor.

    Coverage qualifies the target set and never converts descriptor states;
    entries ascend by repository id (canonical discovery order, ADR-0005).
    """
    entries = []
    for target in targets.discover_targets(page_records):
        inputs, missing = targets.descriptor_inputs(target, descriptor)
        if missing:
            entries.append(_entry(target, descriptor, "unknown",
                                  "missing-required-input", None, None))
            continue
        state, reason, body = _classify_target(raw_dir, target, descriptor)
        entries.append(_entry(target, descriptor, state, reason, body, inputs))
    return {
        "run_id": run_id,
        "state": listing_state([entry["state"] for entry in entries]),
        "coverage": {"basis": COVERAGE_BASIS,
                     "inventory_state": inventory_state,
                     "eligible_target_count": len(entries)},
        "repositories": entries,
    }
