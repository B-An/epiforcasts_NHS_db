import os

# Headless / Cloud-friendly backend before pyplot (faster, no GUI toolkit on servers).
os.environ.setdefault("MPLBACKEND", "Agg")

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import arviz as az

from cache_manager import CacheManager

WEEKLY_CSV = "synthetic_nhs_pressure.csv"
POSTERIORS_NC = "posteriors.nc"

# -----------------------------------------------------------------------------
# Reference levels on the latent index (DEMO ONLY)
# -----------------------------------------------------------------------------
# These positions are fixed cut-points for communication in this prototype. They are
# NOT official NHS escalation thresholds, bed targets, or clinically derived limits.
# For production, replace via co-design with operations / IG and document provenance.
THRESHOLD_BASELINE = 0.0
THRESHOLD_CONCERN = 0.5
THRESHOLD_ELEVATED = 1.1

# -----------------------------------------------------------------------------
# Risk summary band (Low / Medium / Elevated) — UI HEURISTIC
# -----------------------------------------------------------------------------
# Not validated against any real escalation policy. Tune with operations if you adopt
# this pattern; values are posterior probabilities on the same references above.
DEFAULT_RISK_ELEVATED_TIER_MIN_P_HIGH = 0.25  # P(exceeds high ref)
DEFAULT_RISK_ELEVATED_TIER_MIN_P_CONCERN = 0.55  # P(exceeds concern ref) OR gate
DEFAULT_RISK_MEDIUM_TIER_MIN_P_HIGH = 0.08
DEFAULT_RISK_MEDIUM_TIER_MIN_P_CONCERN = 0.30


def _pressure_index_samples(idata: az.InferenceData, icb_idx: int) -> np.ndarray:
    """
    Extract posterior samples of combined system pressure index for a given ICB.
    
    Parameters
    ----------
    idata : az.InferenceData
        Posterior samples from ArviZ (loaded from NetCDF).
    icb_idx : int
        Index of the ICB in the ICB list.
    
    Returns
    -------
    np.ndarray
        Flattened posterior samples of the pressure index for this ICB.
    """
    post = idata.posterior
    mu = post["mu_national"].values  # shape: (chains, draws)
    eff = post["icb_effect"].values  # shape: (chains, draws, n_icbs)
    sig = post["sigma_icb"].values   # shape: (chains, draws)
    
    # Compute combined pressure index: mu + icb_effect[icb_idx] * sigma
    combined = mu + eff[..., icb_idx] * sig
    return combined.astype(float).ravel()


def _risk_band(
    p_elevated: float,
    p_concern: float,
    *,
    pe_hi: float,
    pc_hi: float,
    pe_med: float,
    pc_med: float,
) -> tuple[str, str]:
    """Map probabilities to an indicative label — heuristic only."""
    if p_elevated >= pe_hi or p_concern >= pc_hi:
        return "Elevated", "Prioritise review of capacity, flow, and escalation plans (indicative only)."
    if p_elevated >= pe_med or p_concern >= pc_med:
        return "Medium", "Worth closer monitoring; corroborate with local intelligence."
    return "Low", "No strong signal of unusually high modelled pressure; stay vigilant to new data."


def _credible_triplet(samples: np.ndarray, mass: float) -> tuple[float, float, float]:
    """Equal-tailed interval; returns (lower, median, upper)."""
    alpha = (1.0 - mass) / 2.0
    lo, mid, hi = [
        float(x)
        for x in np.percentile(samples, [100.0 * alpha, 50.0, 100.0 * (1.0 - alpha)])
    ]
    return lo, mid, hi


def _plot_pressure_question(
    samples: np.ndarray,
    *,
    credible_mass: float,
    show_median_line: bool,
) -> plt.Figure:
    lo, mid, hi = _credible_triplet(samples, credible_mass)
    pct_label = f"{int(credible_mass * 100)}% plausible range"

    fig, ax = plt.subplots(figsize=(10, 4.2), layout="constrained")
    ax.hist(
        samples,
        bins=40,
        density=True,
        alpha=0.78,
        color="#1d4ed8",
        edgecolor="white",
        linewidth=0.5,
    )

    ax.axvspan(lo, hi, alpha=0.15, color="#1e3a8a", label=pct_label)

    ax.axvline(
        THRESHOLD_BASELINE,
        color="#64748b",
        linestyle="--",
        linewidth=1.5,
        label="Baseline reference (demo)",
    )
    ax.axvline(
        THRESHOLD_CONCERN,
        color="#d97706",
        linestyle="--",
        linewidth=1.5,
        label="Concern reference (demo)",
    )
    ax.axvline(
        THRESHOLD_ELEVATED,
        color="#b91c1c",
        linestyle="--",
        linewidth=1.5,
        label="High pressure reference (demo)",
    )
    if show_median_line:
        ax.axvline(mid, color="#0f172a", linestyle="-", linewidth=1.0, alpha=0.85, label="Median")

    ax.set_xlabel(
        "System pressure index (modelled, unitless — not an NHS operational metric)"
    )
    ax.set_ylabel("Relative plausibility")
    ax.set_title(
        "Where does the evidence put system pressure for this area?",
        fontsize=13,
        pad=10,
    )
    ax.set_xlim(
        min(samples.min(), THRESHOLD_BASELINE) - 0.35,
        max(samples.max(), THRESHOLD_ELEVATED) + 0.35,
    )

    ax.legend(loc="upper right", fontsize=8, framealpha=0.92)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return fig


