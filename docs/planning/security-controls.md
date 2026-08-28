# Security Controls — Capability Roadmap

**Type:** planning artifact (owner-directed, Architecture Consolidation
2026-07-30). Governed by
[ADR-0008 — Security Control architectural seam](../adr/0008-security-control-model.md).
Planning only: this document authorizes no implementation, schedules no slice,
and creates no descriptor. Future slices select from it at their decision
phase.

## Current capability

The scanner observes repository inventory, default-branch protection,
repository rulesets, and the shared `security-and-analysis` surface with
deterministic evidence and reporting (Slices 1–3: three evidence layers,
byte-identical offline derivation, seven-state taxonomy, bounded waits;
347-test suite; validation runs `20260730T162522Z` and `20260816T134120Z`).
The first two Security Controls — Secret Scanning and Secret Scanning Push
Protection — are implemented under the canonical ADR-0009 realization:
control definitions, control-observation documents, per-control report
aggregates, and live-validated Observation, Applicability (including the
first applicability chain), and Operational State planes.

## Current limitation

Policy Expectation and Conformance conclusions exist for no Security
Control (the policy-definition decision is their prerequisite). Code
scanning, the Dependabot controls, dependency graph, security policy, and
organization security configuration are not yet observed. The ADR-0009
additivity proof covers the same-evidence-surface case only; the
cross-evidence-shape proof is assigned to the next implemented roadmap
control's slice.

## Target capability

Future bounded vertical slices implement GitHub security-control configuration
observation and conformance assessment under ADR-0008 — each slice selecting
**one or more Security Controls** from the roadmap below as its scope. The
Security Control seams are long-lived; they may be implemented across multiple
slices. No monolithic "GHAS slice" is planned.

## Explicit non-goals

Alert inventory, secret inventory, vulnerability finding inventory, malware
detection, risk scoring, and compliance scoring are outside authorized scope
unless separately authorized in a future decision phase. Alert-adjacent data
may be collected only where strictly required to establish configuration or
operational state (ADR-0008).

## Roadmap

| Security Control | Planned | Slice | Status |
|---|---|---|---|
| Secret Scanning | ✓ | 3 | Implemented (Slice 3 complete) |
| Secret Scanning Push Protection | ✓ | 3 | Implemented (Slice 3 complete) |
| Code Scanning | ✓ | TBD | Planned |
| Dependabot Vulnerability Alerts | ✓ | TBD | Planned |
| Dependabot Security Updates | ✓ | TBD | Planned |
| Dependency Graph | ✓ | TBD | Planned |
| Security Policy | ✓ | TBD | Planned |
| Security Configuration (organization-level) | ✓ | TBD | Planned |

## Per-control planning

Evidence-source and endpoint notes below are planning leads, not ratified
request contracts; each control's slice specification pins its actual evidence
rules, and live pinning follows validation-run authority.

### Secret Scanning

