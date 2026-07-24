# CircleCI Support for GitHub Enterprise Cloud EMU and Data Residency (.ghe.com)

**Research question:** What is CircleCI's current, documented support for GitHub Enterprise Cloud with EMU (Enterprise Managed Users), and specifically for data-residency (.ghe.com) tenants?

**Date checked:** 2026-07-24 (all facts below verified against the cited primary sources on this date)

**Sources policy:** Primary sources only — circleci.com/docs, CircleCI Changelog/roadmap, CircleCI Support Center, CircleCI Discuss (staff posts noted), and docs.github.com / github.blog changelog.

---

## TL;DR

- CircleCI Cloud documents support for **GitHub.com, GitHub Enterprise Cloud, and GitHub Enterprise Server** via two integration paths: the legacy **GitHub OAuth app** and the newer **GitHub App**. GitHub Enterprise Server support is an add-on **in Preview** (invite-only). [1][2][3]
- **There is no first-class, documented CircleCI support for GitHub Enterprise Cloud with data residency (.ghe.com) tenants.** CircleCI docs, changelog, and roadmap contain no mention of data residency, ghe.com, or EMU. A December 2025 Discuss thread reports the CircleCI GitHub App setup is "hardcoded to go to github.com" and cannot target a `.ghe.com` tenant; it has no staff resolution. [1][6][7]
- EMU on **github.com** is not explicitly documented as supported or unsupported by CircleCI; community threads exist about EMU migration and connection problems, without a documented first-class EMU path.
- GitHub-side: data-residency tenants **require EMU**, have **no GitHub Marketplace**, and require integrators to call the tenant's dedicated `api.SUBDOMAIN.ghe.com` endpoints — so a github.com-registered OAuth app/GitHub App like CircleCI's cannot work against a .ghe.com tenant without vendor-side changes. [8][9][10]

---

## 1. CircleCI integration paths: GitHub OAuth app vs GitHub App

Checked 2026-07-24.

### GitHub OAuth app (legacy path)
Per CircleCI's "Users, organizations, and integrations guide" [2]:
- Built-in integration for `github`-type CircleCI organizations; "created automatically when you authorize CircleCI to access your GitHub account via OAuth app"; projects imported automatically from the VCS.
- Checkout via SSH deploy keys.
- Pipelines limited to zero or one OAuth trigger; no custom/cross-repo config pipelines.

### GitHub App (newer path)
Per [2] and the VCS integration overview [3]:
- Available as an add-on for both `circleci` and `github` type organizations; installed manually into a GitHub organization.
- HTTPS-based checkout, no SSH/deploy keys; "the GitHub App only asks for fine-grained permissions" and "uses short-lived tokens"; repo-level access selection.
- Exclusive features: multiple pipelines per project each with its own YAML, config stored in a different repo than the code, cross-repo triggers, custom webhook (non-VCS) triggers, scheduled/API triggers. Fine-grained permissions and custom config paths are listed only for GitHub App / GitHub App Server pipeline types [3].
- GitHub Checks is listed for GitHub App and GitHub OAuth pipeline types [3].

### Coexistence and constraints
- Since October 2024, the GitHub App can be installed **alongside** an existing OAuth-app organization ("can co-exist side-by-side in the same organization"), announced by CircleCI staff (sebastian-lerner) on Discuss, 2024-10-23 [4]; also documented in docs [5] and Support Center articles [11][12].
- Staff-listed limitations of the coexistence mode include: GitHub App pipelines not schedulable (at time of post), `CIRCLE_REPOSITORY_URL` returning the project name for GitHub App pipelines, contexts restricted to GitHub security groups erroring with custom webhooks, explicit `git clone` needing extra SSH configuration, and per-user authorization of the GitHub App [4].

### Supported GitHub hosts
- CircleCI Cloud lists integrations with **GitHub.com, GitHub Enterprise Cloud, and GitHub Enterprise Server** [2][3].
- **GitHub Enterprise Server** support on CircleCI Cloud is "currently in Preview" — invite-only, hands-on onboarding by CircleCI, with self-serve onboarding, GitHub Checks, Chunk, and Rollbacks not yet available during Preview (CircleCI product roadmap / changelog) [1][13].

