# Governance Overview

## Audience

Governance leads, delivery managers, and technical contributors.

## Purpose

Summarise governance posture, decision boundaries, and evidence expectations for this prototype.

## Scope

In scope:

1. governance posture for architecture and communication;
2. risk-to-control mappings;
3. evidence requirements for defensible statements.

Out of scope:

1. formal regulatory submission pack;
2. production clinical safety case approval.

## Safety boundary

1. This repository is a prototype.
2. Outputs are analytical signals, not clinical instructions.
3. Human judgement remains mandatory.

## Governance controls in current state

1. Synthetic data only.
2. Explicit non-operational framing in user-facing language.
3. Separation of offline inference and online presentation.
4. Assumptions tracked in a dedicated register.

## Architecture-governance traceability

| Architecture element | Governance risk | Control | Evidence source |
| --- | --- | --- | --- |
| Offline inference and online serving split | Hidden runtime computation may reduce interpretability and reliability. | UI path constrained to cache-backed artifacts; remediation guidance when cache invalid. | [../20-architecture/cache/CACHE_LAYER.md](../20-architecture/cache/CACHE_LAYER.md), [../40-operations/RUNBOOK.md](../40-operations/RUNBOOK.md) |
| Probabilistic pressure outputs | Deterministic interpretation of uncertain estimates. | Probability-first language and mandatory caveats in core docs and dashboards. | [../30-model/TECHNICAL_SUMMARY_ADVANCED.md](../30-model/TECHNICAL_SUMMARY_ADVANCED.md), [../10-product/LAYPERSON_GUIDE.md](../10-product/LAYPERSON_GUIDE.md) |
| Reference lines in visualisations | Misread as policy or escalation thresholds. | Explicit statement that lines are communication aids only; assumptions tracking. | [../70-reference/assumptions-register.md](../70-reference/assumptions-register.md) |
| Prototype status | Treated as production-ready forecasting system. | Scope/non-scope statements across top-level and canonical docs. | [../../README.md](../../README.md), [../README.md](../README.md) |

## Key governance risks

1. Thresholds being interpreted as policy triggers.
2. Prototype outputs being treated as validated forecasts.
3. Terminology drift between technical and non-technical audiences.

## Mitigations

1. Glossary-locked terms.
2. Mandatory caveats in dashboards and documentation.
3. Evidence-first references and review checks.
4. Clear scope and non-scope statements in every key document.

## Evidence standards for claims

1. Any governance-sensitive claim must link to at least one canonical document and one assumptions entry.
2. Any claim suggesting operational readiness must include explicit validation evidence and reviewer sign-off.
3. Any threshold-related language must include non-policy caveats unless an approved decision record states otherwise.

## Decision boundary

This prototype is an analytical support artefact for discussion and review.
It is not authorised for unsupervised operational or clinical decision-making.

## Related links

1. previous governance sense-check: ../GOVERNANCE_SENSE_CHECK.md
2. assumptions register: ../70-reference/assumptions-register.md
3. references: ../70-reference/references.md
4. style guide: ../60-contributing/style-guide.md
5. architecture and rationale: ../20-architecture/README.md
6. operations runbook: ../40-operations/RUNBOOK.md

## Last updated

2026-05-26
