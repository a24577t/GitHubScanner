"""Shared test helpers: invoke the collector CLI at its public seam."""
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src"


def run_cli(args, env=None, cwd=None):
    """Run the collector CLI as a subprocess; return CompletedProcess."""
    full_env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
    full_env["PYTHONPATH"] = str(SRC)
    if env:
        full_env.update(env)
    return subprocess.run(
        [sys.executable, "-m", "collector", *args],
        capture_output=True,
        text=True,
        env=full_env,
        cwd=cwd or REPO_ROOT,
        timeout=120,
    )
