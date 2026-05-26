"""
Resilient dashboard launcher.

This launcher first tries the Pixi task path, then falls back to direct Python
execution if Pixi fails (for example due to environment-specific certificate
or solver issues).

Usage:
    python run_dashboard_resilient.py --app app.py
    python run_dashboard_resilient.py --app app_fast.py --preferred-port 8501
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PIXICERT_HINTS = (
    "unknownissuer",
    "certificate",
    "ssl",
    "solver",
)


def _pixi_task_for_app(app: str) -> str:
    return "run-dashboard-fast" if Path(app).name == "app_fast.py" else "run-dashboard"


def _should_fallback(output: str) -> bool:
    text = output.lower()
    return any(token in text for token in PIXICERT_HINTS)


def _run_pixi(task: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["pixi", "run", task],
        text=True,
        capture_output=True,
        check=False,
    )


def _fallback_python() -> str:
    venv_python = Path(".venv") / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def _run_fallback(app: str, preferred_port: int, max_port: int, headless: str) -> int:
    cmd = [
        _fallback_python(),
        "launch_streamlit.py",
        "--app",
        app,
        "--preferred-port",
        str(preferred_port),
        "--max-port",
        str(max_port),
        "--headless",
        headless,
    ]
    print(f"[FALLBACK] Starting direct launcher: {' '.join(cmd)}")
    return subprocess.call(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run dashboard with Pixi-first fallback.")
    parser.add_argument("--app", default="app.py", help="Dashboard app file (app.py or app_fast.py).")
    parser.add_argument("--preferred-port", type=int, default=8501, help="Preferred starting port.")
    parser.add_argument("--max-port", type=int, default=8510, help="Maximum fallback port.")
    parser.add_argument(
        "--headless",
        choices=["true", "false"],
        default="true",
        help="Set Streamlit headless mode for fallback path.",
    )
    parser.add_argument(
        "--fallback-on-any-failure",
        action="store_true",
        help="Fallback even when Pixi fails for reasons other than certificate/solver.",
    )
    args = parser.parse_args()

    task = _pixi_task_for_app(args.app)
    print(f"[INFO] Trying Pixi path first: pixi run {task}")
    result = _run_pixi(task)

    if result.returncode == 0:
        if result.stdout:
            print(result.stdout, end="")
        return 0

    combined_output = f"{result.stdout}\n{result.stderr}".strip()
    print("[WARN] Pixi launch failed.")
    if combined_output:
        print(combined_output)

    if args.fallback_on_any_failure or _should_fallback(combined_output):
        print("[INFO] Falling back to direct .venv/python launcher.")
        return _run_fallback(
            app=args.app,
            preferred_port=args.preferred_port,
            max_port=args.max_port,
            headless=args.headless,
        )

    print("[FAIL] Pixi failed and fallback criteria were not met.", file=sys.stderr)
    print("[HINT] Re-run with --fallback-on-any-failure to force fallback.", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
