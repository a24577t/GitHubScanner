---
status: accepted
---

# Transfer Architecture — Review Evidence Package and Observer

**Status: accepted (architecture) / implementation deferred.** A *design* under
[MADR-0003](adr/0003-dual-mode-evidence-transport.md), elaborating its accepted
decisions; it may evolve without reopening them. **Nothing in this document is
implemented.** Until the recorded trigger fires, the strict existing rule
stands: a review whose repository artifacts are unavailable remains pending.
Project-independent and agent-neutral (P1, P6); concrete projects and products
appear only as marked *Examples*.

## Operating modes

| | Direct Repository Access | Indirect Review |
|---|---|---|
| Context source | Authoritative repository artifacts, independently reconstructed | Solely the supplied Review Evidence Package (REP) |
| REP role | Supplementary context | The review context |
| Primary review evidence | Repository artifacts (unchanged discipline) | REP artifacts, within its declared scope |
| Claims ceiling | Direct repository verification | Supplied-evidence verification; gaps as attestation or unavailable |
| Out-of-scope evidence | Inspect it directly | Review remains pending, or bounded by attestation |

Mode is declared by the repository owner at session start, as part of role
assignment. **Degradation profiles:** an open environment supports the full
model; an environment with an approved review engine reassigns roles to it
unchanged (P1 — participant swap, no methodology change); a disconnected
environment has no connected observer, and the observer function collapses
into Indirect Review with claims capped accordingly. The architecture is valid
in every profile because roles are engine-neutral and the claim registers cap
what any participant may assert.

## Review Evidence Package

The single sanctioned evidence transport across an access boundary. Design
layout (names indicative; the implementation contract fixes them):

```
review-evidence-package/
├── README.md            purpose · review scope · classification
│                        (Public / Internal / Confidential) · owner approval
│                        state · generation timestamp · generating process
├── manifest.md          included artifacts · per-artifact provenance · integrity
├── review-request.md    what to review · conclusions the reviewer MAY draw ·
│                        conclusions the reviewer MUST NOT draw
├── repository-state.md  the repository-state baseline (absorbed from the
│                        avatar generator's transfer-baseline contract:
│                        repository id · branch · HEAD · relevant PRs ·
│                        working-tree state · Status/continuity verification ·
│                        outstanding reconciliation · next activity ·
│                        verification timestamp)
├── change-summary.md    the change under review, incl. governing decisions
├── validation-results.md validation evidence exportable across the boundary
├── attestations.md      bounded internal attestations (below)
├── exclusions.md        what was withheld, by class — absence made affirmative
└── selected-artifacts/  exportable originals; sanitized derivatives carry
                         transformation provenance
```

**Lifecycle:** produce → owner export review at the deny-by-default release
boundary (intentional selection; classification; the standing exclusion list —
proprietary source, internal URLs and documentation, credentials and tokens,
customer and employee data, vulnerability and exploit detail, infrastructure
identifiers, unreleased product information, internal tickets/mail/chat/
meetings, vendor-confidential material, sensitive logs, protected screenshots)
→ owner approval → **frozen** → transfer. An approved REP is immutable; a
correction is a new package, never an edit.

## Provenance and attestation

Every included artifact carries: source path · source revision or internal
change identifier · transformation class (`original | excerpt | summary |
transformed | sanitized`) · transforming process or person · integrity
information for the included form (and the original where exportable). An
**attestation** records: what was validated · result · evidence class ·
producing authority · why supporting evidence is unavailable externally ·
scope and date. Every load-bearing review claim carries exactly one register
— **direct repository verification · supplied-evidence verification · internal
attestation · inference · unavailable** — and no claim is ever upgraded across
registers (MADR-0003).

## Governed review artifacts

Findings exist only as governed review artifacts: (a) created in an
owner-authorized channel, (b) durable and auditable, (c) visible to the owner
and available to gate adjudication, (d) never a private inter-participant
channel. Per-mode default classes: Direct — repository artifacts (pull-request
reviews, review comments, review documents); Indirect — REP contributions and
owner-authorized review reports.

## Observer design

The observer inspects, validates, and reports — nothing else. Its constraints
are enforced **structurally**: read-only access (it cannot commit, repair, or
merge, rather than merely being told not to); findings land only as governed
review artifacts; validation executes in the observer's own environment, never
in the repository. Independence is preserved without a new gate: implementation
responses to observer findings travel the existing verify chain, the
quality-gate record lists every observer finding and its disposition, and the
owner adjudicates the whole exchange at the existing merge gate — convergence
can occur only in owner-visible artifacts. The observer is one **producer** of
review evidence among several (implementation participants contribute
implementation evidence; internal reviewers contribute attestations); it is
never an authority. The execution-participant threshold of MADR-0003 bounds
this design: scheduling, orchestration, coordination, workflow triggering,
continuous monitoring, or autonomous escalation are outside it.

## Relationships

The repository remains the sole system of record; a REP is subordinate
transport (MADR-0001 D3). The collaboration avatar is orthogonal — durable
collaboration knowledge, repository-independent; either artifact may travel
without the other. The continuity mechanisms remain exactly two; in Indirect
mode a Repository Continuity Artifact's content may travel *inside* a REP.
History packages are inward-facing evolution evidence; the REP is
outward-facing review evidence; they share the package discipline (manifest,
provenance, exclusions, freeze-at-approval) and nothing else.

## Deferred implementation set

Implementation, when triggered, produces — and only then: a REP producer
contract (transition prompt) with the export-boundary procedure; the claim-
register refinement of the review discipline; an engine-neutral observer
contract in the collaborator namespace; a pointer-only entry file for tools
that recognize one (carrying an explicit no-governance disclaimer); the
owner operating-guide authorization point for exports; and the avatar's
conditional reconstruction instruction (Direct → from the repository;
Indirect → from the supplied REP). None of these exists today, by design.

## Validation design (pilot)

Adoption of a connected observer is validated by a **blinded, zero-footprint
retrospective pilot**: the observer receives only repository state, governing
artifacts, one merged change, and its implementation — never prior findings,
expected conclusions, or known defects — and returns a findings document to
the owner; comparison against the historical review record happens only after
completion. Blinding is bounded honestly: review traces embedded in repository
history (commit messages, PR text) cannot be withheld and are recorded as a
contamination factor; scoring weights only findings **beyond** what the
repository text already discloses. Success criteria: correct claim register on
every claim; zero unauthorized writes or side-channel exchanges;
parity-or-better real-defect detection beyond disclosed findings; owner-judged
signal-to-noise and per-review effort acceptable at a real gate.

> *Example (GitHubScanner): the designated pilot subject is merged PR #29 (the
> `.ai` information-architecture migration), whose two prior independent
> reviews provide the comparison baseline; the deferred-implementation trigger
> is recorded on the project roadmap as Slice 2 completion plus explicit
> repository-owner authorization.*

## Traceability

Modes, REP, registers, observer role, governed-artifact invariant, and the
execution-participant threshold implement MADR-0003. Subordination of supplied
evidence implements MADR-0001 (D3). Engine-neutral roles implement P1;
project-independence implements P6. The package discipline reuses the history-
package design. This document is evolvable design: it may be refined without
reopening MADR-0003, and it implements nothing until the trigger fires.
