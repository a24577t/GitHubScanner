"""CLI seam: argument handling and run-frame validation."""
import tempfile
import unittest
from pathlib import Path

from fake_github import response, serve
from helpers import run_cli


class NoArguments(unittest.TestCase):
    def test_no_args_exits_2_with_usage(self):
        result = run_cli([])
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage", result.stderr.lower())


class RunFrameValidation(unittest.TestCase):
    def test_missing_required_args_exit_2(self):
        result = run_cli(["collect", "--org", "x", "--out", "o"])
        self.assertEqual(result.returncode, 2)

    def test_non_https_api_url_rejected_no_scaffold(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = run_cli(
                ["collect", "--api-url", "http://insecure.example", "--org", "x", "--out", str(out)],
                env={"GITHUB_TOKEN": "tok-frame-1"},
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("https", result.stderr.lower())
            self.assertFalse(out.exists(), "frame failure must not produce a scaffold")

    def test_missing_token_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(
                ["collect", "--api-url", "https://api.example", "--org", "x", "--out", tmp]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("GITHUB_TOKEN", result.stderr)


class RunFrameEstablishment(unittest.TestCase):
    def _collect(self, base, out):
        env = {"GITHUB_TOKEN": "tok-frame-2", "COLLECTOR_INSECURE_ALLOW_HTTP": "1"}
        return run_cli(
            ["collect", "--api-url", base, "--org", "acme", "--out", str(out)],
            env=env,
        )

    def test_http_override_never_applies_to_non_loopback_targets(self):
        result = run_cli(
            ["collect", "--api-url", "http://internal.example", "--org", "acme",
             "--out", "o"],
            env={"GITHUB_TOKEN": "tok-frame-2", "COLLECTOR_INSECURE_ALLOW_HTTP": "1"},
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("https", result.stderr.lower())

    def test_unestablished_identity_status_fails_run_frame(self):
        for status in (403, 500):
            with self.subTest(status=status):
                script = {"/user": [response(status, {"message": "no identity"}),
                                    response(status, {"message": "no identity"})]}
                with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
                    out = Path(tmp) / "out"
                    result = self._collect(base, out)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("identity", result.stderr.lower())
                    self.assertFalse(out.exists())

    def test_malformed_identity_response_fails_run_frame(self):
        script = {"/user": [response(200, None)]}
        script["/user"][0]["body"] = "{not-json"
        with serve(script) as (base, _), tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = self._collect(base, out)
            self.assertEqual(result.returncode, 2)
            self.assertIn("identity", result.stderr.lower())
            self.assertFalse(out.exists())

    def test_unwritable_out_fails_before_any_request(self):
        with serve({}) as (base, recorder), tempfile.TemporaryDirectory() as tmp:
            blocker = Path(tmp) / "blocked"
            blocker.write_text("a file where the out dir should go", encoding="utf-8")
            result = self._collect(base, blocker / "out")
            self.assertEqual(result.returncode, 2)
            self.assertIn("output", result.stderr.lower())
            self.assertEqual(recorder.requests, [], "no request before writability check")

    def test_unreachable_target_fails_run_frame_with_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = self._collect("http://127.0.0.1:9", out)
            self.assertEqual(result.returncode, 2)
            self.assertIn("unreachable", result.stderr.lower())
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
