# Descriptor ID scheme

Stable identifiers for every Boulingua Can-Do statement. **Load-bearing across
repos** (the language repos `afl`, `cfl`, `daf`, … reference these IDs), so the
rules below are contractual.

## Format

```
{LEVEL}.{DOMAIN}.{SCALE}.{SEQ}
```

- **LEVEL** — one of `preA1` `A1` `A2` `B1` `B2` `C1` `C2`
- **DOMAIN** — the CEFR CV top-level category (table below)
- **SCALE** — kebab-case slug of the **leaf illustrative scale** (the scale that
  has its own descriptor table in the CV), from `schema/scale-registry.yml`
- **SEQ** — zero-padded 2-digit sequence of Boulingua statements implementing
  that (LEVEL, SCALE), starting `01`

Examples:

```
A2.REC.overall-oral-comprehension.02
B1.MED.collaborating-to-construct-meaning.01
C1.PRAG.thematic-development.01
preA1.INT.online-conversation-and-discussion.01
```

## DOMAIN codes

Mapped 1:1 to the CEFR Companion Volume (2020) structure — not ad hoc.

| Code | CV § | Domain | In-scope scales |
|---|---|---|---|
| `REC`  | 3.1 | Reception (incl. reception strategies) | 13 |
| `PROD` | 3.2 | Production (incl. production strategies) | 12 |
| `INT`  | 3.3 | Interaction (incl. interaction strategies) | 18 |
| `MED`  | 3.4 | Mediation (incl. mediation strategies) | 20 |
| `PLUR` | Ch 4 | Plurilingual & pluricultural competence | 3 |
| `LING` | 5.1 | Linguistic competence | 6 |
| `SOC`  | 5.2 | Sociolinguistic competence | 1 |
| `PRAG` | 5.3 | Pragmatic competence | 6 |
| `SIGN` | Ch 6 | Signing competences | 9 — **out of scope**, no IDs minted |

Strategies live inside their parent activity domain (as in the CV). A scale name
that recurs across domains is disambiguated by the domain: `INT.turntaking` (an
interaction strategy) and `PRAG.turntaking` (a pragmatic scale) are distinct.

`SIGN` scales are catalogued in the registry and the gap report but receive no
IDs — Boulingua covers spoken/written languages.

## The `implements:` reference (required)

Every Can-Do statement MUST carry a resolvable `implements:` block. A statement
without one is a schema error (`schema/can-do.schema.json`).

```yaml
- id: B1.MED.collaborating-to-construct-meaning.01
  can_do: "Can help a group organise its work by restating the goal and weighing options."
  implements:
    source: cefr-cv-2020            # → docs/sources.md entry (checksummed)
    domain: MED
    scale: collaborating-to-construct-meaning
    level: B1
    descriptor_ordinal: 2           # position of the descriptor within B1 for this scale
  cite: "CEFR CV (2020), Mediation › Mediating concepts › Collaborating to construct meaning, B1, desc. 2"
  status: active
```

## Rules (contractual)

1. **Immutable.** Once assigned, an ID never changes meaning. To retire one, set
   `status: deprecated` and add `superseded_by:`. Never renumber.
2. **No invention.** If the CV has no descriptor for a (scale, level) — common;
   many scales lack `preA1`/`A1`/`C2` — the level file records
   `no-official-descriptor` for that cell and **no ID is minted**.
3. **`see-reference` cells.** Where the CV cell says "No descriptors available;
   see X", the cell is recorded as `see-reference` (→ X); no new ID.
4. **One scale, one leaf.** SCALE is always a leaf scale from the registry, never
   a CV sub-group heading.
5. **SEQ is per (LEVEL, SCALE).** Sequences are independent across scales/levels.

`scripts/id-audit.sh` enforces format, global uniqueness, and that every
`implements:` resolves to a real (scale, level) in `schema/scale-registry.yml`.
