"""Automated IA verification: history exclusion and .ai link integrity."""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AI_ROOT = REPO_ROOT / ".ai"
HISTORY = AI_ROOT / "repository" / "history"

# Markdown inline link targets: [text](target)
LINK = re.compile(r"\]\(([^)\s]+)\)")

# Referenced but created lazily by charter; never a broken-link failure.
LAZY_TARGETS = {"observations.md"}


def current_ai_markdown():
    """Every current .ai markdown file — history packages are not current."""
    for path in AI_ROOT.rglob("*.md"):
        if HISTORY in path.parents:
            continue
        yield path


class HistoryExclusion(unittest.TestCase):
    def test_no_current_document_links_into_history_or_legacy(self):
        for path in current_ai_markdown():
            for target in LINK.findall(path.read_text(encoding="utf-8")):
                self.assertNotIn(
                    "legacy/", target,
                    f"{path} links into a legacy snapshot: {target}",
                )
                self.assertNotIn(
                    "history/ia-", target,
                    f"{path} depends on a history package: {target}",
                )

    def test_bootstraps_do_not_load_history(self):
        for name in (
            AI_ROOT / "collaborator" / "bootstrap.md",
            AI_ROOT / "repository-owner" / "bootstrap.md",
        ):
            text = name.read_text(encoding="utf-8")
            for target in LINK.findall(text):
                self.assertNotIn("history", target,
                                 f"{name} must not load history/")


class LinkIntegrity(unittest.TestCase):
    def test_relative_links_resolve(self):
        for path in current_ai_markdown():
            for target in LINK.findall(path.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                clean = target.split("#")[0]
                if not clean or Path(clean).name in LAZY_TARGETS:
                    continue
                resolved = (path.parent / clean).resolve()
                self.assertTrue(
                    resolved.exists(),
                    f"{path} has a dangling link: {target}",
                )


if __name__ == "__main__":
    unittest.main()
