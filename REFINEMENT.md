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

## 31 October 2026 — source and authoring-contract repairs

Restored 29 missing descriptor rows with additive IDs and printed source
provenance, bringing the catalogue to 1,199 statements and 79 populated scales.
The initial 1,170 IDs are retained unchanged. Crosswalk row integrity is now
checked. The omission history remains in a separate restoration record;
independent source review is pending and blocks achieved course claims.

Added the canonical EQS-1 contract, calibrated measurement YAML, step-key label
map, unit-review checklist and rubric interface. `scripts/review_ledger.py`
prepares source-hashed task/mapping review records and per-level missing-cell
lists, refusing to overwrite a potentially edited review ledger. It neither
asserts mappings nor assigns reviewers. These assets prepare actual review;
they do not close course pedagogical readiness.


## Verification continuation — 2 November 2026

All 22 framework tests, the self-audit and coverage consistency check pass
locally: 1,199 statements, 1,199 unique IDs and 79 in-scope scales. The 29
restored statements remain explicitly pending editorial approval; original
descriptors were retained. Documentation now reports the actual counts. The
read-only CI workflow also runs on review branches. No new tag or production
framework release is implied by these local results.
