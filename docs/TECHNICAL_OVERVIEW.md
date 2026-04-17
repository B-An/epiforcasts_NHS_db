# Technical overview — code, model, and assumptions

This document describes how `generate_synthetic_data.py`, `bayesian_pressure_model.py`, and `app.py` work together, including **assumptions** and **parameter choices**. Paths are relative to the project root.

---

## 1. Data generation — `generate_synthetic_data.py`

### Purpose

Produce `synthetic_nhs_pressure.csv` so the app can run without real operational data.

### Behaviour

- For each named ICB, a **latent “pressure”** is simulated as a **cumulative random walk** plus a fixed **scale** per ICB (`ICBS` dict).
- That latent drives:
  - **111-style counts** — negative binomial,
  - **bed occupancy (%)** — linear in latent plus Gaussian noise, **clipped** to `[70, 100]`,
  - **DToC-style counts** — Poisson with rate tied to latent.
- Some **missing** values are applied to `resp_111_calls` (six random rows per ICB).
- Rows for **England** are added by averaging ICB numeric columns by `week`.

### Assumptions

- The generative process is a **toy**; not calibrated to real NHS reporting definitions or lags.
- The synthetic world has **time structure** (random-walk latent); the **fitted model does not** use that time structure (see §2).

### Notable parameter choices

| Item | Value | Role |
|------|--------|------|
| `np.random.seed(2026)` | fixed | Reproducible demo data |
| `N_WEEKS` | 80 | Length of each series |
| ICB scales | e.g. `1.0`, `1.3`, `0.9` | Arbitrary cross-area heterogeneity |
| Bed clip | `70`–`100` | Crude realism for occupancy % |

---

## 2. Bayesian model — `bayesian_pressure_model.py`

### Purpose

Fit a **Bayesian** model mapping observed **bed occupancy** to a **low-dimensional latent** “pressure” with **national** and **ICB** random effects.

### Structure (conceptual)

- `mu_national` — scalar latent, prior `Normal(0, 1)`.
- `icb_effect` — one effect per **distinct** ICB category in the input frame, prior `Normal(0, 1)` with shape `K = len(unique(icb_codes))`.
- `sigma_icb` — `Exponential(1)` scales ICB deviations.
- **Latent:** `latent_pressure = mu_national + icb_effect[icb_codes] * sigma_icb`.
- **Likelihood:** `bed_obs ~ Normal(mu = 85 + latent_pressure * 6, sigma = sigma_obs)` with `sigma_obs ~ Exponential(5)`.

### Sampling

- `pm.sample(draws=1000, tune=1000, chains=1, cores=1, …)` — inexpensive for a demo; **single chain** limits standard MCMC diagnostic practice.

### Assumptions

- **Gaussian** observation model on bed occupancy; **IID** across rows (no explicit **time series** structure in the likelihood).
- **Only** `bed_occupancy` is used; `resp_111_calls` and `dtoc_patients` are **not** in the likelihood (even though they exist in the CSV).
- **Linearity** `85 + 6 * latent_pressure`: intercept and slope are **fixed**, not learned, and they **do not match** the synthetic generator (`84 + latent * 7`).

### Interpretation caveat (single-ICB subset)

When `app.py` passes a dataframe with **one** ICB, `K = 1`. The “national vs ICB” split is then **not** identifiable in the intuitive way: you are effectively fitting a **single** combined latent structure for that slice. The UI still labels output around `mu_national`, which can **read** as a national quantity even when the fit is **local** to one area.

---

## 3. Application — `app.py`

### Purpose

**Streamlit** UI: load CSV, filter by selected `icb`, run **`fit_pressure_model`** (cached via `@st.cache_resource`), display:

- `prob_unsafe = mean(latent > 1.1)` where `latent` is the posterior of `mu_national`,
- a posterior plot for `mu_national` via ArviZ.

### Assumptions and implementation notes

- **`1.1` is an arbitrary threshold** on the **unitless** latent scale — not calibrated to any operational “unsafe” definition.
- **`st.cache_resource`** caches by the `df` argument; code or data changes may require a **cache clear** in Streamlit to avoid stale runs.
- The headline metric is formally **P(mu_national > 1.1 | model, data subset)** under the stated priors and likelihood — **not** a validated operational risk probability.

---

## 4. Cross-cutting limitations

| Topic | Issue |
|--------|--------|
| Generator vs model | Different **equations** and **no** use of time in the fit |
| Multivariate data | Extra columns in CSV are **ignored** by the fit |
| Threshold | **Demo only** — needs co-design for any real use |
| Hierarchy | Per-ICB UI subset **collapses** partial pooling for that run |

For governance-oriented discussion and next steps, see [GOVERNANCE_SENSE_CHECK.md](GOVERNANCE_SENSE_CHECK.md).
