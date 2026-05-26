# UK Policy Alignment for Winter Pressure PoC

## Audience

Trust operational leaders, ICB analytics and performance teams, and governance reviewers.

## Purpose

Show how this prototype can be positioned as a practical proof of concept for late autumn and deep winter demand management, while staying inside clear governance boundaries.

## Scope

In scope:

1. policy-aware framing for a non-production proof of concept;
2. utility hypotheses for Trust and ICB use;
3. evidence expectations before any wider operational use.

Out of scope:

1. policy interpretation as legal advice;
2. replacement of local winter plans or statutory reporting;
3. direct clinical decision automation.

## Policy-alignment map (UK, high level)

Use the latest published editions each season.

| Policy area | Typical source family | Relevance to this PoC | PoC contribution |
| --- | --- | --- | --- |
| Seasonal operational planning | NHS England operational planning and contracting guidance; local winter resilience plans | Requires earlier risk visibility and cross-system coordination | Probabilistic early-signal views to support anticipatory planning |
| UEC flow and escalation | NHS England UEC recovery and escalation frameworks; local OPEL/escalation playbooks | Requires timely situational awareness under pressure | Trend-plus-uncertainty signal to complement existing escalation judgement |
| Population and infectious pressure context | UKHSA surveillance publications (for example respiratory and syndromic trends) | Provides contextual leading indicators for demand pressure | Integrates external pressure context as explanatory covariates over time |
| Data governance and digital safety | NHS digital governance standards, clinical safety standards, UK GDPR controls | Requires safe handling, transparency, and traceability | Synthetic-first development, explicit assumptions, auditable change trail |

## Trust and ICB utility hypotheses

1. Trust site operations can use uncertainty-aware trend direction to prioritize proactive actions before deterministic thresholds are crossed.
2. ICB teams can compare trend trajectories across place and provider footprints to coordinate mitigation and mutual aid.
3. Joint Trust-ICB forums can use a shared probabilistic language to reduce interpretation drift in winter planning discussions.

## Minimal PoC operating model for critical months

1. Weekly refresh: run offline inference once per reporting cycle.
2. Local review huddle: interpret signal movement, uncertainty width, and known contextual drivers.
3. Decision log: record what changed, what action was considered, and confidence level.
4. Retrospective loop: check whether early signals were timely and practically useful.

## Data integration direction (latest information)

Potential additions for seasonal use, subject to approval and availability:

1. UKHSA published surveillance indicators relevant to respiratory/syndromic pressure;
2. NHS operational indicators used in local winter dashboards;
3. ONS and other public contextual indicators where locally meaningful.

Integration rule:

1. add a source only with a named assumption and explicit limitation;
2. map each new source to review cadence and data-quality checks;
3. keep provenance in [../70-reference/references.md](../70-reference/references.md).

## Evidence required before wider adoption claims

1. two or more consecutive green acceptance cycles in CI and local operations;
2. documented utility feedback from at least one Trust and one ICB review context;
3. explicit caveat language retained in product and governance docs;
4. updated assumptions and references for each newly integrated external source.

## Boundary statement

This is a policy-aligned proof-of-concept framing document.
It does not imply policy approval, commissioning approval, or production readiness.

## Related links

1. governance overview: [GOVERNANCE_OVERVIEW.md](GOVERNANCE_OVERVIEW.md)
2. robustness plan: [ROBUSTNESS_TARGET_95.md](ROBUSTNESS_TARGET_95.md)
3. assumptions register: [../70-reference/assumptions-register.md](../70-reference/assumptions-register.md)
4. references: [../70-reference/references.md](../70-reference/references.md)
5. lifecycle changelog: [../90-changelog/logs/LIFECYCLE_GIT_CHANGELOG.md](../90-changelog/logs/LIFECYCLE_GIT_CHANGELOG.md)

## Last updated

2026-05-26
