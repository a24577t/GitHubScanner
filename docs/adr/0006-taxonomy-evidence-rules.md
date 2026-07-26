# Taxonomy evidence rules

**Status:** accepted

Runtime taxonomy claims require retained evidence. Descriptor metadata defines
how affirmative runtime evidence is interpreted, but is never itself evidence: a
static property must never establish that an endpoint or platform capability is
unsupported. For per-repository descriptors an ambiguous 404 must not derive to
`unsupported`; when a response neither affirmatively establishes resource
absence nor permits successful collection, derivation takes the accepted safe
uncertainty state (currently `inaccessible`) without claiming a cause the
evidence does not establish, and never emits a platform-support conclusion from
an individual repository response. `unsupported` is an affirmative
platform-capability conclusion: per-repository resources may derive to it only
under a future approved evidence rule that is affirmative, deterministic from
retained evidence, non-contradictory within the run, compatible with ADR-0003,
and validated against the environment it certifies. The run-wide "no 2xx
responses" consistency check is explicitly not preselected as sufficient —
uniform authorization failure produces the same evidence. Accepted Slice 1
`/meta` behavior is preserved in its established scope and is not authorization
to classify repository-scoped endpoints the same way.

**Affirmative absence** is descriptor-anchored: derive `absent` only when the
response has the expected status, a shape-valid JSON body, a string `message`
field, and an exact case-sensitive match to the absence message pinned by live
fixture evidence — validation evidence, not a permanent GitHub API contract. On
any failed condition: do not infer absence; derive the safe uncertainty state;
retain the complete raw response; and preserve a deterministic reason
distinguishing an unrecognized absence response from other `inaccessible`
outcomes. The degradation direction is fixed: recognized affirmative absence →
`absent`; unrecognized or drifted ambiguous responses → `inaccessible`; never
`inaccessible` → `absent` through permissive matching. Matching is never
loosened (substring checks, case folding, broad patterns, expanded message sets)
merely to preserve historical state counts — a changed response is first
validated through new evidence and reviewed as a taxonomy-classification change.
Emptiness of a successfully collected listing is observed data (`collected`,
count zero), never `absent`.

## Consequences

- Derived entries retain deterministic classification reasons; aggregate report
  counts can reveal drift but are never the sole detection mechanism.
- The mirror may under-claim knowledge; it never fabricates resource absence or
  platform non-support (ADR-0002 preserved and sharpened).
- *Deferred:* any per-repository `unsupported` mechanism, until a confirmed
  supported-platform requirement exists (wayfinder tickets #2/#3).
