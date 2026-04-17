# User explainer — NHS system pressure demo

## What this is

This is a small **demonstration** application. It loads **synthetic (made-up)** NHS-style numbers—such as bed occupancy and, in the data file, other pressure-related signals—for a few named geographic areas. It is **not** connected to live NHS systems and **does not** use real patient data.

## What you do

You choose an area (for example an ICB name) from a list. The app **runs a statistical model** that estimates an underlying “pressure” score from **bed occupancy** over time for that area.

## What you see

- A **percentage** shown as the chance that “pressure” is above a **demonstration threshold**. This threshold is **not** an official NHS standard or a clinical rule.
- A **chart** showing how **uncertain** the model is about one of its internal parameters (a national-level latent pressure term).

## What to remember

- Results are **exploratory** and aim to be **uncertainty-aware**. They are **not** instructions for clinical care or operational command.
- On-screen **labels** should be read as **illustrative**. Any serious operational or assurance use would need proper governance, data agreements, calibration, and **human oversight**.

## Related reading

- [Technical overview](TECHNICAL_OVERVIEW.md) — how the code and model work.
- [Governance sense-check](GOVERNANCE_SENSE_CHECK.md) — limitations, risks beyond Discovery, and sensible next steps.
- [Interaction log](../INTERACTION_LOG.md) — optional human record of changes and demos.
