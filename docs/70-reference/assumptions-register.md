# Assumptions Register

## Audience
Engineering, governance, and delivery stakeholders.

## Purpose
Track explicit assumptions so decisions are reviewable and updates are controlled.

## Register

| ID | Assumption | Type | Impact if wrong | Validation approach | Owner | Status |
|---|---|---|---|---|---|---|
| A-001 | Synthetic data structure is sufficient for demonstration narratives. | Methodological | Misleading confidence in real-world transferability. | Compare narrative claims against real aggregate patterns before any operational pilot. | Engineering lead | Open |
| A-002 | Threshold reference lines are communication aids only. | Communication | Stakeholders may misread as policy triggers. | Prominent caveats in UI and docs; stakeholder walkthrough. | Product owner | Open |
| A-003 | Zero-MCMC serving improves reliability for user sessions. | Technical | UI latency and instability under load. | Load test cached path; monitor startup and render timings. | Operations lead | Open |
| A-004 | Single-chain fast inference is acceptable for prototype cycles. | Statistical | Under-detected convergence issues. | Use multi-chain diagnostics in periodic full runs. | Modelling lead | Open |
| A-005 | Organisational labels in synthetic data do not create governance confusion. | Governance | Readers infer live NHS linkage. | Label controls in README, UI text, and lay-person guide. | Governance lead | Open |

## Change control

1. Any new major claim must add or update at least one assumption.
2. Closed assumptions require evidence link and reviewer sign-off.
3. Assumptions affecting safety language require governance review.

## Related links

1. glossary: glossary.md
2. references: references.md
3. governance overview: ../50-governance/GOVERNANCE_OVERVIEW.md
