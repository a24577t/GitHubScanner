Review Discipline

This is the repository's authoritative Review Discipline methodology. A participant acting as reviewer or quality gate follows it. It is engine-neutral: any capable engine — or a human — assigned the review function applies it.

Review evidence — primary sources

Independent reviews are grounded in inspectable repository artifacts. The required primary evidence is the relevant repository state under review — the pull-request diff, the changed files, or the equivalent committed artifacts — inspected directly.

An implementation report or summary is supporting context only. It may orient a review, but it is never authoritative evidence of what was implemented, and a final quality-gate PASS must not be issued from an implementation summary alone.

If the repository artifacts are unavailable, the review remains pending rather than being inferred from the report.

A focused re-review may inspect only the changed artifact and the previously recorded finding, rather than repeating the whole review, provided no unrelated change has entered the change set under review.

Every finding must be classified as one of the following:

1. Repository Inconsistency (Must Fix)

The finding identifies a contradiction or inconsistency between authoritative project artifacts.

Every Repository Inconsistency must:

cite the authoritative artifact(s);
quote or summarize the conflicting statements;
explain the inconsistency objectively;
avoid proposing a preferred solution as though it were required.
2. Architecture Proposal

The reviewer recommends changing the architecture or design.

Architecture Proposals must be clearly identified as recommendations.

They are not defects unless they contradict an authoritative artifact.

3. Implementation Recommendation

The reviewer recommends an implementation approach, simplification, optimization, or engineering practice.

Implementation Recommendations are suggestions, not repository defects.

4. Editorial Improvement

The reviewer recommends improving clarity, wording, organization, or documentation.

Editorial Improvements are optional unless they conceal a Repository Inconsistency.

Evidence First

Whenever possible:

Cite the authoritative artifact.
Explain the observed inconsistency.
Clearly separate facts from recommendations.

Do not present a preferred solution as though it is mandated by the repository unless an authoritative artifact explicitly requires it.