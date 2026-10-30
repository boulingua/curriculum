# Conformance

Boulingua is a reference framework, not an accreditation body. Conformance is
traceable coverage of descriptors by reviewed learning activities. The resolver
checks the structure and consistency of that evidence; it cannot establish
that an activity actually teaches or assesses a descriptor well.

## Target and achieved status

A course publishes `curriculum.yml` at its root. `declared_conformance` is its
target; `conformance_status: in-progress` does not claim that target is met.

| Target | Required span |
|---|---|
| `core` | A1–B1 |
| `full` | A1–C1 |
| `complete` | A1–C2 |
| `core-restricted` | A1–B1 within an approved profile; currently Latin only |

Pre-A1 is an optional additional claim, selected by `preA1` in `levels_claimed`.
It is not implicitly part of `complete`. The generated `coverage.yml` records
current framework counts; dated counts in old roadmaps are not authoritative.

For `met`, each level in the target span must cover at least 90% of its
populated, in-scope `(level, scale)` cells, rounded **up** to a whole cell.
A cell is covered by at least one active descriptor realized by a source page.
Every remaining uncovered cell must appear exactly once in `gaps`, with a reason
and a quoted ISO calendar date in `scheduled`. A gap records missing work; it
does not count as coverage. Officially empty framework cells are not required.

The Latin `classical-reception` profile excludes only the listed spoken
production and spoken interaction scales. Reception, mediation, plurilingual,
linguistic, sociolinguistic and pragmatic cells remain fully required, as set
out in organisation ADR-0013. Capacity constraints are gaps, never exclusions.
See `profiles/classical-reception.yml` for the machine-readable list.

## Source evidence

Pin `framework_version` to the framework's `VERSION`. The resolver requires:

- Active descriptor IDs, within the declared target and profile.
- A unique `(page, implements_id)` pair per realization. Reusing a descriptor
  on different pages is valid and does not multiply coverage.
- Paths relative to `content`, without `.md` or a final `/index`.
- The exact same pairs in the manifest and page front matter. IDs mentioned
  only in body text are not implementation evidence.
- `curriculum.level` consistent with each page's descriptors.
- Summary fields, when supplied, matching the actual source pages and mappings.
- For `met`, source pages with `curriculum.implements_basis: asserted`.
  Proposed or unreviewed mappings cannot establish an achieved claim.

Use `schema/conformance.schema.json` and the example manifest in
`examples/de-a1/`. `schema/scale-registry.yml` defines the closed scale set.

## Reproduce the checks

With Python 3.12, from this repository:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/conformance_audit.py self-audit
python scripts/conformance_audit.py coverage --check
python scripts/conformance_audit.py ../efl
```

For an explicit manifest/content pair:

```sh
python scripts/conformance_audit.py resolve \
  --manifest ../efl/curriculum.yml --content ../efl/content
```

An `in-progress` success means that the supplied structural evidence agrees.
It does not establish curricular coverage, native-language review or course
readiness. `self-audit` separately reports gaps in the framework catalogue.
