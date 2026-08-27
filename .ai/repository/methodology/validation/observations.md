# Methodology Observations

Immutable, append-only, evidence-first records of the methodology in practice (see
[README.md](README.md)). Each observation states verifiable evidence and its observed impact
only — no disposition and no remedy. Dispositions live exclusively in [`reviews/`](reviews/)
records referencing the `MO-NNN` identifiers below.

---

## MO-001 — Dangling `observations.md` link in the validation charter; contested bootstrap outcome

**Recorded:** 2026-08-21.

**Evidence.** `.ai/repository/methodology/validation/README.md` has linked `observations.md`
since the subsystem's creation in the IA migration (commit `2eb9561`, 2026-07); `git log --all`
shows the file never existed in any commit. `reviews/` was seeded with a `.gitkeep`;
`observations.md` was not seeded. During a session bootstrap on 2026-08-21, the missing file
was flagged under session-bootstrap's "Internal references resolve (ADR / MADR / specification /
baseline cross-references)" check, and — per the repository owner's account — that session then
proceeded into PR review activity after reporting Bootstrap Failed. A succeeding remediation
session adjudicated the link as a charter reference to a lazily created evidence file outside
the check's parenthetical scope, and seeded this file.

**Observed impact.** The internal-references check's scope is ambiguous for design-document
links to lazily created evidence files: two sessions reached opposite bootstrap adjudications
from the same repository state. Separately, the no-work-after-Bootstrap-Failed rule
(session-bootstrap: "the session does not proceed to Working") was not honored by the first
session, and its review findings were subsequently withdrawn by the owner.

## MO-002 — Session ended mid-transition without a Repository Continuity Artifact

**Recorded:** 2026-08-21.

**Evidence.** A session ended on 2026-08-21 while Slice 3 T7 (#73) was mid-transition — the
completion reconciliation prepared and open as PR #89, its predecessor ⟦G-Merge⟧ review
WITHHELD and later withdrawn — with no `.ai/repository/state/repository-continuity.md`
emitted. The lifecycle model requires one when any work-item instance is not at a stable
state ("a session ending then must emit a Repository Continuity Artifact for that work
item"), and the Status Artifact's last-stable-state semantics rely on that artifact to carry
the in-flight position. The succeeding session's bootstrap could not reconcile the observed
working state (non-`main` checkout, unmerged reconciliation commit, open PR asserting T7's
verify chain complete) against any continuity artifact, and a remediation session
reconstructed the in-flight intent from PR artifacts before creating the missing artifact.

**Observed impact.** Bootstrap's working-state reconciliation check failed; the in-flight
position had to be reconstructed from non-authoritative review context rather than read from
the designated continuity mechanism; the gap went undetected until an independent bootstrap
evaluation ran.
