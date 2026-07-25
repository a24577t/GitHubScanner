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
    raw_root = Path(out_dir) / "evidence" / "raw"
    runs = sorted(p.name for p in raw_root.iterdir() if p.is_dir())
    if not runs:
        raise ValueError("no raw evidence runs found under " + str(raw_root))
    return runs[-1]


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
    if not isinstance(mapping, dict):
        return {field: None for field in fields}
    return {field: mapping.get(field) for field in fields}


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


# Response bodies that affirmatively signal "not configured" (never mere "Not Found").
ABSENCE_MESSAGES = frozenset({"Branch not protected"})


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
            repos.extend(_pick(item, REPO_FIELDS) for item in body)
    repos.sort(key=lambda item: (item["id"] is None, item["id"]))
    write_canonical(
        out_dir / "observed" / "repositories.json",
        {"count": len(repos), "repositories": repos,
         "run_id": run_id, "state": listing_state},
    )
    return run_id
