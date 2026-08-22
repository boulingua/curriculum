#!/usr/bin/env python3
"""The one conformance resolver. Framework-side and consumer-side, one tool.

    conformance_audit.py self-audit
    conformance_audit.py resolve --manifest conformance.yml --content content/
    conformance_audit.py coverage [--emit-yaml] [--check]
    conformance_audit.py explain A1.REC.overall-oral-comprehension.01
    conformance_audit.py suggest --level A1 --domain INT

WHY THIS EXISTS. `id-audit.sh` hard-codes its own repo root and globs this
repo's `levels/*.md`. It has no --manifest flag and no way to be pointed at a
course, so run from anywhere it audits the framework's own 1,170 statements,
prints OK and exits 0 — regardless of what the course contains. Fifteen course
roadmaps nevertheless wired it as their CI gate and as a milestone acceptance
criterion. Every one of those gates would have passed vacuously, and
`docs/verification.md` ticked a box for a check nothing performed.

THE EXIT CODES ARE THE CONTRACT, and splitting them is the point:

    0  conformant
    1  usage error
    2  manifest fails schema
    3  a WRONG id — malformed, dangling, deprecated, duplicated, out of span
    4  front-matter <-> manifest drift, or coverage --check disagreement
    5  declared level NOT MET — a silently missing in-scope scale
    6  framework version pin mismatch

3 and 5 are different failures and must not be conflated. A course ramping up
its coverage has to fail hard on a *wrong* id while merely being warned about
an *incomplete* one. Collapsing them into a single boolean is how the previous
gate ended up either blocking everything or checking nothing.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LEVELS = ["preA1", "A1", "A2", "B1", "B2", "C1", "C2"]
# preA1 is NOT in any span. It is counted separately and added to a course's
# denominator only when that course lists it in levels_claimed — most do not,
# because preA1 is a literacy-and-first-contact level that a Klasse 5 English
# course has no reason to claim. Folding it into `complete` made that span 441
# where the framework defines it as 412, which would have understated every
# course's coverage by the 29 cells it never intended to cover.
SPANS = {"core": ["A1", "A2", "B1"],
         "core-restricted": ["A1", "A2", "B1"],
         "full": ["A1", "A2", "B1", "B2", "C1"],
         "complete": ["A1", "A2", "B1", "B2", "C1", "C2"]}
PREA1 = "preA1"

# `declared_conformance` is the TARGET. Whether it has been reached is a
# separate field, `conformance_status`, and conflating them was the error in an
# earlier pass of this file: `partial` was accepted as a level, which made
# "aiming at core and not there yet" indistinguishable from a different, lesser
# target. A course does not aim at partial.
STATUSES = {"in-progress", "met"}
# Eight domains. LING and PRAG are real ones, and any grep written from a
# five-domain assumption misses them silently.
DOMAINS = ["REC", "PROD", "INT", "MED", "PLUR", "LING", "SOC", "PRAG"]
ID_RE = re.compile(rf"^({'|'.join(LEVELS)})\.({'|'.join(DOMAINS)})\.([a-z0-9-]+)\.(\d{{2}})$")
COVERAGE_THRESHOLD = 0.90


def load_registry() -> dict[tuple[str, str], dict]:
    """Keyed on (domain, scale): a slug like `turntaking` exists under both INT
    and PRAG, so the slug alone is not a key."""
    rows = yaml.safe_load((ROOT / "schema" / "scale-registry.yml").read_text(encoding="utf-8"))
    return {(r["domain"], r["scale"]): r for r in rows}


def load_statements() -> list[dict]:
    out: list[dict] = []
    for md in sorted((ROOT / "levels").glob("*.md")):
        for block in re.findall(r"```yaml\n(.*?)```", md.read_text(encoding="utf-8"), re.S):
            data = yaml.safe_load(block)
            if isinstance(data, list):
                out += [d for d in data if isinstance(d, dict) and "id" in d]
    return out


def load_empty_scales() -> dict[tuple[str, str], dict]:
    f = ROOT / "schema" / "known-empty-scales.yml"
    if not f.exists():
        return {}
    doc = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    return {(e["domain"], e["scale"]): e for e in doc.get("scales", [])}


def load_excused() -> dict[tuple[str, str], dict]:
    """Every recorded empty scale is excused from coverage — a course cannot
    realize a descriptor that does not exist. The distinction that matters is
    whether the emptiness was CHECKED (empty-in-cv, cited) or merely observed
    (pending), and that shows up as a warning rather than a silent pass."""
    return load_empty_scales()


def cells() -> tuple[dict[str, set], dict[str, set]]:
    """(populated, in_scope) cells per level. A cell is a (level, scale) pair
    where the scale is in_scope; it is populated if an active statement carries
    that level and scale."""
    reg, sts = load_registry(), load_statements()
    in_scope = {(d, s) for (d, s), r in reg.items() if r.get("in_scope")}
    pop: dict[str, set] = defaultdict(set)
    for st in sts:
        if st.get("status") != "active":
            continue
        imp = st.get("implements", {})
        key = (imp.get("domain"), imp.get("scale"))
        if key in in_scope:
            pop[imp.get("level")].add(key)
    return pop, {lv: in_scope for lv in LEVELS}


# ── self-audit ──────────────────────────────────────────────────────────────
def cmd_self_audit(a) -> int:
    reg, sts = load_registry(), load_statements()
    excused = load_excused()
    bad = 0
    seen: set[str] = set()
    for st in sts:
        sid = st["id"]
        m = ID_RE.match(sid)
        if not m:
            print(f"::error::malformed id {sid}")
            bad += 1
            continue
        if sid in seen:
            print(f"::error::duplicate id {sid}")
            bad += 1
        seen.add(sid)
        lv, dom, scale, _ = m.groups()
        if (dom, scale) not in reg:
            print(f"::error::{sid} names no scale in scale-registry.yml")
            bad += 1
    print(f"  {len(sts)} statements, {len(seen)} unique ids, "
          f"{len([r for r in reg.values() if r.get('in_scope')])} in-scope scales")

    # The empty-scale guard. An in-scope scale with zero statements at every
    # level is normally an authoring omission wearing the costume of an empty
    # CV cell — and it matters because the descriptor-existence matrix is what
    # EXCUSES a course from covering a cell. Two falsely-empty scales silently
    # excuse all eighteen courses from ever teaching that thing.
    pop, _ = cells()
    everywhere = set().union(*pop.values()) if pop else set()
    empty = sorted({(d, s) for (d, s), r in reg.items()
                    if r.get("in_scope") and (d, s) not in everywhere})
    unrecorded = [k for k in empty if k not in excused]
    for d, s in unrecorded:
        print(f"::error::in-scope scale {d}.{s} has ZERO statements at any level "
              f"and is not recorded in known-empty-scales.yml. An unrecorded "
              f"empty scale silently excuses all eighteen courses from ever "
              f"teaching it.")
    bad += len(unrecorded)
    pending = [k for k in empty if excused.get(k, {}).get("status") == "pending"]
    for d, s in pending:
        print(f"::warning::{d}.{s} is empty and nobody has checked whether the "
              f"CV has descriptors for it. Recorded as pending, not decided.")
    cited = len(excused) - len(pending)
    if excused:
        print(f"  {len(excused)} empty in-scope scale(s): {cited} verified "
              f"empty in the CV, {len(pending)} pending a determination")
    if bad:
        print(f"\nself-audit FAIL — {bad} problem(s)", file=sys.stderr)
        return 3
    print("self-audit OK")
    return 0


# ── resolve: the consumer gate ──────────────────────────────────────────────
def cmd_resolve(a) -> int:
    man_path = Path(a.manifest)
    if not man_path.exists():
        print(f"::error::no manifest at {man_path}", file=sys.stderr)
        return 1
    man = yaml.safe_load(man_path.read_text(encoding="utf-8")) or {}

    for field in ("framework", "framework_version", "language", "declared_conformance"):
        if field not in man:
            print(f"::error::manifest is missing required field {field!r}", file=sys.stderr)
            return 2
    if man["framework"] != "boulingua-curriculum":
        print(f"::error::framework is {man['framework']!r}, expected "
              f"'boulingua-curriculum'", file=sys.stderr)
        return 2
    declared = man["declared_conformance"]
    if declared not in SPANS:
        print(f"::error::declared_conformance {declared!r} is not one of "
              f"{sorted(SPANS)}", file=sys.stderr)
        return 2

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip() \
        if (ROOT / "VERSION").exists() else "0"
    if str(man["framework_version"]).split("+")[0] != version:
        print(f"::error::manifest pins framework {man['framework_version']}, "
              f"this checkout is {version}", file=sys.stderr)
        return 6

    reg = load_registry()
    valid = {st["id"] for st in load_statements() if st.get("status") == "active"}
    deprecated = {st["id"] for st in load_statements() if st.get("status") != "active"}
    span = SPANS[declared]

    claimed: set[str] = set()
    bad = 0
    for r in man.get("realizations", []) or []:
        rid = r.get("implements_id")
        if not rid:
            print(f"::error::realization with no implements_id: {r}")
            bad += 1
            continue
        m = ID_RE.match(rid)
        if not m:
            print(f"::error::malformed id {rid}")
            bad += 1
            continue
        if rid in deprecated:
            print(f"::error::{rid} is deprecated in the framework")
            bad += 1
            continue
        if rid not in valid:
            print(f"::error::{rid} does not resolve to an active statement")
            bad += 1
            continue
        lv = m.group(1)
        if lv not in span:
            print(f"::error::{rid} is at level {lv}, outside the declared "
                  f"span for {declared} ({'/'.join(span)})")
            bad += 1
            continue
        claimed.add(rid)
    if bad:
        print(f"\nresolve FAIL — {bad} wrong id(s). A wrong id is exit 3 and "
              f"blocks; incomplete coverage is exit 5 and can be warned during "
              f"a ramp. They are not the same failure.", file=sys.stderr)
        return 3

    # ── front matter <-> manifest drift ───────────────────────────────────
    content = Path(a.content) if a.content else None
    if content and content.exists():
        in_content: set[str] = set()
        for md in content.rglob("*.md"):
            for hit in ID_RE.findall(""):    # placeholder, real scan below
                pass
            txt = md.read_text(encoding="utf-8", errors="replace")
            in_content |= set(re.findall(
                rf"\b(?:{'|'.join(LEVELS)})\.(?:{'|'.join(DOMAINS)})\.[a-z0-9-]+\.\d{{2}}\b", txt))
        drift = in_content - claimed
        if drift:
            for d in sorted(drift)[:10]:
                print(f"::error::{d} appears in content but not in the manifest")
            print(f"\nresolve FAIL — {len(drift)} id(s) drift between content "
                  f"and manifest", file=sys.stderr)
            return 4

    # ── coverage against the declared level ───────────────────────────────
    # in-progress: every id must still be correct (exit 3 applies in full), but
    # coverage is not yet asserted, so a shortfall is reported and not failed.
    # This is what makes the per-level backfill tranches possible — a tranche
    # that is not done must not block one that is.
    status = man.get("conformance_status", "in-progress")
    if status not in STATUSES:
        print(f"::error::conformance_status {status!r} is not one of "
              f"{sorted(STATUSES)}", file=sys.stderr)
        return 2
    if status == "in-progress":
        print(f"  {len(claimed)} realizations resolve, targeting {declared}, "
              f"framework {version}")
        print("resolve OK — in-progress: ids verified, coverage not yet claimed")
        return 0

    pop, _ = cells()
    excused = load_excused()
    missing_total = 0
    for lv in span:
        want = {k for k in pop.get(lv, set()) if k not in excused}
        got = {(ID_RE.match(c).group(2), ID_RE.match(c).group(3))
               for c in claimed if c.startswith(lv + ".")}
        covered = len(want & got)
        need = int(len(want) * COVERAGE_THRESHOLD)
        if covered < need:
            print(f"::warning::{lv}: {covered}/{len(want)} in-scope scales covered, "
                  f"{need} needed for {declared}")
            missing_total += need - covered
    print(f"  {len(claimed)} realizations resolve, span {declared} "
          f"({'/'.join(span)}), framework {version}")
    if missing_total:
        print(f"\nresolve: declared level not met — {missing_total} scale(s) short. "
              f"This is exit 5, not exit 3: nothing here is WRONG, it is "
              f"incomplete, and a ramping course may warn on it.", file=sys.stderr)
        return 5
    print("resolve OK — conformant at the declared level")
    return 0


# ── coverage ────────────────────────────────────────────────────────────────
def cmd_coverage(a) -> int:
    pop, scope = cells()
    excused = load_excused()
    doc = {"_generated_by": "scripts/conformance_audit.py coverage --emit-yaml",
           "_rule": ("A cell is a (level, scale) pair where the scale is in_scope. "
                     "It is populated if at least one active statement carries that "
                     "level and scale, and excused if listed in "
                     "known-empty-scales.yml with a CV citation."),
           "levels": {}, "spans": {}, "statements": {}}
    # Cells AND statements. The coverage rule is cell-based — a cell is
    # populated if at least ONE active statement carries it — so deleting a
    # single statement from a scale that has siblings changes no cell count and
    # would slip past a cell-only fingerprint. Recording both means the file
    # detects an edit to the corpus as well as a change in shape.
    sts = [x for x in load_statements() if x.get("status") == "active"]
    doc["statements"]["total"] = len(sts)
    for lv in LEVELS:
        want = {k for k in pop.get(lv, set()) if k not in excused}
        doc["levels"][lv] = len(want)
        doc["statements"][lv] = sum(
            1 for x in sts if x.get("implements", {}).get("level") == lv)
    for name, span in SPANS.items():
        doc["spans"][name] = sum(doc["levels"][lv] for lv in span)
    out = ROOT / "coverage.yml"
    text = yaml.dump(doc, sort_keys=False, allow_unicode=True)
    if a.check:
        if not out.exists():
            print("::error::coverage.yml missing — run coverage --emit-yaml", file=sys.stderr)
            return 4
        if out.read_text(encoding="utf-8") != text:
            print("::error::coverage.yml disagrees with a recomputation. Three "
                  "integers in prose are three integers a gate will eventually "
                  "contradict; regenerate rather than editing.", file=sys.stderr)
            return 4
        print("coverage --check OK")
        return 0
    if a.emit_yaml:
        out.write_text(text, encoding="utf-8")
    for lv in LEVELS:
        print(f"  {lv:5s} {doc['levels'][lv]:3d} cells")
    for name in ("core", "full", "complete"):
        print(f"  {name:16s} {doc['spans'][name]:3d}")
    return 0


def cmd_explain(a) -> int:
    for st in load_statements():
        if st["id"] == a.id:
            print(yaml.dump(st, sort_keys=False, allow_unicode=True))
            return 0
    print(f"::error::{a.id} is not a statement in this framework", file=sys.stderr)
    return 3


SKILL_DOMAIN = {"reading": "REC", "listening": "REC", "speaking_interaction": "INT",
                "speaking_production": "PROD", "writing": "PROD", "mediation": "MED",
                "language_awareness": "LING", "intercultural": "SOC"}
STOP = set("""der die das ein eine und oder aber ich kann nicht mit von zu in an auf
für über the a an and or but can i not with from to in on for of about""".split())


def words(text: str) -> set[str]:
    return {w for w in re.findall(r"[\wäöüßÄÖÜ]{4,}", (text or "").lower())
            if w not in STOP}


def cmd_suggest(a) -> int:
    """Rank the catalogue against ONE page, or list a level when given no page.

    This used to print the first N entries at a level in file order. It read no
    page, saw no skills_focus, and ranked nothing — so the programme's estimate
    that assigning implements costs ten minutes a page rather than thirty rested
    on a filter, not on a suggestion. An author still had to read the catalogue.

    It cannot choose the ids. That is the point of `implements` — a human
    asserted the mapping, and a script that guessed would put a conformance
    claim in a manifest that nobody made. What it can do is put the plausible
    candidates at the top, which is the difference between confirming and
    searching.
    """
    page_terms, page_skills, page_level = set(), [], None
    if a.page:
        raw = Path(a.page).read_text(encoding="utf-8", errors="replace")
        m = re.match(r"\A---\n(.*?)\n---\n(.*)", raw, re.S)
        if not m:
            print(f"::error::{a.page} has no front matter", file=sys.stderr)
            return 2
        fm = yaml.safe_load(m.group(1)) or {}
        page_skills = [str(x) for x in (fm.get("skills_focus") or [])]
        page_level = (fm.get("curriculum") or {}).get("level") or fm.get("cefr_level")
        page_terms = words(m.group(2)[:4000]) | words(str(fm.get("title", "")))
        for c in (fm.get("cefr_can_do") or []):
            page_terms |= words(str(c))

    level = a.level or page_level
    if not level:
        print("::error::give --level, or a --page carrying curriculum.level or "
              "cefr_level", file=sys.stderr)
        return 2

    want = {SKILL_DOMAIN[s] for s in page_skills if s in SKILL_DOMAIN}
    unmapped = [s for s in page_skills if s not in SKILL_DOMAIN]

    scored = []
    for st in load_statements():
        imp = st.get("implements", {})
        if imp.get("level") != level:
            continue
        dom = imp.get("domain")
        if a.domain and dom != a.domain:
            continue
        text = st.get("can_do", "")
        overlap = len(page_terms & words(text)) if page_terms else 0
        # Domain match is worth more than any single shared word: a unit's
        # skills are asserted by its author, its wording is incidental.
        score = (3 if dom in want else 0) + overlap
        scored.append((score, overlap, dom in want, st["id"], text))

    if not scored:
        print(f"  no statements at level {level}"
              + (f" in domain {a.domain}" if a.domain else ""))
        return 0

    scored.sort(key=lambda z: (-z[0], z[3]))
    if a.page:
        print(f"  {Path(a.page).name} — level {level}, skills {page_skills or '(none)'}")
        if unmapped:
            print(f"  ::warning::{unmapped} maps to no domain, so nothing was "
                  f"ranked up for it. Split it first, or these suggestions are "
                  f"blind to half the page.")
        print(f"  ranked against {len(page_terms)} term(s) from the page body, "
              f"title and cefr_can_do\n")
    for score, overlap, dommatch, sid, text in scored[:a.limit]:
        why = []
        if dommatch:
            why.append("domain matches skills_focus")
        if overlap:
            why.append(f"{overlap} shared term(s)")
        tag = f"   [{', '.join(why)}]" if why else ""
        print(f"  {sid}{tag}\n      {text}")
    if a.page and not any(z[0] for z in scored[:a.limit]):
        print("\n  ::warning::nothing scored above zero — no domain matched and no "
              "term overlapped. These are the catalogue in file order, which is "
              "what this command used to print unconditionally.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("self-audit")
    r = sub.add_parser("resolve")
    r.add_argument("--manifest", required=True)
    r.add_argument("--content", default=None)
    c = sub.add_parser("coverage")
    c.add_argument("--emit-yaml", action="store_true")
    c.add_argument("--emit-md", action="store_true")
    c.add_argument("--check", action="store_true")
    e = sub.add_parser("explain")
    e.add_argument("id")
    s = sub.add_parser("suggest")
    s.add_argument("--level", default=None,
                   help="omit when --page carries curriculum.level or cefr_level")
    s.add_argument("--page", default=None, type=str,
                   help="rank the catalogue against this content file")
    s.add_argument("--domain", default=None)
    s.add_argument("--limit", type=int, default=10)
    a = ap.parse_args()
    return {"self-audit": cmd_self_audit, "resolve": cmd_resolve,
            "coverage": cmd_coverage, "explain": cmd_explain,
            "suggest": cmd_suggest}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