- **Purpose:** whether secret scanning is enabled for the repository.
- **Evidence sources:** repository `security_and_analysis.secret_scanning`
  (already present in collected inventory evidence — cross-reference
  issue #27); organization security configuration where observable.
- **Applicability:** plan/product-gated (GHAS licensing or public-repository
  availability; platform facts from wayfinder #2/#3).
- **Operational states (expected subset):** `enabled`, `disabled`,
  `unavailable`, `inaccessible`, `unknown`.
- **Dependencies / prerequisites:** #2 platform, #3 licensing; credential
  permissions per the documentation-first discipline.
- **Validation:** live pinning of enabled and disabled evidence classes;
  permission-denial classes; GHAS-gated fixtures (trial organization — absolute
  expiry 2026-08-28) or public-repository defaults.
- **Slice candidacy:** near-term — single-source, evidence surface partly
  collected today.

### Secret Scanning Push Protection

- **Purpose:** whether push protection is enabled.
- **Evidence sources:** repository
  `security_and_analysis.secret_scanning_push_protection`; organization
  security configuration where observable.
- **Applicability:** as Secret Scanning; additionally push protection is
  meaningful only where secret scanning itself is available — an explicit
  applicability chain, never collapsed into one boolean.
- **Operational states (expected subset):** `enabled`, `disabled`,
  `unavailable`, `inaccessible`, `unknown`.
- **Dependencies / validation / candidacy:** as Secret Scanning; natural
  companion in the same slice.

### Code Scanning

- **Purpose:** whether code scanning is configured and operationally active.
- **Evidence sources (composite — the designated multi-source case,
  ADR-0008):** default-setup state; advanced CodeQL workflow presence,
  including disabled or stale workflow state; external SARIF / third-party
  upload configuration where observable; intended branch and event coverage; supported-language coverage;
  organization security-configuration inheritance. Analysis presence may serve
  solely as operational-state evidence — never as alert inventory.
- **Applicability:** language coverage and plan gating; `not-applicable` is an
  expected real outcome (for example no supported language).
- **Operational states (expected subset):** full set, including `configured`,
  `not-configured`, `partially-configured`.
- **Dependencies / prerequisites:** ADR-0004's deferred multi-request
  combination-semantics decision (this control and per-ruleset detail,
  issue #28, are the candidates that trigger it); #2/#3; permissions.
- **Validation:** multi-source fixtures (default setup vs. workflow vs. none);
  stale-workflow and disabled-workflow states; coverage assertions.
- **Slice candidacy:** later — blocked on combination semantics; the metadata
  flag alone is never sufficient proof of complete coverage (ADR-0008).

### Dependabot Vulnerability Alerts

- **Purpose:** whether Dependabot vulnerability alerts are enabled.
- **Evidence sources:** the repository vulnerability-alerts enablement check
  (status-class response); organization security configuration where
  observable. The ambiguous-404 rule applies in full (ADR-0006): a 404 must
  not derive `disabled` without a descriptor-anchored affirmative rule.
- **Applicability:** requires Dependency Graph enablement — an applicability
  chain.
- **Operational states (expected subset):** `enabled`, `disabled`,
  `unavailable`, `inaccessible`, `unknown`.
- **Dependencies:** permissions (administration-read class); #2/#3.
- **Slice candidacy:** near-term — single-source status-class evidence.

### Dependabot Security Updates

- **Purpose:** whether automated security updates are enabled.
- **Evidence sources:** the automated-security-fixes enablement surface where
  observable; organization security configuration where observable.
- **Applicability:** requires Dependency Graph and vulnerability alerts — the
  longest applicability chain among the near-term controls.
- **Operational states (expected subset):** `enabled`, `disabled`,
  `unavailable`, `inaccessible`, `unknown`.
- **Slice candidacy:** near-term, alongside Vulnerability Alerts.

### Dependency Graph

- **Purpose:** whether the dependency graph is enabled — the prerequisite
  control for both Dependabot controls.
- **Evidence sources:** repository `security_and_analysis` surface and/or
  dedicated enablement evidence where observable; visibility-dependent
  defaults (public repositories) are applicability facts, not assumptions.
- **Operational states (expected subset):** `enabled`, `disabled`,
  `unavailable`, `inaccessible`, `unknown`.
- **Slice candidacy:** near-term — should accompany or precede the Dependabot
  controls to ground their applicability plane.

### Security Policy

- **Purpose:** whether a repository security policy (for example
  `SECURITY.md`) is present and observable.
- **Evidence sources:** community-profile / content-presence evidence.
- **Applicability:** broadly applicable; minimal gating.
- **Operational states (expected subset):** `configured`, `not-configured`,
  `inaccessible`, `unknown`.
- **Slice candidacy:** near-term — simplest control; useful vocabulary proof
  for the `configured`/`not-configured` states.

### Security Configuration (organization-level)

- **Purpose:** organization security configurations and their
  attachment/inheritance state — both a Security Control in its own right and
  an evidence source for the repository-level controls above.
- **Evidence sources:** organization security-configurations surface where
  observable.
- **Applicability:** organization-scoped — an organization-level observation
  target, not forced into repository-only concepts.
- **Dependencies / prerequisites:** the Observation Target Model
  generalization decision (issue #26) — the concrete case that makes it
  necessary; permissions; #2/#3.
- **Slice candidacy:** after the #26 decision; unblocks inheritance evidence
  for every other control.

## Cross-control dependencies and prerequisites

- **Platform and licensing facts:** wayfinder #2 (platform/identity) and #3
  (licensing) gate applicability knowledge for every GHAS-related control;
  the trial-organization route expires **2026-08-28**.
- **Permissions:** each control's credential needs are provisioned
  documentation-first per the established discipline (no silent substitution
  or broadening; divergences recorded).
- **Policy-definition model:** a policy artifact class (repository-class
  requirements, expectations) does not exist and is a **prerequisite decision
  for the Policy Expectation and Conformance planes of every control**. No
  conformance implementation precedes it (ADR-0008).
- **Multi-request combination semantics:** ADR-0004's deferred decision,
  triggered by the first composite control (Code Scanning) or multi-request
  descriptor (issue #28).
- **Observation Target Model:** issue #26, prerequisite for
  organization-scoped controls and inheritance evidence.
- **Live validation:** every control's slice pins its live evidence classes
  under validation-run authority; conditional rows degrade to recorded
  limitations exactly as V10/V12 did.

## Sequencing guidance

Future planning selects one or more controls as a bounded slice at its
decision phase. On current facts: **near-term candidates** — Dependency Graph, Dependabot
Vulnerability Alerts, Dependabot Security Updates, Security Policy
(single-source evidence, largely observable surfaces, no blocking
architecture decisions beyond #2/#3 facts and permissions); Secret Scanning
and Push Protection are implemented (Slice 3 complete) and no longer
candidates. **Later candidates** — Code Scanning (combination semantics
first), Security Configuration (#26 first). Conformance planes for any control
follow the policy-definition decision. This document schedules nothing.

Current status: the Secret Scanning control family — **Slice 3 — is
complete** (T1–T7, tickets #67–#73, each through the independent Quality
Gate and ⟦G-Merge⟧; consolidation record:
[slice-3-architecture-consolidation.md](../consolidation/slice-3-architecture-consolidation.md)).
Accepted specification:
[vertical-slice-3-secret-scanning-control-family.md](../specifications/vertical-slice-3-secret-scanning-control-family.md)
(canonical realization pattern: ADR-0009, proven in implementation). The
accepted Slice 3 subset excludes `unavailable` pending an affirmative
discriminator (#2/#3) — the "expected subset" leads in the two
secret-scanning sections above remain planning leads that the accepted
specification supersedes. The cross-evidence-shape additivity proof of the
control pattern remains assigned to the next implemented roadmap control's
slice. Grill input materials:
[slice-3-architecture-grill.md](slice-3-architecture-grill.md). All other
rows stay `TBD`/`Planned`; every control remains an independent seam.
