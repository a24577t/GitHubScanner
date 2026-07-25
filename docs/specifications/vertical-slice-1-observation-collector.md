# Vertical Slice 1 — Observation Collector

**Status:** approved (architecture grill, 2026-07-24). Governing decisions: [ADR-0001](../adr/0001-collector-architecture-three-evidence-layers.md), [ADR-0002](../adr/0002-evidence-state-taxonomy.md), [ADR-0003](../adr/0003-explicit-environment-targeting.md).

## Purpose

Prove the collector architecture, not the security model: faithfully mirror one GitHub organization's repository inventory (identity and near-immutable metadata only) into a deterministic filesystem scaffold of raw evidence, observed state, and collection reports. Phase 1 is observation only.

## CLI contract

Two subcommands, non-interactive, exit code 0 on an orderly run (including partial evidence), non-zero only when the run frame cannot be established.

```
GITHUB_TOKEN=<token> collector collect --api-url <https-base> --org <login> --out <dir> [--run-id <id>] [--max-pages <n>]
collector derive --out <dir>
```

- `--api-url` — required, HTTPS, no default (ADR-0003). Examples: `https://api.github.com`, `https://<host>/api/v3`, `https://api.<sub>.ghe.com`.
- `--org` — required; exactly one named organization per run. Accessible scope is recorded, not swept.
- `--out` — required; operator-directed output directory (repository-agnostic; git is out of scope).
- `--run-id` — optional override; default is generated UTC timestamp form `YYYYMMDDTHHMMSSZ`.
- `--max-pages` — pagination safety cap, default 100; breach marks the affected collection `incomplete`, never truncates silently.
- `derive` — offline; regenerates observed state from raw evidence alone, byte-identically (ADR-0001 derivability rule).

## Runtime

Python 3.12+, standard library only; no package installation, no virtual environment. Transport (HTTP), collection, serialization, and persistence remain separable concerns; no fixed module count or file layout is mandated — the implementation stays as small as the contract allows. The repository file-size rule (300 physical lines, CLAUDE.md) applies as a review boundary with its documented exception process; do not force artificial splits to satisfy it.

## Collection behavior

1. **Authenticate** — token from `GITHUB_TOKEN` only; opaque; never persisted, logged, echoed, hashed, or written to evidence. Record the authenticated identity (`GET /user`). A 401 here fails the run frame.
2. **Platform evidence** — `GET /meta` and relevant response headers captured as raw evidence; recorded, never branched on.
3. **Collect** — `GET /orgs/{org}` and `GET /orgs/{org}/repos` (Link-header full drain, `per_page=100`, sequential). Rate-limit responses: plain wait-and-retry per `Retry-After`, recorded when it occurs.
4. **Persist** — write the scaffold (below).
5. **Summarize** — write the collection report.

Denials (401/403 on resources after the run frame is established) are evidence per ADR-0002; collection of unaffected resources continues.

## Output scaffold

Identical structure wherever `--out` resides:

```
<out>/
  evidence/raw/<run-id>/
    meta.json                # envelope + verbatim body per request
    user.json
    org.json
    repos.page-<n>.json
  observed/
    org.json                 # latest only; regenerable
    repositories.json
  reports/
    <run-id>.json
    <run-id>.md
```

**Envelope** (wraps every raw capture): request URL, method, response status, captured-at (ISO-8601 UTC), page number and item count where paginated, and the run-id. No sensitive headers, nothing token-derived.

**Observed state** — derived solely from raw. Org: identity/profile fields. Per repository: `id`, `name`, `full_name`, `visibility`, `fork`, `archived`, `created_at`, `default_branch`. Every entity carries its taxonomy state; values raw evidence cannot determine are `unknown`. Serialization: UTF-8, LF, sorted object keys, lists sorted by stable identity (repo `id`), timestamps from envelopes only — no wall-clock reads during derivation.

**Report** — JSON (machine) and Markdown (human): target host and API base, authenticated identity, run-id, scope attempted, per-state counts (all seven states), pages/items drained per listing with completeness stated as fact, rate-limit waits, and failures.

## Evidence-state taxonomy

Per ADR-0002: `collected`, `absent` (affirmative evidence required), `inaccessible` (includes all ambiguous 404s), `unsupported` (endpoint absent on this platform, recorded once per run), `failed` (transport/5xx after retry, parse errors), `incomplete` (bounded partial evidence), `unknown` (derivation cannot determine a value).

## Acceptance criteria

1. Fresh workstation, Python 3.12+, no installs: `collect` completes against a real org with only the documented inputs.
2. The scaffold above is produced identically regardless of where `--out` resides.
3. `derive` offline regenerates observed state byte-identical to the collected run's.
4. A listing spanning more than one page drains completely; the report states pages/items as fact.
5. An under-privileged token yields `inaccessible` recordings per taxonomy while unaffected collection continues, ending orderly.
6. A scan of all artifacts and logs finds no token material.
7. The report distinguishes, with counts, every taxonomy state present in the run.

## Failure cases

Non-zero exit with a clear diagnostic, without a misleading partial scaffold: missing/invalid `--api-url` or `--org`; missing token; 401 on identity; unwritable output directory; unparseable responses after retry exhaustion. Partial evidence is never failure.

## Non-goals

Compliance evaluation, desired state, remediation, dashboards, databases, a governance engine or product, scheduling/orchestration, environment-specific behavior, GraphQL, git automation, and any write operation against the target environment.

## Deferred (require a real environment / RBI specifics)

Security-configuration sweep; GHES version-specific behavior; enterprise/multi-org scope; rate-limit strategy beyond wait-and-retry; evidence retention and git automation; execution wrappers (Actions, schedulers, containers); GraphQL; history/trending or any evaluation of collected state.
