# German A1 — reference instantiation

A minimal, testable example of how a language repository consumes this framework.

## What it shows

- **Declaring conformance** (`conformance.yml`): a consumer names the framework
  version, the level it targets, and — for each of its own realizations — the
  curriculum descriptor ID it `implements`.
- **Traceability both ways**: the framework says *what* a learner can do (the
  grounded CEFR descriptor); the instantiation says *how* it is realised in
  German. Neither reproduces Council of Europe text.
- **Validation**: every `implements_id` must resolve to a statement in
  `curriculum/levels/`. `docs/verification.md` runs this check; it is the
  concrete evidence for the §7 item *"German A1 example passes conformance at its
  declared level."*

## What it is not

This is a **starter**, deliberately partial (8 realizations across domains, not
the full A1 scale set). The authoritative German instantiation belongs in the
`daf` repo, which should implement every in-scope scale carrying an A1
descriptor and declare `core` conformance. Extending to the mediation and
plurilingual A1 descriptors (present in `levels/a1.md`) is the obvious next step.

## Note on scope (deliverable 11)

The brief asked to "re-validate `languages/de` against the framework". No
`languages/de` directory exists in this environment (the sibling `daf` repo is
the German site). This example stands in as the conformance demonstration; a
full re-validation of `daf` against v1.0.0 is a separate task once its structure
is mapped.
