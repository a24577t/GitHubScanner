"""Derivation, determinism, and token secrecy through the CLI seam."""
import shutil
import tempfile
import unittest
from pathlib import Path

from fake_github import response, serve
from helpers import run_cli
from test_collect import HAPPY_SCRIPT, RUN_ID, TOKEN, collect


def scaffold_bytes(out):
    return {
        str(p.relative_to(out)): p.read_bytes()
        for p in sorted(out.rglob("*")) if p.is_file()
    }


class OfflineDerivation(unittest.TestCase):
    def test_derive_regenerates_observed_byte_identical_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            with serve(HAPPY_SCRIPT) as (base, _):
                self.assertEqual(collect(base, out, ["--run-id", RUN_ID]).returncode, 0)
            # server is down now: derivation must be fully offline
            original = {k: v for k, v in scaffold_bytes(out).items()
                        if k.startswith("observed")}
            shutil.rmtree(out / "observed")
            result = run_cli(["derive", "--out", str(out)])
            self.assertEqual(result.returncode, 0, result.stderr)
            regenerated = {k: v for k, v in scaffold_bytes(out).items()
                           if k.startswith("observed")}
            self.assertEqual(original, regenerated)

    def test_serialization_is_lf_utf8_with_trailing_newline(self):
        with serve(HAPPY_SCRIPT) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(collect(base, out, ["--run-id", RUN_ID]).returncode, 0)
            for name, data in scaffold_bytes(out).items():
                self.assertNotIn(b"\r\n", data, f"CRLF found in {name}")
                self.assertTrue(data.endswith(b"\n"), f"no trailing newline in {name}")


class TokenSecrecy(unittest.TestCase):
    def test_token_appears_in_no_artifact_or_output(self):
        with serve(HAPPY_SCRIPT) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = collect(base, out, ["--run-id", RUN_ID])
            self.assertEqual(result.returncode, 0)
            token_bytes = TOKEN.encode("utf-8")
            for name, data in scaffold_bytes(out).items():
                self.assertNotIn(token_bytes, data, f"token leaked into {name}")
            self.assertNotIn(TOKEN, result.stdout)
            self.assertNotIn(TOKEN, result.stderr)


class LatestRunSelection(unittest.TestCase):
    def test_derive_selects_actual_latest_run_despite_run_id_ordering(self):
        import time

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            with serve(HAPPY_SCRIPT) as (base, _):
                self.assertEqual(
                    collect(base, out, ["--run-id", "zzz-first-run"]).returncode, 0)
            time.sleep(1.1)
            with serve(HAPPY_SCRIPT) as (base, _):
                self.assertEqual(
                    collect(base, out, ["--run-id", "aaa-second-run"]).returncode, 0)
            shutil.rmtree(out / "observed")
            result = run_cli(["derive", "--out", str(out)])
            self.assertEqual(result.returncode, 0, result.stderr)
            observed = (out / "observed" / "org.json").read_text(encoding="utf-8")
            import json

            self.assertEqual(json.loads(observed)["run_id"], "aaa-second-run")


class MarkdownReportContent(unittest.TestCase):
    def test_markdown_report_carries_target_and_failures(self):
        run_id = RUN_ID
        script = dict(HAPPY_SCRIPT)
        script["/orgs/acme"] = [response(200, None)]
        script["/orgs/acme"][0]["body"] = "{not-json"
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            with serve(script) as (base, _):
                self.assertEqual(collect(base, out, ["--run-id", run_id]).returncode, 0)
            markdown = (out / "reports" / f"{run_id}.md").read_text(encoding="utf-8")
            self.assertIn("**API base:**", markdown)
            self.assertIn("**Target host:** 127.0.0.1", markdown)
            self.assertIn("## Failures", markdown)
            self.assertIn("/orgs/acme", markdown)
            self.assertIn("200", markdown)


class ReportCounts(unittest.TestCase):
    def test_report_counts_every_state_present(self):
        script = dict(HAPPY_SCRIPT)
        script["/meta"] = [response(403, {"message": "denied"})]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            with serve(script) as (base, _):
                self.assertEqual(collect(base, out, ["--run-id", RUN_ID]).returncode, 0)
            import json

            report = json.loads(
                (out / "reports" / f"{RUN_ID}.json").read_text(encoding="utf-8")
            )
            counts = report["state_counts"]
            self.assertEqual(sorted(counts), ["absent", "collected", "failed",
                                              "inaccessible", "incomplete",
                                              "unknown", "unsupported"])
            self.assertEqual(counts["inaccessible"], 1)
            self.assertEqual(counts["collected"], 3)
            markdown = (out / "reports" / f"{RUN_ID}.md").read_text(encoding="utf-8")
            self.assertIn("| inaccessible | 1 |", markdown)


class StdlibConstraint(unittest.TestCase):
    def test_production_code_imports_stdlib_only(self):
        import ast
        import sys

        src = Path(__file__).resolve().parent.parent / "src"
        for module_path in src.rglob("*.py"):
            tree = ast.parse(module_path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    names = [node.module]
                for name in names:
                    top = (name or "").split(".")[0]
                    self.assertTrue(
                        top == "collector" or top in sys.stdlib_module_names,
                        f"non-stdlib import '{name}' in {module_path.name}",
                    )


class LocationIndependence(unittest.TestCase):
    def test_cli_from_outside_repo_with_spaced_out_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            outside_cwd = Path(tmp) / "elsewhere"
            outside_cwd.mkdir()
            out_a = Path(tmp) / "an ordinary path with spaces" / "out"
            out_b = Path(tmp) / "plain" / "out"
            with serve(HAPPY_SCRIPT) as (base, _):
                result = run_cli(
                    ["collect", "--api-url", base, "--org", "acme",
                     "--out", str(out_a), "--run-id", RUN_ID],
                    env={"GITHUB_TOKEN": TOKEN, "COLLECTOR_INSECURE_ALLOW_HTTP": "1"},
                    cwd=outside_cwd,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
            with serve(HAPPY_SCRIPT) as (base, _):
                self.assertEqual(collect(base, out_b, ["--run-id", RUN_ID]).returncode, 0)
            files_a = sorted(str(p.relative_to(out_a)) for p in out_a.rglob("*") if p.is_file())
            files_b = sorted(str(p.relative_to(out_b)) for p in out_b.rglob("*") if p.is_file())
            self.assertEqual(files_a, files_b, "identical scaffold regardless of location")
            for name in ("org.json", "repositories.json"):
                self.assertEqual((out_a / "observed" / name).read_bytes(),
                                 (out_b / "observed" / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
