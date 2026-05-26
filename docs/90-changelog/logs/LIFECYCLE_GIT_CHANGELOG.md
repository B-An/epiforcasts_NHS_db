# Lifecycle Git Changelog (Single Source)

## Purpose

This document is the single, complete record of git lifecycle changes for this repository up to the latest commit listed below.

Scope:
- Root repository commit history only.
- Includes commit metadata and file-level change deltas.
- Includes key project decisions reflected by those commits.

As-of commit:
- `a73194d45c1f4e83d7289e2d24986c03994faa4e`

---

## Lifecycle Decisions Summary

1. Initial baseline established with core Bayesian demo app, model, docs, and synthetic dataset.
2. Repository expanded into full documentation taxonomy and operational structure.
3. Architecture and rationale evidence pack made explicit in canonical docs.
4. Technical summary simplified for readability and decision clarity.
5. Runtime stability improved in inference and Streamlit cache paths.
6. Robustness hardening added deterministic fallback behavior, one-command health checks, and CI smoke workflow.
7. Added measurable acceptance gates (artifact, metadata, governance-document, and ignore-policy checks) to support defensible robustness scoring.

Pending working-tree updates (not yet represented as a git commit in this ledger):
- Added `acceptance_check.py` and CI acceptance gate execution.
- Added `docs/50-governance/ROBUSTNESS_TARGET_95.md` with per-dimension measurable checks.
- Added `pixi` one-command `acceptance-check` task.

---

## Complete Commit Ledger (Chronological)

### 1) d31d0cf1648d21772c96f9197a269ffd920bd814
- Date: 2026-04-17 14:22:05 +0100
- Author: An Te
- Message: closer final version made at this time
- Change type summary: initial repository baseline

File-level delta:
- A .cursor/rules/epiforcasts-demo-bayesian.mdc
- A .gitattributes
- A .gitignore
- A INTERACTION_LOG.md
- A README.md
- A RULES_CURSOR_NHS.md
- A __pycache__/bayesian_pressure_model.cpython-314.pyc
- A app.py
- A bayesian_pressure_model.py
- A docs/GOVERNANCE_SENSE_CHECK.md
- A docs/README.md
- A docs/TECHNICAL_OVERVIEW.md
- A docs/USER_EXPLAINER.md
- A generate_synthetic_data.py
- A pixi.toml
- A synthetic_nhs_pressure.csv

### 2) 2efcc3c787ac3969e3d92d87027fec84af1d71f9
- Date: 2026-05-21 10:02:39 +0100
- Author: An Te
- Message: Auto-generated: update scripts, documentation, and configuration files
- Change type summary: major repo expansion and documentation taxonomy rollout

