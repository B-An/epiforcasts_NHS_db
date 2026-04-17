
import numpy as np
import pandas as pd

np.random.seed(2026)

ICBS = {
    "Birmingham & Solihull ICB": 1.0,
    "Greater Manchester ICB": 1.3,
    "South East London ICB": 0.9,
}

N_WEEKS = 80  # ~18 months

def generate_icb(icb, scale):
    latent_pressure = np.cumsum(
        np.random.normal(0, 0.12, N_WEEKS)
    ) + scale

    resp_111 = np.random.negative_binomial(
        n=25,
        p=1 / (1 + np.exp(latent_pressure))
    )

    bed_occ = np.clip(
        84 + latent_pressure * 7 + np.random.normal(0, 3, N_WEEKS),
        70, 100
    )

    dtoc = np.random.poisson(
        np.maximum(2 + latent_pressure * 2.5, 0)
    )

    df = pd.DataFrame({
        "week": np.arange(N_WEEKS),
        "icb": icb,
        "resp_111_calls": resp_111.astype(float),
        "bed_occupancy": bed_occ,
        "dtoc_patients": dtoc
    })

    # Missing data (realistic NHS issues)
    missing = np.random.choice(df.index, size=6, replace=False)
    df.loc[missing, "resp_111_calls"] = np.nan

    return df

icb_data = pd.concat(
    [generate_icb(icb, scale) for icb, scale in ICBS.items()]
)

england = (
    icb_data
    .groupby("week")
    .mean(numeric_only=True)
    .assign(icb="England")
    .reset_index()
)

final = pd.concat([icb_data, england])
final.to_csv("synthetic_nhs_pressure.csv", index=False)
