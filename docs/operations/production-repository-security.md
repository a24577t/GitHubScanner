# Production Repository Security — Operational Record

**Type: operational documentation only.** This records the security
configuration of the production repository `a24577t/GitHubScanner` itself.
It is **not** validation evidence, is **not** normative for any Slice 3
artifact, and pins nothing: the production repository is never a validation
fixture, and matrix-row acceptance remains exclusively validation-run
authority over GHScannerLab (accepted Slice 3 specification and matrix).

## State as of 2026-07-31 (after owner-authorized changes)

| Feature | State | Note |
|---|---|---|
| Secret Scanning | enabled | pre-existing |
| Secret Scanning Push Protection | enabled | pre-existing |
| Secret scanning — non-provider patterns | **disabled — plan-gated** | see constraint below |
| Secret scanning — validity checks | disabled — **deferred by owner decision** | pending an explicit decision on partner validation / privacy |
| Dependabot vulnerability alerts | enabled | pre-existing |
| Dependabot security updates | **enabled** | changed 2026-07-31 (owner-authorized) |
| Dependency graph | enabled | public-repository default |
| CodeQL code scanning (default setup) | **configured** | changed 2026-07-31 (owner-authorized); default query suite; first analysis run launched at configuration |
| Private vulnerability reporting | **enabled** | changed 2026-07-31 (owner-authorized) |
| `main` branch protection | active ruleset "PR required on main" | PR required, deletions blocked, force-pushes blocked, no bypass actors; name typo corrected 2026-07-31 (owner-authorized) |

## Changes applied 2026-07-31 (explicit owner authorization)

1. CodeQL default setup enabled (`not-configured` → `configured`).
2. Dependabot security updates enabled.
3. Private vulnerability reporting enabled.
4. Ruleset renamed "PR reuired on main" → "PR required on main" (rules and
   enforcement unchanged).
5. Secret-scanning non-provider patterns enablement **attempted and not
   applied** — see constraint below.

## Constraints and deferrals

- **Non-provider patterns (plan-gated):** the REST update returns success
  but the field remains `disabled`; on a Free-plan user-owned repository
  this feature requires GitHub Advanced Security (Secret Protection) and the
  API silently ignores the toggle. Operationally notable: this is live
  incidental corroboration of the settings-surface behavior class
  (plan-gated fields, silent non-application) that the Slice 3 architecture
  degrades to `unknown` — recorded here as context only, never as
  validation evidence.
- **Validity checks (owner-deferred):** enabling would transmit detected
  token candidates to providers for liveness verification; deferred pending
  an explicit owner privacy decision.

## Boundaries

- GHScannerLab fixtures are untouched by this record and by the changes
  above; their controlled enablement belongs exclusively to Ticket #72 (T6)
  provisioning under the accepted validation matrix (disabled-pin fixtures
  remain disabled until then).
- No Slice 3 validation artifact was altered.
- Future changes to production security settings are owner-authorized
  operations; update this record when they occur.
