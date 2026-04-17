import pymc as pm
import numpy as np

def fit_pressure_model(df):
    icb_codes = df["icb"].astype("category").cat.codes.values
    beds = df["bed_occupancy"].values

    with pm.Model() as model:
        mu_national = pm.Normal("mu_national", 0, 1)

        sigma_icb = pm.Exponential("sigma_icb", 1)
        icb_effect = pm.Normal(
            "icb_effect",
            0, 1,
            shape=len(np.unique(icb_codes))
        )

        latent_pressure = (
            mu_national + icb_effect[icb_codes] * sigma_icb
        )

        sigma_obs = pm.Exponential("sigma_obs", 5)

        pm.Normal(
            "bed_obs",
            mu=85 + latent_pressure * 6,
            sigma=sigma_obs,
            observed=beds
        )

        trace = pm.sample(
            draws=1000,
            tune=1000,
            chains=1,       
            cores=1,         
            target_accept=0.9,
            progressbar=False
        )


    return model, trace