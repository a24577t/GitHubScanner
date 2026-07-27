"""Fan-out collection for repository resources (Slice 2 T5; V33 at this seam)."""
import json
import tempfile
import unittest
from pathlib import Path

from fake_github import response, serve
from test_collect import HAPPY_SCRIPT, META_OK, ORG_OK, RUN_ID, USER_OK, collect, repo

PROTECTION_BODY = {
    "enforce_admins": {"enabled": True},
    "required_pull_request_reviews": {"required_approving_review_count": 1},
}
ABSENCE_BODY = {"message": "Branch not protected"}


def protection_path(i, branch="main"):
    return f"/repos/acme/repo-{i}/branches/{branch}/protection"


def org_script(repos, **endpoints):
    return {
        "/user": [USER_OK], "/meta": [META_OK], "/orgs/acme": [ORG_OK],
        "/orgs/acme/repos": [response(200, repos)],
        **endpoints,
    }


def raw_files(out):
    raw = out / "evidence" / "raw" / RUN_ID
    return sorted(str(p.relative_to(raw)).replace("\\", "/")
                  for p in raw.rglob("*") if p.is_file())


class ScaffoldExactness(unittest.TestCase):
    def test_fanout_scaffold_is_exact_and_bodies_verbatim(self):
        script = org_script(
            [repo(2), repo(1)],
            **{protection_path(1): [response(200, PROTECTION_BODY)],
               protection_path(2): [response(404, ABSENCE_BODY)]},
        )
        with serve(script) as (base, recorder), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = collect(base, out, ["--run-id", RUN_ID])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(raw_files(out), [
                "meta.json", "org.json", "repos.page-1.json",
                "repos/1-repo-1/default-branch-protection.json",
                "repos/2-repo-2/default-branch-protection.json",
                "user.json",
            ])
            record = json.loads(
                (out / "evidence" / "raw" / RUN_ID / "repos" / "1-repo-1" /
                 "default-branch-protection.json").read_text(encoding="utf-8")
            )
            self.assertEqual(json.loads(record["body_text"]), PROTECTION_BODY)
            # A 404 absence candidate is partial evidence, persisted verbatim.
            absent = json.loads(
                (out / "evidence" / "raw" / RUN_ID / "repos" / "2-repo-2" /
                 "default-branch-protection.json").read_text(encoding="utf-8")
            )
            self.assertEqual(absent["envelope"]["status"], 404)
            self.assertEqual(json.loads(absent["body_text"]), ABSENCE_BODY)

    def test_envelope_extensions_repo_resource_branch(self):
        script = org_script(
            [repo(1)], **{protection_path(1): [response(200, PROTECTION_BODY)]}
        )
        with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(collect(base, out, ["--run-id", RUN_ID]).returncode, 0)
            envelope = json.loads(
                (out / "evidence" / "raw" / RUN_ID / "repos" / "1-repo-1" /
                 "default-branch-protection.json").read_text(encoding="utf-8")
            )["envelope"]
            self.assertEqual(envelope["repo"], {"id": 1, "full_name": "acme/repo-1"})
            self.assertEqual(envelope["resource"], "default-branch-protection")
            self.assertEqual(envelope["branch"], "main")
            for field in ("url", "method", "status", "captured_at", "run_id",
                          "attempts", "waits_seconds", "response_headers"):
                self.assertIn(field, envelope)
            self.assertEqual(envelope["method"], "GET")
            self.assertTrue(envelope["url"].endswith(protection_path(1)))

    def test_fanout_requests_ascend_by_repository_id_after_org_stage(self):
        script = org_script(
            [repo(9), repo(4), repo(7)],
            **{protection_path(i): [response(200, PROTECTION_BODY)]
               for i in (4, 7, 9)},
        )
        with serve(script) as (base, recorder), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(collect(base, out, ["--run-id", RUN_ID]).returncode, 0)
            fanout = [r["path"] for r in recorder.requests
                      if "/branches/" in r["path"]]
            self.assertEqual(
                fanout, [protection_path(4), protection_path(7), protection_path(9)]
            )
            org_stage = [r["path"] for r in recorder.requests
                         if "/branches/" not in r["path"]]
            self.assertEqual(len(org_stage) + len(fanout), len(recorder.requests))

    def test_annotation_unsafe_name_yields_id_only_directory(self):
        # T4-settled addressing applied in the real tree: annotation omitted,
        # identity and observation untouched.
        unsafe = {**repo(3), "name": "repo."}
        script = org_script(
            [unsafe], **{protection_path(3): [response(200, PROTECTION_BODY)]}
        )
        with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(collect(base, out, ["--run-id", RUN_ID]).returncode, 0)
            self.assertIn("repos/3/default-branch-protection.json", raw_files(out))


if __name__ == "__main__":
    unittest.main()
