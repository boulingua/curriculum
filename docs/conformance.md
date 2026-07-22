# Conformance

Boulingua's framework is a **reference model**, not a certification. Conformance
here means *documented, traceable coverage* — every claim resolves to an official
CEFR descriptor — not accreditation. See
`docs/adr/0001-cefr-conformance-not-certification.md` for that boundary.

## Conformance levels

A consuming repository (a language instantiation such as `daf`, `fle`, …)
declares which conformance level it meets:

| Level | CEFR range | Requirement |
|---|---|---|
| `core` | A1–B1 | Implements every **in-scope** scale that has an official descriptor at A1, A2 or B1. |
| `full` | A1–C1 | `core` plus B2 and C1 coverage of every in-scope scale that has a descriptor there. |
| `complete` | **Pre-A1–C2** | `full` plus Pre-A1 and C2 coverage of every in-scope scale that has a descriptor there. |

At every level, a cell the CV leaves empty is satisfied by recording
`no-official-descriptor` — absence of an official descriptor is never a
conformance failure, but a **silently missing scale is**.

## Scope declaration (required of consumers)

A conforming repository MUST publish, in machine-readable form, the set of scales
it implements and, per scale, the levels covered vs. `no-official-descriptor`.
This is what makes coverage auditable rather than asserted. The framework
provides `schema/scale-registry.yml` (the closed set of scales) and
`scripts/id-audit.sh` (which checks that every implemented ID resolves).

## Honest note on instantiation

The framework specifies Pre-A1–C2 across all in-scope scales. **Instantiations
will legitimately declare gaps** — freely-available teaching material rarely
reaches C2 for any language, and mediation/plurilingual material is thin. The
framework specifying a level and an instantiation declaring it unmet is the
correct division of labour, not a defect. Declare the gap; do not lower the
framework to hide it.
