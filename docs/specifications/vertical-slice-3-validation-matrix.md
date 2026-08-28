# Vertical Slice 3 — Normative Validation Matrix

**Status:** approved (companion to
[vertical-slice-3-secret-scanning-control-family.md](vertical-slice-3-secret-scanning-control-family.md);
accepted at ⟦G-Accept⟧ via the Slice 3 acceptance PR).

Row IDs continue the global sequence from Slice 2 (V01–V40) so every row ID
is unique across slices. Field key per row: **Mode** live | offline | both |
cond (conditionally live-verifiable). **Cred** S = standing PAT,
R = restricted PAT, F = fake. **Expected** = response class → evidence
taxonomy state · reason, and/or control-plane state · reason. **St** M =
mandatory, C = conditional (recorded gap if not provisionable, V10/V12
mechanics), O = optional (grill-directed partition extension; never blocks
acceptance). Matrix-row acceptance occurs only at the T6 validation run. A
live run never validates offline-only rows.

| ID | Rule / capability | Mode | Fixture / input | Cred | Expected | Projection / report effect | St |
|----|-------------------|------|-----------------|------|----------|----------------------------|----|
| V41 | Descriptor collected with real values | both | all fixtures | S | 200 object → collected · collected | visibility + both status fields projected | M |
| V42 | Dedicated-request response surface pin | live | all fixtures | S | `security_and_analysis` fields visible under standing credential recorded | Pins the unpinned single-repo GET surface before any row acceptance | M |
| V43 | Affirmative disabled pin | live | archived-repo, empty-repo, Hello-World | S | status `"disabled"` → disabled · affirmative-status-disabled | disabled counts; never from absence | M |
| V44 | Affirmative enabled pin — **provisioning-time obligation** | live | standard-repo, unprotected-repo (SS enabled by owner) | S | status `"enabled"` → enabled · affirmative-status-enabled | Enablement operation itself proves public/Free-plan availability (applicability rule 2's platform fact) | M |
| V45 | Push-protection enabled + coupled transition | live | standard-repo (SS+PP enabled by owner) | S | PP status `"enabled"` → enabled; provisioning records that PP enable required SS enabled | Chain evidence; PP applicable · affirmative-enabled-status | M |
| V46 | Push protection disabled while SS enabled | live | unprotected-repo | S | PP `"disabled"` → disabled · affirmative-status-disabled; PP applicable · secret-scanning-available | Distinguishes the pair; chain via availability | M |
| V47 | Public-visibility applicability rule | both | all public fixtures | S | visibility `"public"` → applicable · public-repository-visibility (where rule 1 not hit) | applicability counts | M |
| V48 | Restricted-credential field visibility | cond | standard-repo | R | fields absent/partial in collected body → unknown · status-undetermined; never disabled | Gap recorded if R not provisionable (V10 successor) | C |
| V49 | Private-repository plan gating | cond | private fixture (if provisioned) | S | Pinned by run → applicability-unknown · visibility-not-public; field behavior recorded | Pins the #2/#3-adjacent boundary; gap recorded if not provisioned | C |
| V50 | `security_and_analysis` absent in collected body | offline | fake | F | → unknown · status-undetermined | Absence never derives disabled (ADR-0008) | M |
| V51 | Unrecognized / non-string status value | offline | fake (e.g. `"paused"`, `5`) | F | → unknown · status-undetermined; never coerced | Drift visible in reason counts | M |
| V52 | Evidence inaccessible (401/403) | offline | fake | F | evidence inaccessible · authorization-denied → operational inaccessible · evidence-inaccessible; applicability-unknown · evidence-unavailable | Both planes degrade; no fabrication | M |
| V53 | Raw evidence absent | offline | tree without artifact | F | evidence unknown · raw-evidence-absent → unknown · evidence-unavailable; applicability-unknown · evidence-unavailable | Recorded-failure trace honored | M |
| V54 | 404 on dedicated request | offline | fake | F | → inaccessible · absence-rule-unmatched-404 (no absence anchor) → inaccessible · evidence-inaccessible | Never absent; never disabled | M |
| V55 | Chain unknown when SS not established | offline | fake (SS evidence unusable) | F | PP → applicability-unknown · secret-scanning-availability-unknown; PP operational state still from own field | Planes independent | M |
| V56 | PP self-evidencing applicability | offline | fake (PP `"enabled"`, visibility undetermined) | F | PP → applicable · affirmative-enabled-status | Asymmetric rule 1 precedence over chain | M |
| V57 | Control-document shape, order, coverage | offline | fake tree | F | `{run_id, state, coverage, repositories}`; entries ascend by id; citations `{resource, state, reason}` | Byte-identical offline rederivation | M |
| V58 | Evidence-plane rollup only | offline | mixed-state fake tree | F | Top-level `state` = listing rule over cited evidence states | No operational/applicability rollup anywhere | M |
| V59 | Report control aggregates | offline | rows V50–V56 evidence | F | Closed-vocabulary distribution counts only | Estate-independent; type-deep tolerant | M |
| V60 | Slice-1/2-tree compatibility | offline | committed prior run trees | F | Control entries derive evidence-unavailable; existing observed docs byte-stable | Historical derivability preserved | M |
| V61 | Inventory vs dedicated cross-source coherence | offline | same-run listing + dedicated evidence | F | Field values agree, or divergence surfaced as review evidence, never auto-resolved | The Q2 duplication converted into evidence | O |
| V62 | Envelope/header shapes and token secrecy | live | all new artifacts | S | Allowlisted headers only; no token material | Standing integrity row | M |

**Condition mechanics (grill condition 5):** every C row not provisioned at
T6 becomes an explicit recorded validation gap in
`docs/validation/validation-environment.md` with its offline analog carrying
the scenario, exactly as V10/V12 were recorded. The 2026-08-28 trial-route
expiry affects no row: no row consumes a GHAS surface.

**Provisioning-failure rule (owner-directed factual correction):** V44/V45's
enablement obligations are mandatory; if either operation proves impossible
at provisioning, that is a blocking architectural finding (applicability
rule 2 loses its platform fact) routed to the owner for decision — it must
not degrade into a recorded gap.

**Editorial clarification (Slice 3 consolidation, 2026-08-28; append-only):**
V52's Expected column states the applicability outcome for the
visibility-kind control (`applicability-unknown` · `evidence-unavailable`,
secret-scanning rule 5). For the chained control the specification's chain
rule 3 governs the same evidence class:
`applicability-unknown` · `secret-scanning-availability-unknown`. The row's
state-level claim — both planes degrade, no fabrication — holds for both
controls; only the deterministic reason literal differs, and both outcomes
are pinned in the offline suite.
