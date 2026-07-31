"""Descriptor-generic paginated drain at the fan-out seam (Slice 2 T5).

The descriptor table is the architecture's ratified extension point
(ADR-0004: adding a descriptor touches only the table, tests, fixtures — T8's
architectural AC). These tests drive the engine's object_array branch through
that seam with a synthetic descriptor; rulesets themselves are T8 (V37).
"""
import json
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path

from collector import controls, resources
from collector import collect as collect_module
from fake_github import response, serve
from test_collect import META_OK, ORG_OK, RUN_ID, USER_OK, repo

FAKE_LISTING = {
    "name": "fake-listing",
    "path_template": "/repos/{full_name}/fake-listing",
    "shape": "object_array",
    "required_inputs": (),
    "absence_message": None,
    "projection": (("count", ("count", "items")),),
}


def drain_script(listing_responses):
    return {
        "/user": [USER_OK], "/meta": [META_OK], "/orgs/acme": [ORG_OK],
        "/orgs/acme/repos": [response(200, [repo(1)])],
        "/repos/acme/repo-1/fake-listing": listing_responses,
    }


def run(base, out, max_pages=100):
    # The synthetic-descriptor world has no controls: the control table is
    # emptied alongside the replaced descriptor table (T3's loud pairing
    # invariant — a control may only reference a derived descriptor).
    with mock.patch.object(resources, "DESCRIPTORS",
                           (resources.DEFAULT_BRANCH_PROTECTION, FAKE_LISTING)), \
            mock.patch.object(controls, "CONTROLS", ()):
        return collect_module.run_collect(
            base, "acme", out, "tok-inproc", run_id=RUN_ID, max_pages=max_pages)


def load(out, name):
    return json.loads(
        (out / "evidence" / "raw" / RUN_ID / "repos" / "1-repo-1" / name)
        .read_text(encoding="utf-8"))


class PaginatedDrain(unittest.TestCase):
    def test_synthetic_descriptor_is_table_legal(self):
        resources.validate_table(
            (resources.DEFAULT_BRANCH_PROTECTION, FAKE_LISTING))

    def test_object_array_descriptor_drains_pages_with_page_fields(self):
        pages = [
            response(200, [{"id": 1}, {"id": 2}],
                     {"Link": '<http://x/p?page=2>; rel="next"'}),
            response(200, [{"id": 3}]),
        ]
        with serve(drain_script(pages)) as (base, _), \
                tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(run(base, out), 0)
            one = load(out, "fake-listing.page-1.json")
            two = load(out, "fake-listing.page-2.json")
            self.assertEqual(one["envelope"]["page"], 1)
            self.assertEqual(one["envelope"]["item_count"], 2)
            self.assertEqual(two["envelope"]["page"], 2)
            self.assertEqual(two["envelope"]["item_count"], 1)
            for envelope in (one["envelope"], two["envelope"]):
                self.assertEqual(envelope["repo"],
                                 {"id": 1, "full_name": "acme/repo-1"})
                self.assertEqual(envelope["resource"], "fake-listing")
                self.assertNotIn("incomplete", envelope)
                self.assertNotIn("branch", envelope)
            # Descriptors ran in table order: protection artifact coexists.
            self.assertEqual(
                load(out, "default-branch-protection.json")["envelope"]
                ["resource"], "default-branch-protection")

    def test_max_pages_caps_the_drain_and_marks_incomplete_never_truncates_silently(self):
        pages = [
            response(200, [{"id": 1}],
                     {"Link": '<http://x/p?page=2>; rel="next"'}),
            response(200, [{"id": 2}]),
        ]
        with serve(drain_script(pages)) as (base, _), \
                tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(run(base, out, max_pages=1), 0)
            one = load(out, "fake-listing.page-1.json")
            self.assertIs(one["envelope"]["incomplete"], True)
            self.assertEqual(one["envelope"]["item_count"], 1)
            raw_repo = out / "evidence" / "raw" / RUN_ID / "repos" / "1-repo-1"
            self.assertFalse((raw_repo / "fake-listing.page-2.json").exists())


if __name__ == "__main__":
    unittest.main()
