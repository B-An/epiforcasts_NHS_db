# High-Level Folder Structure Options

## Purpose
Provide clean structure options before finalising release governance artefacts.

## Option A: Minimal and lightweight

Use this if you want fewer folders and very low maintenance overhead.

```text
repo/
  src/
  docs/
    product/
    technical/
    operations/
    governance/
    reference/
  tests/
  .github/
```

Pros:

1. simple mental model;
2. low admin overhead.

Cons:

1. weaker separation between architecture and model content;
2. less explicit lifecycle traceability.

## Option B: Balanced taxonomy-first (recommended)

Use this for professional collaboration with clear ownership and moderate complexity.

```text
repo/
  app and model files
  docs/
    00-overview/
    10-product/
    20-architecture/
    30-model/
    40-operations/
    50-governance/
    60-contributing/
    70-reference/
    80-decisions/
    90-changelog/
  .github/
    ISSUE_TEMPLATE/
    pull_request_template.md
```

Pros:

1. clear audience and ownership boundaries;
2. strong governance and audit support;
3. supports progressive maturity.

Cons:

1. slightly higher documentation discipline needed.

## Option C: Enterprise release-train

Use this for larger teams with formal release and assurance gates.

```text
repo/
  src/
    data/
    model/
    serving/
  docs/
    handbook/
    architecture/
    validation/
    risk/
    release/
    adr/
  governance/
    controls/
    evidence/
    audits/
  .github/
  scripts/
  tests/
```

Pros:

1. strongest governance signal;
2. very clear release controls;
3. scales for multi-team contribution.

Cons:

1. overhead is heavy for a prototype.

## Recommendation

Choose Option B now.

Reason:

1. it preserves your current migration direction;
2. it is clean and professional;
3. it supports both prototype speed and governance quality.

## Next step after selection

1. release-grade changelog at repository root;
2. decision record template in docs/80-decisions;
3. changelog conventions in docs/90-changelog.