@st.cache_data(show_spinner="Loading weekly panel…")
def load_weekly_data(path: str, _file_mtime: float) -> pd.DataFrame:
    return pd.read_csv(path)


@st.cache_resource(show_spinner="Loading cached posteriors…")
def load_posteriors(_cache_manager: CacheManager) -> az.InferenceData:
    """Load posteriors from cache (no MCMC, guaranteed)."""
    return _cache_manager.load_posteriors()


@st.cache_resource(show_spinner="Loading cached statistics…")
def load_summary_stats(_cache_manager: CacheManager) -> dict:
    """Load pre-computed summary statistics (instant access)."""
    return _cache_manager.load_summary_stats()


# -----------------------------------------------------------------------------
# Streamlit UI
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="System pressure — early signal (demo)")
st.title("NHS system pressure — early signal (demo)")
st.caption(
    "Helps teams ask: **How worried should we be, given the current evidence?** "
    "This is **decision support**, not a forecast, clinical guidance, or official NHS metric."
)

path = WEEKLY_CSV
mtime = os.path.getmtime(path) if os.path.isfile(path) else 0.0
df = load_weekly_data(path, mtime)

# Initialize cache manager
cache = CacheManager(posteriors_path=POSTERIORS_NC)

# Validate cache is ready
if not cache.is_valid():
    st.error(
        f"❌ Posterior cache is not ready\n\n"
        f"**Status:**\n"
        f"- Posterior available: {cache.is_posterior_available()}\n"
        f"- Cache warm: {cache.is_cache_warm()}\n\n"
        f"**Fix:**\n"
        f"```bash\n"
        f"python inference_daemon.py --once\n"
        f"```\n"
        f"or\n"
        f"```bash\n"
        f"python -c 'from cache_manager import CacheManager; CacheManager().warm_cache()'\n"
        f"```"
    )
    st.stop()

# Load from cache (guaranteed zero computation)
idata = load_posteriors(cache)
stats = load_summary_stats(cache)

with st.sidebar:
    st.header("Scope")
    icb = st.selectbox(
        "Geography",
        df["icb"].unique(),
        help="Synthetic demo panel; organisational names for grounding only.",
    )

    st.header("Display")
    credible_choice = st.radio(
        "Credible band on chart & summary",
        options=["90% (default)", "50% (tighter)"],
        index=0,
        help="Equal-tailed interval from the posterior — not a prediction interval.",
    )
    credible_mass = 0.9 if credible_choice.startswith("90") else 0.5

    show_median_line = st.checkbox(
        "Show median line on chart",
        value=True,
        help="Turn off for a more probability-first / interval-first visual.",
    )

    with st.expander("Assumptions & limits (serious deployments)", expanded=False):
        st.markdown(
            """
- **Reference line positions** (baseline / concern / high) are **fixed demo cut-points** on a **unitless model index**. They are **not** national operational thresholds.
- **Risk band** (Low / Medium / Elevated) is a **UI heuristic**, **not** validated against real escalation policy — **co-design with ops** to tune cut-offs (see Advanced).
- The index is **not calibrated** to NHS units; lean on **probabilities** and **credible intervals**, not the absolute value of the index.
            """
        )

    with st.expander("Advanced: risk band heuristics (probabilities)", expanded=False):
        st.caption("Thresholds on **posterior probabilities** for the summary label only.")
        c1, c2 = st.columns(2)
        with c1:
            pe_hi = st.number_input(
                "Elevated if P(high) ≥",
                min_value=0.0,
                max_value=1.0,
                value=DEFAULT_RISK_ELEVATED_TIER_MIN_P_HIGH,
                step=0.01,
                key="pe_hi",
            )
            pe_med = st.number_input(
                "Medium if P(high) ≥",
                min_value=0.0,
                max_value=1.0,
                value=DEFAULT_RISK_MEDIUM_TIER_MIN_P_HIGH,
                step=0.01,
                key="pe_med",
            )
        with c2:
            pc_hi = st.number_input(
                "… or P(concern) ≥",
                min_value=0.0,
                max_value=1.0,
                value=DEFAULT_RISK_ELEVATED_TIER_MIN_P_CONCERN,
                step=0.01,
                key="pc_hi",
            )
            pc_med = st.number_input(
                "… or P(concern) ≥",
                min_value=0.0,
                max_value=1.0,
                value=DEFAULT_RISK_MEDIUM_TIER_MIN_P_CONCERN,
                step=0.01,
                key="pc_med",
            )

