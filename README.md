# curriculum — the boulingua CEFR descriptor framework

1,199 can-do statements across 7 levels and 79 populated scales out of 79
in-scope scales, each carrying a
stable id, a citation to the CEFR Companion Volume (2020), and an `implements`
block naming the domain, scale, level and descriptor ordinal it realizes.

A course does not copy from here. It **maps to** here: its own can-dos are its
own, and `curriculum.yml` records which framework statement each one realizes.
That is what makes a conformance claim checkable and what keeps Council of
Europe text out of the courses.

## The id grammar

```
{LEVEL}.{DOMAIN}.{scale-slug}.{NN}
  LEVEL   preA1 A1 A2 B1 B2 C1 C2
  DOMAIN  REC PROD INT MED PLUR LING SOC PRAG      <- eight, not five
  slug    [a-z0-9-]+, must exist in schema/scale-registry.yml
  NN      exactly two digits
```

Eight domains. `LING` and `PRAG` are real ones, and a grep written from a
five-domain assumption misses them without saying so. The slug is keyed on
`(domain, scale)` and not on the slug alone, because `turntaking` exists under
both `INT` and `PRAG`.

Ids are **additive and never renumbered**. A statement that is withdrawn gets
`status: deprecated`; nothing downstream breaks when the framework grows.

## Using it from a course

The framework is a **CI-time checkout at a pinned tag**. Never vendored, never
a Hugo module, never a submodule — and `hugo --minify --gc` must succeed with
it absent, because conformance is a gate and not a build input.

```bash
python .curriculum/scripts/conformance_audit.py \
    resolve --manifest curriculum.yml --content content/
```

### Exit codes are the contract

| | |
|---|---|
| 0 | valid for the declared status; in-progress is not conformance approval |
| 1 | usage |
| 2 | manifest fails schema |
| 3 | a **wrong** id — malformed, dangling, deprecated, duplicated, out of span |
| 4 | front-matter ↔ manifest drift, or `coverage --check` disagreement |
| 5 | declared level **not met** — a silently missing in-scope scale |
| 6 | framework version pin mismatch |

3 and 5 are deliberately separate. A course ramping up its coverage must fail
hard on a *wrong* id while merely being warned about an *incomplete* one.
Collapsing them into one boolean is how the previous gate ended up checking
nothing.

## `id-audit.sh` is deprecated

It globs *this* repo's `levels/` and has no way to be pointed at a course, so
run from a course it audited the framework's own statements, printed OK and
exited 0 whatever the course contained. Fifteen course roadmaps had wired it as
their conformance gate. Use `conformance_audit.py resolve`.

## Coverage

`coverage.yml` is generated, never hand-written — three integers in prose are
three integers a gate will eventually contradict.

> A **cell** is a `(level, scale)` pair where the scale is `in_scope`. It is
> **populated** if at least one `status: active` statement carries that level
> and that scale, and **excused** only when the official source genuinely has no applicable descriptor.
> Entries marked `missing-in-repository` are blockers, never exemptions.
> A course conforming at level *L* covers ≥ 90 % of the populated, non-excused
> cells at every level up to and including *L*.

Current counts are generated in [`coverage.yml`](coverage.yml); see [conformance rules](docs/conformance.md) for target spans and the restricted profile.

## Open

The dated official-source check confirms that `PROD.addressing-audiences` and
`INT.co-operating` contain descriptors missing from this repository.
`schema/known-empty-scales.yml` records their source levels and required repair.
`self-audit` fails for these omissions; an applicable `met` conformance claim
also fails. A qualified reviewer must add and verify the missing statements
before a conformance release. See [REFINEMENT.md](REFINEMENT.md).

## Licence

Code MIT. The statements are the author's own formulations, oriented on the CEFR
Companion Volume; no Council of Europe text is reproduced in bulk. See
`NOTICE.md`.

## Current source restoration

The two omitted scales were restored on 31 October 2026 with 29 additive IDs.
Their explicit printed pages and source-level ordinals are recorded in each
statement. Independent source review remains pending in
[schema/source-restoration-2026-10-31.yml](schema/source-restoration-2026-10-31.yml).
Structural completeness does not establish pedagogical approval or validate
course mappings. The canonical course contract is [EQS-1](standards/EQS-1.md).
