# Reference Level Descriptions (RLDs) — catalogue

Reference Level Descriptions specify the **language-specific** content (words,
grammar, notions, functions) that realises the CEFR levels for one language.
They are **not** part of this shared framework — they belong to each language's
instantiation (the `daf`, `fle`, `ele`, … repos) — but are catalogued here so an
instantiation knows which authority to build its level content on, alongside the
CEFR CV grounding.

All entries are third-party works, **all-rights-reserved** unless noted; catalogue
and cite, do not reproduce. Add the freely-linkable ones to the `ressources`
site registry as first-class entries (the `resources/` deliverable).

| Framework lang | RLD | Author / publisher | CEFR | Access |
|---|---|---|---|---|
| `de` | **Profile Deutsch** | Glaboniat, Müller, Rusch, Schmitz, Wertenschlag / Klett-Langenscheidt | A1–C2 | commercial (book + CD-ROM) |
| `fr` | **Niveaux pour le français : un référentiel** (A1.1, A1, A2, B1, B2) + **Référentiel C1/C2** | Beacco, Porquier, de Ferrari et al. / Didier | A1–C2 | commercial; some CoE summaries free |
| `es` | **Plan curricular del Instituto Cervantes (PCIC)** | Instituto Cervantes / Biblioteca Nueva | A1–C2 | reference online at `cvc.cervantes.es/…/plan_curricular` (free to consult) |
| `it` | **Profilo della lingua italiana** | Spinelli, Parizzi / La Nuova Italia | A1–B2 | commercial |
| `nl` | **Nederlands Profiel** / Threshold (Drempel) level | Nederlandse Taalunie | A1–C1 | institutional |
| `en` | **English Profile** (English Grammar Profile, English Vocabulary Profile) | Cambridge University Press / Cambridge Assessment | A1–C2 | free registration at `englishprofile.org` |
| `pt` | **Referencial Camões PLE** / QuaREPE | Instituto Camões / DGE | A1–C1 | institutional |
| — (all) | **Reference Level Descriptions** (programme overview) | Council of Europe | — | free at `coe.int` (browser; see `docs/sources.md`) |

## How an instantiation uses these

1. Ground each Can-Do target on the CEFR CV descriptor (the framework already
   provides the ID and the operational statement).
2. Use the language's RLD to fill in **what specifically** realises that
   descriptor at that level (the vocabulary/grammar/notions), citing the RLD.
3. Where a language has **no** RLD at a level, say so and fall back to the CEFR
   descriptor alone — do not invent an inventory.

## Retrieval status

None of the RLDs are retrieved into `.sources/` yet (most are commercial). PCIC,
English Profile and the CoE RLD overview are freely consultable and are the
first candidates to catalogue in the `ressources` site registry.
