import numpy as np
import streamlit as st
import pandas as pd
import arviz as az

from bayesian_pressure_model import fit_pressure_model


@st.cache_resource
def run_model(df):
    return fit_pressure_model(df)


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(layout="wide")
st.title("Probabilistic NHS Winter / System Pressure (Demo)")

# Load data
df = pd.read_csv("synthetic_nhs_pressure.csv")

# Select geography
icb = st.selectbox(
    "Select geography",
    df["icb"].unique()
)

# ✅ DEFINE subset BEFORE using it
subset = df[df["icb"] == icb]

# Run model
with st.spinner("Running Bayesian model (cached, single-core)…"):
    _, trace = run_model(subset)

# -----------------------------
# Outputs
# -----------------------------
latent = trace.posterior["mu_national"].values.flatten()
prob_unsafe = (latent > 1.1).mean()

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Probability of unsafe system pressure",
        f"{prob_unsafe:.0%}"
    )

with col2:
    st.write(
        "Uncertainty reflects data sparsity, "
        "heterogeneity, and reporting gaps."
    )

st.subheader("Posterior Distribution")
# ArviZ returns Axes or an array of Axes; st.pyplot needs a Figure (savefig lives on Figure).
_posterior_axes = az.plot_posterior(trace, var_names=["mu_national"])
_ax = np.ravel(np.asarray(_posterior_axes, dtype=object))[0]
st.pyplot(_ax.figure)
