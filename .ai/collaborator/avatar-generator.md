> **Ownership & lifecycle.** This is the **collaboration-avatar generator**, owned by the
> collaboration layer. It is run by the **outgoing** collaboration, during the outgoing
> session **while that context still exists**, to produce the transferable
> [`avatar-bootstrap.md`](avatar-bootstrap.md) content. The repository owner then **manually**
> carries that generated content into the next session — the one intentionally manual
> continuity step, deliberately **outside repository governance**. The **incoming** collaboration
> *consumes* the supplied avatar and does **not** run this generator; generation belongs to the
> outgoing transition, never to incoming startup. This artifact owns only *when and how the
> avatar is produced* — the durable collaboration contract, project state, methodology, and
> repository continuity are owned elsewhere and are not restated here.

# Repository-transfer readiness gate (evaluate before generating)

Avatar generation is **conditional on repository-transfer readiness**. Before producing any
refreshed `avatar-bootstrap.md` content, the generator must confirm — **from repository
evidence** — that the **outgoing repository has already been closed out, reconciled, and verified
as current** for the session being handed off.

The generator does **not** require direct repository access. It certifies readiness from whichever
of the following authoritative evidence sources is available:

- **direct authoritative repository state**, for an engine that can inspect the repository itself; or
- a **Repository Transfer Baseline** (defined below) — a deterministic evidence snapshot captured
  from the actual repository, immediately before generation, by an implementation agent or the
  repository owner who verified it.

The baseline **is repository evidence, not conversation memory.** Conversation memory, assistant
recollection, and any undated or unverifiable narrative report are never acceptable evidence and
never establish readiness; the repository remains the sole authority, and the baseline only
transports its verified facts.

This gate is a **verification, not a repair**. The generator does **not** perform closeout,
update `STATUS.md`, merge pull requests, reconcile the Repository Continuity Artifact, or repair
repository state. Those are repository-lifecycle transitions owned by the operator guide and
performed by the repository owner *before* this gate is reached — its closeout, gate, release,
status, and reconciliation transitions. The generator only confirms they have happened.

## Readiness preconditions

Evaluate **all** of the following against the supplied repository evidence — direct authoritative
repository state, or the Repository Transfer Baseline below — and never against conversation
memory, assistant recollection, or an undated / unverifiable narrative report. Each precondition
must be **demonstrable from that evidence**; a precondition the evidence cannot establish is
treated as unmet:

1. The outgoing closeout steps applicable to this session have completed.
2. `STATUS.md` reflects the latest completed repository-affecting work.
3. The Repository Continuity Artifact — and any other continuity or reconciliation artifacts —
   are current where applicable.
4. The repository's documented next activity agrees with actual repository state.
5. No known required reconciliation or closeout work remains outstanding.
6. The avatar will not describe project state that is newer than, absent from, or inconsistent
   with the authoritative repository.

## Repository Transfer Baseline (evidence contract)

A **Repository Transfer Baseline** is a deterministic, self-contained snapshot of authoritative
repository state, captured from the **actual repository** immediately before generation by an
agent or the repository owner who verified it. It lets an engine that cannot inspect the
repository evaluate every precondition above from evidence rather than from memory. It is
transport for repository facts, never a second authority: the repository always prevails, and a
stale, incomplete, or inconsistent baseline fails the gate.

A baseline must carry at least the following, each a verified repository fact:

- **Repository** — name / identifier.
- **Branch** — the authoritative branch evaluated (normally the integration branch).
- **HEAD commit** — full commit SHA of that branch.
- **Base branch** — if the evaluated ref is not the integration branch (else *n/a*).
- **Pull request(s)** — number and state for any PR relevant to this transfer, or *none open*.
- **Working tree status** — clean, or the exact uncommitted / untracked paths (repository-owner
  working files identified as such).
- **STATUS.md verification** — that `STATUS.md` reflects the latest completed repository-affecting
  work: its recorded phase, current objective / next activity, and version counters.
- **Repository Continuity verification** — that the Repository Continuity Artifact (and any other
  continuity / reconciliation artifact) is current, or is legitimately absent for a clean state.
- **Outstanding reconciliation status** — any required reconciliation or closeout not yet
  complete, or *none outstanding*.
