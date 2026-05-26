# Assumptions Register

## Audience

Engineering, governance, and delivery stakeholders.

## Purpose

Track explicit assumptions so decisions are reviewable and updates are controlled.

## Register

| ID | Assumption | Type | Impact if wrong | Validation approach | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| A-001 | Synthetic data structure is sufficient for demonstration narratives. | Methodological | Misleading confidence in real-world transferability. | Compare narrative claims against real aggregate patterns before any operational pilot. | Engineering lead | Open |
| A-002 | Threshold reference lines are communication aids only. | Communication | Stakeholders may misread as policy triggers. | Prominent caveats in UI and docs; stakeholder walkthrough. | Product owner | Open |
| A-003 | Zero-MCMC serving improves reliability for user sessions. | Technical | UI latency and instability under load. | Load test cached path; monitor startup and render timings. | Operations lead | Open |
| A-004 | Single-chain fast inference is acceptable for prototype cycles. | Statistical | Under-detected convergence issues. | Use multi-chain diagnostics in periodic full runs. | Modelling lead | Open |
| A-005 | Organisational labels in synthetic data do not create governance confusion. | Governance | Readers infer live NHS linkage. | Label controls in README, UI text, and lay-person guide. | Governance lead | Open |

## Architecture control mapping

| Assumption ID | Architecture dependency | Primary control | Supporting evidence |
| --- | --- | --- | --- |
| A-001 | Synthetic-data evidence layer | Explicit scope boundary and transferability caveats. | [../../README.md](../../README.md), [../20-architecture/README.md](../20-architecture/README.md) |
| A-002 | UI communication and reference lines | Mandatory wording that lines are communication aids, not policy triggers. | [../10-product/LAYPERSON_GUIDE.md](../10-product/LAYPERSON_GUIDE.md), [../50-governance/GOVERNANCE_OVERVIEW.md](../50-governance/GOVERNANCE_OVERVIEW.md) |
| A-003 | Cache-backed serving contract | Cache validity checks and fail-fast behaviour on invalid state. | [../20-architecture/cache/CACHE_LAYER.md](../20-architecture/cache/CACHE_LAYER.md), [../40-operations/RUNBOOK.md](../40-operations/RUNBOOK.md) |
| A-004 | Fast-mode inference strategy | Scheduled full diagnostics and explicit fast-mode caveats. | [../30-model/TECHNICAL_SUMMARY_ADVANCED.md](../30-model/TECHNICAL_SUMMARY_ADVANCED.md) |
| A-005 | Audience interpretation boundary | Non-operational language controls and glossary alignment. | [../50-governance/GOVERNANCE_OVERVIEW.md](../50-governance/GOVERNANCE_OVERVIEW.md), [glossary.md](glossary.md) |

## Change control

1. Any new major claim must add or update at least one assumption.
2. Closed assumptions require evidence link and reviewer sign-off.
3. Assumptions affecting safety language require governance review.

## Evidence expectation

For each assumption update, include:

1. the architectural component affected;
2. the control that mitigates impact if wrong;
3. a reference to at least one canonical evidence page.

## Related links

1. glossary: glossary.md
2. references: references.md
3. governance overview: ../50-governance/GOVERNANCE_OVERVIEW.md
4. architecture and rationale: ../20-architecture/README.md

## Last updated

2026-05-26