File-level delta:
- M .cursor/rules/epiforcasts-demo-bayesian.mdc
- A .github/ISSUE_TEMPLATE/bug_report.md
- A .github/ISSUE_TEMPLATE/config.yml
- A .github/ISSUE_TEMPLATE/documentation_request.md
- A .github/ISSUE_TEMPLATE/feature_request.md
- A .github/pull_request_template.md
- A CHANGELOG.md
- A CONTRIBUTING.md
- A EpiNow2
- M README.md
- M __pycache__/bayesian_pressure_model.cpython-314.pyc
- A __pycache__/cache_manager.cpython-314.pyc
- M app.py
- A app_fast.py
- M bayesian_pressure_model.py
- A cache_manager.py
- A docs/00-overview/DOCS_TAXONOMY_MIGRATION_PLAN.md
- A docs/00-overview/FOLDER_STRUCTURE_OPTIONS.md
- A docs/00-overview/README.md
- A docs/00-overview/legacy-redirects/OFFLINE_INFERENCE.md
- A docs/00-overview/legacy-redirects/QUICKRUN.md
- A docs/00-overview/legacy-redirects/QUICK_START.md
- A docs/00-overview/legacy-redirects/README.md
- A docs/10-product/LAYPERSON_GUIDE.md
- A docs/20-architecture/README.md
- A docs/20-architecture/cache/CACHE_LAYER.md
- A docs/20-architecture/cache/README.md
- A docs/20-architecture/oop/CODE_EXAMPLES_OOP.md
- A docs/20-architecture/oop/OOP_DESIGN_ANALYSIS.md
- A docs/20-architecture/oop/README.md
- A docs/30-model/README.md
- A docs/30-model/TECHNICAL_SUMMARY_ADVANCED.md
- A docs/30-model/classDiagram.mmd
- A docs/40-operations/FIRST_RUN_DUMMIES.md
- A docs/40-operations/PYTENSOR_COMPILER.md
- A docs/40-operations/README.md
- A docs/40-operations/RUNBOOK.md
- A docs/50-governance/GOVERNANCE_OVERVIEW.md
- A docs/50-governance/README.md
- A docs/50-governance/policies/README.md
- R100 RULES_CURSOR_NHS.md -> docs/50-governance/policies/RULES_CURSOR_NHS.md
- A docs/60-contributing/README.md
- A docs/60-contributing/retrospectives/LESSONS_FOR_NEXT_PROJECT.md
- A docs/60-contributing/retrospectives/README.md
- A docs/60-contributing/style-guide.md
- A docs/70-reference/assumptions-register.md
- A docs/70-reference/glossary.md
- A docs/70-reference/references.md
- A docs/80-decisions/ADR-0001-taxonomy-and-canonical-docs.md
- A docs/80-decisions/ADR_TEMPLATE.md
- A docs/80-decisions/README.md
- A docs/90-changelog/README.md
- R070 INTERACTION_LOG.md -> docs/90-changelog/logs/INTERACTION_LOG.md
- A docs/90-changelog/logs/README.md
- M docs/GOVERNANCE_SENSE_CHECK.md
- M docs/README.md
- M docs/TECHNICAL_OVERVIEW.md
- M docs/USER_EXPLAINER.md
- M generate_synthetic_data.py
- A inference_daemon.log
- A inference_daemon.py
- M pixi.toml
- A run_inference.py
- M synthetic_nhs_pressure.csv
- A synthetic_patient_episodes.csv

### 3) a69fb2f2ca4332660e00096038eabf1daaefbcc2
- Date: 2026-05-26 16:38:00 +0100
- Author: An Te
- Message: docs: add architecture and rationale evidence pack
- Change type summary: architecture and governance evidence strengthening

File-level delta:
- M README.md
- M docs/20-architecture/README.md
- M docs/30-model/TECHNICAL_SUMMARY_ADVANCED.md
- M docs/50-governance/GOVERNANCE_OVERVIEW.md
- M docs/70-reference/assumptions-register.md
- M docs/70-reference/references.md
- M docs/README.md

### 4) fcdc3420f042f8c499760a4a61ff2de28a88d109
- Date: 2026-05-26 16:46:10 +0100
- Author: An Te
- Message: docs: simplify technical summary
- Change type summary: simplification and clarity improvement

File-level delta:
- M docs/30-model/TECHNICAL_SUMMARY_ADVANCED.md

### 5) ccf7438f8b7c55adaec86f8e1e41364b0a455954
- Date: 2026-05-26 19:00:34 +0100
- Author: An Te
- Message: fix: stabilize inference and streamlit cache handling
- Change type summary: runtime stability fixes in inference and dashboard caching

File-level delta:
- M .cursor/rules/epiforcasts-demo-bayesian.mdc
- A AGENTS.md
- M app.py
- M app_fast.py
- M run_inference.py

### 6) a73194d45c1f4e83d7289e2d24986c03994faa4e
- Date: 2026-05-26 19:40:41 +0100
- Author: An Te
- Message: Harden inference fallback, add health checks, and CI smoke workflow
- Change type summary: robustness hardening and release safeguards

File-level delta:
- A .github/workflows/smoke-check.yml
- M .gitignore
- M README.md
- A health_check.py
- M pixi.toml
- M run_inference.py

---

## Notes for Audit Clarity

- `EpiNow2` appears in the root repository history as an added path in commit `2efcc3c...`; it is a nested repository path and can have its own independent git history.
- This document is intentionally complete but simple: one place to trace what changed, when, and why.