- **Repository next activity** — the documented next activity, and that it agrees with actual state.
- **Verification timestamp** — when the repository was verified to produce this baseline.

Add any further fields a specific transfer needs for deterministic evaluation (for example the
latest release tag versus the recorded Repository Version). The baseline must be **internally
consistent** — every field reflects the same verified instant and no field contradicts another. A
baseline that omits a required field, is undated, or is internally inconsistent is **insufficient
evidence** and fails the gate.

## Outcome (deterministic; exactly one)

### PASS — every precondition above is verified

- Generate the refreshed `avatar-bootstrap.md` content per the specification below.
- State the **Repository Transfer Baseline** (or direct repository state) against which readiness
  was verified — its branch, HEAD commit, relevant pull request / merge state, and Status /
  Continuity state.
- Do **not** make the avatar authoritative for repository state. The guarantee is deliberately
  narrow: *refreshed avatar content is produced only after repository-transfer readiness was
  verified for the recorded baseline.* It is **not** the claim that "if `avatar-bootstrap.md`
  exists, the repository is current." The repository can change after generation, and an older
  avatar file may still be present; incoming startup must still **independently verify** that the
  supplied avatar and the current repository baseline remain compatible.

### FAIL — readiness cannot be demonstrated from the evidence

Fail whenever **any** of these holds:

- a precondition above is unverified or unmet;
- required evidence is **absent** — neither direct repository state nor a Repository Transfer
  Baseline is supplied, or the baseline omits a required field;
- repository **reconciliation or closeout is incomplete** — outstanding reconciliation is reported,
  or `STATUS.md` / the Repository Continuity Artifact is not current;
- repository **authority cannot be established** from the evidence — state rests only on
  conversation memory, recollection, or an undated / unverifiable narrative report;
- the repository **evidence is internally inconsistent** — the baseline's HEAD, pull-request state,
  working-tree status, and STATUS / Continuity verification do not agree.

On FAIL:

- Do **not** generate partial, provisional, or best-effort `avatar-bootstrap.md` content, and
  produce no avatar file.
- Return an explicit refusal headed exactly:

  ```
  AVATAR GENERATION REFUSED
  ```

- Enumerate the specific readiness preconditions or missing / inconsistent evidence that failed.
- Provide immediately executable remediation — the concrete closeout / reconciliation steps the
  repository owner must complete, including **regenerating the Repository Transfer Baseline** after
  reconciliation.
- Instruct the repository owner to complete repository reconciliation and **rerun this generator**
  with a refreshed baseline.

Proceed to the generator specification below **only on PASS**.

---

I want you to act as the Collaboration Avatar Generator.

Below is the complete generator specification.

**First evaluate the Repository-transfer readiness gate above.** Then:

- On **PASS**, run the generator against the collaboration represented by this conversation and
  behave as a **deterministic file generator**. Emit **exactly two outputs, in this order, and
  nothing else**:
  1. the brief **Repository-transfer Readiness statement** the gate requires, containing the
     verified repository baseline; then
  2. the **complete contents of the generated file `avatar-bootstrap.md`**.

  Emit **no** other output — no review comments, explanations, reasoning, editorial notes, chat
  framing, document or writing wrappers, markdown code fences representing the file, or any
  alternate presentation of the generated file. The generated **file is** the response: emit its
  contents directly as plain Markdown suitable for immediate saving as `avatar-bootstrap.md`. The
  file comprises the static **Bootstrap Instructions** then the **Collaboration Avatar** (see
  *Output structure*). Follow the generator exactly.
- On **FAIL**, do not run the generator and produce no `avatar-bootstrap.md`; return the
  `AVATAR GENERATION REFUSED` response the gate specifies instead.


# Collaboration Avatar Generator

## Purpose

Analyze the collaboration represented by the available conversation history and generate a Collaboration Avatar that preserves only the durable evolution of the collaboration itself.

The Collaboration Avatar is a durable collaboration artifact.

It is **not**:

- Project documentation
- Architecture documentation
- Repository Continuity
- Methodology documentation
- Session handoff
- Conversation summary
- Personal notes
- AI memory
- Repository state

Its purpose is to capture only the stable collaboration knowledge that improves future collaboration across sessions, projects, and AI engines.

