"""
Fast serving UI for pre-computed posteriors.

Minimal overhead version that loads only cached results.
Ideal for dashboards, read-only access, or high-traffic scenarios.

Compare to app.py:
- app.py: Full UI with tuning, data loading, comprehensive explainers
- app_fast.py: Lightweight display of current estimates only

Usage:
    streamlit run app_fast.py
"""

import os

# Headless backend
os.environ.setdefault("MPLBACKEND", "Agg")

from pathlib import Path
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import arviz as az

from cache_manager import CacheManager

POSTERIORS_NC = "posteriors.nc"

# Fixed thresholds (not tunable in fast path)
THRESHOLD_BASELINE = 0.0
THRESHOLD_CONCERN = 0.5
THRESHOLD_ELEVATED = 1.1

DEFAULT_RISK_ELEVATED_TIER_MIN_P_HIGH = 0.25
DEFAULT_RISK_ELEVATED_TIER_MIN_P_CONCERN = 0.55
DEFAULT_RISK_MEDIUM_TIER_MIN_P_HIGH = 0.08
DEFAULT_RISK_MEDIUM_TIER_MIN_P_CONCERN = 0.30


def _pressure_index_samples(idata: az.InferenceData, icb_idx: int) -> np.ndarray:
    """Extract posterior samples for a given ICB."""
    post = idata.posterior
    mu = post["mu_national"].values
    eff = post["icb_effect"].values
    sig = post["sigma_icb"].values
    combined = mu + eff[..., icb_idx] * sig
    return combined.astype(float).ravel()


def _credible_triplet(samples: np.ndarray, mass: float = 0.9) -> tuple[float, float, float]:
    """Equal-tailed interval."""
    alpha = (1.0 - mass) / 2.0
    lo, mid, hi = [
        float(x)
        for x in np.percentile(samples, [100.0 * alpha, 50.0, 100.0 * (1.0 - alpha)])
    ]
    return lo, mid, hi


def _risk_band_summary(
    p_elevated: float,
    p_concern: float,
) -> tuple[str, str]:
    """Simple risk classification."""
    if p_elevated >= DEFAULT_RISK_ELEVATED_TIER_MIN_P_HIGH or p_concern >= DEFAULT_RISK_ELEVATED_TIER_MIN_P_CONCERN:
        return "🔴 Elevated", "Prioritise review of capacity and escalation plans."
    if p_elevated >= DEFAULT_RISK_MEDIUM_TIER_MIN_P_HIGH or p_concern >= DEFAULT_RISK_MEDIUM_TIER_MIN_P_CONCERN:
        return "🟡 Medium", "Worth closer monitoring."
    return "🟢 Low", "No strong signal of elevated pressure."


