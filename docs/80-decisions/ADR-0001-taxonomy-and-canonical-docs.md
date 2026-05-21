# ADR-0001: Adopt taxonomy-first canonical documentation

Status: Accepted
Date: 2026-05-20
Owners: Repository maintainers
Review date: 2026-08-20

## Context

Documentation existed across mixed root and docs locations, with overlapping quick-start and architecture content. Contributors lacked a single canonical route for updates, increasing drift risk and onboarding friction.

## Decision

Adopt a taxonomy-first documentation model under docs with explicit audience pathways and canonical ownership. Legacy pages are retained as short redirect stubs.

## Options considered

1. Keep existing mixed structure.
2. Minimal consolidation under a few broad docs folders.
3. Taxonomy-first numbered structure with canonical ownership.

## Consequences

1. Improved discoverability and review consistency.
2. Slightly higher process discipline for contributors.
3. Better traceability for governance and launch communication.

## Governance impact

1. Reduces ambiguity in safety and non-scope messaging.
2. Enables clearer assumption and evidence linkage.
3. Supports structured launch governance artefacts.

## Evidence and references

1. docs/README.md
2. docs/00-overview/DOCS_TAXONOMY_MIGRATION_PLAN.md
3. docs/70-reference/references.md

## Follow-up actions

1. Add release template and versioned changelog process.
2. Add ADR review cadence in contribution workflow.
3. Add docs-link checks in CI.
