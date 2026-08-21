# curriculum — the boulingua CEFR descriptor framework

1,170 can-do statements across 7 levels and 79 in-scope scales, each carrying a
stable id, a citation to the CEFR Companion Volume (2020), and an `implements`
block naming the domain, scale, level and descriptor ordinal it realizes.

A course does not copy from here. It **maps to** here: its own can-dos are its
own, and `conformance.yml` records which framework statement each one realizes.
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
    resolve --manifest conformance.yml --content content/
```

### Exit codes are the contract

| | |
|---|---|
| 0 | conformant |
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
> and that scale, and **excused** if listed in `schema/known-empty-scales.yml`.
> A course conforming at level *L* covers ≥ 90 % of the populated, non-excused
> cells at every level up to and including *L*.

`core` (A1–B1) = 206 cells · `full` (A1–C1) = 356 · all seven = 441.

## Open

Two in-scope scales carry zero statements at every level:
`PROD.addressing-audiences` and `INT.co-operating`. Their siblings are
populated throughout, so an authoring omission is the likelier explanation than
a genuinely empty CV cell — and the distinction matters, because the
descriptor-existence matrix is what *excuses* a course from covering a cell.
Both are recorded in `schema/known-empty-scales.yml` as `pending`, and
`self-audit` warns on every run until someone checks the CV. See that file for
the procedure.

## Licence

Code MIT. The statements are the author's own formulations, oriented on the CEFR
Companion Volume; no Council of Europe text is reproduced in bulk. See
`NOTICE.md`.
