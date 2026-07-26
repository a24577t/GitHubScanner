# Repository Resource Observation Model

**Status:** accepted

Repository-scoped configuration is observed under a **Repository Resource
Observation Model**: every observed GitHub resource is described by a **resource
descriptor** — a declarative statement of what is observed, not merely endpoint
metadata. A descriptor represents one coherently scoped observed resource holding
exactly one taxonomy state and one observed-state projection; it may evolve to
comprise one or more API requests while remaining a single observed resource.
Slice 2 realizes each descriptor with exactly one request (an object GET or one
paginated listing drain); the rule combining multi-request outcomes into one
state is designed when the first multi-request descriptor is introduced, not
before. Orchestration is a single generic fan-out interpreting descriptors;
taxonomy classification, evidence generation, derivation, and reporting are
generic and resource-independent, parameterized only by descriptor content. The
current implementation of the model is a static, in-code declarative resource
table — implementation data governed under the model, not the model itself.

**Observation/governance boundary.** Resource descriptors address GitHub
resources and record observed facts using GitHub-domain vocabulary. Descriptor
targeting and resource addressing may derive from authoritative execution scope,
scanner configuration, and observed GitHub facts; they must not derive from
expected compliance outcomes, policy requirements, exception status, severity,
or other governance judgments. The observed layer records no requirements,
expectations, compliance conclusions, or policy interpretations; identical
GitHub facts produce identical observed states regardless of organizational
intent or approved exceptions. Standards, applicability, waivers, exclusions,
and other relief artifacts belong to governance evaluation: they may change the
governance disposition of an observation, but never the collected evidence or
its observational taxonomy state.

## Consequences

- Adding an observed resource touches only its descriptor, its projection,
  tests, and fixtures; orchestration, taxonomy, evidence generation, derivation,
  and reporting remain unchanged and resource-independent.
- Every descriptor carries an explicit resource-semantics statement claiming
  exactly what it observes and nothing more.
- *Deferred:* hierarchical organization of descriptors (for example Security,
  Actions, Governance) is intentionally permitted without changing orchestration
  semantics; reopened only when a slice concretely requires grouping.
- *Deferred:* multi-request combination semantics; reopened when the first
  concrete multi-request descriptor (designated candidate: per-ruleset detail)
  is specified against a real requirement.
- *Rejected:* plugin frameworks, runtime discovery, dependency injection, and
  dynamic loading — descriptors are reviewed in-code data; and any bespoke
  governance engine (per ADR-0001).