## 2. First-class support for .ghe.com data-residency hosts

Checked 2026-07-24.

- **None found.** CircleCI's docs [2][3], product roadmap [1], and changelog [13] contain **no mention** of GitHub Enterprise Cloud with data residency, `.ghe.com` hosts, or EMU. The only enterprise-host work in flight is the GitHub Enterprise **Server** (self-hosted) Preview [1].
- A CircleCI Discuss thread (2025-12-19, "Unable to connect to github enterprise with enterprise managed users") reports that CircleCI cannot be connected to a `.ghe.com` EMU tenant: "The github app setup seems to be hardcoded to go to github.com." The user notes their GHE.com instance supports GitHub Apps but only via manual configuration (no Marketplace). **No CircleCI staff reply or resolution is visible in the thread** [6].
- Conclusion: as of 2026-07-24, connecting a data-residency tenant to CircleCI Cloud is not documented as possible; the observed behavior is that CircleCI's app registration targets github.com only.

## 3. Known EMU-related limitations on CircleCI

Checked 2026-07-24.

- CircleCI publishes **no dedicated EMU documentation** — no docs page or Support Center article specific to EMU was found; EMU appears only in community Discuss threads.
- Community-reported issues:
  - `.ghe.com` EMU tenants cannot connect at all (see section 2) [6].
  - Organizations migrating to EMU raise questions about preserving org identity and re-granting access for new EMU user accounts ("Changing orgs and moving to EMU, but keeping the name", Discuss) [7] — because EMU provisions **new** user accounts, prior CircleCI OAuth identities/permissions do not carry over automatically.
- GitHub-side constraints that bear on CircleCI usage with EMU (github.com-hosted EMU):
  - Managed user accounts "cannot create public content or collaborate outside your enterprise" [14].
  - Managed users cannot install standard GitHub Apps on their user accounts; org installs require org-owner rights; paid Marketplace apps require enterprise-owner rights [15].
  - EMU enterprises typically enforce IdP-driven auth and app-access policies, so CircleCI's OAuth app / GitHub App must be explicitly approved by enterprise/org owners.

## 4. CircleCI guidance and roadmap statements

Checked 2026-07-24.

- **Roadmap** [1]: GitHub Enterprise Server integration "currently in Preview," invite-only. No item for GHE Cloud data residency or EMU.
- **Changelog** [13]: entries cover the GHES add-on Preview and fixes (e.g., deploy-key links previously hardcoded to github.com now displaying GHES domains); nothing on .ghe.com/EMU.
- **Staff Discuss post** (2024-10-23) [4]: GitHub App functionality in OAuth orgs, with the limitations listed in section 1.
- **Support Center** [11][12][16][17]: articles on distinguishing OAuth vs GitHub App projects, best practices for running both, and OAuth connection how-tos — none address EMU or data residency.

## 5. GitHub-side background facts

Checked 2026-07-24.

