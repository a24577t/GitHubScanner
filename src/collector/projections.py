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


def structural_report(raw_dir):
    """Invoke ADR-0005 structural validation over the evidence tree as found.

    Claims pair each directory name with the repository IDs its enclosed
    envelopes assert; paths are never evidence, so the report only gates
    which evidence may surface — it asserts no GitHub fact.
    """
    repos_root = raw_dir / "repos"
    claims = []
    if repos_root.is_dir():
        for directory in sorted(p for p in repos_root.iterdir() if p.is_dir()):
            envelope_ids = []
            for artifact in sorted(directory.glob("*.json")):
                envelope = json.loads(
                    artifact.read_text(encoding="utf-8")).get("envelope", {})
                repo = envelope.get("repo")
                if isinstance(repo, dict) and "id" in repo:
                    envelope_ids.append(repo["id"])
            claims.append((directory.name, tuple(envelope_ids)))
    return targets.structural_conflicts(claims)


def resource_document(run_id, raw_dir, descriptor, page_records,
                      inventory_state):
    """The latest-only observed document for one descriptor.

    Coverage qualifies the target set and never converts descriptor states;
    entries ascend by repository id (canonical discovery order, ADR-0005).
    Entry precedence: the no-request rule (missing input) is evaluated before
    tree inspection; a structural conflict then suppresses artifact reads so
    no affected evidence surfaces as an apparently valid observation.
    """
    conflicted = {targets.claimed_repository_id(name)
                  for name in structural_report(raw_dir)["conflicted_directories"]}
    entries = []
    for target in targets.discover_targets(page_records):
        inputs, missing = targets.descriptor_inputs(target, descriptor)
        if missing:
            entries.append(_entry(target, descriptor, "unknown",
                                  "missing-required-input", None, None))
            continue
        if target["id"] in conflicted:
            entries.append(_entry(target, descriptor, "unknown",
                                  "structural-conflict", None, inputs))
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
