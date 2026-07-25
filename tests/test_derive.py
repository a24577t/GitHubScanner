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


if __name__ == "__main__":
    unittest.main()
