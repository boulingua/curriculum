# Verification (§7)

Evidence for each requirement. Reproduce the audit with `bash scripts/id-audit.sh`.

- [x] **Every CV illustrative scale enumerated and accounted for** — `schema/scale-registry.yml` lists **88** scales (79 in-scope + 9 signing out-of-scope); `docs/coverage-gap-report.md` marks each implemented / out-of-scope / no-official-descriptor.
- [x] **Every Can-Do has a resolving `implements:`** — **1199** statements, `scripts/id-audit.sh` passes (format + uniqueness + (domain,scale) resolution). Missing: 0.
- [x] **Source wording distinguished from authored reformulation** — level files carry Boulingua reformulations; the crosswalk contains brief source gists and authored paraphrases for restored entries. Attributed quotations follow `NOTICE.md`. Source comparison does not replace editorial approval.
- [x] **All seven levels present (Pre-A1 and C2 included)** — A1, A2, B1, B2, C1, C2, preA1. Counts: preA1=42, A1=102, A2=243, B1=296, B2=270, C1=159, C2=87.
- [x] **Mediation and plurilingual scales implemented, not stubbed** — MED: 289 statements across 20 scales; PLUR: 52 statements across 3 scales.
- [x] **ID audit passes** — unique, well-formed, fully resolved (`scripts/id-audit.sh`).
- [x] **Rubrics traceable to Table 3 / CV analytic scales** — `assessment/rubrics/speaking-analytic.md` bands the six Appendix 3 aspects via their CV scales.
- [x] **Sources archived with checksums and retrieval dates** — `docs/sources.md` (CV2020 EN/FR + DE-2018 + Sign; SHA-256; retrieved 2026-07-22, browser method).
- [x] **German A1 example passes conformance at declared level** — `examples/de-a1/conformance.yml` — 8 realizations, all resolving. Verified by `conformance_audit.py resolve --manifest examples/de-a1/conformance.yml --content examples/de-a1/`, which CI runs. This box was ticked for months against a check nothing performed: `id-audit.sh` globs this repo's own levels/ and cannot read a consumer manifest.

## Numbers

- Scales: 88 total, 79 in-scope, 9 signing (out of scope).
- Grounded Can-Do statements: **1199** (1170 preserved entries and 29 additive restorations).
- By level: preA1 42, A1 102, A2 243, B1 296, B2 270, C1 159, C2 87.

The counts were refreshed on 2 November 2026. The 29 restorations populate
Addressing audiences and Co-operating; source pages, ordinals and B2+ distinctions
are recorded in `schema/source-restoration-2026-10-31.yml`. Their independent
text comparison is complete, while editorial approval remains pending. Framework
population does not establish a course's task coverage or approve its mappings.
