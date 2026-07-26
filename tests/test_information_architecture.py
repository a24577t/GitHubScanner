"""IA verification per .ai/README.md: history is evidence, never a dependency.

Enforced rules, exactly as recorded:
- Nothing inside a history legacy/ snapshot is ever a link target for any
  current document, repository-wide.
- Role bootstraps load no history artifact at all.
- Informational links into a history package from other current documents are
  permitted (they are not dependencies on legacy content).
- Current .ai relative links resolve (migration reference-integrity evidence).
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AI_ROOT = REPO_ROOT / ".ai"
HISTORY = AI_ROOT / "repository" / "history"

LINK = re.compile(r"\]\(([^)\s]+)\)")

# Referenced but created lazily by charter; never a broken-link failure.
LAZY_TARGETS = {"observations.md"}


def markdown_files(root, exclude_history=True):
    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        if exclude_history and HISTORY in path.parents:
            continue
        yield path


def resolved_links(path):
    """Yield (raw target, resolved path) for every relative markdown link."""
    for target in LINK.findall(path.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean = target.split("#")[0]
        if clean:
            yield target, (path.parent / clean).resolve()


def is_within(candidate, ancestor):
    return candidate == ancestor or ancestor in candidate.parents


def is_legacy_snapshot_path(resolved):
    if not is_within(resolved, HISTORY):
        return False
    relative = resolved.relative_to(HISTORY)
    return "legacy" in relative.parts


class HistoryExclusion(unittest.TestCase):
    def test_no_current_document_links_into_legacy_snapshots(self):
        # Repository-wide: legacy content is evidence, never a link target.
        for path in markdown_files(REPO_ROOT):
            for target, resolved in resolved_links(path):
                self.assertFalse(
                    is_legacy_snapshot_path(resolved),
                    f"{path} uses a legacy snapshot as a link target: {target}",
                )

    def test_bootstraps_do_not_load_history(self):
        # Stricter than the general rule: bootstraps load no history at all.
        for manifest in (
            AI_ROOT / "collaborator" / "bootstrap.md",
            AI_ROOT / "repository-owner" / "bootstrap.md",
        ):
            for target, resolved in resolved_links(manifest):
                self.assertFalse(
                    is_within(resolved, HISTORY),
                    f"{manifest} must not load history: {target}",
                )


class LinkIntegrity(unittest.TestCase):
    def test_current_ai_relative_links_resolve(self):
        for path in markdown_files(AI_ROOT):
            for target, resolved in resolved_links(path):
                if Path(target.split("#")[0]).name in LAZY_TARGETS:
                    continue
                self.assertTrue(
                    resolved.exists(),
                    f"{path} has a dangling link: {target}",
                )


if __name__ == "__main__":
    unittest.main()
