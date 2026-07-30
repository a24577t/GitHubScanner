# Security Control architectural seam

**Status:** accepted

A **Security Control** is the first-class architectural unit for GitHub
security-configuration observation and assessment. Each Security Control is an
independent, long-lived seam with its own evidence collection, normalization,
applicability, operational state, policy expectation, conformance evaluation,
and reporting projection. "Posture" is a projection over Security Controls,
never a model of its own. The model of every Security Control:

> **Security Control** — Observation → Applicability → Operational State →
> Policy Expectation → Conformance

The planes and their closed vocabularies:

- **Observation** — collected evidence under the existing evidence
  architecture (ADR-0001 layers and derivability, ADR-0002/0006 taxonomy and
  affirmative-evidence rules): verbatim, retained, evidence-cited.
- **Applicability** — whether the control meaningfully applies to the target:
  `applicable`, `not-applicable`, `applicability-unknown`. Itself
  evidence-derived (platform, plan, visibility, language, repository
  characteristics), never assumed.
- **Operational State** — the normalized, evidence-derived conclusion about
  the control's configuration: `enabled`, `disabled`, `configured`,
  `not-configured`, `partially-configured`, `unavailable`, `inaccessible`,
  `unknown`. Each control's specification pins which subset of this closed set
  it can produce and the evidence rule for each value.
- **Policy Expectation** — what is required of the target: an explicit
  repository or repository-class requirement, an inherited organization
  expectation where observable, or `no-expectation-defined`. Expectations are
  committed policy artifacts or observed platform configuration — never
  inferred universal standards.
- **Conformance** — `conforming`, `non-conforming`, `indeterminate`,
  `not-applicable`. Computable only when the lower planes are determinate;
  on any indeterminacy it degrades to `indeterminate`. Derivation never
  guesses.

**Governing principle: "Enabled properly" is a conformance conclusion derived
from evidence and policy, never a raw GitHub boolean.**

**Evidence rules.** Every conclusion on every plane cites the retained
collected evidence it derives from. Absence of evidence is never evidence of
disablement — like ADR-0002's absence, disablement is a positive finding
requiring affirmative evidence. Zero alerts are never proof that a control is
enabled. Repository metadata flags (for example the `security_and_analysis`
object) are never sufficient proof of complete code-scanning coverage.
Alert-adjacent data may be collected only where strictly required to establish
configuration or operational state; alert, secret, vulnerability, and malware
finding inventory is outside this decision's scope.

**Composite evidence.** A Security Control may require multiple evidence
sources. Code scanning is the designated composite case: default-setup state,
advanced-workflow presence and staleness, external SARIF or third-party upload
configuration where observable, intended branch and event coverage,
supported-language coverage, and organization security-configuration
inheritance. Each control is realized through one or more resource descriptors
under ADR-0004; the first multi-source control triggers ADR-0004's deferred
multi-request combination-semantics decision at its slice, not before.
Organization-level security configuration is a first-class evidence source and
control in its own right — organization-scoped, never forced into
repository-only concepts (evaluated with the Observation Target Model,
issue #26).

**Boundary.** Observation, Applicability, and Operational State are collector
scope — the observation side of ADR-0004's observation/governance boundary:
judgment-free, with identical GitHub facts producing identical states
regardless of organizational intent. Policy Expectation and Conformance are
governance evaluation — a distinct downstream layer that never alters
collected evidence or observational taxonomy states. This records the first
accepted architecture for the evaluation side that ADR-0004 anticipated; it
does not reopen ADR-0001's rejection of a governance product — evaluation
remains deterministic derivation over committed evidence and committed policy.

## Consequences

- Planning enumerates Security Controls as long-lived seams
  (`docs/planning/security-controls.md`); future slices select one or more
  controls as bounded slice candidates — never a monolithic "GHAS slice."
- Prerequisite decisions, each at its own gate: a policy-definition artifact
  class (none exists today) before any Policy Expectation or Conformance
  implementation; ADR-0004's combination semantics before any composite
  control; the Observation Target Model (issue #26) before organization-scoped
  controls.
- *Deferred:* the policy artifact class; risk scoring, compliance scoring, and
  any finding inventory — outside authorized scope unless a future decision
  phase authorizes them.
- *Rejected:* modeling enablement as a raw boolean; conflating Operational
  State with Conformance; inferring enablement from alert data or metadata
  flags alone.
