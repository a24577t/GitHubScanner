"""CLI seam: argument handling and run-frame validation."""
import unittest

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
        import tempfile
        from pathlib import Path

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
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli(
                ["collect", "--api-url", "https://api.example", "--org", "x", "--out", tmp]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("GITHUB_TOKEN", result.stderr)


if __name__ == "__main__":
    unittest.main()
