# epiforecasts NHS Pressure Demo

Probabilistic, uncertainty-aware, synthetic-data demonstration for NHS-style system pressure analytics.

This repository is designed for safe experimentation, transparent communication, and collaborative engineering practice. It does not contain real patient-identifiable data.

## 1. Purpose

This project demonstrates how a Bayesian workflow can support conversation about system pressure in a way that:

1. shows uncertainty explicitly;
2. separates offline model inference from online user experience;
3. keeps governance and plain-language communication central.

## 2. What is in scope

In scope:

1. synthetic weekly panel generation;
2. Bayesian model fitting using PyMC;
3. cached posterior serving to Streamlit applications;
4. documentation for technical and non-technical audiences;
5. prototype governance framing.

Out of scope:

1. production clinical decision support;
2. live NHS integration;
3. validated operational thresholds;
4. patient-level inference.

## 3. Quick start

Install and run a development flow:

```bash
pixi install
pixi run dev
```

Run inference once and then launch the full dashboard:

```bash
pixi run daemon-once
pixi run run-dashboard
```

For full operational guidance, read [docs/40-operations/RUNBOOK.md](docs/40-operations/RUNBOOK.md).
For a minimal first run, read [docs/40-operations/FIRST_RUN_DUMMIES.md](docs/40-operations/FIRST_RUN_DUMMIES.md).

## 4. Repository structure

Core Python components:

1. [generate_synthetic_data.py](generate_synthetic_data.py)
2. [bayesian_pressure_model.py](bayesian_pressure_model.py)
3. [run_inference.py](run_inference.py)
4. [inference_daemon.py](inference_daemon.py)
5. [cache_manager.py](cache_manager.py)
6. [app.py](app.py)
7. [app_fast.py](app_fast.py)

Primary documentation home:

1. [docs/README.md](docs/README.md)
2. [docs/10-product/LAYPERSON_GUIDE.md](docs/10-product/LAYPERSON_GUIDE.md)
3. [docs/30-model/TECHNICAL_SUMMARY_ADVANCED.md](docs/30-model/TECHNICAL_SUMMARY_ADVANCED.md)
4. [docs/70-reference/glossary.md](docs/70-reference/glossary.md)

## 5. Documentation taxonomy migration plan

The documentation set is being normalised into a stable taxonomy:

1. `docs/00-overview`: orientation, scope, document map, migration notes;
2. `docs/10-product`: user and stakeholder explainers;
3. `docs/20-architecture`: software architecture and component contracts;
4. `docs/30-model`: statistical and methodological documentation;
5. `docs/40-operations`: runbooks, deployment and support;
6. `docs/50-governance`: safety, assurance, compliance artefacts;
7. `docs/60-contributing`: contribution, style, review standards;
8. `docs/70-reference`: glossary, references, assumptions register;
9. `docs/80-decisions`: architecture and model decision records;
10. `docs/90-changelog`: release and change history.

Migration principles:

1. each topic has one canonical home;
2. old pages become short stubs with links, then retire;
3. every page includes Audience, Purpose, Scope, Assumptions, Limitations, Owner, and References;
4. cross-links are mandatory for discoverability and handover;
5. unresolved terms are added to the glossary before merge.

Detailed plan: [docs/00-overview/DOCS_TAXONOMY_MIGRATION_PLAN.md](docs/00-overview/DOCS_TAXONOMY_MIGRATION_PLAN.md).
High-level structure options: [docs/00-overview/FOLDER_STRUCTURE_OPTIONS.md](docs/00-overview/FOLDER_STRUCTURE_OPTIONS.md).

## 6. Collaboration standards

Before submitting changes:

1. read [CONTRIBUTING.md](CONTRIBUTING.md);
2. apply [docs/60-contributing/style-guide.md](docs/60-contributing/style-guide.md);
3. use shared terminology in [docs/70-reference/glossary.md](docs/70-reference/glossary.md);
4. support claims with evidence from [docs/70-reference/references.md](docs/70-reference/references.md).

## 7. Audience pathways

1. Non-technical readers: [docs/10-product/LAYPERSON_GUIDE.md](docs/10-product/LAYPERSON_GUIDE.md)
2. Delivery and governance teams: [docs/50-governance/GOVERNANCE_OVERVIEW.md](docs/50-governance/GOVERNANCE_OVERVIEW.md)
3. Engineers and analysts: [docs/30-model/TECHNICAL_SUMMARY_ADVANCED.md](docs/30-model/TECHNICAL_SUMMARY_ADVANCED.md)
4. Operators: [docs/40-operations/RUNBOOK.md](docs/40-operations/RUNBOOK.md)

## 8. Current status

This repository is a prototype and communication artefact for collaborative design and safe experimentation. It is not production-authorised clinical software.

Release tracking: [CHANGELOG.md](CHANGELOG.md)

