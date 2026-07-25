# Seven-state evidence taxonomy; absence requires affirmative evidence

**Status:** accepted

Every targeted resource is recorded in exactly one of seven states: `collected`, `absent`, `inaccessible`, `unsupported`, `failed`, `incomplete`, `unknown`. Because the GitHub API returns 404 both for "does not exist" and "you may not see it", **an ambiguous 404 is classified `inaccessible`, never `absent`** — absence is a positive finding requiring affirmative evidence (e.g., a 404 whose body states "Branch not protected" on an otherwise readable repository). The mirror may under-claim knowledge but must never fabricate a "not configured" finding.

## Consequences

- `failed` (collector-side malfunction) stays separate from `incomplete` (bounded partial evidence, e.g., a pagination cap breach) — audit needs the distinction.
- Denials (401/403) are evidence, not collector failure; collection of unaffected resources continues.
- The observed layer marks any value raw evidence cannot determine as `unknown`; derivation never guesses.
