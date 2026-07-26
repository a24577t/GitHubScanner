---
status: accepted
---

# MADR-0003 — Dual-mode evidence transport and the Observer role

**Status: accepted. Architecture accepted / implementation deferred** (see
Consequences). Project-independent and agent-neutral (P1, P6); a concrete
project appears only as a marked *Example*.

**Two operating modes.** Collaboration operates identically whether or not a
participant can inspect the repository. In **Direct Repository Access** mode, a
participant independently reconstructs repository state from the authoritative
artifacts. In **Indirect Review** mode, a participant reconstructs review
context solely from a supplied, owner-approved **Review Evidence Package
(REP)**. In both modes the repository remains the sole system of record
([MADR-0001](0001-repository-authoritative-continuity.md) D3): supplied
evidence is temporary transport, never independent truth; when access is
restored it is verified against the repository, the repository prevails, and
divergence is surfaced.

**Review Evidence Package.** The REP is the **single sanctioned evidence
transport** across an access boundary, generalizing and absorbing the
repository-transfer baseline previously defined for avatar generation. A REP is
owner-approved before it crosses the boundary and immutable once approved;
it carries per-artifact provenance (source, source revision, transformation
class — original, excerpt, summary, transformed, or sanitized — transformer,
and integrity information), explicit exclusions, and the conclusions a reviewer
may and may not draw. Export is governed by a **deny-by-default release
boundary**: nothing crosses unless intentionally selected, classified
(Public / Internal / Confidential), and owner-approved.

**Claim registers.** Every load-bearing review claim carries exactly one
register: **direct repository verification · supplied-evidence verification ·
internal attestation · inference · unavailable**. Direct repository
verification is claimed only when direct inspection actually occurred. An
attestation is a bounded statement that a named internal authority validated
something whose evidence cannot travel; it is evidence of an internal claim,
never independently verifiable, and never upgradeable to verification.

**The Observer role.** The controlled role vocabulary gains **observer**: a
first-class, engine-neutral collaboration role that inspects repository state,
validates, and reports findings — with **no verdict or gate standing**. An
observer never commits, repairs, merges, approves, or begins subsequent work;
these constraints are enforced structurally (read-only access) rather than
behaviorally. Roles remain assigned by the human architect and interchangeable
without methodology change (P1); durable artifacts never name engines.

**Governed review artifacts.** Observer and review findings exist only as
**governed review artifacts**: created in an owner-authorized channel, durable
and auditable, visible to the owner and available to gate adjudication, and
never a private inter-participant channel. In Direct mode this class defaults
to repository artifacts (for example pull-request reviews); other classes
exist only where the owner establishes them (for example a REP contribution).

**Execution-participant threshold.** The observer remains a refinement of the
existing review model while it only inspects, validates, and reports. An
observer that acquires lifecycle capability — scheduling reviews, orchestrating
reviewers, coordinating participants, triggering workflow progression,
continuous monitoring, or autonomous escalation — becomes an **execution
participant**; crossing that line requires a new methodology decision before
any such capability is exercised.

## Consequences

- **Implementation deferred.** This decision implements nothing: no REP
  tooling, no observer assignment, no review-discipline refinement. The strict
  existing rule — review pending when repository artifacts are unavailable —
  stands until implementation lands. Implementation triggers on explicit
  repository-owner authorization after the current work item stabilizes.
  > *Example (GitHubScanner): recorded as a roadmap issue; trigger is Slice 2
  > completion.*
- Design documentation elaborating this decision (package layout, operating
  profiles, pilot protocol) is produced separately and is subordinate to it.
- The continuity mechanisms of MADR-0001 are **unchanged — exactly two**; the
  REP is evidence transport, not a third continuity mechanism. In Indirect
  mode, a Repository Continuity Artifact's content may travel inside a REP.
- Rejected: the REP as a universal review contract (in Direct mode, primary
  review evidence remains the repository itself); a third continuity
  mechanism; write access for observers; engine-named roles in durable
  artifacts.
