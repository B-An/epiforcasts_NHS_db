# Documentation Standard (Internal)

This internal standard applies to every documentation area in the repository taxonomy.

## Required section contract

Each canonical document should include:

1. Audience
2. Purpose
3. Scope and non-scope
4. Assumptions
5. Limitations
6. Owner
7. References
8. Last updated

## Structural rules

1. One canonical home per topic.
2. Cross-links between architecture, operations, governance, references.
3. Avoid duplicate source-of-truth pages.
4. Use concise, decision-oriented language.

## Quality rules

1. Governance-sensitive claims require evidence links.
2. Operational instructions require runnable commands.
3. Model statements must include uncertainty caveats.
4. Production-readiness claims require explicit evidence.

## Review gates

1. Markdown lint clean.
2. Link checks for local canonical references.
3. Changelog/log update when meaningfully changed.
4. Decision log entry for architectural/policy-impacting updates.
