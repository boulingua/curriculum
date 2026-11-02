# Sources — CEFR primary documents

All descriptor grounding in this repository traces to the primary sources below.
Retrieved sources are archived under `.sources/` (git-ignored — copyrighted, not
redistributed) and verified by SHA-256. **Retrieval method:** the entire
`coe.int` estate returns HTTP 403 to automated clients (curl, WebFetch); the
documents below were obtained through a normal web browser (residential IP) on
the retrieval date and moved into `.sources/`.

## Retrieved and archived (grounding basis)

Index page:
<https://www.coe.int/en/web/common-european-framework-reference-languages/cefr-companion-volume-and-its-language-versions>

| File (`.sources/`) | Document | Ed. | Pages | Bytes | Source URL | Retrieved |
|---|---|---|---|---|---|---|
| `cefr-companion-volume-2020-en.pdf` | CEFR Companion Volume (English) — **primary descriptor authority** | 2020 | 278 | 1 784 779 | `rm.coe.int/…/16809ea0d4` | 2026-07-22 |
| `cefr-companion-volume-2020-fr.pdf` | CECR Volume complémentaire (French) | 2020 | 292 | 2 449 574 | `rm.coe.int/…/1680a4e270` | 2026-07-22 |
| `cefr-companion-volume-2018-de.pdf` | GER Begleitband (German) — translation of the 2018 edition | 2018 | 202 | 15 402 627 | `rm.coe.int/cefr-cv-2018-german/48802a849a` | 2026-07-22 |
| `cefr-companion-volume-2020-intl-sign.pdf` | CEFR CV — International Sign version | 2020 | 276 | 4 600 781 | (CV language-versions page) | 2026-07-22 |

**SHA-256**

```
bfbd8c74090419ac4b9b352d6ba26e180713b31f45265d7d775b7c36dd7ad1b1  cefr-companion-volume-2020-en.pdf
64e46ce90fc56e5f0dec470e13b926b70c69b9384fbbca26270b7077601de01c  cefr-companion-volume-2020-fr.pdf
17707030052c3349b11547db3938b5f0bf18d46b56090c8b6b85d262f6a71d65  cefr-companion-volume-2018-de.pdf
482f713a79b31158950ab7068f2cf6d40075d7782d95370b9dbdd33f04854329  cefr-companion-volume-2020-intl-sign.pdf
```

**Canonical citation.** Council of Europe (2020), *Common European Framework of
Reference for Languages: Learning, teaching, assessment – Companion volume*,
Council of Europe Publishing, Strasbourg. ISBN 978-92-871-8621-8.
Provenance verified from the English title page (© Council of Europe, April
2020; `www.coe.int/lang-cefr`).

**What the CV2020 supplies.** The English CV2020 contains the full set of
illustrative descriptor scales that supersede the 2001 set, plus: the Global
Scale, the Self-Assessment Grid (Appendix 2), the qualitative features of spoken
language / **Table 3** (Appendix 3), the written assessment grid (Appendix 4),
and the salient features of the levels (Appendix 1). It introduces **Pre-A1**
and the new scales for **mediation**, **online interaction**, **plurilingual/
pluricultural competence** and **signing competences**. This single document
therefore satisfies source items 1, 3, 4 and 5 of the acquisition brief.

## Cited but not yet archived (follow-up retrieval)

The following are referenced by the framework but not required to ground the
descriptor scales; retrieve into `.sources/` (same browser method) when a
section needs them. The German CV is the **2018** translation (the only official
German version); EN/FR are 2020.

- **CEFR 2001** — *Common European Framework of Reference for Languages*,
  Council of Europe / Cambridge University Press, 2001. Normative for the
  general competence model and the notional-functional apparatus not restated in
  the CV. Not freely downloadable from coe.int (bookshop / controlled-lending
  scan only). **Status: pending.**
- **Threshold / Waystage / Vantage** (van Ek & Trim); **Breakthrough** (A1) —
  notional-functional inventories. Reference, not descriptor authority. Pending.
- **ALTE Can-Do statements** — domain (social/tourist, work, study) breakdowns.
  Pending.
- **Manual for Relating Language Examinations to the CEFR** — assessment /
  alignment. Pending (relevant only if formal alignment is ever pursued — see
  `docs/adr/0001-cefr-conformance-not-certification.md`).
- **CEFR-J** (Tokyo Univ. of Foreign Studies) — validated sub-level breakdown;
  precedent for A1.1–A1.3 splitting. Reference, not authority. Pending.
- **Reference Level Descriptions (RLDs)** — *Profile Deutsch*, *Un référentiel
  pour le français*, *Plan Curricular del Instituto Cervantes*, *Profilo della
  lingua italiana*, *Nederlands Profiel*, *English Profile*. Language-specific;
  belong under `boulingua/languages/*` and are catalogued in the `ressources`
  registry, not in this shared framework. Pending.

## Coverage recheck, 30 October 2026

The official English PDF was accessible during this audit. Pages 65–66 and
88–89 confirm that the two repository-wide empty scales are omissions here,
not empty official scales. `schema/known-empty-scales.yml` records the affected
levels and citations. Framework self-audit blocks release, and course resolution
refuses `met` while an applicable omission remains. In-progress manifests can
still be checked for structural integrity. Existing descriptor IDs are unchanged.

## Source restoration, 31 October 2026

The authoritative English PDF was read directly at the Council of Europe URL
above, tables on printed pages 65–66 and 88–89. It supplies 18 rows for Addressing
audiences and 11 for Co-operating. The latter explicitly distinguishes its B2+
rows from B2; that distinction is retained as source metadata. Twenty-nine
additive operational statements restore these rows without replacing existing
IDs. The old omission record and pending independent review are retained in
`schema/source-restoration-2026-10-31.yml`. A structural self-audit may pass after
restoration; a `met` course claim remains blocked until independent source review
is actually recorded. No human approval is implied by the restoration.
