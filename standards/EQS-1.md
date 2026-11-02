# EQS-1 — the Boulingua teaching-unit contract

This is the canonical implementation of accepted organisation ADR 0014. Numeric
limits and counting rules live in [eqs.yml](eqs.yml); labels and transitional
synonyms live in [step-map.yml](step-map.yml). A structural pass does not imply
linguistic, educational or curriculum approval.

## A complete learning unit

Each unit starts with clear learner goals and a purposeful lead-in. It then
contains exactly five level-two keyed sections, in this order:

1. **activate**: elicit relevant knowledge and an initial learner response.
2. **input**: supply the actual text, recording or other model needed by the tasks,
   with enough language support for the declared learner level.
3. **practise**: develop and check useful component skills with feedback.
4. **apply**: ask learners to achieve a communicative result for a stated audience
   or situation. A gap-fill, isolated transformation or translation drill alone
   does not fulfil this step.
5. **reflect**: let learners check their work against the stated outcomes, identify
   evidence and decide a next step. Relate this to reviewed descriptor mappings.

```yaml
steps: [activate, input, practise, apply, reflect]
exam:
  page: course/units/example-exam
  format: written-and-oral
  duration_minutes: 45
  points: 30
  skills: [reading, speaking_interaction, writing]
```

These illustrative assessment values must be replaced by the actual exam's
instructions and arithmetic. `exam.page` is a relative path beneath `content`,
without the extension or trailing `/index`. It is not a public URL or filename
of a worksheet. Unit and exam remain independently printable and reviewable.

Write headings such as `## 2. Apporter {#input}`. Preserve the visible language
and wording; the anchor carries identity. The renderer preserves prior heading
fragments as aliases alongside the canonical anchor. A lead-in is not silently
relabeled Activate: the first step needs an actual learner activation task.
German instructions are the current scaffold default; reviewed target-language
labels can be added without changing any key.

## Assessment and solutions

Every unit has exactly one sibling exam page. The unit's `## … {#exam}` section
contains only the format, duration, points, assessed skills and a link to that
page. Transfer an existing assessment before replacing its old block; never
discard tasks or keys to pass a structural check. An existing exam's differing
version is retained as a clearly identified rehearsal or archive while the
canonical assessment is reconciled. New examinations need a realistic duration,
explicit task maxima, correct arithmetic, answer/marking guidance and accessible
inputs. A model or rehearsal is labeled as such, not presented as a full exam.

Keys use `{{< details summary="Solutions" >}} … {{< /details >}}`.
The `callout collapse="true"` alias remains valid when it renders the same key
semantics. Learner PDFs exclude keys; teacher PDFs retain them. Teacher notes,
source attribution and alignment remain available but do not inflate learner
body or exam lengths. An input needed for a task must appear in the standalone
material or have an explicit usable access path.

## Calibrated length and counting

Bands I, II and III require respectively 950–1500, 1000–1800 and 1500–2800 learner
body words; exams require at least 1900, 1900 and 2200 rendered characters.
For school courses, `klassenstufe` selects the band (5–7, 8–10, 11–13); otherwise
`curriculum.level` selects it (preA1–A2, B1–B2, C1–C2). This keeps an advanced
school assessment from silently receiving a lower threshold because its
proposed descriptor level has not yet been reviewed.

Count the learner body through Reflect, excluding separately identified keys,
exam pointer, teacher notes, alignment, sources and download sections. Strip
front matter, fenced code, shortcode delimiters, HTML and Markdown syntax; keep
actual text inside ordinary shortcodes. Count table cells, link labels and image
alternative text. Word tokens are Unicode letter/number runs allowing internal
apostrophes or hyphens. Exam character counts use learner-facing rendered text,
with whitespace collapsed to one space, measured as Unicode code points.

These are fixed measurement choices, not permission to pad content. Counts flag
review work; they do not certify the pedagogical value of words. Existing
courses retain their documented warning ramp until content retrofit is closed.
A course must not label that milestone complete merely by weakening a limit.

## Evidence and review

Use [the unit checklist](checklists/unit-review.md) for each reviewed tranche.
Use [rubric definitions](../assessment/rubrics/rubrics.yml) to choose criteria;
record the actual task, criterion weights and evidence rather than presenting
an illustrative rubric as official CEFR certification. Keep proposed mappings
proposed until a reviewer reads the relevant tasks. Never fabricate listener,
native-language reviewer or descriptor-approval records.

Audio is optional. A logged transcript-only decision is supported; a listening
task needs a real listening route (reviewed recording or a suitable live-reader
script) and must state its conditions. A readable transcript does not, by itself,
prove that listening was assessed.
