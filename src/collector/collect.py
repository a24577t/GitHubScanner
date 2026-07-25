"""Collection flow: authenticate, gather evidence for one organization, persist."""
import datetime
import json
from pathlib import Path

from collector import derive, report, transport
from collector.serialize import write_canonical


class RunFrameError(Exception):
    pass


# Non-sensitive response headers retained as evidence: platform identity,
# pagination, and rate-limit/retry context. Request headers are never persisted.
HEADER_ALLOWLIST = frozenset({
    "link",
    "retry-after",
    "x-ratelimit-limit",
    "x-ratelimit-remaining",
    "x-ratelimit-reset",
    "x-ratelimit-used",
    "x-github-enterprise-version",
    "x-github-media-type",
    "x-github-api-version-selected",
})


def _evidence_headers(headers):
    return {
        name.lower(): value
        for name, value in headers.items()
        if name.lower() in HEADER_ALLOWLIST
    }


def _generated_run_id():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _record(result, run_id, **extra):
    envelope = {
        "captured_at": result.captured_at,
        "method": "GET",
        "run_id": run_id,
        "response_headers": _evidence_headers(result.headers),
        "status": result.status,
        "url": result.url,
        "attempts": result.attempts,
        "waits_seconds": result.waits,
    }
    envelope.update(extra)
    return {"envelope": envelope, "body_text": result.body_text}


def run_collect(api_url, org, out_dir, token, run_id=None, max_pages=100):
    run_id = run_id or _generated_run_id()
    out_dir = Path(out_dir)
    raw_dir = out_dir / "evidence" / "raw" / run_id
    if raw_dir.exists():
        raise RunFrameError(
            f"raw evidence for run {run_id} already exists; "
            "raw evidence is append-only and is never modified"
        )

    identity = transport.get(api_url, "/user", token)
    if identity.status == 401:
        raise RunFrameError("authentication rejected by target (401 on /user)")
    try:
        identity_login = json.loads(identity.body_text).get("login")
    except (json.JSONDecodeError, AttributeError):
        identity_login = None

    meta = transport.get(api_url, "/meta", token)
    org_result = transport.get(api_url, f"/orgs/{org}", token)
    pages, listing_complete = transport.paginate(
        api_url, f"/orgs/{org}/repos", token, max_pages=max_pages
    )

    write_canonical(raw_dir / "user.json", _record(identity, run_id))
    write_canonical(raw_dir / "meta.json", _record(meta, run_id, endpoint_optional=True))
    write_canonical(raw_dir / "org.json", _record(org_result, run_id))
    item_total = 0
    for number, page in enumerate(pages, start=1):
        try:
            items = len(json.loads(page.body_text))
        except (json.JSONDecodeError, TypeError):
            items = 0
        item_total += items
        incomplete = ((number == len(pages)) and not listing_complete
                      and 200 <= page.status < 300)
        write_canonical(
            raw_dir / f"repos.page-{number}.json",
            _record(page, run_id, page=number, item_count=items,
                    **({"incomplete": True} if incomplete else {})),
        )

    derive.derive_observed(out_dir, run_id=run_id)

    resource_states = {}
    for name, resource, expect in (("user", "user.json", None),
                                   ("meta", "meta.json", None),
                                   ("org", "org.json", "object")):
        record = json.loads((raw_dir / resource).read_text(encoding="utf-8"))
        resource_states[name] = derive.state_of(record, expect=expect)
    listing_states = []
    for page_path in sorted(raw_dir.glob("repos.page-*.json")):
        record = json.loads(page_path.read_text(encoding="utf-8"))
        listing_states.append(derive.state_of(record, expect="object_array"))
    resource_states["repositories"] = next(
        (s for s in listing_states if s != "collected"), "collected"
    ) if listing_states else "unknown"

    waits = [w for page in pages for w in page.waits]
    waits += [w for r in (identity, meta, org_result) for w in r.waits]
    report.write_report(out_dir, report.build_report(
        api_url, org, run_id, identity_login, resource_states,
        {"repositories": {"pages": len(pages), "items": item_total,
                          "complete": listing_complete}},
        waits,
    ))
    return 0
