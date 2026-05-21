# Interaction & audit log — epiforcasts NHS pressure demo

**Related documents:** [docs/README.md](docs/README.md) (index), [docs/10-product/LAYPERSON_GUIDE.md](docs/10-product/LAYPERSON_GUIDE.md), [docs/30-model/TECHNICAL_SUMMARY_ADVANCED.md](docs/30-model/TECHNICAL_SUMMARY_ADVANCED.md), [docs/50-governance/GOVERNANCE_OVERVIEW.md](docs/50-governance/GOVERNANCE_OVERVIEW.md).

**Purpose:** Human-maintained record of **who did what**, **where** (code, git, app), and **why**, for auditability and handover. This does **not** replace Git history; it adds **context** Git cannot store (app usage intent, Cursor sessions, governance notes).

**How to use:** Append a new row under the right section when something meaningful happens. Prefer **dated** entries and **no patient-identifiable** content.

---

## 1. Codebase & Git interactions

| Date (UTC) | Actor | Action | Files / scope | Notes |
|------------|-------|--------|----------------|-------|
| _example_ | _name / role_ | _commit, PR, branch_ | _paths_ | _rationale, ticket_ |

**Git note:** While this directory is **untracked** in the parent `.dotfiles` repo, `git log` will not show file-specific history here. After `git add` / first commit including this folder, use `git log -- epiforcasts_NHS_db` (from repo root) for file-level history. Record **merge decisions** and **release tags** here in plain language.

---

## 2. App-facing interactions (Streamlit / deployment)

Use for: demo sessions, **who** ran the app for **which audience** (internal demo, training), configuration changes, incidents.

| Date (UTC) | Actor / audience | Environment | Action | Notes |
|------------|------------------|---------------|--------|-------|
| _example_ | _e.g. team demo_ | _local / URL_ | _e.g. reviewed ICB selector_ | _no PII; purpose of session_ |

**Not logged automatically today:** Streamlit Community / local `streamlit run` does not write an audit trail of “who opened the app” unless you add instrumentation (see suggestions below).

---

## 3. Tooling & AI-assisted work (optional)

Optional short notes when significant **Cursor / agent** or **pair-programming** sessions change behaviour or assumptions (no need to log every keystroke).

| Date (UTC) | Tool / channel | Summary | Link / commit |
|------------|----------------|---------|---------------|
| 2026-04-17 | Cursor | Project rule added: `.cursor/rules/epiforcasts-demo-bayesian.mdc` | — |
| 2026-04-17 | Cursor | Docs added: `docs/USER_EXPLAINER.md`, `TECHNICAL_OVERVIEW.md`, `GOVERNANCE_SENSE_CHECK.md`, `docs/README.md` | — |
| 2026-04-17 | Cursor | Expanded `generate_synthetic_data.py`: many weekly features + `synthetic_patient_episodes.csv`; `TECHNICAL_OVERVIEW` updated | — |
| 2026-04-17 | Cursor | `SIMULATION_REPLICATES=100`, shared latent `lp` weekly/episodes, `MEASUREMENT_NOISE_SCALE`; `app.py` filters replicate 0 | — |
| 2026-04-17 | Cursor | Removed Monte Carlo replicates; standalone panel: `NUM_INDEPENDENT_ICBS` x `N_WEEKS`, independent RNG per ICB; dropped `simulation_replicate_id` | — |
| 2026-04-17 | Cursor | Real NHS ICB labels in `ICBS`; `N_WEEKS=156`; app `cache_data`+mtime, Agg backend, fast PyMC; `PRESSURE_MODEL_FAST` | — |
| 2026-04-17 | Cursor | `pixi.toml`: `cxx-compiler`, `platforms`; added `docs/PYTENSOR_COMPILER.md` | — |
| 2026-04-17 | Cursor | `app.py`: decision-first UI, pressure index, refs, 90% range, Bayesian explainer; `pm.sample` uses draws/tune vars | — |
| 2026-04-17 | Cursor | `app.py`: sidebar (cred 50/90%, median line, assumptions, advanced risk heuristics); explicit demo/non-calibration copy | — |

---

## Suggested improvements (governance & operability)

1. **Track this folder in Git** when ready, so authorship and diffs are authoritative; keep this log for narrative and app/demo context.
2. **App-side logging (if you need it):** Only with **IG sign-off** — e.g. append-only **anonymous** event log (timestamp, event type: `model_run`, `icb_changed`) to a secured sink; **avoid** logging free text or identifiable geography if combined with other data. For local demos, **manual** rows in section 2 are often enough.
3. **Streamlit / hosting:** If deployed, use **platform logs** (reverse proxy, auth layer) for access audit; document retention in a DPIA if not purely local synthetic data.
4. **CHANGELOG.md:** For **versioned** user-visible or model-behaviour changes, add a short `CHANGELOG.md` and reference it from PRs (see `docs/50-governance/policies/RULES_CURSOR_NHS.md` if you adopt that rigour).

---

## Append new entries below

_(Add rows to sections 1–3 as events occur.)_
