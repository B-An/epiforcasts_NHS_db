# Documentation Taxonomy Migration Plan

## Audience
Documentation maintainers, engineering leads, and contributors.

## Purpose
Migrate documentation from mixed-location files to a stable, audience-oriented structure with one canonical page per topic.

## Scope
In scope:

1. document classification and relocation;
2. canonical ownership assignment;
3. de-duplication and cross-linking;
4. common language and referencing discipline.

Out of scope:

1. major software refactoring;
2. replacing governance policy outside this repository.

## Target taxonomy

1. docs/00-overview
2. docs/10-product
3. docs/20-architecture
4. docs/30-model
5. docs/40-operations
6. docs/50-governance
7. docs/60-contributing
8. docs/70-reference
9. docs/80-decisions
10. docs/90-changelog

## Migration phases

### Phase 1: Stabilise entry points

1. publish root README with pathway links;
2. publish docs index as canonical documentation gateway;
3. create contribution and writing standards.

Exit criteria:

1. all major audiences can find their starting page in under 30 seconds;
2. duplicate onboarding instructions are removed.

### Phase 2: Move and consolidate content

1. convert legacy pages into canonical homes;
2. add short redirect stubs in legacy files;
3. remove conflicting definitions and duplicate process steps.

Exit criteria:

1. no topic appears as full text in more than one place;
2. each migrated page links back to docs home.

### Phase 3: Strengthen governance and evidence

1. align terminology to glossary;
2. ensure each claim has a cited reference where relevant;
3. add assumptions register and decision records.

Exit criteria:

1. key terms have approved definitions;
2. evidence and assumptions are traceable.

### Phase 4: Continuous maintenance

1. enforce documentation checks in PR review;
2. maintain changelog and ownership metadata;
3. review taxonomy quarterly.

Exit criteria:

1. no stale top-level documentation pages;
2. documentation quality debt is visible and prioritised.

## Legacy-to-target mapping

1. docs/USER_EXPLAINER.md -> docs/10-product/LAYPERSON_GUIDE.md
2. docs/TECHNICAL_OVERVIEW.md -> docs/20-architecture and docs/30-model
3. docs/GOVERNANCE_SENSE_CHECK.md -> docs/50-governance/GOVERNANCE_OVERVIEW.md
4. docs/00-overview/legacy-redirects/QUICK_START.md, docs/00-overview/legacy-redirects/QUICKRUN.md, docs/00-overview/legacy-redirects/OFFLINE_INFERENCE.md -> docs/40-operations/RUNBOOK.md
5. docs/90-changelog/logs/INTERACTION_LOG.md -> docs/80-decisions and docs/90-changelog

## Ownership model

1. Product owner: 10-product
2. Engineering lead: 20-architecture, 30-model, 40-operations
3. Governance lead: 50-governance
4. Maintainers: 60-contributing, 70-reference
5. Project lead: 00-overview, 80-decisions, 90-changelog

## Definition of done for a migrated page

1. includes Audience, Purpose, Scope, Assumptions, Limitations, Owner, and References;
2. has at least two inbound and two outbound links;
3. uses terms defined in docs/70-reference/glossary.md;
4. includes a last-updated date;
5. has no contradictory duplicate elsewhere.

## Risks and mitigations

1. Risk: contributors continue editing legacy pages.
Mitigation: add stubs and PR checklist gate.
2. Risk: terminology drift.
Mitigation: glossary-first review and style guide enforcement.
3. Risk: over-long documents become unreadable.
Mitigation: split by audience and question type.

## Related links

1. docs home: ../README.md
2. contribution rules: ../../CONTRIBUTING.md
3. style guide: ../60-contributing/style-guide.md
4. glossary: ../70-reference/glossary.md
5. references: ../70-reference/references.md