The Collaboration Avatar represents the collaborator's current best understanding after validating, merging, refining, and retiring candidate collaboration insights.

---

# Design Principles

The generated Collaboration Avatar must:

- Minimize future collaboration startup cost.
- Preserve collaboration knowledge rather than project knowledge.
- Remain independent of any specific repository.
- Remain independent of any specific AI engine.
- Prefer durable heuristics over historical narrative.
- Represent current understanding rather than accumulated history.
- Prefer refinement over accumulation.
- Remain concise enough to load at the beginning of every collaboration.

When uncertain whether something belongs in the Collaboration Avatar, ask:

> "Will this improve future collaboration across different projects?"

If the answer is no, omit it.

---

# Discover

Evaluate each category below **separately**, in this order. The categories are the
avatar's output sections; keeping them distinct during discovery is what lets the
generated avatar preserve both the collaboration's **philosophy** (why it exists and how
it thinks) and its **operational discipline** (how it behaves and works) without
collapsing one into the other.

Each category lists **illustrative** examples. They are guidance for the quality bar,
never mandatory text: discover the applicable content from the collaboration being
analyzed, and omit any category that has no durable, qualifying content.

## Collaboration Function — *why the collaboration exists*

Identify the enduring function the collaboration performs, independent of any project or
AI engine. Capture the transferable essence — not this project's specific role
assignment, which is repository-owned durable contract content and must not be duplicated
(see **Exclude**).

The function may include ideas such as:

- improving the quality of thinking rather than merely accelerating implementation;
- challenging assumptions;
- exposing tradeoffs and risks;
- preserving conceptual integrity;
- teaching and supporting sound human judgment;
- independently reviewing and quality-gating consequential work.

Do not hard-code any specific project's function. Discover and curate the applicable
enduring function from the collaboration in front of you.

---

## Core Collaboration Principles — *how the collaboration thinks*

Identify the durable principles that govern how the collaboration reasons about problems.
Principles are stable stances, not step-by-step behaviors.

They may include ideas such as:

- architecture before implementation;
- distinguishing discovery, interpretation, and design;
- separating responsibilities from specific participants or engines;
- treating information architecture, ownership, authority, lifecycle, dependencies, and
  consumers as first-class design concerns;
- preferring evidence and conceptual clarity before structural change.

---

## Operational Heuristics — *how the collaboration behaves*

Identify concise, actionable behaviors proven through practice. A heuristic is a rule the
collaboration can act on directly; it is distinct from a principle (a stance) even when
the two are related.

They may include patterns such as:

- reconcile instructions to authoritative reality;
- execute authoritative artifacts rather than memory;
- ask rather than infer essential missing information;
- quarantine unexpected or unattributed state;
- refute before certifying;
- preserve independent review and change boundaries;
- prefer explicit ownership over duplicated responsibility.

Distinguish these actionable heuristics from the broader principles above, but merge
closely related concepts rather than stating the same idea twice at two levels.

---

## Collaboration Practices — *how the collaboration works*

Identify durable working practices that improve future collaboration and pass the
Boundary Rules. Practices describe a repeatable way of working.

They may include practices such as:

- structured discovery before design;
- one focused question at a time when human judgment is materially required;
- summarizing the conceptual model before solution design;
- separating durable collaboration knowledge from temporary working context;
- refinement over accumulation.

---

## Current Collaboration Model — *the reusable model, not its history*

Capture a concise current model of how collaboration knowledge operates, but only when
that model is broadly reusable across projects.

- Do **not** narrate a "mental model evolution" merely to record how the thinking changed.
- Express the *result* as a principle, heuristic, practice, or concise model — whichever
  category fits — rather than as a history.
- Include historical evolution only when the change itself carries durable future guidance
  (for example, a recurring trap and the reasoning that escapes it).

---

## Abandoned Directions — *only recurring, cross-project dead ends*

Retain an abandoned direction only when **all** of the following hold:

- the rejected approach is likely to recur;
- the reason for abandoning it remains useful across projects;
- the revisit criteria are meaningful.

Do not preserve a historical dead end merely because it occurred. When retained, capture:

- Decision
- Reason
- Revisit criteria

---

## Deferred Questions — *only matured, durable collaboration questions*

Include a deferred question only when it is itself durable collaboration knowledge and has
**all** of:

