"""Derive observed state solely from raw evidence (ADR-0001 derivability rule)."""
import json
from pathlib import Path

from collector import controls, projections, resources, summary
from collector.serialize import write_canonical
from collector.taxonomy import body_of, classify, usable_page

ORG_FIELDS = ("login", "id", "created_at")
REPO_FIELDS = (
    "id", "name", "full_name", "visibility", "fork", "archived",
    "created_at", "default_branch",
)


def latest_run_id(out_dir):
    """The actual latest collected run: by envelope captured_at, then run-id."""
    raw_root = Path(out_dir) / "evidence" / "raw"
    runs = [p for p in raw_root.iterdir() if p.is_dir()]
    if not runs:
        raise ValueError("no raw evidence runs found under " + str(raw_root))

    def collected_at(run_dir):
        record = _load(run_dir, "user.json")
        captured = record["envelope"]["captured_at"] if record else ""
        return (captured, run_dir.name)

    return max(runs, key=collected_at).name


def _load(raw_dir, name):
    path = raw_dir / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _pick(mapping, fields):
    """Project entity fields; undetermined values are 'unknown', never null."""
    if not isinstance(mapping, dict):
        mapping = {}
    return {
        field: mapping[field] if mapping.get(field) is not None else "unknown"
        for field in fields
    }


# Slice 1 absence anchor, preserved for org-scoped resources; repository
# resources anchor to their descriptor's absence_message when wired (T6).
ABSENCE_MESSAGE = "Branch not protected"

RESOURCES = (("user", "user.json", "object"),
             ("meta", "meta.json", "object"),
             ("org", "org.json", "object"))


def run_summary(out_dir, run_id):
    """Aggregate a run's states, failures, listing facts, and waits — from raw only."""
    raw_dir = Path(out_dir) / "evidence" / "raw" / run_id
    resource_states, failures, waits = {}, [], []

    def note(name, record, state):
        resource_states[name] = state
        envelope = record["envelope"]
        waits.extend(envelope.get("waits_seconds", []))
        if state == "failed":
            failures.append({"resource": name, "status": envelope["status"],
                             "url": envelope["url"]})

    for name, filename, expect in RESOURCES:
        record = _load(raw_dir, filename)
        if record is None:
            resource_states[name] = "unknown"
            continue
        note(name, record,
             classify(record, shape=expect, absence_message=ABSENCE_MESSAGE)[0])

    pages = sorted(raw_dir.glob("repos.page-*.json"),
                   key=lambda p: int(p.stem.split("-")[-1]))
    page_records = [json.loads(p.read_text(encoding="utf-8")) for p in pages]
    page_states, items = [], 0
    for number, record in enumerate(page_records, start=1):
        state, _ = classify(record, shape="object_array",
                            absence_message=ABSENCE_MESSAGE)
        note(f"repositories.page-{number}", record, state)
        del resource_states[f"repositories.page-{number}"]
        page_states.append(state)
        items += record["envelope"].get("item_count", 0)
    resource_states["repositories"] = projections.listing_state(page_states)
    complete = bool(page_states) and all(s == "collected" for s in page_states)
    structural = projections.structural_report(raw_dir)
    return {
        "resource_states": resource_states,
        "failures": failures,
        "listings": {"repositories": {"pages": len(pages), "items": items,
                                      "complete": complete}},
        "waits": waits,
        # Additive keys for T7's report growth; Slice 1 report assembly reads
        # only the four keys above, so its output is untouched this ticket.
        "resources": _fanout_summary(run_id, raw_dir, page_records,
                                     resource_states["repositories"],
                                     projections.conflicted_ids(structural)),
        "structural": {key: list(value) for key, value in structural.items()},
        "execution": summary.execution_summary(raw_dir, page_records),
    }


def _fanout_summary(run_id, raw_dir, page_records, inventory_state,
                    conflicted):
    """Estate-independent per-descriptor aggregates (failures excepted by
    design live in reason_counts until T7 decides its rendering)."""
    waits_by_resource = {}
    repos_root = raw_dir / "repos"
    if repos_root.is_dir():
        for artifact in sorted(repos_root.rglob("*.json")):
            envelope = projections.scan_envelope(artifact) or {}
            name = envelope.get("resource")
            if name is not None:
                waits_by_resource.setdefault(name, []).extend(
                    envelope.get("waits_seconds", []))
    aggregates = {}
    for descriptor in resources.DESCRIPTORS:
        document = projections.resource_document(
            run_id, raw_dir, descriptor, page_records, inventory_state,
            conflicted)
        state_counts, reason_counts = {}, {}
        for entry in document["repositories"]:
            state_counts[entry["state"]] = (
                state_counts.get(entry["state"], 0) + 1)
            reason_counts[entry["reason"]] = (
                reason_counts.get(entry["reason"], 0) + 1)
        aggregates[descriptor["name"]] = {
            "state": document["state"],
            "state_counts": state_counts,
            "reason_counts": reason_counts,
            "waits_seconds": waits_by_resource.get(descriptor["name"], []),
        }
    return aggregates


