# Verification (§7)

Evidence for each requirement. Reproduce the audit with `bash scripts/id-audit.sh`.

- [x] **Every CV illustrative scale enumerated and accounted for** — `schema/scale-registry.yml` lists **88** scales (79 in-scope + 9 signing out-of-scope); `docs/coverage-gap-report.md` marks each implemented / out-of-scope / no-official-descriptor.
- [x] **Every Can-Do has a resolving `implements:`** — **1170** statements, `scripts/id-audit.sh` passes (format + uniqueness + (domain,scale) resolution). Missing: 0.
- [x] **No official descriptor text reproduced beyond brief attributed quotation** — level files carry Boulingua reformulations; the crosswalk stores only <=12-word attributed gists; the grounding verify-pass asserted `no_bulk_copy`. Policy in `NOTICE.md`.
- [x] **All seven levels present (Pre-A1 and C2 included)** — A1, A2, B1, B2, C1, C2, preA1. Counts: preA1=42, A1=101, A2=238, B1=289, B2=262, C1=154, C2=84.
- [x] **Mediation and plurilingual scales implemented, not stubbed** — MED: 289 statements across 20 scales; PLUR: 52 statements across 3 scales.
- [x] **ID audit passes** — unique, well-formed, fully resolved (`scripts/id-audit.sh`).
- [x] **Rubrics traceable to Table 3 / CV analytic scales** — `assessment/rubrics/speaking-analytic.md` bands the six Appendix 3 aspects via their CV scales.
- [x] **Sources archived with checksums and retrieval dates** — `docs/sources.md` (CV2020 EN/FR + DE-2018 + Sign; SHA-256; retrieved 2026-07-22, browser method).
- [x] **German A1 example passes conformance at declared level** — `examples/de-a1/conformance.yml` — 8 realizations, all resolving. Verified by `conformance_audit.py resolve --manifest examples/de-a1/conformance.yml --content examples/de-a1/`, which CI runs. This box was ticked for months against a check nothing performed: `id-audit.sh` globs this repo's own levels/ and cannot read a consumer manifest.

## Numbers

- Scales: 88 total, 79 in-scope, 9 signing (out of scope).
- Grounded Can-Do statements: **1170**.
- By level: preA1 42, A1 101, A2 238, B1 289, B2 262, C1 154, C2 84.