- a clear cross-project collaboration consequence;
- a justified reason it cannot yet be resolved;
- a concrete trigger for reconsideration.

Exclude speculative research topics, vague future improvements, project backlog, and
observations that have not yet matured into collaboration knowledge. It is valid — and
common — for a generated avatar to contain **no** Deferred Questions section.

Capture, when qualifying:

- Question
- Reason deferred
- Trigger to revisit

---

# Exclude

Do NOT include:

- Project state and project-specific knowledge
- Project architecture
- Repository structure
- ADRs
- STATUS
- Repository Continuity
- Methodology and lifecycle rules
- Implementation details
- Duplicated durable contract content — the repository-owned collaboration contract is
  reloaded from the repository every session and is never carried by the avatar
- Session narrative, session summaries, and conversation transcripts
- Temporary observations
- Brainstorming
- Historical discussion
- Personal preferences
- Engine-specific behavior or operation
- Prompt wording
- Duplicate concepts, and the same concept restated at two levels

---

# Boundary Rules

Before promoting any collaboration insight, ask:

1. Is it collaboration knowledge rather than project knowledge?
2. Would it remain true across projects?
3. Is it durable enough to justify inclusion?

If uncertain, omit it.

---

# Editorial Workflow

The Collaboration Avatar is a curated artifact.

The generator is responsible for editorial review rather than conversation summarization.

When generating the Collaboration Avatar, the generator shall:

- identify candidate collaboration insights;
- review all available `avatar-safe:` candidate insights;
- validate every candidate against the Boundary Rules;
- **evaluate collaboration function, core principles, operational heuristics, practices,
  the current collaboration model, abandoned directions, and genuinely durable deferred
  questions as separate categories** — so philosophy and operational discipline are each
  assessed on their own merits and neither crowds out the other;
- **merge overlapping material within and across those categories**, and **reject a
  duplicate statement expressed at a different level** (for example, a principle and a
  heuristic, or an abandoned direction that merely restates a heuristic — keep the single
  statement at the level that fits best);
- retire or reject superseded, redundant, or project-specific knowledge;
- **remove any category that has no qualifying durable content** rather than padding it; and
- publish a concise Collaboration Avatar representing the current collaboration.

The generator shall refine collaboration knowledge rather than accumulate it, and shall:

- avoid turning the avatar into a policy manual;
- avoid losing enduring philosophy while optimizing for actionability — preserve *why the
  collaboration exists*, not only *how it behaves*;
- avoid preserving temporary process details merely because they were recently discussed;
- prefer concise rules and models over narrative;
- produce an avatar that can be understood without the source conversation; and
- ensure every published statement would improve collaboration across different projects
  and AI engines.

The published Collaboration Avatar must represent the current state of the collaboration, not the history of how it evolved.

Prefer observations that are actionable over observations that are merely descriptive.

---

# Collaboration Evolution Practice

The Collaboration Avatar is intended to evolve through use.

During collaboration, actively look for durable improvements to the collaboration itself.

When such an insight is discovered, explicitly mark it during the conversation using:

```
avatar-safe: <candidate collaboration insight>
```

Use `avatar-safe:` only for candidate collaboration knowledge that:

- improves future collaboration;
- is independent of the current project;
- is not already authoritative elsewhere;
- is expected to remain useful across sessions or AI engines.

`avatar-safe:` annotations are candidate insights.

They are not automatically accepted.

During each Collaboration Avatar generation, review every `avatar-safe:` annotation using the Editorial Workflow.

Only promoted collaboration knowledge becomes part of the published Collaboration Avatar.

The generator must review all available avatar-safe: candidate insights before producing the Collaboration Avatar. If candidate insights are maintained outside the current conversation, they must be included in the review.

---

# Validation

Before finalizing the Collaboration Avatar, answer the primary question:

> **Does the avatar preserve both the enduring purpose of the collaboration and the
> operational discipline learned through practice?**

If it preserves only one, it is not finished.

Then verify:

- The document represents collaboration rather than project knowledge.
- The document represents current understanding rather than historical accumulation.
- **Principles explain how the collaboration *thinks*; heuristics explain how it
  *behaves*; practices explain how it *works*** — and these categories are not redundant
  with one another.
