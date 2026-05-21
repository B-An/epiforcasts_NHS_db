"""
Offline Bayesian inference script.

Runs the pressure model on synthetic data and saves posterior summaries to disk.
Run this once (or on a schedule) to update posterior estimates; the Streamlit app
consumes the stored results.

Usage:
    python run_inference.py [--data-path synthetic_nhs_pressure.csv] [--output-path posteriors.nc] [--fast]

Environment:
    PRESSURE_MODEL_FAST=0  to use fuller sampling (1000 draws, 1000 tune) instead of defaults.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az

from cache_manager import CacheManager


def fit_pressure_model(df: pd.DataFrame, *, fast: bool = True) -> tuple[pm.Model, az.InferenceData]:
    """
    Fit Bayesian latent pressure model on bed occupancy.

    Parameters
    ----------
    df : pd.DataFrame
        Data with columns: 'icb', 'bed_occupancy', etc.
    fast : bool
        If True, use reduced sampling (400 draws, 400 tune).
        If False, use fuller sampling (1000 draws, 1000 tune).

    Returns
    -------
    model : pm.Model
        Fitted PyMC model.
    idata : az.InferenceData
        ArviZ InferenceData object (posterior, diagnostics, etc.).
    """
    icb_codes = df["icb"].astype("category").cat.codes.values
    beds = df["bed_occupancy"].values

    draws = 400 if fast else 1000
    tune = 400 if fast else 1000

    print(f"Sampling with draws={draws}, tune={tune}, fast={fast}")

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
            progressbar=True,
            compute_convergence_checks=True,
        )

    # Convert PyMC trace to ArviZ InferenceData for persistence
    idata = az.from_pymc3(trace)
    return model, idata


def save_posterior_summaries(
    idata: az.InferenceData,
    df: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Save posterior InferenceData and metadata to NetCDF.

    Parameters
    ----------
    idata : az.InferenceData
        Posterior samples from ArviZ.
    df : pd.DataFrame
        Original data (for metadata).
    output_path : Path
        Output NetCDF file path.
    """
    # Add metadata to InferenceData
    idata.attrs = {
        "n_obs": len(df),
        "n_icbs": int(df["icb"].nunique()),
        "icbs": list(df["icb"].unique()),
    }

    # Save to NetCDF
    idata.to_netcdf(str(output_path))
    print(f"✓ Posterior saved to {output_path}")

    # Also save ICB index mapping as JSON for UI reference
    icb_names = df["icb"].astype("category").cat.categories.tolist()
    metadata = {
        "icbs": icb_names,
        "n_icbs": len(icb_names),
        "n_obs": len(df),
    }
    metadata_path = output_path.with_stem(output_path.stem + "_metadata")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved to {metadata_path}")
    
    # Warm cache for instant UI access
    print("Warming cache for instant UI access…")
    cache = CacheManager(posteriors_path=output_path)
    if cache.warm_cache():
        print(cache.get_status_report())
    else:
        print("⚠ Cache warming failed; UI will be slower on first access")


def main():
    parser = argparse.ArgumentParser(
        description="Run offline Bayesian inference on pressure model."
    )
    parser.add_argument(
        "--data-path",
        type=Path,
        default=Path("synthetic_nhs_pressure.csv"),
        help="Path to input CSV data.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=Path("posteriors.nc"),
        help="Path to output NetCDF file.",
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

    args = parser.parse_args()

    # Resolve fast flag
    fast = not args.full

    # Load data
    if not args.data_path.exists():
        print(f"✗ Data file not found: {args.data_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading data from {args.data_path}…")
    df = pd.read_csv(args.data_path)
    print(f"✓ Loaded {len(df)} rows, {df['icb'].nunique()} ICBs")

    # Fit model
    print("Fitting Bayesian model…")
    model, idata = fit_pressure_model(df, fast=fast)
    print(f"✓ Model fitted; posterior has {idata.posterior.dims['draw']} draws")

    # Save results
    print(f"Saving to {args.output_path}…")
    save_posterior_summaries(idata, df, Path(args.output_path))

    print("✓ Done!")


if __name__ == "__main__":
    main()
