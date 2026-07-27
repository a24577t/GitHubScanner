"""Collection flow: authenticate, gather evidence for one organization, persist."""
import datetime
import json
from pathlib import Path

from collector import derive, report, resources, targets, transport
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


def _generated_run_id():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _record(result, run_id, **extra):
    envelope = {
        "captured_at": result.captured_at,
        "method": "GET",
        "response_headers": {
            name: value for name, value in result.headers.items()
            if name in HEADER_ALLOWLIST
        },
        "run_id": run_id,
        "status": result.status,
        "url": result.url,
        "attempts": result.attempts,
        "waits_seconds": result.waits,
    }
    envelope.update(extra)
    return {"envelope": envelope, "body_text": result.body_text}


def _page_records(pages, complete, run_id, **extra):
    """Raw records for one paginated listing drain; a capped drain marks its
    last collected page incomplete, never truncates silently."""
    records = []
    for number, page in enumerate(pages, start=1):
        try:
            body = json.loads(page.body_text)
        except (json.JSONDecodeError, TypeError):
            body = None
        items = len(body) if isinstance(body, list) else 0
        incomplete = ((number == len(pages)) and not complete
                      and 200 <= page.status < 300)
        records.append(_record(page, run_id, page=number, item_count=items,
                               **({"incomplete": True} if incomplete else {}),
                               **extra))
    return records


def _collect_repo_resources(api_url, token, raw_dir, run_id, page_records,
                            max_pages):
    """Fan-out stage (ADR-0004/0005): canonical targets in ascending id order,
    descriptors in table order, through the existing transport."""
    for target in targets.discover_targets(page_records):
        repo_dir = raw_dir / "repos" / targets.directory_key(
            target["id"], target["name"])
        for descriptor in resources.DESCRIPTORS:
            inputs, missing = targets.descriptor_inputs(target, descriptor)
            if missing:
                # ADR-0005: no request and no fabricated artifact; the
                # resource derives unknown from the absence (T6). Other
                # descriptors still observe this repository.
                continue
            path = descriptor["path_template"].format(
                full_name=target["full_name"], **inputs)
            extra = {"repo": {"id": target["id"],
                              "full_name": target["full_name"]},
                     "resource": descriptor["name"]}
            if "default_branch" in inputs:
                extra["branch"] = inputs["default_branch"]
            result = transport.get(api_url, path, token)
            write_canonical(repo_dir / f"{descriptor['name']}.json",
                            _record(result, run_id, **extra))


def _prepare_out_dir(out_dir):
    """Verify writability before any request; return dirs created for rollback."""
    created, probe_parent = [], out_dir
    while not probe_parent.exists():
        created.append(probe_parent)
        probe_parent = probe_parent.parent
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        probe = out_dir / ".write-probe"
        probe.write_text("", encoding="utf-8")
        probe.unlink()
    except OSError as err:
        raise RunFrameError(f"output directory is not writable: {err}")
    return created


def _rollback(created_dirs):
    for path in created_dirs:
        try:
            path.rmdir()
        except OSError:
            pass


def _establish_identity(api_url, token):
    identity = transport.get(api_url, "/user", token)
    if identity.status == 0:
        raise RunFrameError(f"target unreachable: {identity.body_text}")
    if identity.status == 401:
        raise RunFrameError("authentication rejected by target (401 on /user)")
    if not 200 <= identity.status < 300:
        raise RunFrameError(
            f"identity not established ({identity.status} on /user)"
        )
    try:
        login = json.loads(identity.body_text).get("login")
    except (json.JSONDecodeError, AttributeError):
        login = None
    if login is None:
        raise RunFrameError(
            "identity response unparseable (2xx on /user without a login)"
        )
    return identity, login


def run_collect(api_url, org, out_dir, token, run_id=None, max_pages=100):
    run_id = run_id or _generated_run_id()
    out_dir = Path(out_dir)
    raw_dir = out_dir / "evidence" / "raw" / run_id
    if raw_dir.exists():
        raise RunFrameError(
            f"raw evidence for run {run_id} already exists; "
            "raw evidence is append-only and is never modified"
        )
    created_dirs = _prepare_out_dir(out_dir)
    try:
        identity, identity_login = _establish_identity(api_url, token)
    except RunFrameError:
        _rollback(created_dirs)
        raise

    meta = transport.get(api_url, "/meta", token)
    org_result = transport.get(api_url, f"/orgs/{org}", token)
    pages, listing_complete = transport.paginate(
        api_url, f"/orgs/{org}/repos", token, max_pages=max_pages
    )

    write_canonical(raw_dir / "user.json", _record(identity, run_id))
    write_canonical(raw_dir / "meta.json", _record(meta, run_id, endpoint_optional=True))
    write_canonical(raw_dir / "org.json", _record(org_result, run_id))
    page_records = _page_records(pages, listing_complete, run_id)
    for number, record in enumerate(page_records, start=1):
        write_canonical(raw_dir / f"repos.page-{number}.json", record)

    # Discovery consumes the exact records persisted above — the canonical
    # rule is shared with offline rederivation (ADR-0005, V38).
    _collect_repo_resources(api_url, token, raw_dir, run_id, page_records,
                            max_pages)

    derive.derive_observed(out_dir, run_id=run_id)
    summary = derive.run_summary(out_dir, run_id)
    report.write_report(out_dir, report.build_report(
        api_url, org, run_id, identity_login, summary,
    ))
    return 0
