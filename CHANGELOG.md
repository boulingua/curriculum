# Changelog

All notable changes to the Boulingua CEFR curriculum framework.
Format follows [Keep a Changelog](https://keepachangelog.com/); versioning is
[SemVer](https://semver.org/).

> **Versioning note.** The brief described this as a MAJOR bump to `v2.0.0`
> assuming a prior C1-capped framework. On inspection the `curriculum/` repo was
> empty (only `LICENSE`); there is no prior version to supersede. This is a
> greenfield initial release, so it is **`v1.0.0`**, not `v2.0.0`.

## [1.0.0] — 2026-07-22

Greenfield initial release: a CEFR Pre-A1–C2 descriptor framework grounded in the
CEFR Companion Volume (2020), with **1170** Boulingua Can-Do statements, each
carrying a resolvable `implements:` reference. All §7 verification items pass
(`docs/verification.md`).

### Added
- **Primary-source grounding.** CEFR Companion Volume (2020) retrieved (EN/FR +
  DE-2018 + International Sign), archived under `.sources/` (git-ignored),
  checksummed and cited in `docs/sources.md`.
- **Scale registry** (`schema/scale-registry.yml`) — the 88 CV2020 illustrative
  scales (79 in-scope; 9 signing catalogued out-of-scope), extracted from the CV
  table of contents and verified against the body text.
- **ID scheme** (`docs/id-scheme.md`) — `{LEVEL}.{DOMAIN}.{SCALE}.{SEQ}`,
  leaf-scale granularity, Pre-A1–C2, `implements:` required and resolvable.
- **Can-Do schema** (`schema/can-do.schema.json`) — `implements:` is a required
  field on every statement.
- **Conformance** (`docs/conformance.md`) — `core` (A1–B1), `full` (A1–C1),
  `complete` (Pre-A1–C2); consumers must declare implemented scales.
- **`NOTICE.md`** — Council of Europe attribution and the no-bulk-reproduction
  policy.
- **`scripts/id-audit.sh`** — format, uniqueness and reference-resolution audit.
- **ADR 0001** — records that grounding is conformance, not certification.

- **`levels/pre-a1.md … levels/c2.md`** — 1170 grounded Can-Do statements
  (preA1 42, A1 101, A2 238, B1 289, B2 262, C1 154, C2 84). Empty (scale,level)
  cells recorded as `no-official-descriptor`.
- **`docs/descriptor-crosswalk.md`** — 1170 rows, Boulingua id ↔ CV descriptor.
- **`docs/coverage-gap-report.md`** — all 88 CV scales accounted for; none dropped.
- **`assessment/rubrics/speaking-analytic.md`** — the six CV Table 3 (Appendix 3)
  aspects banded via their illustrative scales.
- **`docs/verification.md`** — §7 checklist, all nine items pass.
- **`examples/de-a1/`** — reference German A1 instantiation (conformance demo).
- **`docs/rld-catalog.md`** — Reference Level Descriptions per language.

### Scope
- Extends the CEFR range to **Pre-A1** and **C2** throughout.
- Mediation (20 scales) and plurilingual/pluricultural (3 scales) are fully in
  scope. Signing competences (9 scales) are catalogued but out of scope.

[Unreleased]: https://github.com/boulingua/curriculum/commits/main
