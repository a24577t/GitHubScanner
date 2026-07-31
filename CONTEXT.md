# GitHubScanner

Deterministic, evidence-first observation of GitHub security configuration.
This glossary was created at Slice 3 domain modeling under an owner-directed
scope constraint: ADR-0008 domain concepts only.

## Language

**Security Control**:
An independent, long-lived unit of GitHub security capability observed and
assessed through five planes — Observation, Applicability, Operational
State, Policy Expectation, Conformance. "Posture" is only a projection over
Security Controls.
_Avoid_: check, feature, setting, toggle, GHAS control

**Observation**:
Collected, verbatim, evidence-cited facts about a target — the evidence
plane every other plane derives from. Observations record no requirements
or judgments.
_Avoid_: scan result, finding, assessment

**Applicability**:
The evidence-derived conclusion whether a Security Control meaningfully
applies to a target: `applicable`, `not-applicable`, or
`applicability-unknown`. Never assumed; derived from platform, plan,
visibility, and repository characteristics.
_Avoid_: eligibility, relevance, coverage

**Applicability Chain**:
An Applicability rule under which one Security Control applies only where
another control is available. Chains key on availability, never on
enablement, and are never collapsed into one boolean.
_Avoid_: dependency flag, prerequisite toggle

**Operational State**:
The normalized, evidence-derived conclusion about a Security Control's
configuration on a target, from the closed set `enabled`, `disabled`,
`configured`, `not-configured`, `partially-configured`, `unavailable`,
`inaccessible`, `unknown`. Each control pins its reachable subset and the
evidence rule per value. "Enabled properly" is never an Operational State —
it is a Conformance conclusion.
_Avoid_: enablement, status flag, configuration state

**Resource Descriptor**:
The declarative statement of one coherently scoped observed GitHub
resource — what is observed and nothing more — through which Security
Controls obtain their Observations. One descriptor may serve several
controls that share an evidence surface.
_Avoid_: endpoint definition, API mapping, collector config
