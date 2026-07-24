# GHAS SKU and pricing mechanics post-unbundling (Code Security / Secret Protection)

Research for issue [#8](https://github.com/a24577t/GitHubScanner/issues/8). All facts checked **2026-07-24** against primary sources (docs.github.com, github.blog changelog).

## 1. "Unique active committer" billing metric

- A committer is **active** when "one of their commits has been pushed to the repository within the last 90 days, regardless of when it was originally authored" — a **rolling 90-day window keyed to push recency**, not author date. ([docs: About billing for GitHub Advanced Security products](https://docs.github.com/en/billing/concepts/product-billing/github-advanced-security), checked 2026-07-24)
- **Deduplication:** usage is "measured across the whole organization or enterprise to ensure that each member uses one license regardless of how many repositories or organizations the user contributes to" — one license per person enterprise-wide, per product. (same source, 2026-07-24)
- **Bots:** "GitHub App bots are ignored" for license counting; ordinary machine/user accounts can still consume a license. (same source, 2026-07-24)
- Each product (Code Security, Secret Protection) meters its own active-committer count; a person committing to repos with both products enabled consumes one license of each.

## 2. Independent SKUs per repository

- Post-unbundling, "users can enable GitHub Secret Protection or GitHub Code Security independently" — a repo can have Code Security without Secret Protection and vice versa; they are separate SKUs with separate meters. ([docs: About billing for GitHub Advanced Security](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-advanced-security/about-billing-for-github-advanced-security) and the [2025-03-04 changelog](https://github.blog/changelog/2025-03-04-introducing-github-secret-protection-and-github-code-security/), checked 2026-07-24)
- Customers previously on contractual GHAS limited to secret scanning "will be able to optionally choose to transition with only Secret Protection enabled". ([2025-04-01 Enterprise changelog](https://github.blog/changelog/2025-04-01-github-secret-protection-and-github-code-security-for-github-enterprise/), checked 2026-07-24)

## 3. Availability and version gates (GHEC vs GHES)

- **GA date:** standalone products announced 2025-03-04, available **2025-04-01**, including to **GitHub Team** plan orgs for the first time (metered/pay-as-you-go only for Team). ([changelog 2025-03-04](https://github.blog/changelog/2025-03-04-introducing-github-secret-protection-and-github-code-security/); [changelog 2025-04-01 (Team)](https://github.blog/changelog/2025-04-01-github-advanced-security-is-here-for-github-team-organizations/), checked 2026-07-24)
- **GHEC:** both products available with metered billing (or enterprise volume/subscription licensing); existing subscription customers transition at renewal, pay-as-you-go customers anytime. ([Enterprise changelog 2025-04-01](https://github.blog/changelog/2025-04-01-github-secret-protection-and-github-code-security-for-github-enterprise/), checked 2026-07-24)
- **GHES:** standalone SKUs available **starting GHES 3.17**; metered billing on GHES requires **GitHub Connect** (metered GHAS billing existed from GHES 3.13+; pre-3.17 servers use the bundled/volume model). (same changelog + [billing docs](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-advanced-security/about-billing-for-github-advanced-security), checked 2026-07-24)

## 4. Unlicensed repos in security overview

- Security overview's Advanced Security data (code scanning, secret scanning) "is shown for organizations and enterprises that use GitHub Secret Protection, GitHub Code Security, or GitHub Advanced Security"; **Dependabot data is available for all repos** regardless of license. ([docs: About security overview](https://docs.github.com/en/enterprise-cloud@latest/code-security/security-overview/about-security-overview), checked 2026-07-24)
- The docs caution that absence of alerts may simply mean "the feature may not be enabled for that repository" — unlicensed/unenabled repos surface in coverage/enablement views as not-enabled rather than being flagged as unlicensed; the coverage view docs make no explicit licensed/unlicensed distinction. ([about-security-overview](https://docs.github.com/en/enterprise-cloud@latest/code-security/security-overview/about-security-overview), [assessing adoption](https://docs.github.com/en/enterprise-cloud@latest/code-security/security-overview/assessing-adoption-code-security), checked 2026-07-24)

## 5. List pricing (verified)

- **GitHub Secret Protection: $19 per active committer per month.**
- **GitHub Code Security: $30 per active committer per month.**
- Source: [changelog 2025-03-04 "Introducing GitHub Secret Protection and GitHub Code Security"](https://github.blog/changelog/2025-03-04-introducing-github-secret-protection-and-github-code-security/), checked 2026-07-24. The billing docs themselves defer pricing to GitHub's pricing pages.

## Caveats

- Billing docs do not spell out git author-vs-committer email mechanics beyond "commits pushed"; counting is based on commit authors of pushed commits within the 90-day window.
- Security overview docs (checked 2026-07-24) do not describe a dedicated "unlicensed" repo state; treat non-enabled as the observable proxy.