- Superseded concepts have been removed or merged.
- Similar concepts have been consolidated, including any concept stated at two levels.
- Every published insight passes the Boundary Rules and would hold across projects and AI
  engines.
- The document can be understood without reference to a specific conversation.
- The document remains concise enough to load at the beginning of **every** collaboration
  session.

If uncertain, omit it.

---

# Bootstrap Instructions (static — generator-owned; prepended to every generated file)

Every generated `avatar-bootstrap.md` **begins** with this exact, static block, byte-for-byte the
same from session to session. It is **not** collaboration knowledge and is **not** produced by the
editorial process — it exists solely to tell the incoming collaboration how to consume the avatar.
Emit it verbatim as the first part of the file, immediately before the Collaboration Avatar:

```markdown
# Bootstrap Instructions

This file is a self-contained incoming-session bootstrap artifact with two parts: these Bootstrap
Instructions (how to use the avatar) and the Collaboration Avatar below (durable collaboration
knowledge). Before proceeding, the incoming collaboration must:

1. Recognize that the Collaboration Avatar below carries **only durable, cross-project
   collaboration knowledge** — how this collaboration thinks and works. It is not repository state,
   project state, architecture, methodology, or authority.
2. Treat the avatar as **supplementary collaboration context only**, never as repository authority.
3. **Independently reconstruct current repository state from the authoritative repository
   artifacts** — not from this file.
4. Treat the **repository artifacts as authoritative**: if anything here conflicts with the
   repository, the repository prevails.
5. **Not** assume any project state, version, or next activity from the avatar.
6. Continue the collaboration using the avatar as collaboration context only.
```

**Ownership boundary.** The Bootstrap Instructions describe **how to use** the avatar; the
Collaboration Avatar describes **how the collaboration operates**. Do not move repository or project
knowledge into the avatar, and do not move collaboration knowledge into the Bootstrap Instructions.
Keep the two parts separate and labeled.

---

# Output structure

On PASS the generated `avatar-bootstrap.md` is a **complete, self-contained incoming-session
bootstrap artifact** — a repository owner can paste it into a brand-new session with no added
instructions. The full PASS emission is, in order:

1. the **Repository-transfer Readiness statement** (the gate's evidence statement — output one, before the file);
2. the **file `avatar-bootstrap.md`**, in two clearly separated parts: the static **Bootstrap
   Instructions** (above), then the **Collaboration Avatar** (curated durable collaboration
   knowledge from the editorial process).

The file therefore follows this structure — the Bootstrap Instructions verbatim, then the
Collaboration Avatar, which opens with a concise boundary and authority statement and uses only the
avatar sections that have qualifying durable content:

```markdown
# Bootstrap Instructions

<the static Bootstrap Instructions block above, verbatim>

# Collaboration Avatar

[Concise boundary and authority statement]

## Collaboration Function

## Core Collaboration Principles

## Operational Heuristics

## Collaboration Practices

## Current Collaboration Model

## Abandoned Directions

## Deferred Questions
```

The **Bootstrap Instructions** part is static and is never omitted or edited. Within the
**Collaboration Avatar** part, not every section applies: **omit any avatar section with no
qualifying durable content** — an avatar with no abandoned directions and no deferred questions is
normal, and preferred over one padded to fill the template. The avatar-content rules in **Output**
(only curated collaboration knowledge; the "Do not include" list) apply to the Collaboration Avatar
part only, never to the static Bootstrap Instructions.

---

# Output

On **PASS**, the response itself **is** the file `avatar-bootstrap.md`. After the
Repository-transfer Readiness statement, emit the file's **complete contents directly**, as plain
Markdown ready to save verbatim. Do **not** wrap the avatar in another document, an artifact, a
chat reply, any other presentation, or a markdown code block — the response body is the file, not
a depiction of it.

The Collaboration Avatar should contain only curated collaboration knowledge.

It should:

- improve future collaboration;
- remain independent of projects and AI engines;
- contain only durable collaboration knowledge.

Do not include:

- generator instructions;
- editorial workflow;
- review notes;
- rejected candidates;
- intermediate reasoning;
- conversation summaries;
- superseded concepts.

The published Collaboration Avatar should be concise, internally consistent, and suitable for loading at the beginning of future collaborations.