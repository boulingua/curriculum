# Refinement record — 30 October 2026

This is a local engineering candidate on `refine/2026-10-30`. No hosted CI,
published release or production deployment of these changes has been observed.
The suite strategy and integration order live in the organisation repository,
`docs/refinement-2026-10-30.md` and `docs/release-candidate-2026-10-30.md`.

## Findings and changes

- High: malformed manifests, incomplete page/descriptor pairs and proposed mappings could support misleading conformance claims. The resolver now validates the schema, framework version, source levels, pair symmetry, explicit gaps and a rounded-up 90% threshold. A `met` claim rejects proposed mappings and applicable unresolved framework omissions.
- High: the official Companion Volume contains descriptors for `PROD.addressing-audiences` and `INT.co-operating`; this repository has none. The dated source check is in `schema/known-empty-scales.yml` and `docs/sources.md`. These are missing statements, not legitimate curriculum exemptions. `self-audit` now fails until reviewed source additions resolve them.
- Medium: Latin's accepted reception profile was not reflected consistently in coverage. Profile exclusions now follow ADR-0013; non-oral domains remain in scope. The generated coverage table was recomputed.

## Validation

15 regression tests passed. All 1,170 existing statements passed structural schema validation. Existing course manifests remain in progress; successful resolution is not an approval of their proposed educational mappings. `coverage --check` verifies the committed derived table. `self-audit` intentionally returns a nonzero result for the two confirmed source omissions; the new CI must remain red for that finding until repaired.

## Roadmap and acceptance

First, a framework reviewer must add faithful statements with stable additive IDs, exact source levels/ordinals and citations for the two missing scales. Review the new statements independently, regenerate crosswalk/coverage, and rerun self-audit and course resolution. Next, course reviewers must check actual teaching/assessment evidence before changing proposed assertions or `in-progress` status. Do not reinterpret an absent framework statement as an exemption or change the threshold to make a course pass.

See README.md for the reproducible resolver commands. This framework is not yet ready for a new conformance release.
