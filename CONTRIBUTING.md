# Contributing Guide

Thank you for improving this repository.

## Audience
Contributors, reviewers, and maintainers.

## Principles

1. Safety and clarity before speed.
2. Explicit assumptions before interpretation.
3. Reproducibility before convenience.
4. Respectful collaboration in all reviews.

## Before you start

1. Read docs home: [docs/README.md](docs/README.md)
2. Read style guide: [docs/60-contributing/style-guide.md](docs/60-contributing/style-guide.md)
3. Use repository terminology: [docs/70-reference/glossary.md](docs/70-reference/glossary.md)
4. Check references for claim quality: [docs/70-reference/references.md](docs/70-reference/references.md)

## Contribution workflow

1. Open an issue or note rationale in your PR.
2. Keep changes focused and logically scoped.
3. Update documentation with any behavioural change.
4. Add or update tests where applicable.
5. Submit a PR with clear summary and impact statement.

## Pull request expectations

A good PR contains:

1. Problem statement.
2. What changed and why.
3. Assumptions introduced or removed.
4. Operational, governance, and user impact.
5. Documentation updates.
6. Evidence links for non-trivial claims.

Use the repository template:

1. .github/pull_request_template.md

## Review checklist

1. Terminology aligns with glossary.
2. User-facing language is clear and non-ambiguous.
3. Safety boundary is explicit.
4. No unverifiable claims.
5. Cross-links are present and correct.

## Documentation requirements

If code changes behaviour, update at least one of:

1. [docs/40-operations/RUNBOOK.md](docs/40-operations/RUNBOOK.md)
2. [docs/30-model/TECHNICAL_SUMMARY_ADVANCED.md](docs/30-model/TECHNICAL_SUMMARY_ADVANCED.md)
3. [docs/50-governance/GOVERNANCE_OVERVIEW.md](docs/50-governance/GOVERNANCE_OVERVIEW.md)

## Writing and tone requirements

1. Use UK English.
2. Avoid undefined acronyms.
3. Prefer short, direct sentences.
4. State uncertainty openly.

See full policy: [docs/60-contributing/style-guide.md](docs/60-contributing/style-guide.md)

## Branch and commit hygiene

1. One concern per commit where practical.
2. Use descriptive commit messages.
3. Avoid bundling unrelated refactors.

## Governance records and release hygiene

1. For major decisions, create an ADR from docs/80-decisions/ADR_TEMPLATE.md.
2. For user-visible changes, update CHANGELOG.md under Unreleased.
3. Keep entries concise and outcome-focused.

## Support new contributors

If a PR includes domain-specific assumptions, add or update:

1. glossary entry;
2. assumptions register;
3. short rationale in the technical summary.

## Questions

Start with docs home and open a discussion issue if any guidance conflicts.
