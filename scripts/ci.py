"""Local equivalent of required Jenkins validation gates."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(name, arguments):
    print("Running", name, flush=True)
    with (ROOT / "reports" / (name + ".txt")).open("w", encoding="utf-8") as output:
        result = subprocess.run(
            [sys.executable, *arguments], cwd=ROOT, stdout=output, stderr=subprocess.STDOUT
        )
    return result.returncode


def main():
    (ROOT / "reports").mkdir(exist_ok=True)
    stages = [
        ("artifacts", ["scripts/check_artifacts.py"]),
        ("environment", ["scripts/check_environment.py"]),
        ("compile", ["-m", "compileall", "-q", "workspace_app", "helper/src"]),
        (
            "helper-build",
            [
                "-m",
                "build",
                "--wheel",
                "--no-isolation",
                "--outdir",
                "reports/helper-wheel",
                "helper",
            ],
        ),
        (
            "ruff",
            [
                "-m",
                "ruff",
                "check",
                "workspace_app",
                "scripts",
                "tests",
                "helper/src",
                "run.py",
                "--output-format",
                "json",
                "--output-file",
                "reports/ruff.json",
            ],
        ),
        (
            "format",
            [
                "-m",
                "ruff",
                "format",
                "--check",
                "workspace_app",
                "scripts",
                "tests",
                "helper/src",
                "run.py",
            ],
        ),
        (
            "bandit",
            [
                "-m",
                "bandit",
                "-r",
                "workspace_app",
                "helper/src",
                "-f",
                "json",
                "-o",
                "reports/bandit.json",
            ],
        ),
        (
            "dependency-audit",
            [
                "-m",
                "pip_audit",
                "--local",
                "--format",
                "json",
                "--output",
                "reports/dependency-audit.json",
            ],
        ),
        ("tests", ["-m", "pytest", "-q", "--junitxml=reports/tests.xml"]),
        ("smoke", ["scripts/run.py", "smoke"]),
    ]
    results = {name: run(name, arguments) for name, arguments in stages}
    # An unknown public dependency must not silently escape advisory analysis.
    audit_path = ROOT / "reports/dependency-audit.json"
    if audit_path.exists():
        audit = json.loads(audit_path.read_text())
        unexpected_skips = [
            d
            for d in audit.get("dependencies", [])
            if "skip_reason" in d and d["name"] != "workspace-csv"
        ]
        if unexpected_skips:
            results["dependency-audit"] = 1
    (ROOT / "reports/gates.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    raise SystemExit(1 if any(results.values()) else 0)


if __name__ == "__main__":
    main()
