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


class MissingRequiredInput(unittest.TestCase):
    def test_v33_missing_default_branch_no_request_no_artifact(self):
        # V33 at the T5 seam: the eligible repository stays discovered, the
        # descriptor gets no request and no fabricated artifact; other
        # repositories are still observed and the run stays orderly.
        no_branch = {k: v for k, v in repo(1).items() if k != "default_branch"}
        script = org_script(
            [no_branch, repo(2)],
            **{protection_path(2): [response(200, PROTECTION_BODY)]},
        )
        with serve(script) as (base, recorder), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = collect(base, out, ["--run-id", RUN_ID])
            self.assertEqual(result.returncode, 0, result.stderr)
            fanout = [r["path"] for r in recorder.requests
                      if "/branches/" in r["path"]]
            self.assertEqual(fanout, [protection_path(2)])
            files = raw_files(out)
            self.assertNotIn("repos/1-repo-1/default-branch-protection.json", files)
            self.assertIn("repos/2-repo-2/default-branch-protection.json", files)

    def test_unusable_default_branch_values_are_missing_not_repaired(self):
        # Ratified refinement (E1 Q2): None / empty / non-string inputs are
        # missing — never coerced into a request path.
        script = org_script(
            [{**repo(1), "default_branch": ""},
             {**repo(2), "default_branch": None}],
        )
        with serve(script) as (base, recorder), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(collect(base, out, ["--run-id", RUN_ID]).returncode, 0)
            self.assertEqual(
                [r["path"] for r in recorder.requests if "/branches/" in r["path"]],
                [],
            )
            self.assertEqual([f for f in raw_files(out) if f.startswith("repos/")],
                             [])


class IneligibleItems(unittest.TestCase):
    def test_ineligible_inventory_items_get_no_directory_and_no_request(self):
        # V32 consequence at the fan-out seam: ineligible items are never
        # targets; inventory projection semantics stay untouched.
        script = org_script(
            [{"id": True, "name": "bool", "full_name": "acme/bool",
              "default_branch": "main"},
             {**repo(2), "full_name": "not-owner-name"},
             repo(3)],
            **{protection_path(3): [response(200, PROTECTION_BODY)]},
        )
        with serve(script) as (base, recorder), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(collect(base, out, ["--run-id", RUN_ID]).returncode, 0)
            self.assertEqual(
                [r["path"] for r in recorder.requests if "/branches/" in r["path"]],
                [protection_path(3)],
            )
            self.assertEqual(
                [f for f in raw_files(out) if f.startswith("repos/")],
                ["repos/3-repo-3/default-branch-protection.json"],
            )
            observed = json.loads(
                (out / "observed" / "repositories.json").read_text(encoding="utf-8")
            )
            self.assertEqual(observed["count"], 3)


class OrderlyContinuation(unittest.TestCase):
    def test_transport_failure_on_one_repo_resource_never_stops_the_run(self):
        script = org_script(
            [repo(1), repo(2)],
            **{protection_path(1): [response(500, {"message": "boom"})],
               protection_path(2): [response(200, PROTECTION_BODY)]},
        )
        with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = collect(base, out, ["--run-id", RUN_ID])
            self.assertEqual(result.returncode, 0, result.stderr)
            raw = out / "evidence" / "raw" / RUN_ID / "repos"
            failed = json.loads(
                (raw / "1-repo-1" / "default-branch-protection.json")
                .read_text(encoding="utf-8")
            )
            # The failure is itself evidence: persisted verbatim with the
            # bounded-retry attempt count (ADR-0007).
            self.assertEqual(failed["envelope"]["status"], 500)
            self.assertEqual(failed["envelope"]["attempts"], 3)
            ok = json.loads(
                (raw / "2-repo-2" / "default-branch-protection.json")
                .read_text(encoding="utf-8")
            )
            self.assertEqual(ok["envelope"]["status"], 200)

    def test_write_failure_is_a_collection_failure_never_a_crash(self):
        # Collection model 6: filesystem path-creation failures are collection
        # failures, not crashes — surfaced, and the run continues.
        import contextlib
        import io
        import unittest.mock as mock

        from collector import collect as collect_module
        from collector.serialize import write_canonical as real_write

        def failing_write(path, obj):
            if "1-repo-1" in str(path):
                raise OSError("simulated path-creation failure")
            return real_write(path, obj)

        script = org_script(
            [repo(1), repo(2)],
            **{protection_path(1): [response(200, PROTECTION_BODY)],
               protection_path(2): [response(200, PROTECTION_BODY)]},
        )
        with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            stderr = io.StringIO()
            with mock.patch.object(collect_module, "write_canonical",
                                   side_effect=failing_write), \
                    contextlib.redirect_stderr(stderr):
                code = collect_module.run_collect(
                    base, "acme", out, "tok-inproc", run_id=RUN_ID)
            self.assertEqual(code, 0)
            files = raw_files(out)
            self.assertNotIn("repos/1-repo-1/default-branch-protection.json", files)
            self.assertIn("repos/2-repo-2/default-branch-protection.json", files)
            self.assertIn("collection failure", stderr.getvalue())
            self.assertIn("simulated path-creation failure", stderr.getvalue())


class TokenSecrecyOverFanoutArtifacts(unittest.TestCase):
    def test_token_appears_in_no_new_artifact_or_output(self):
        from test_collect import TOKEN

        script = org_script(
            [repo(1), repo(2)],
            **{protection_path(1): [response(200, PROTECTION_BODY)],
               protection_path(2): [response(404, ABSENCE_BODY)]},
        )
        with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = collect(base, out, ["--run-id", RUN_ID])
            self.assertEqual(result.returncode, 0, result.stderr)
            token_bytes = TOKEN.encode("utf-8")
            scanned = 0
            for artifact in sorted(out.rglob("*")):
                if artifact.is_file():
                    scanned += 1
                    self.assertNotIn(token_bytes, artifact.read_bytes(),
                                     f"token leaked into {artifact}")
            fanout = [p for p in out.rglob("repos/*/*.json")]
            self.assertEqual(len(fanout), 2, "both fan-out artifacts scanned")
            self.assertGreater(scanned, len(fanout))
            self.assertNotIn(TOKEN, result.stdout)
            self.assertNotIn(TOKEN, result.stderr)


if __name__ == "__main__":
    unittest.main()
