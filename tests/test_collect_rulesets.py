"""Rulesets collection at the fan-out seam (Slice 2 T8; V11 + V37 drain half).

The engine is descriptor-generic (ADR-0004), so these tests pin its behavior
through the shipped repository-rulesets descriptor: the raw request contract
(V11), the drained page layout, the cap breach (V37's collection half), and
the two T5-carried test-plan notes (multi-descriptor coexistence on a
missing-input repository; list-only envelope fields absent from object
envelopes).
"""
import json
import tempfile
import unittest
from pathlib import Path

from fake_github import response, serve
from test_collect import META_OK, ORG_OK, RUN_ID, USER_OK, collect, repo
from test_collect_fanout import (
    PROTECTION_BODY, org_script, protection_path, raw_files, rulesets_path,
)
from test_resources_rulesets import RULESET_ITEM


def load(out, repo_dir, name):
    return json.loads(
        (out / "evidence" / "raw" / RUN_ID / "repos" / repo_dir / name)
        .read_text(encoding="utf-8"))


class RequestContract(unittest.TestCase):
    def test_v11_raw_url_proves_parent_exclusion_and_page_size(self):
        script = org_script(
            [repo(1)],
            **{protection_path(1): [response(200, PROTECTION_BODY)],
               rulesets_path(1): [response(200, [RULESET_ITEM])]},
        )
        with serve(script) as (base, recorder), \
                tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = collect(base, out, ["--run-id", RUN_ID])
            self.assertEqual(result.returncode, 0, result.stderr)
            requested = [r["path"] for r in recorder.requests
                         if r["path"].startswith(rulesets_path(1))]
            self.assertEqual(requested, [
                rulesets_path(1) + "?includes_parents=false&per_page=100&page=1",
            ])
            # The raw envelope URL is the durable V11 evidence.
            record = load(out, "1-repo-1", "repository-rulesets.page-1.json")
            self.assertIn("includes_parents=false", record["envelope"]["url"])
            self.assertEqual(json.loads(record["body_text"]), [RULESET_ITEM])

    def test_list_envelope_fields_present_and_branch_absent(self):
        script = org_script(
            [repo(1)],
            **{protection_path(1): [response(200, PROTECTION_BODY)],
               rulesets_path(1): [response(200, [])]},
        )
        with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(collect(base, out, ["--run-id", RUN_ID]).returncode, 0)
            envelope = load(out, "1-repo-1",
                            "repository-rulesets.page-1.json")["envelope"]
            self.assertEqual(envelope["repo"],
                             {"id": 1, "full_name": "acme/repo-1"})
            self.assertEqual(envelope["resource"], "repository-rulesets")
            self.assertEqual(envelope["page"], 1)
            self.assertEqual(envelope["item_count"], 0)
            # The rulesets descriptor consumes no per-repository input, so
            # the input-derived branch extension never appears.
            self.assertNotIn("branch", envelope)
            self.assertNotIn("incomplete", envelope)

    def test_object_envelope_carries_no_list_only_fields(self):
        # T5-carried note: the object-shaped protection envelope from the
        # same run asserts the list-only fields are absent.
        script = org_script(
            [repo(1)],
            **{protection_path(1): [response(200, PROTECTION_BODY)],
               rulesets_path(1): [response(200, [])]},
        )
        with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(collect(base, out, ["--run-id", RUN_ID]).returncode, 0)
            envelope = load(out, "1-repo-1",
                            "default-branch-protection.json")["envelope"]
            for list_only in ("page", "item_count", "incomplete"):
                self.assertNotIn(list_only, envelope)
            self.assertEqual(envelope["branch"], "main")


class PaginatedRulesetsDrain(unittest.TestCase):
    def _paged_script(self):
        first = response(200, [RULESET_ITEM],
                         {"Link": '<http://x/p?page=2>; rel="next"'})
        second = response(200, [{**RULESET_ITEM, "id": 7}])
        return org_script(
            [repo(1)],
            **{protection_path(1): [response(200, PROTECTION_BODY)],
               rulesets_path(1): [first, second]},
        )

    def test_multi_page_drain_persists_every_page(self):
        with serve(self._paged_script()) as (base, _), \
                tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(collect(base, out, ["--run-id", RUN_ID]).returncode, 0)
            one = load(out, "1-repo-1", "repository-rulesets.page-1.json")
            two = load(out, "1-repo-1", "repository-rulesets.page-2.json")
            self.assertEqual(one["envelope"]["page"], 1)
            self.assertEqual(two["envelope"]["page"], 2)
            self.assertNotIn("incomplete", one["envelope"])
            self.assertNotIn("incomplete", two["envelope"])

    def test_v37_cap_breach_marks_incomplete_never_truncates_silently(self):
        with serve(self._paged_script()) as (base, recorder), \
                tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = collect(base, out, ["--run-id", RUN_ID, "--max-pages", "1"])
            self.assertEqual(result.returncode, 0, result.stderr)
            one = load(out, "1-repo-1", "repository-rulesets.page-1.json")
            self.assertIs(one["envelope"]["incomplete"], True)
            self.assertEqual(one["envelope"]["item_count"], 1)
            files = raw_files(out)
            self.assertNotIn("repos/1-repo-1/repository-rulesets.page-2.json",
                             files)
            requested = [r["path"] for r in recorder.requests
                         if r["path"].startswith(rulesets_path(1))]
            self.assertEqual(len(requested), 1)


class DescriptorCoexistence(unittest.TestCase):
    def test_missing_input_repo_still_gets_its_rulesets_drain(self):
        # T5-carried note: dedicated coexistence coverage - on a repository
        # missing one descriptor's required input, the other descriptor
        # still observes it, and fully-usable repositories get both.
        no_branch = {k: v for k, v in repo(1).items() if k != "default_branch"}
        script = org_script(
            [no_branch, repo(2)],
            **{protection_path(2): [response(200, PROTECTION_BODY)],
               rulesets_path(1): [response(200, [RULESET_ITEM])],
               rulesets_path(2): [response(200, [])]},
        )
        with serve(script) as (base, recorder), \
                tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = collect(base, out, ["--run-id", RUN_ID])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                [f for f in raw_files(out) if f.startswith("repos/")],
                ["repos/1-repo-1/repository-rulesets.page-1.json",
                 "repos/2-repo-2/default-branch-protection.json",
                 "repos/2-repo-2/repository-rulesets.page-1.json"])
            self.assertEqual(
                [r["path"] for r in recorder.requests
                 if "/branches/" in r["path"]],
                [protection_path(2)])


if __name__ == "__main__":
    unittest.main()
