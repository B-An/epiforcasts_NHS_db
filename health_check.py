"""
One-command local health checks for the NHS pressure demo.

Usage:
    python health_check.py
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from cache_manager import CacheManager


def _ok(msg: str) -> None:
    print(f"[OK] {msg}")


def _warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def _fail(msg: str) -> None:
    print(f"[FAIL] {msg}")


def main() -> int:
    failures = 0

    _ok(f"Python executable: {sys.executable}")
    if shutil.which("g++") or shutil.which("clang++") or shutil.which("cl"):
        _ok("C/C++ compiler detected for PyTensor acceleration")
    else:
        _warn("No C/C++ compiler detected; inference may be significantly slower")

    data_path = Path("synthetic_nhs_pressure.csv")
    if data_path.exists():
        _ok(f"Data file present: {data_path}")
    else:
        _fail(f"Missing data file: {data_path}")
        failures += 1

    posterior_path = Path("posteriors.nc")
    if posterior_path.exists():
        _ok(f"Posterior artifact present: {posterior_path}")
    else:
        _warn("Posterior artifact missing: run `python run_inference.py --fast`")

    cache = CacheManager(posteriors_path=posterior_path)
    if cache.is_valid():
        _ok("Cache is valid and ready for dashboards")

        health = cache.get_health_check()
        if health.get("status") != "not_warmed":
            _ok(
                "Cache health metadata loaded"
                f" (n_icbs={health.get('n_icbs')}, n_draws={health.get('n_draws')})"
            )
        else:
            _warn("Cache health metadata not found")

        summary_path = cache.summary_stats_path
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                stats = json.load(f)
            _ok(f"Summary stats readable: {summary_path} ({len(stats)} areas)")
        except Exception as exc:
            _fail(f"Could not read summary stats: {exc}")
            failures += 1
    else:
        _warn("Cache is not valid yet. Run inference then warm cache.")

    if failures:
        print(f"\nHealth check failed with {failures} blocking issue(s).")
        return 1

    print("\nHealth check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
