# Project Release

## Purpose

An intentional repository release is being prepared. Your responsibility is to determine whether the repository is ready for release and to produce a **Release Plan** the human architect executes.

This prompt is **evaluation-only**: it determines the release type, verifies the applicable prerequisites and repository consistency, and produces recommendations plus the human release steps. It never creates tags, publishes releases, or modifies repository artifacts.

A release governs the **repository-wide Repository Version** — the latest release tag. Repository Version is distinct from the Architecture Version and the Architecture Baseline, which evolve separately; a release does not change either.

## Release Type

Determine the release type first — it decides which prerequisites apply. A release may originate from:

- a gated project-phase milestone;
- an approved-specification milestone;
- an architecture-refinement milestone;
- a methodology milestone;
- an implementation milestone;
- a maintenance or correction release.

Verify only the prerequisites applicable to the determined type. Do not invent prerequisites the release type does not require.

## Preconditions

**Every release requires:**

- internally consistent repository state;
- an intentional, human-authorized release scope.

**Type-conditional prerequisites — verify only when applicable:**

- **Phase completion is claimed** → a successful Phase Gate Review (PASS or PASS WITH CONDITIONS) must exist as a repository artifact.
- **The milestone requires a new Architecture Baseline** → Baseline Publication must already be complete.
- **Neither applies** → do not require a Phase Gate or a Baseline.

If an applicable prerequisite is missing, **stop and report** why the repository is not ready for release review.

## Inputs

Review only what the release type requires. Prefer **consuming other transitions' proving artifacts** over re-deriving their conclusions.

- `.ai/architecture/STATUS.md` (the Status Artifact)
- The applicable prerequisite record(s): the Phase Gate Review Record and/or the published Architecture Baseline, only when the type requires them
- Existing Git tags and GitHub Releases
- `RELEASES.md` / `CHANGELOG.md` (if present)
- A Repository Continuity Artifact (if present)

Do not repeat a full bootstrap or a full architecture-gate review; consume their results.

## Responsibilities

### 1. Establish release scope and authorization

Confirm the release type, the intended scope, and that a human has authorized this release.

### 2. Verify applicable prerequisite records

For the determined type only, confirm the required prerequisite artifacts exist and are consistent (for example, the Phase Gate Review Record for a phase-completion release; the published Baseline for a baseline-milestone release). Do not re-run those reviews.

### 3. Select the Repository Version

Recommend the next Semantic Version, explaining major / minor / patch in terms of **repository evolution**, not architectural evolution. Repository Version is repository-wide; it does not distinguish product from methodology streams.

### 4. Repository Continuity Artifact check (conditional)

If a Repository Continuity Artifact exists, verify whether unresolved transient work affects release readiness. Do **not** require one for a clean, stable, fully committed release, and do **not** summarize committed repository history into it — committed history is authoritative repository content, not a continuity aid.

### 5. Tag and GitHub Release recommendation

Recommend an annotated Git tag whose name matches the selected Repository Version; verify it does not already exist and identify its target commit. When appropriate, recommend a GitHub Release with title, summary, highlights, known limitations, and next milestone.

### 6. Methodology Observations

Record process improvements discovered during the release. These are not release-readiness findings and do not affect the decision.

## Release Postcondition

**The release is incomplete until the Git tag, the release metadata, and the Status Artifact all agree on the released Repository Version.** Do not declare the repository bootstrap-safe until all three agree. A tag created before the Status Artifact is reconciled leaves the release **transient and incomplete** until the reconciliation commit is merged.

## Release Plan

This prompt is evaluation-only, so it produces the plan; the human architect executes it. Produce the plan with explicit human repository updates — never leave Status reconciliation implicit. The order below **prevents** drift rather than detecting it later:

1. Approve the release version and scope.
2. Update the Status Artifact to the intended Repository Version and next objective.
3. Commit and merge that release-state update.
4. Create the annotated tag from the intended commit.
5. Publish the GitHub Release.
6. Verify that the tag, the release metadata, and the Status Artifact agree — the repository is bootstrap-safe.

If the project's Git practice creates the tag before the Status update (for example, tagging at merge), the release remains **transient and incomplete** until the reconciliation commit is merged. Do not declare bootstrap-safe until all three agree.

## Release Readiness

Determine one of: **Ready for Release**, **Ready with Conditions**, **Not Ready**. Explain why.

## Deliverables

- Release type and authorization
- Applicable prerequisite verification
- Selected Repository Version
- Tag and GitHub Release recommendation
- Repository Continuity Artifact disposition (if any)
- Release Plan (human execution order)
- Remaining risks and known limitations
- Next milestone

## Constraints

Do not:

- modify repository files;
- create Git tags;
- publish releases;
- reconcile the Status Artifact yourself — produce the plan; the human executes it;
- redesign architecture, create ADRs, or recommend new architectural decisions;
- re-run a full bootstrap or architecture-gate review.

This prompt verifies release readiness and produces a release plan. It does not evolve the project and does not mutate repository state.

## Success Criteria

A successful review:

- correctly determines the release type and verifies only its applicable prerequisites;
- selects a coherent repository-wide Repository Version;
- produces a release plan whose execution leaves the tag, release metadata, and Status Artifact in agreement;
- leaves no ambiguity about whether the repository is bootstrap-safe after the release.
