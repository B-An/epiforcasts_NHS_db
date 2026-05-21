import os
import pymc as pm
import numpy as np

# Streamlit / interactive demos: fewer posterior draws = faster cold starts.
# Set PRESSURE_MODEL_FAST=0 for fuller sampling (e.g. offline evaluation).
_FAST = os.environ.get("PRESSURE_MODEL_FAST", "1").strip().lower() not in (
    "0",
    "false",
    "no",
)


def fit_pressure_model(df, *, fast: bool | None = None):
    """
    Bayesian latent pressure on bed occupancy.

    fast=True (default when PRESSURE_MODEL_FAST unset): fewer draws/tune for responsive UI.
    """
    if fast is None:
        fast = _FAST

    icb_codes = df["icb"].astype("category").cat.codes.values
    beds = df["bed_occupancy"].values

    if fast:
        draws, tune = 400, 400
    else:
        draws, tune = 1000, 1000

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
            compute_convergence_checks=False,
        )


    return model, trace