def _control_documents(table, documents):
    """(name, document) per control — assembly from derived resource-document
    entries only (ADR-0009 element 3): every conclusion cites its retained
    descriptor evidence; the top-level state is the Slice 1 listing rule over
    the cited evidence states (evidence-plane rollup only); coverage is the
    descriptor document's block verbatim. Controls evaluate in table order,
    each target's applicability conclusions accumulating in ``resolved`` so a
    chained control receives its predecessor's conclusion — T2's validation
    guarantees the predecessor precedes it, so one pass is deterministic and
    a future chained definition needs no change here (T5's architectural AC).
    """
    resolved = {}
    for control in table:
        source = documents.get(control["descriptor"])
        if source is None:
            # Unreachable when the control and descriptor tables agree
            # (import-time validation pins every shipped control's descriptor
            # to the shipped table; derivation covers the whole table): a
            # divergent pairing is an invariant violation, surfaced loudly.
            raise ValueError(
                f"control {control['name']!r} references descriptor "
                f"{control['descriptor']!r} absent from the derived table")
        entries = []
        for entry in source["repositories"]:
            conclusions = resolved.setdefault(entry["id"], {})
            applicability, applicability_reason = controls.applicability(
                control, entry, conclusions)
            operational, operational_reason = controls.operational_state(
                control, entry)
            conclusions[control["name"]] = applicability
            entries.append({
                "id": entry["id"], "full_name": entry["full_name"],
                "applicability": applicability,
                "applicability_reason": applicability_reason,
                "operational_state": operational,
                "operational_state_reason": operational_reason,
                "evidence": {"resource": control["descriptor"],
                             "state": entry["state"],
                             "reason": entry["reason"]},
            })
        yield control["name"], {
            "run_id": source["run_id"],
            "state": projections.listing_state(
                [entry["evidence"]["state"] for entry in entries]),
            "coverage": source["coverage"],
            "repositories": entries,
        }


def derive_observed(out_dir, run_id=None):
    out_dir = Path(out_dir)
    run_id = run_id or latest_run_id(out_dir)
    raw_dir = out_dir / "evidence" / "raw" / run_id

    org_record = _load(raw_dir, "org.json")
    org_state, _ = classify(org_record, shape="object",
                            absence_message=ABSENCE_MESSAGE)
    org_value = _pick(body_of(org_record), ORG_FIELDS) if org_state == "collected" else None
    write_canonical(
        out_dir / "observed" / "org.json",
        {"org": org_value, "run_id": run_id, "state": org_state},
    )

    pages = sorted(raw_dir.glob("repos.page-*.json"),
                   key=lambda p: int(p.stem.split("-")[-1]))
    page_records = [json.loads(p.read_text(encoding="utf-8")) for p in pages]
    repos, listing_state = [], "unknown"
    for record in page_records:
        page_state, _ = classify(record, shape="object_array",
                                 absence_message=ABSENCE_MESSAGE)
        if listing_state in ("unknown", "collected"):
            listing_state = page_state
        if usable_page(record):
            # collected and incomplete pages both carry valid partial evidence;
            # shape-invalid pages contribute nothing.
            repos.extend(
                {**_pick(item, REPO_FIELDS), "state": "collected"}
                for item in body_of(record)
            )
    repos.sort(key=lambda item: (not isinstance(item["id"], int), str(item["id"])
                                 if not isinstance(item["id"], int) else item["id"]))
    write_canonical(
        out_dir / "observed" / "repositories.json",
        {"count": len(repos), "repositories": repos,
         "run_id": run_id, "state": listing_state},
    )
    conflicted = projections.conflicted_ids(projections.structural_report(raw_dir))
    documents = {}
    for descriptor in resources.DESCRIPTORS:
        document = projections.resource_document(run_id, raw_dir, descriptor,
                                                 page_records, listing_state,
                                                 conflicted)
        documents[descriptor["name"]] = document
        write_canonical(
            out_dir / "observed" / (descriptor["name"] + ".json"), document)
    for name, document in _control_documents(controls.CONTROLS, documents):
        write_canonical(
            out_dir / "observed" / "controls" / (name + ".json"), document)
    return run_id
