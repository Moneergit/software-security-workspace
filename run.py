"""Set up, run and verify the workspace with one command per task."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENVIRONMENT = ROOT / ".venv"
PYTHON = ENVIRONMENT / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def execute(interpreter: Path, *arguments: str) -> None:
    """Use fixed argument lists and the project folder, including paths with spaces."""
    subprocess.run([str(interpreter), *arguments], cwd=ROOT, check=True)


def setup() -> None:
    """Verify artifacts, install the approved environment, and seed synthetic data."""
    execute(Path(sys.executable), "scripts/check_artifacts.py")
    if not PYTHON.exists():
        print("Creating the project virtual environment...", flush=True)
        execute(Path(sys.executable), "-m", "venv", str(ENVIRONMENT))
    # Update pip separately before installing the rest of the locked environment.
    for lock in ["bootstrap.lock", "requirements.lock"]:
        execute(
            PYTHON,
            "-m",
            "pip",
            "install",
            "--no-index",
            "--find-links",
            "vendor",
            "--require-hashes",
            "-r",
            lock,
        )
    execute(PYTHON, "scripts/check_environment.py")
    execute(PYTHON, "scripts/run.py", "seed")
    print("\nSetup complete. Next: py -3.12 run.py run", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        nargs="?",
        default="run",
        choices=["setup", "run", "demo", "test", "check", "seed", "build", "smoke"],
        help="setup once; run the services; test behavior; check all release gates",
    )
    command = parser.parse_args().command
    if sys.version_info[:2] != (3, 12):
        parser.error("Use Python 3.12 x64: py -3.12 run.py " + command)
    if command != "setup" and not PYTHON.exists():
        parser.error("Set up the project first: py -3.12 run.py setup")
    try:
        if command == "setup":
            setup()
        elif command == "test":
            (ROOT / "reports").mkdir(exist_ok=True)
            execute(PYTHON, "-m", "pytest", "-q", "--junitxml=reports/tests.xml")
        elif command == "check":
            execute(PYTHON, "scripts/ci.py")
        elif command == "build":
            execute(
                PYTHON,
                "-m",
                "build",
                "--wheel",
                "--no-isolation",
                "--outdir",
                "reports/helper-wheel",
                "helper",
            )
        else:
            execute(PYTHON, "scripts/run.py", "serve" if command == "run" else command)
    except KeyboardInterrupt:
        return 130
    except subprocess.CalledProcessError as error:
        print(
            f"\nThe command failed (exit {error.returncode}). See the output above.",
            file=sys.stderr,
        )
        return error.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
