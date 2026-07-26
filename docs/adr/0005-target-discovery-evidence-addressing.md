# Canonical target discovery and evidence addressing

**Status:** accepted

One rationale unifies this decision: **canonical repository identity governs
target selection, evidence addressing, and structural reconciliation.** Fan-out
targets derive deterministically from the current run's raw repository-inventory
page sequence, processed in page order and item source order. An inventory item
is an eligible target only when it occurs on a shape-valid page and carries a
positive integer repository ID (boolean values excluded) and a structurally
valid `owner/name` repository identity; missing or malformed target identity is
never repaired, inferred, or synthesized. Eligibility is evaluated before
deduplication — an earlier malformed occurrence of an ID never suppresses a
later eligible occurrence — then eligible candidates deduplicate by repository
ID, first eligible occurrence in source order winning. Descriptor-specific
required inputs are evaluated only after target eligibility: an eligible
repository missing a required input (for example `default_branch`) remains in
the discovered set, receives no request and no fabricated artifact for that
descriptor, and derives `unknown`. Collection planning and offline rederivation
share one canonical discovery rule, proven equivalent by fixture. Ineligible
items keep their existing inventory-projection semantics, are never fan-out
targets, and carry no descriptor taxonomy state.

**Addressing.** Evidence envelopes carry authoritative observed identity;
filesystem paths are scanner-defined storage addresses and are not evidence of
GitHub facts. Repository evidence lives under
`repos/<repository-id>[-<name-annotation>]/`: the ID is the addressing key and
structural consistency check; the optional annotation derives from the GitHub
`name` field (never `full_name`), is non-evidentiary, and is included verbatim
only when it satisfies the scanner's deliberately conservative annotation-safety
rule — otherwise omitted, never normalized, escaped, replaced, truncated,
hashed, or repaired. Annotation eligibility never affects target eligibility or
any observed state. Paths may be examined for storage addressing and structural
validation, but never used as the authoritative source of an observed GitHub
fact. Every per-resource projection carries a coverage qualification (basis,
inventory state, eligible-target count) reusing the accepted inventory
completeness vocabulary; coverage describes the target set's limits and never
converts descriptor states.

## Consequences

- More than one directory claiming one repository ID, or a path ID disagreeing
  with the enclosed envelope's repository ID, is a **structural evidence
  conflict**: derivation selects no winner, silently deduplicates nothing, uses
  no path text to override envelope content, lets no affected evidence surface
  as an apparently valid observation, and reports the integrity gap
  deterministically.
- Git provides versioned byte preservation and history for committed evidence;
  the scanner remains responsible for validating the semantic and structural
  consistency of evidence it collects or rederives.
- Within-run addressing collisions are structurally impossible for eligible
  targets (ID deduplication).
- *Rejected:* name-keyed directories (collisions, reserved device names);
  sanitization maps (identity repair by another name); entity-aggregated
  observed documents absent an approved requirement.
