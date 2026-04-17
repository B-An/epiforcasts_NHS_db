# Governance sense-check — Discovery framing and beyond

This note **does not** replace legal, IG, or clinical sign-off. It summarises **limitations**, **risks if scope grows**, and **proportionate** next steps. Prefer **calibrated, auditable** progress over novelty or scale.

---

## 1. Is the approach appropriate?

**Partly, for Discovery.** A **Bayesian, latent-state** view is a **reasonable** way to foreground **uncertainty** in **system** pressure analytics when the goal is exploration and transparency, not a single point forecast.

**Caveats in the current artefact:**

- The model is only **lightly hierarchical**; fitting on a **single-ICB** subset **collapses** the intended national/ICB separation (see [TECHNICAL_OVERVIEW.md](TECHNICAL_OVERVIEW.md)).
- **Only bed occupancy** is fitted; other simulated signals are unused.
- The **synthetic generator** uses **time-structured** latent dynamics; the fitted model does **not** — so “validation on synthetic data” is **misleading** unless generator and model are aligned.

**Conclusion:** The **concept** (Bayesian latent pressure + uncertainty) fits an NHS **system analytics** narrative; the **implementation** is a **prototype** where statistical narrative and UI metrics need tightening before stronger claims.

---

## 2. Main assumptions and fragility

| Area | What is assumed | Fragility |
|------|------------------|-----------|
| Data | Beds as proxy; complete/representative series | **High** with real ops data (definitions, lag, site mix) |
| Likelihood | Gaussian beds, linear link | **High** (bounds, skew; mismatch to generator) |
| Time | Effectively IID over weeks | **High** (real pressure is autocorrelated) |
| Multivariate | Other signals irrelevant | **Medium–high** (111/DToC simulated but unused) |
| Priors | Scale on **unitless** latent | **Medium** — not elicited from NHS units |
| Pooling | Partial pooling when jointly fitting ICBs | **Context-dependent** — per-ICB UI removes cross-ICB learning |
| “Unsafe” threshold | e.g. `latent > 1.1` | **Very high** — **uncalibrated** |
| MCMC | Single chain in code | **Medium** for Discovery; **high** if outputs are treated as assured |

**Most fragile:** unvalidated **threshold** and **wording** (“unsafe”); **structural** mismatch (time + multivariate neglect); interpretation of **`mu_national`** on a single-ICB slice.

---

## 3. Risks if extended beyond Discovery

- **Decision support:** Any headline probability can be read as a **trigger** for action without calibration, ownership, or documented limits — **accountability and assurance** risk.
- **Equity:** Models can encode **reporting bias** or historical resourcing patterns; cross-area comparison needs explicit **bias and coverage** analysis.
- **Transparency:** Clear boundary — **not** patient-level clinical AI; **system analytics** still needs IG/DPIA if non-synthetic or identifiable operational data appear.
- **Overconfidence:** Omitting diagnostics, data lineage, and limits undermines **auditability** and responsible use.

---

## 4. Sensible next directions

### A. Strengthen the statistical story (still Discovery-friendly)

Align **generator ↔ model** (or simplify the generator), add **time** structure, optionally **joint** use of multiple indicators, and **multiple chains + diagnostics** in development.

- **Discovery-safe:** Yes, as research code and internal demos.
- **Stronger bar:** External claims of “validated” forecasting need **pre-specified** evaluation and documented **limitations**.

### B. Governance-friendly framing

Rename outputs to a **model-defined index (uncalibrated)**; show **intervals**; treat thresholds as **explicitly configurable** and **non-official** unless co-signed. Co-design **language** with ops/clinical informatics.

- **Discovery-safe:** Yes.
- **Stronger bar:** **Operational** use needs agreed **human decision paths**, escalation, and **logging** (who saw what, when).

### C. Evidence path (Alpha / beyond)

Backtesting against agreed **operational outcomes**, **calibration**, **change control** (model version, data version).

- **Discovery-safe:** Methods design and dry-runs on synthetic or anonymised aggregates.
- **Stronger bar:** Real operational data, cross-system deployment, or use affecting **funding/performance** → **DPIA**, equality impact, appropriate **clinical/operational** sign-off, **audit trails**.

---

## 5. Where human judgement must stay

- What “unsafe” or “elevated pressure” **means** operationally.
- Whether any number should **trigger** action.
- Which data are **legitimate and fair** for comparison across geographies.
- How to respond when the model is **uncertain** or **conflicts** with local intelligence.
- Any step toward **resourcing, triage, or performance management** from model outputs.

---

## Related documents

- [User explainer](USER_EXPLAINER.md)
- [Technical overview](TECHNICAL_OVERVIEW.md)
- [Interaction log](../INTERACTION_LOG.md)