def _plot_minimal(samples: np.ndarray) -> plt.Figure:
    """Minimal histogram for fast rendering."""
    lo, mid, hi = _credible_triplet(samples, 0.9)
    
    fig, ax = plt.subplots(figsize=(10, 3), layout="constrained")
    ax.hist(
        samples,
        bins=40,
        density=True,
        alpha=0.75,
        color="#1d4ed8",
        edgecolor="white",
        linewidth=0.5,
    )
    
    ax.axvspan(lo, hi, alpha=0.15, color="#1e3a8a", label="90% plausible range")
    ax.axvline(THRESHOLD_BASELINE, color="#64748b", linestyle="--", linewidth=1.2, label="Baseline")
    ax.axvline(THRESHOLD_CONCERN, color="#d97706", linestyle="--", linewidth=1.2, label="Concern")
    ax.axvline(THRESHOLD_ELEVATED, color="#b91c1c", linestyle="--", linewidth=1.2, label="High pressure")
    
    ax.set_xlabel("System pressure index (unitless model)")
    ax.set_ylabel("Plausibility")
    ax.set_title(f"Where does evidence put pressure? (median: {mid:.2f})", fontsize=11)
    ax.legend(loc="upper right", fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    return fig


@st.cache_resource(show_spinner="Loading cached posteriors…")
def load_posteriors(_cache_manager: CacheManager) -> az.InferenceData:
    """Load posteriors from cache (no MCMC, guaranteed)."""
    return _cache_manager.load_posteriors()


@st.cache_resource(show_spinner="Loading cached statistics…")
def load_summary_stats(_cache_manager: CacheManager) -> dict:
    """Load pre-computed summary statistics (instant access)."""
    return _cache_manager.load_summary_stats()


def get_last_update_time(path: str) -> str:
    """Get human-readable last update time."""
    if not Path(path).exists():
        return "never"
    mtime = Path(path).stat().st_mtime
    from datetime import datetime
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S UTC")


# ============================================================================
# UI
# ============================================================================

st.set_page_config(layout="wide", page_title="NHS Pressure — Fast View (demo)")
st.title("🏥 NHS System Pressure — Current Status (demo)")
st.caption(
    "**Read-only fast view** | Updated automatically in background. "
    "[Full interactive version →](http://localhost:8501) "
    "| [Docs →](OFFLINE_INFERENCE.md)"
)

# Initialize cache manager
cache = CacheManager(posteriors_path=POSTERIORS_NC)

# Validate cache is ready (no MCMC runs guaranteed here)
if not cache.is_valid():
    st.error(
        f"❌ Cache not ready\n\n"
        f"**Status:** Posterior {'✓' if cache.is_posterior_available() else '✗'} | "
        f"Cache {'✓' if cache.is_cache_warm() else '✗'}\n\n"
        f"**Run:** `python inference_daemon.py --once`"
    )
    st.stop()

# Load from cache (guaranteed zero computation)
idata = load_posteriors(cache)
stats = load_summary_stats(cache)
last_update = get_last_update_time(POSTERIORS_NC)

# Get ICB list from metadata
icbs = idata.attrs.get("icbs", [])
if not icbs:
    st.error("No ICB metadata in posterior file. Please regenerate.")
    st.stop()

# Sidebar: quick select
with st.sidebar:
    st.header("⚡ Quick Select")
    selected_icb = st.radio(
        "Geography",
        options=icbs,
        label_visibility="collapsed",
    )
    
    st.divider()
    st.caption(f"**Last updated:** {last_update}")
    st.caption(f"**Posterior samples:** {int(idata.posterior.dims.get('draw', 0)):,}")
    st.caption(f"**Geographic areas:** {len(icbs)}")

# Main display
icb_idx = icbs.index(selected_icb)
samples = _pressure_index_samples(idata, icb_idx)

p_above_baseline = float(np.mean(samples > THRESHOLD_BASELINE))
p_above_concern = float(np.mean(samples > THRESHOLD_CONCERN))
p_above_elevated = float(np.mean(samples > THRESHOLD_ELEVATED))

lo, mid, hi = _credible_triplet(samples, 0.9)
risk_label, risk_hint = _risk_band_summary(p_above_elevated, p_above_concern)

# Summary card
with st.container(border=True):
    col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1])
    
    with col1:
        st.markdown(f"## {risk_label}")
        st.caption(risk_hint)
    
    with col2:
        st.metric(
            label="P(baseline)",
            value=f"{p_above_baseline:.0%}",
            delta="threshold: 0.0",
        )
    
    with col3:
        st.metric(
            label="P(concern)",
            value=f"{p_above_concern:.0%}",
            delta="threshold: 0.5",
        )
    
    with col4:
        st.metric(
            label="P(high)",
            value=f"{p_above_elevated:.0%}",
            delta="threshold: 1.1",
        )

st.markdown(
    f"**90% plausible range:** {lo:.2f} — {hi:.2f} "
    f"(median {mid:.2f}). Not NHS-calibrated units."
)

# Chart
st.markdown("### Evidence Distribution")
fig = _plot_minimal(samples)
st.pyplot(fig, use_container_width=True)
plt.close(fig)

# Footer
st.divider()
st.caption(
    f"**Area:** {selected_icb} | "
    f"**Model:** Latent pressure on bed occupancy (demo only) | "
    f"[Docs](OFFLINE_INFERENCE.md) | [Full UI](http://localhost:8501)"
)
