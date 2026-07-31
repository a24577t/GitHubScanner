"""Append-only collection reports: JSON for machines, Markdown for humans."""
from collector.serialize import write_canonical, write_text
from collector.summary import WAIT_CATEGORIES

ALL_STATES = (
    "collected", "absent", "inaccessible", "unsupported",
    "failed", "incomplete", "unknown",
)


def _resource_aggregates(resources):
    """Per-descriptor aggregates bounded by the closed state and reason
    vocabularies; raw per-repository wait lists never reach the report."""
    return {
        name: {
            "state": block["state"],
            "state_counts": block["state_counts"],
            "reason_counts": block["reason_counts"],
            "waits": {"count": len(block["waits_seconds"]),
                      "total_seconds": sum(block["waits_seconds"])},
        }
        for name, block in resources.items()
    }


def build_report(api_url, org, run_id, identity_login, summary):
    counts = {state: 0 for state in ALL_STATES}
    for state in summary["resource_states"].values():
        counts[state] += 1
    return {
        "api_url": api_url,
        "controls": summary["controls"],
        "execution": summary["execution"],
        "failures": summary["failures"],
        "identity_login": identity_login,
        "listings": summary["listings"],
        "org": org,
        "rate_limit": {
            "occurrences": len(summary["waits"]),
            "total_seconds": sum(summary["waits"]),
        },
        "resource_states": summary["resource_states"],
        "resources": _resource_aggregates(summary["resources"]),
        "run_id": run_id,
        "state_counts": counts,
    }


def render_markdown(report):
    import urllib.parse

    host = urllib.parse.urlsplit(report["api_url"]).hostname
    lines = [
        f"# Collection report {report['run_id']}",
        "",
        f"- **API base:** {report['api_url']}",
        f"- **Target host:** {host}",
        f"- **Organization:** {report['org']}",
        f"- **Authenticated identity:** {report['identity_login']}",
        "",
        "## Resource states",
        "",
        "| Resource | State |",
        "| --- | --- |",
    ]
    for resource in sorted(report["resource_states"]):
        lines.append(f"| {resource} | {report['resource_states'][resource]} |")
    lines += ["", "## State counts", "", "| State | Count |", "| --- | --- |"]
    for state in ALL_STATES:
        lines.append(f"| {state} | {report['state_counts'][state]} |")
    lines += ["", "## Listings", "", "| Listing | Pages | Items | Complete |",
              "| --- | --- | --- | --- |"]
    for name in sorted(report["listings"]):
        listing = report["listings"][name]
        lines.append(
            f"| {name} | {listing['pages']} | {listing['items']} "
            f"| {str(listing['complete']).lower()} |"
        )
    lines += ["", "## Failures", ""]
    if report["failures"]:
        lines += ["| Resource | Status | URL |", "| --- | --- | --- |"]
        lines += [f"| {f['resource']} | {f['status']} | {f['url']} |"
                  for f in report["failures"]]
    else:
        lines.append("None.")
    rate = report["rate_limit"]
    lines += ["", f"Rate-limit waits: {rate['occurrences']} "
                  f"(total {rate['total_seconds']}s)"]
    lines += _aggregate_lines(report["resources"])
    lines += _control_lines(report["controls"])
    lines += _execution_lines(report["execution"])
    return "\n".join(lines)


def _counts(mapping):
    return ", ".join(f"{key}: {mapping[key]}" for key in sorted(mapping))


def _aggregate_lines(resources):
    lines = ["", "## Per-resource aggregates", "",
             "| Resource | State | State counts | Reason counts | Waits |",
             "| --- | --- | --- | --- | --- |"]
    for name in sorted(resources):
        block = resources[name]
        lines.append(
            f"| {name} | {block['state']} | {_counts(block['state_counts'])} "
            f"| {_counts(block['reason_counts'])} "
            f"| {block['waits']['count']} ({block['waits']['total_seconds']}s) |"
        )
    return lines


def _control_lines(control_blocks):
    """One bounded row per control: the four closed-vocabulary count
    families, rendered as derived — no rollup, no citation, no per-entry
    content (V59)."""
    lines = ["", "## Per-control aggregates", "",
             "| Control | Applicability | Applicability reasons "
             "| Operational states | Operational reasons |",
             "| --- | --- | --- | --- | --- |"]
    for name in sorted(control_blocks):
        block = control_blocks[name]
        lines.append(
            f"| {name} | {_counts(block['applicability_counts'])} "
            f"| {_counts(block['applicability_reason_counts'])} "
            f"| {_counts(block['operational_state_counts'])} "
            f"| {_counts(block['operational_state_reason_counts'])} |")
    return lines


def _execution_lines(execution):
    requests, waits = execution["requests"], execution["waits"]
    lines = [
        "", "## Execution", "",
        f"- **Planned:** {requests['planned_singles']} singles, "
        f"{requests['planned_drains']} drains "
        f"(missing input: {requests['missing_input']})",
        f"- **Retained records:** {requests['retained_records']} "
        f"(attempts {requests['attempts']}; completed {requests['completed']}, "
        f"failed {requests['failed']}, "
        f"evidence absent {requests['evidence_absent']})",
        "", "| Wait category | Count | Requested s | Slept s |",
        "| --- | --- | --- | --- |",
    ]
    for category in WAIT_CATEGORIES:
        bucket = waits[category]
        lines.append(f"| {category} | {bucket['count']} "
                     f"| {bucket['requested_seconds']} "
                     f"| {bucket['slept_seconds']} |")
    lines += [
        "",
        f"Refused waits: {waits['refused']}; maximum single wait (requested): "
        f"{waits['max_single_wait_seconds']}s; total requested (waits taken): "
        f"{waits['total_wait_seconds']}s",
        "",
        "Terminations: " + (_counts(execution["terminations"])
                            if execution["terminations"] else "none") + ".",
        "",
        f"Capture window: {execution['captured']['first']} — "
        f"{execution['captured']['last']}",
        "",
    ]
    return lines


def write_report(out_dir, report):
    write_canonical(out_dir / "reports" / (report["run_id"] + ".json"), report)
    write_text(out_dir / "reports" / (report["run_id"] + ".md"), render_markdown(report))