- **EMU**: lets an enterprise "manage the lifecycle and authentication of your users on GitHub.com or GHE.com from an external identity management system, or IdP" (SCIM provisioning + SAML/OIDC SSO); accounts are isolated from the public community [14].
- **Data residency (GHE.com)**: enterprise hosted "on a dedicated subdomain of GHE.com" with a choice of storage region (EU, Australia, US, Japan); **Enterprise Managed Users is the only identity model** on GHE.com [8][9].
- **Third-party app constraints on GHE.com** [9]:
  - "GitHub Marketplace, as a means of searching for, purchasing, and installing apps and actions, is unavailable." Ecosystem apps can be installed from source repositories but "may require modification."
  - "Integrators with the REST and GraphQL APIs must send requests to your enterprise's dedicated URL on GHE.com" (e.g., `https://api.octocorp.ghe.com`) [8][9].
  - Tokens are tenant-scoped: a `GITHUB_TOKEN` on GHE.com does not grant access to GitHub.com resources [9].
  - Net effect: a CI vendor whose OAuth app/GitHub App is registered on github.com (as CircleCI's is) must add tenant-aware app registration and API routing before it can serve .ghe.com customers — consistent with the failure reported in [6].
- Data residency GA milestones (GitHub Changelog): US region generally available 2025-05-12 [10]; feature build-out continues (e.g., Codespaces public preview for data residency, 2026-01-29) [18].

---

## Sources

1. CircleCI Product roadmap — https://circleci.com/product-roadmap/
2. CircleCI Docs, Users, organizations, and integrations guide — https://circleci.com/docs/guides/permissions-authentication/users-organizations-and-integrations-guide/
3. CircleCI Docs, Version control systems, pipeline types, and feature support — https://circleci.com/docs/guides/integration/version-control-system-integration-overview/
4. CircleCI Discuss (staff), [Product Update] Using GitHub App functionality in a GitHub OAuth App organization — https://discuss.circleci.com/t/product-update-using-github-app-functionality-in-a-github-oauth-app-organization/52204
5. CircleCI Docs, Using the CircleCI GitHub App in an OAuth organization — https://circleci.com/docs/guides/integration/using-the-circleci-github-app-in-an-oauth-org/
6. CircleCI Discuss, Unable to connect to github enterprise with enterprise managed users — https://discuss.circleci.com/t/unable-to-connect-to-github-enterprise-with-enterprise-managed-users/54292
7. CircleCI Discuss, Changing orgs and moving to EMU, but keeping the name — https://discuss.circleci.com/t/changing-orgs-and-moving-to-emu-but-keeping-the-name/50729
8. GitHub Docs, About GitHub Enterprise Cloud with data residency — https://docs.github.com/en/enterprise-cloud@latest/admin/data-residency/about-github-enterprise-cloud-with-data-residency
9. GitHub Docs, Feature overview for GitHub Enterprise Cloud with data residency — https://docs.github.com/en/enterprise-cloud@latest/admin/data-residency/feature-overview-for-github-enterprise-cloud-with-data-residency
10. GitHub Changelog, GitHub Enterprise Cloud Data Residency in the US is generally available (2025-05-12) — https://github.blog/changelog/2025-05-12-github-enterprise-cloud-data-residency-in-the-us-is-generally-available/
11. CircleCI Support, Using GitHub App Functionality in a GitHub OAuth App Organization — https://support.circleci.com/hc/en-us/articles/36266044809243-Using-GitHub-App-Functionality-in-a-GitHub-OAuth-App-Organization
12. CircleCI Support, Best practices for using GitHub App functionality alongside the GitHub OAuth App — https://support.circleci.com/hc/en-us/articles/34843379697563-Best-practices-for-using-GitHub-App-functionality-alongside-the-GitHub-OAuth-App
13. CircleCI Changelog — https://circleci.com/changelog/index.html
14. GitHub Docs, About Enterprise Managed Users — https://docs.github.com/en/enterprise-cloud@latest/admin/managing-iam/understanding-iam-for-enterprises/about-enterprise-managed-users
15. GitHub Docs, Abilities and restrictions of managed user accounts — https://docs.github.com/en/enterprise-cloud@latest/admin/managing-iam/understanding-iam-for-enterprises/abilities-and-restrictions-of-managed-user-accounts
16. CircleCI Support, Is my project setup using GitHub OAuth or GitHub Apps? — https://support.circleci.com/hc/en-us/articles/20302893166363-Is-my-project-setup-using-GitHub-OAuth-or-GitHub-Apps
17. CircleCI Support, How to connect CircleCI using the GitHub OAuth Integration — https://support.circleci.com/hc/en-us/articles/25329740211227-How-to-connect-CircleCI-using-the-GitHub-OAuth-Integration
18. GitHub Changelog, Codespaces public preview for GitHub Enterprise with data residency (2026-01-29) — https://github.blog/changelog/2026-01-29-codespaces-is-now-in-public-preview-for-github-enterprise-with-data-residency/
