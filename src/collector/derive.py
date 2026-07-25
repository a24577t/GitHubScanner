"""Derive observed state solely from raw evidence (ADR-0001 derivability rule)."""
import json
from pathlib import Path

from collector.serialize import write_canonical

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


def _body(record):
    try:
        return json.loads(record["body_text"])
    except (json.JSONDecodeError, TypeError):
        return None


def _pick(mapping, fields):
    """Project entity fields; undetermined values are 'unknown', never null."""
    if not isinstance(mapping, dict):
        mapping = {}
    return {
        field: mapping[field] if mapping.get(field) is not None else "unknown"
        for field in fields
    }


# Response bodies that affirmatively signal "not configured" (never mere "Not Found").
ABSENCE_MESSAGES = frozenset({"Branch not protected"})

RESOURCES = (("user", "user.json", "object"),
             ("meta", "meta.json", "object"),
             ("org", "org.json", "object"))


def _shape_ok(body, expect):
    if body is None:
        return False
    if expect == "object":
        return isinstance(body, dict)
    if expect == "object_array":
        return isinstance(body, list) and all(isinstance(item, dict) for item in body)
    return True


def state_of(record, expect=None):
    """Classify a raw record per the ADR-0002 taxonomy."""
    if record is None:
        return "unknown"
    status = record["envelope"]["status"]
    if record["envelope"].get("incomplete"):
        return "incomplete"
    if 200 <= status < 300:
        # A 2xx whose body is not the expected JSON shape is a failed
        # collection, never a collected one; no values are derived from it.
        return "collected" if _shape_ok(_body(record), expect) else "failed"
    if status in (401, 403):
        return "inaccessible"
    if status == 404:
        body = _body(record)
        message = body.get("message", "") if isinstance(body, dict) else ""
        if message in ABSENCE_MESSAGES:
            return "absent"
        if record["envelope"].get("endpoint_optional"):
            return "unsupported"
        return "inaccessible"
    return "failed"


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
        note(name, record, state_of(record, expect=expect))

    pages = sorted(raw_dir.glob("repos.page-*.json"),
                   key=lambda p: int(p.stem.split("-")[-1]))
    page_states, items = [], 0
    for number, page_path in enumerate(pages, start=1):
        record = json.loads(page_path.read_text(encoding="utf-8"))
        state = state_of(record, expect="object_array")
        note(f"repositories.page-{number}", record, state)
        del resource_states[f"repositories.page-{number}"]
        page_states.append(state)
        items += record["envelope"].get("item_count", 0)
    resource_states["repositories"] = next(
        (s for s in page_states if s != "collected"), "collected"
    ) if page_states else "unknown"
    complete = bool(page_states) and all(s == "collected" for s in page_states)
    return {
        "resource_states": resource_states,
        "failures": failures,
        "listings": {"repositories": {"pages": len(pages), "items": items,
                                      "complete": complete}},
        "waits": waits,
    }


def derive_observed(out_dir, run_id=None):
    out_dir = Path(out_dir)
    run_id = run_id or latest_run_id(out_dir)
    raw_dir = out_dir / "evidence" / "raw" / run_id

    org_record = _load(raw_dir, "org.json")
    org_state = state_of(org_record, expect="object")
    org_value = _pick(_body(org_record), ORG_FIELDS) if org_state == "collected" else None
    write_canonical(
        out_dir / "observed" / "org.json",
        {"org": org_value, "run_id": run_id, "state": org_state},
    )

    pages = sorted(raw_dir.glob("repos.page-*.json"),
                   key=lambda p: int(p.stem.split("-")[-1]))
    repos, listing_state = [], "unknown"
    for page_path in pages:
        record = json.loads(page_path.read_text(encoding="utf-8"))
        page_state = state_of(record, expect="object_array")
        if listing_state in ("unknown", "collected"):
            listing_state = page_state
        body = _body(record)
        status = record["envelope"]["status"]
        if 200 <= status < 300 and _shape_ok(body, "object_array"):
            # collected and incomplete pages both carry valid partial evidence;
            # shape-invalid pages contribute nothing.
            repos.extend(
                {**_pick(item, REPO_FIELDS), "state": "collected"} for item in body
            )
    repos.sort(key=lambda item: (not isinstance(item["id"], int), str(item["id"])
                                 if not isinstance(item["id"], int) else item["id"]))
    write_canonical(
        out_dir / "observed" / "repositories.json",
        {"count": len(repos), "repositories": repos,
         "run_id": run_id, "state": listing_state},
    )
    return run_id
