# NOTICE — third-party rights and attribution

## Council of Europe — CEFR

This project's descriptor framework is **grounded in, and derived from**, the
Council of Europe's *Common European Framework of Reference for Languages:
Learning, teaching, assessment* (CEFR) and its **Companion Volume (2020)**.

> Council of Europe (2020), *Common European Framework of Reference for
> Languages: Learning, teaching, assessment – Companion volume*, Council of
> Europe Publishing, Strasbourg. ISBN 978-92-871-8621-8.
> Available at <https://www.coe.int/lang-cefr>. © Council of Europe.

**What Boulingua does and does not reproduce.** The CEFR illustrative
descriptors are © Council of Europe; all rights reserved. This repository does
**not** reproduce the descriptor scales in bulk. It instead:

- records each official descriptor by **stable reference** (source, scale,
  level, position) in `docs/descriptor-crosswalk.md`;
- quotes official wording only **briefly and with attribution**, where a phrase
  is pedagogically load-bearing (never a whole scale);
- publishes **Boulingua's own operational Can-Do statements** that *implement*
  the official descriptors, each carrying an `implements:` reference to the
  source. These operational statements are Boulingua's; the underlying
  competence targets are the Council of Europe's.

The retrieved source PDFs are stored locally under `.sources/` (git-ignored,
see `docs/sources.md`) for grounding and verification only; they are **not**
redistributed through this repository.

Reproduction of Council of Europe material beyond brief attributed quotation
requires prior written permission from the Council of Europe
(publishing@coe.int).

## Boulingua-authored content

Boulingua's operational Can-Do statements, the scale registry, the ID scheme,
schemas, rubrics, tooling and documentation in this repository are licensed
under the repository `LICENSE` (MIT), except where a file states otherwise.
This licence covers Boulingua's own material only; it does not extend to the
Council of Europe descriptors those statements implement.
