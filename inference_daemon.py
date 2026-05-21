"""
Background inference daemon.

Continuously runs model fitting on a schedule and writes results to disk.
The UI consumes these pre-computed posteriors without waiting.

Usage:
    python inference_daemon.py [--interval 3600] [--data-path synthetic_nhs_pressure.csv]

Environment:
    INFERENCE_DAEMON_INTERVAL=7200  Set check interval in seconds (default: 3600 = 1 hour)
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("inference_daemon.log"),
    ],
)
logger = logging.getLogger(__name__)


def load_data(data_path: Path) -> pd.DataFrame:
    """Load synthetic data, return None if missing."""
    if not data_path.exists():
        logger.warning(f"Data file not found: {data_path}")
        return None
    return pd.read_csv(data_path)


def should_rerun_inference(
    data_path: Path,
    posterior_path: Path,
    force: bool = False,
) -> bool:
    """
    Check if inference should be rerun.
    
    Returns True if:
    - force=True, or
    - posterior file missing, or
    - data file is newer than posterior file
    """
    if force:
        return True
    
    if not posterior_path.exists():
        logger.info(f"Posterior file missing: {posterior_path}")
        return True
    
    if not data_path.exists():
        logger.warning(f"Data file missing: {data_path}")
        return False
    
    data_mtime = data_path.stat().st_mtime
    posterior_mtime = posterior_path.stat().st_mtime
    
    if data_mtime > posterior_mtime:
        logger.info(f"Data updated; posterior is stale ({posterior_mtime} < {data_mtime})")
        return True
    
    logger.debug(f"Posterior is current; skipping inference")
    return False


def run_inference_safe(
    data_path: Path,
    posterior_path: Path,
    fast: bool = True,
) -> bool:
    """
    Safely run inference and save results.
    
    Returns True if successful, False otherwise.
    """
    try:
        # Import here to avoid loading PyMC/PyTensor if not needed
        import numpy as np
        import pymc as pm
        import arviz as az
        
        logger.info(f"Loading data from {data_path}…")
        df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(df)} rows, {df['icb'].nunique()} ICBs")
        
        # Fit model
        logger.info("Fitting Bayesian model…")
        icb_codes = df["icb"].astype("category").cat.codes.values
        beds = df["bed_occupancy"].values
        
        draws = 400 if fast else 1000
        tune = 400 if fast else 1000
        
        with pm.Model() as model:
            mu_national = pm.Normal("mu_national", 0, 1)
            sigma_icb = pm.Exponential("sigma_icb", 1)
            icb_effect = pm.Normal(
                "icb_effect",
                0,
                1,
                shape=len(np.unique(icb_codes)),
            )
            latent_pressure = mu_national + icb_effect[icb_codes] * sigma_icb
            sigma_obs = pm.Exponential("sigma_obs", 5)
            
            pm.Normal(
                "bed_obs",
                mu=85 + latent_pressure * 6,
                sigma=sigma_obs,
                observed=beds,
            )
            
            trace = pm.sample(
                draws=draws,
                tune=tune,
                chains=1,
                cores=1,
                target_accept=0.9,
                progressbar=False,
                compute_convergence_checks=True,
            )
        
        idata = az.from_pymc(trace)
        idata.attrs = {
            "n_obs": len(df),
            "n_icbs": int(df["icb"].nunique()),
            "icbs": list(df["icb"].unique()),
            "timestamp": datetime.now().isoformat(),
        }
        
        # Save
        logger.info(f"Saving posterior to {posterior_path}…")
        idata.to_netcdf(str(posterior_path))
        logger.info(f"✓ Inference complete; {posterior_path.stat().st_size / (1024**2):.1f} MB")
        
        # Warm cache for instant UI access
        logger.info("Warming cache for instant UI access…")
        try:
            from cache_manager import CacheManager
            cache = CacheManager(posteriors_path=posterior_path)
            if cache.warm_cache():
                logger.info("✓ Cache warmed successfully")
            else:
                logger.warning("⚠ Cache warming failed")
        except Exception as e:
            logger.warning(f"Could not warm cache: {e}")
        
        return True
    
    except Exception as e:
        logger.error(f"Inference failed: {e}", exc_info=True)
        return False


def daemon_loop(
    data_path: Path = Path("synthetic_nhs_pressure.csv"),
    posterior_path: Path = Path("posteriors.nc"),
    interval_seconds: int = 3600,
    fast: bool = True,
):
    """
    Run continuous inference loop.
    
    Checks every `interval_seconds` if data is newer than posterior;
    if so, reruns inference in the background.
    """
    logger.info(f"Starting inference daemon (interval={interval_seconds}s, fast={fast})")
    logger.info(f"Data: {data_path.absolute()}")
    logger.info(f"Posteriors: {posterior_path.absolute()}")
    
    iteration = 0
    last_success = None
    
    try:
        while True:
            iteration += 1
            now = datetime.now()
            logger.info(f"\n--- Iteration {iteration} @ {now.strftime('%Y-%m-%d %H:%M:%S')} ---")
            
            try:
                if should_rerun_inference(data_path, posterior_path, force=False):
                    logger.info("Running inference…")
                    success = run_inference_safe(data_path, posterior_path, fast=fast)
                    if success:
                        last_success = now
                        logger.info(f"Success! Last successful inference: {last_success}")
                    else:
                        logger.error("Inference failed")
                else:
                    logger.info("No update needed")
            
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt; shutting down gracefully")
                break
            except Exception as e:
                logger.error(f"Unexpected error in loop iteration: {e}", exc_info=True)
            
            # Sleep until next check
            logger.info(f"Sleeping for {interval_seconds}s until next check…")
            time.sleep(interval_seconds)
    
    except KeyboardInterrupt:
        logger.info("Daemon stopped by user")
    finally:
        logger.info(f"Daemon exiting. Last successful inference: {last_success}")


def main():
    parser = argparse.ArgumentParser(
        description="Background daemon for continuous model inference.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Check every hour (default)
  python inference_daemon.py

  # Check every 30 minutes
  python inference_daemon.py --interval 1800

  # Use full sampling
  python inference_daemon.py --full

  # Exit after first run (useful for CI/scheduled jobs)
  python inference_daemon.py --once
        """,
    )
    parser.add_argument(
        "--data-path",
        type=Path,
        default=Path("synthetic_nhs_pressure.csv"),
        help="Path to input CSV data.",
    )
    parser.add_argument(
        "--posterior-path",
        type=Path,
        default=Path("posteriors.nc"),
        help="Path to output NetCDF file.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=int(os.environ.get("INFERENCE_DAEMON_INTERVAL", 3600)),
        help="Check interval in seconds (default: 3600).",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        default=True,
        help="Use reduced sampling (400 draws). Default behavior.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Use full sampling (1000 draws, 1000 tune).",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (useful for scheduled jobs).",
    )

    args = parser.parse_args()
    fast = not args.full

    if args.once:
        # Single run mode (for CI/cron)
        logger.info("Running inference once…")
        success = run_inference_safe(args.data_path, args.posterior_path, fast=fast)
        sys.exit(0 if success else 1)
    else:
        # Daemon mode (continuous)
        daemon_loop(
            data_path=args.data_path,
            posterior_path=args.posterior_path,
            interval_seconds=args.interval,
            fast=fast,
        )


if __name__ == "__main__":
    main()
