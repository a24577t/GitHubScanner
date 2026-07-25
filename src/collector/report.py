"""Append-only collection reports: JSON for machines, Markdown for humans."""
from collector.serialize import write_canonical, write_text

ALL_STATES = (
    "collected", "absent", "inaccessible", "unsupported",
    "failed", "incomplete", "unknown",
)


def build_report(api_url, org, run_id, identity_login, summary):
    counts = {state: 0 for state in ALL_STATES}
    for state in summary["resource_states"].values():
        counts[state] += 1
    return {
        "api_url": api_url,
        "failures": summary["failures"],
        "identity_login": identity_login,
        "listings": summary["listings"],
        "org": org,
        "rate_limit": {
            "occurrences": len(summary["waits"]),
            "waits_seconds": summary["waits"],
        },
        "resource_states": summary["resource_states"],
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
                  f"(total {sum(rate['waits_seconds'])}s)", ""]
    return "\n".join(lines)


def write_report(out_dir, report):
    write_canonical(out_dir / "reports" / (report["run_id"] + ".json"), report)
    write_text(out_dir / "reports" / (report["run_id"] + ".md"), render_markdown(report))
