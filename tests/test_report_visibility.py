"""Report aggregates and wait visibility (Slice 2 T7; V30 at the report seam).

The report renders derived facts only: the execution block verbatim from the
summary, and per-descriptor aggregates whose size is bounded by the closed
state/reason vocabularies — never by the estate (failures excepted).
"""
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path

from collector import resources
from collector.derive import run_summary
from collector.report import build_report, render_markdown
from collector.serialize import canonical_dumps
from test_derive_resources import (
    PROTECTION_BODY, RUN, page_record, protection, record, repo_item,
    write_tree,
)
from test_derive_rulesets import rs_file


def summary_for(repos, resources):
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        write_tree(out, [page_record(repos)], resources)
        return run_summary(out, RUN)


def collected_estate(count):
    repos = [repo_item(i) for i in range(1, count + 1)]
    artifacts = [protection(f"{i}-repo-{i}", 200, PROTECTION_BODY,
                            repo={"id": i, "full_name": f"acme/repo-{i}"},
                            resource="default-branch-protection")
                 for i in range(1, count + 1)]
    return summary_for(repos, artifacts)


class ReportAggregates(unittest.TestCase):
    def test_execution_block_travels_verbatim_from_summary(self):
        summary = collected_estate(2)
        report = build_report("https://api.example", "acme", RUN, "op",
                              summary)
        self.assertEqual(report["execution"], summary["execution"])

    def test_resource_aggregates_are_bounded_no_raw_wait_lists(self):
        waited = record(200, PROTECTION_BODY,
                        repo={"id": 1, "full_name": "acme/repo-1"},
                        resource="default-branch-protection")
        waited["envelope"]["waits_seconds"] = [1, 30]
        summary = summary_for([repo_item(1)],
                              [("1-repo-1", "default-branch-protection.json",
                                waited)])
        report = build_report("https://api.example", "acme", RUN, "op",
                              summary)
        block = report["resources"]["default-branch-protection"]
        self.assertEqual(sorted(block), ["reason_counts", "state",
                                         "state_counts", "waits"])
        self.assertEqual(block["state"], "collected")
        self.assertEqual(block["waits"], {"count": 2, "total_seconds": 31})

    def test_rate_limit_block_is_size_bounded(self):
        # S10 run-1 finding: the Slice-1 raw wait list grew with estate
        # pages; T7's size-independence AC bounds it to aggregate figures.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            page = page_record([repo_item(1)])
            page["envelope"]["waits_seconds"] = [2, 3]
            write_tree(out, [page])
            report = build_report("https://api.example", "acme", RUN, "op",
                                  run_summary(out, RUN))
        self.assertEqual(report["rate_limit"],
                         {"occurrences": 2, "total_seconds": 5})

    def test_report_size_independent_of_estate_size(self):
        small = build_report("https://api.example", "acme", RUN, "op",
                             collected_estate(2))
        large = build_report("https://api.example", "acme", RUN, "op",
                             collected_estate(12))
        self.assertEqual(canonical_dumps(small).count("\n"),
                         canonical_dumps(large).count("\n"))
        self.assertEqual(render_markdown(small).count("\n"),
                         render_markdown(large).count("\n"))


class RulesetsAggregates(unittest.TestCase):
    def test_rulesets_report_row_is_bounded_and_rendered(self):
        # T8 report effect (V06/V07): the second descriptor surfaces as one
        # bounded aggregate row per format, never per-ruleset content.
        summary = summary_for([repo_item(1)], [rs_file(1, 1, [])])
        report = build_report("https://api.example", "acme", RUN, "op",
                              summary)
        block = report["resources"]["repository-rulesets"]
        self.assertEqual(sorted(block), ["reason_counts", "state",
                                         "state_counts", "waits"])
        self.assertEqual(block["state"], "collected")
        self.assertEqual(block["state_counts"], {"collected": 1})
        markdown = render_markdown(report)
        self.assertIn("| repository-rulesets | collected |", markdown)


class SecurityAnalysisAdditivity(unittest.TestCase):
    def test_pre_t1_report_rows_byte_identical_new_row_additive(self):
        # The T1 preservation AC's report half (T8 precedent): the same tree
        # reported under the pre-T1 table and the shipped table keeps every
        # pre-existing per-resource aggregate byte-identical; the extension
        # is one additive row. The planned-request execution counts follow
        # the descriptor table by design - the disclosed T8-precedent
        # consequence pinned in test_summary_execution.py.
        def report_with(table):
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / "out"
                write_tree(out, [page_record([repo_item(1)])],
                           [protection("1-repo-1", 200, PROTECTION_BODY,
                                       repo={"id": 1,
                                             "full_name": "acme/repo-1"},
                                       resource="default-branch-protection"),
                            rs_file(1, 1, [])])
                with mock.patch.object(resources, "DESCRIPTORS", table):
                    return build_report("https://api.example", "acme", RUN,
                                        "op", run_summary(out, RUN))

        before = report_with((resources.DEFAULT_BRANCH_PROTECTION,
                              resources.REPOSITORY_RULESETS))
        after = report_with(resources.DESCRIPTORS)
        for name in ("default-branch-protection", "repository-rulesets"):
            self.assertEqual(canonical_dumps(before["resources"][name]),
                             canonical_dumps(after["resources"][name]), name)
        self.assertEqual(sorted(after["resources"]),
                         ["default-branch-protection", "repository-rulesets",
                          "security-and-analysis"])
        self.assertNotIn("security-and-analysis", before["resources"])
        after_markdown = render_markdown(after)
        for line in render_markdown(before).splitlines():
            if line.startswith(("| default-branch-protection",
                                "| repository-rulesets")):
                self.assertIn(line, after_markdown)


class MarkdownWaitVisibility(unittest.TestCase):
    def test_markdown_renders_execution_and_aggregates(self):
        summary = collected_estate(1)
        markdown = render_markdown(
            build_report("https://api.example", "acme", RUN, "op", summary))
        self.assertIn("## Per-resource aggregates", markdown)
        self.assertIn("| default-branch-protection | collected |", markdown)
        self.assertIn("## Execution", markdown)
        self.assertIn("planned", markdown.lower())
        self.assertIn("| primary-park | 0 | 0 | 0 |", markdown)
        self.assertIn("| retry-after | 0 | 0 | 0 |", markdown)
        self.assertIn("| retry | 0 | 0 | 0 |", markdown)
        self.assertIn("Terminations: none.", markdown)
        self.assertIn("Capture window: 2026-01-01T00:00:00Z", markdown)

    def test_markdown_renders_terminations_when_present(self):
        marked = record(429, {"message": "limit"},
                        headers={"retry-after": "9999"},
                        repo={"id": 1, "full_name": "acme/repo-1"},
                        resource="default-branch-protection",
                        termination_reason="retry-after-exceeds-maximum")
        summary = summary_for([repo_item(1)],
                              [("1-repo-1", "default-branch-protection.json",
                                marked)])
        markdown = render_markdown(
            build_report("https://api.example", "acme", RUN, "op", summary))
        self.assertIn("retry-after-exceeds-maximum: 1", markdown)


if __name__ == "__main__":
    unittest.main()
