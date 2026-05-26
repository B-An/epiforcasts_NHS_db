# References and Reading List

## Audience

Contributors, reviewers, and stakeholders requiring source-backed documentation.

## Purpose

List authoritative references used for governance framing, communication standards, and methodological orientation.

## Core governance and policy references

1. NHS England digital and transformation guidance.
URL: [https://www.england.nhs.uk/digitaltechnology/](https://www.england.nhs.uk/digitaltechnology/)
2. NICE evidence standards framework for digital health technologies.
URL: [https://www.nice.org.uk/about/what-we-do/our-programmes/evidence-standards-framework-for-digital-health-technologies](https://www.nice.org.uk/about/what-we-do/our-programmes/evidence-standards-framework-for-digital-health-technologies)
3. ICO UK GDPR guidance and resources.
URL: [https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/)
4. NHS clinical safety standards DCB0129 and DCB0160.
URL: [https://digital.nhs.uk/services/clinical-safety/clinical-risk-management-standards-dcb0129-and-dcb0160](https://digital.nhs.uk/services/clinical-safety/clinical-risk-management-standards-dcb0129-and-dcb0160)

## Communication and documentation references

1. UK Government Service Manual: writing for user needs.
URL: [https://www.gov.uk/service-manual/design/writing-for-user-needs](https://www.gov.uk/service-manual/design/writing-for-user-needs)
2. Diataxis documentation framework.
URL: [https://diataxis.fr/](https://diataxis.fr/)
3. Keep a Changelog specification.
URL: [https://keepachangelog.com/en/1.1.0/](https://keepachangelog.com/en/1.1.0/)
4. Semantic Versioning.
URL: [https://semver.org/](https://semver.org/)

## Methodological references

1. CONSORT-AI reporting extension.
URL: [https://www.nature.com/articles/s41591-020-1034-x](https://www.nature.com/articles/s41591-020-1034-x)
2. TRIPOD-AI statement context and reporting trajectory.
URL: [https://www.bmj.com/content/370/bmj.m3164](https://www.bmj.com/content/370/bmj.m3164)
3. ArviZ documentation for Bayesian analysis workflows.
URL: [https://python.arviz.org/](https://python.arviz.org/)
4. PyMC documentation for Bayesian modelling in Python.
URL: [https://www.pymc.io/](https://www.pymc.io/)

## Claim-to-evidence map

Use this table to support defensible architecture statements in reviews and presentations.

| Claim area | Core claim | Supporting references |
| --- | --- | --- |
| Uncertainty-aware communication | Probabilistic framing is safer than deterministic overstatement in uncertain systems. | CONSORT-AI, TRIPOD-AI |
| Bayesian workflow integrity | Inference and posterior analysis should use transparent, inspectable tools and diagnostics. | PyMC docs, ArviZ docs |
| Governance boundary discipline | Prototype analytics must not be conflated with approved clinical decision support. | NICE Evidence Standards Framework, NHS clinical safety standards DCB0129/DCB0160 |
| Data protection framing | Use synthetic or controlled data handling and explicit governance language for safe exploration. | ICO UK GDPR guidance, NHS England digital guidance |
| Documentation quality and interpretation consistency | Audience-specific structure and plain-language standards reduce misunderstanding risk. | Diataxis, UK Government Service Manual |

## How to use these references

1. Cite at least one authoritative source for governance-sensitive claims.
2. Distinguish external evidence from local assumptions.
3. Record deviations or local policy overlays in governance documentation.

## Related architecture links

1. architecture and rationale: ../20-architecture/README.md
2. technical summary: ../30-model/TECHNICAL_SUMMARY_ADVANCED.md
3. governance overview: ../50-governance/GOVERNANCE_OVERVIEW.md
4. assumptions register: assumptions-register.md

## Related links

1. glossary: glossary.md
2. style guide: ../60-contributing/style-guide.md
3. governance overview: ../50-governance/GOVERNANCE_OVERVIEW.md

## Last updated

2026-05-26
