# ADR 0001 — CEFR grounding is conformance, not certification

- **Status:** accepted
- **Date:** 2026-07-22

## Context

This framework grounds every Can-Do statement in the Council of Europe's CEFR
Companion Volume (2020) and enforces traceability. It is tempting to read that
rigour as "CEFR-certified" or "CEFR-compliant". It is not, and conflating the
two would mislead downstream users (learners, schools, anyone issuing
statements of level).

The CEFR is explicitly **non-prescriptive** — a reference framework, not a
syllabus specification or an accreditation scheme. There is no body that
certifies a curriculum as "CEFR-compliant". The one official empirical process
that *relates* an instrument to the CEFR is standard-setting for **language
examinations**, described in the *Manual for Relating Language Examinations to
the CEFR*. That process requires standard-setting panels and learner
performance data — it is not a documentation exercise.

## Decision

We define **conformance** (see `docs/conformance.md`) as *every descriptor claim
is accounted for and traceable to an official source*, enforced by the schema
and `scripts/id-audit.sh`. We do **not** claim, and repositories consuming this
framework must not claim, that the framework or its instantiations are
"CEFR-certified", "CEFR-compliant", or equivalent to an exam-board alignment.

Public-facing language uses "grounded in / aligned to the CEFR descriptors",
never "certified".

## Consequences

- Traceability is a documentation guarantee, verified in CI. It is strong and
  meaningful — but it is not accreditation.
- If formal alignment is ever required (e.g. to issue level certificates), that
  is a **separate downstream project**: retrieve the *Manual for Relating
  Language Examinations to the CEFR*, run standard-setting panels, gather pilot
  cohort data. This ADR marks that boundary so the framework's rigour is not
  later mistaken for accreditation.
