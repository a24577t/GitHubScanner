# Validation Environment

A minimal, manually-managed GitHub organization used as the live validation target for releases that change collection or derivation behavior. Documentation, not automation: this file records intent; the authoritative record of the environment's actual state is the scanner's own committed run evidence under `docs/validation/runs/`.

## Organization

- **Name:** `GHScannerLab` (github.com, Free plan, owned by `a24577t`)
- **Content policy:** synthetic and public-by-default. The organization holds nothing sensitive; every repository is treated as public regardless of visibility, because committed run evidence names the organization, its inventory, and the authenticated identity.
- **Disposability:** this document must remain sufficient to rebuild an equivalent organization under any name from scratch. If rebuilding from this document is cheap, the environment stays disposable and drift loses its teeth.

## GHAS trial organization (reconnaissance target)

> **Synthetic test values — workflow validation only.** Recorded 2026-07-29 to validate the repository's reconnaissance-planning workflow; not operational production configuration. An owner-authorized update replaces them when a real trial is activated; trial-dependent work is blocked until then.

- **Name:** `GHScannerLab-Trial` (github.com; a separate organization from `GHScannerLab`; GHAS trial).
- **Absolute trial expiry date:** 2026-08-28 — an environment property: trial-dependent conditional validation (e.g., V12 organization-ruleset behavioral parent exclusion) completes before this date or resolves as a recorded limitation per the Slice 2 specification.
- **Role:** target for owner-authorized bounded live reconnaissance runs and trial-dependent conditional validation only, per the live-run classes clarification (Slice 2 specification, Validation section) and the ratified bounds in [issue #47](https://github.com/a24577t/GitHubScanner/issues/47). Reconnaissance evidence never accepts a validation-matrix row.
- **Credentials:** same discipline as validation runs — documentation-first provisioning; no silent credential-type substitution, no permission broadening, and no reduction of required validation coverage; divergences recorded and grade-marked.
- **Content policy and disposability:** as for `GHScannerLab` — synthetic, public-by-default, rebuildable from this document.

## Repository inventory

| Repository | Purpose | Visibility | Plan requirement | Expected observed values | Introduced |
| --- | --- | --- | --- | --- | --- |
| `standard-repo` | Plain baseline repository | public | Free | `archived: false`, `fork: false`, `default_branch: main`, state `collected` | Validation Environment release (post-v0.1.0) |
| `archived-repo` | Archived-state fixture | public | Free | `archived: true`, state `collected` | Validation Environment release (post-v0.1.0) |
| `Hello-World` | Fork fixture (fork of `octocat/Hello-World`) | public | Free | `fork: true`, `default_branch: master`, state `collected` | Validation Environment release (post-v0.1.0) |

Repositories are added lazily: only when an approved vertical slice's specification requires a new fixture, in the same change set that approves the capability. No repository exists ahead of an approved specification.

## Validation runs

- One manual `collect` + `derive` run per release that changes collection or derivation behavior.
- Each run's complete output tree (raw evidence, observed state, reports) is committed as a **self-contained** directory under `docs/validation/runs/<date>-<org>/`. Self-containment matters: `derive` selects the latest run within a tree, so runs are never mixed in one tree.
- The evidence is the collector's own output — no separate record format, no expected-vs-actual tooling, no comparator. A human reads the committed report against this document's inventory table.
- Committed evidence is token-free by construction (token-secrecy acceptance criterion AC6; response-header allowlist) and is verified by scan before commit.

## Credentials

- Standing rule: validation runs use a dedicated fine-grained personal access token, read-only, scoped to `GHScannerLab` only, supplied via `GITHUB_TOKEN`. The organization-admin credential used to configure fixtures is never the run credential.
- **Recorded divergence (first run, 20260725T184527Z):** the run used the operator's existing `gh` CLI token (scopes broader than the standing rule) by explicit owner decision, to avoid blocking the first evidence capture. The standing rule applies from the next validation run onward.

## What this environment validates — and what it does not

It validates the scanner against **live github.com on a Free-plan organization**: real REST API behavior, authentication, organization endpoints, effective permissions, pagination and response formats — the assumptions otherwise encoded only in the scripted test fixture (`tests/fake_github.py`).

It does **not** certify: GitHub Enterprise Server, GitHub Enterprise Cloud, Enterprise Managed Users, GitHub Advanced Security, or any enterprise governance feature (organization/enterprise rulesets, security overview, audit log). Those remain future work, deferred exactly as the Slice 1 specification records; a green run here is never release evidence for enterprise-only endpoints. Revisit this scope when the platform-confirmation discovery ticket (#2 on the wayfinder map) is resolved.

Known live-coverage limits at Slice 1: a run of this size exercises the authenticated happy path, real envelope and header shapes, and single-page listing only. Multi-page drain, rate-limit waits, retries, and the `absent`/`unsupported`/`failed`/`incomplete` states remain proven by the offline test suite.