subset = df[df["icb"] == icb]
icb_codes = subset["icb"].astype("category").cat.codes.values

# Extract posterior samples for this ICB from the pre-computed posteriors
samples = _pressure_index_samples(idata, int(icb_codes[0]))

p_above_baseline = float(np.mean(samples > THRESHOLD_BASELINE))
p_above_concern = float(np.mean(samples > THRESHOLD_CONCERN))
p_above_elevated = float(np.mean(samples > THRESHOLD_ELEVATED))
lo, mid, hi = _credible_triplet(samples, credible_mass)
cred_pct = int(credible_mass * 100)

risk_label, risk_hint = _risk_band(
    p_above_elevated,
    p_above_concern,
    pe_hi=pe_hi,
    pc_hi=pc_hi,
    pe_med=pe_med,
    pc_med=pc_med,
)

with st.container(border=True):
    st.subheader("Summary — current pressure risk (indicative)")
    c0, c1, c2, c3 = st.columns([1.1, 1, 1, 1.2])
    with c0:
        st.markdown(f"### {risk_label}")
        st.caption(risk_hint)
    with c1:
        st.metric(
            label="Chance pressure exceeds baseline reference",
            value=f"{p_above_baseline:.0%}",
            help="Posterior probability that the modelled index sits above the baseline reference line.",
        )
    with c2:
        st.metric(
            label="Chance pressure exceeds concern reference",
            value=f"{p_above_concern:.0%}",
        )
    with c3:
        st.metric(
            label="Chance pressure exceeds high reference",
            value=f"{p_above_elevated:.0%}",
            help="Stricter threshold on the same index — useful as a stronger (still non-clinical) flag.",
        )

    st.markdown(
        f"**{cred_pct}% plausible range** (equal-tailed) for the system pressure index: "
        f"**{lo:.2f}** to **{hi:.2f}** (median **{mid:.2f}**). "
        "This describes **where posterior mass sits**, not NHS-calibrated units. "
        "It is not a confidence interval on a future outcome."
    )

with st.expander("How this system updates its view of pressure", expanded=False):
    st.markdown(
        """
This system starts with a **baseline expectation** of NHS system pressure, informed by historical patterns and prior knowledge.

As new data arrive (e.g. bed occupancy, flow indicators, respiratory demand), the system:

- **Assesses** how consistent the new signals are with previous evidence  
- **Updates** its belief **gradually**, rather than jumping to conclusions  
- **Maintains uncertainty**, reflecting data gaps, noise, and disagreement between signals  

The result is a **probabilistic assessment** of current system pressure, **not a point prediction**.  
Strong or consistent evidence moves the estimate more; weak or noisy evidence moves it less.
        """
    )

st.markdown("---")
st.markdown("### Chart — what does the evidence say about pressure?")
st.caption(
    "Question answered: **How much posterior weight sits above routine vs elevated pressure?** "
    "Dashed lines are **demo reference** cut-points — not national operational thresholds."
)

fig = _plot_pressure_question(
    samples,
    credible_mass=credible_mass,
    show_median_line=show_median_line,
)
st.pyplot(fig, clear_figure=True)
plt.close(fig)

st.caption(
    f"Area: {icb}. Values to the right of the dashed references indicate stronger posterior "
    "support for elevated modelled pressure (given assumptions and available indicators in this demo)."
)

st.markdown(
    f"""
**Reading the chart:** The blue bars show which values of the **system pressure index** are most plausible **after** seeing bed occupancy in this area.  
The shaded band is the **{cred_pct}% plausible range** (see sidebar). Dashed lines are **demo reference levels** for conversation — they do not replace local judgement or official escalation rules.  
**Calibration:** The index is an internal model construct; interpret **probabilities and intervals**, not the numeric scale as an NHS operational measure.
    """
)

st.info(
    "**Uncertainty:** Spreads can reflect sparse weeks, conflicting signals, reporting gaps, and model simplifications. "
    "Use alongside operational intelligence and governance processes."
)
