# Glossary

## Audience
All readers.

## Purpose
Provide shared, non-ambiguous definitions for common parlance in this repository.

## Terms

| Term | Definition | In scope | Out of scope |
|---|---|---|---|
| Bayesian model | A probabilistic model that updates beliefs using observed data. | Uncertainty-aware inference for system pressure signals. | Deterministic forecasting with no uncertainty expression. |
| Credible interval | A probability-based interval from the posterior distribution. | Communicating plausible ranges from model output. | Frequentist confidence interval claims unless explicitly stated. |
| ICB | Integrated Care Board in NHS England organisational structure. | Geography label in synthetic demo data. | Any claim of live operational integration in this prototype. |
| Latent pressure index | Model-defined, unitless construct used to summarise inferred pressure. | Internal modelling and communication aid. | Official NHS metric or validated escalation trigger. |
| Posterior | Distribution of parameter values after combining priors and observed data. | Stored in posteriors.nc and used by dashboards. | A definitive truth statement. |
| Partial pooling | Hierarchical sharing of information across groups. | Joint inference across multiple ICBs. | Full pooling or complete independence assumptions. |
| Synthetic data | Fabricated data produced for demonstration and testing. | Safe prototyping and communication. | Real patient-level records or live NHS returns. |
| Threshold reference | Chosen reference line for communication within the demo. | Indicative discussion support. | Authoritative policy limit or mandated trigger. |
| Zero-MCMC serving | UI serves cached outputs without running sampling online. | Fast and predictable user interaction. | Elimination of offline computational requirements. |

## Usage notes

1. If a term is interpreted differently by two audiences, add a separate entry.
2. If a term implies authority, include explicit non-scope wording.
3. Use this glossary in code reviews for language consistency.

## Related links

1. style guide: ../60-contributing/style-guide.md
2. references: references.md
3. assumptions register: assumptions-register.md
