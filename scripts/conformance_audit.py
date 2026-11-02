#!/usr/bin/env python3
"""The one conformance resolver. Framework-side and consumer-side, one tool.

    conformance_audit.py self-audit
    conformance_audit.py COURSE_REPO                 <- the battery's shape
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
import math
import json
from datetime import date
from jsonschema import Draft202012Validator, FormatChecker
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
    return {key: row for key, row in load_empty_scales().items()
            if row.get('status') == 'empty-in-cv'}


def pending_source_reviews() -> list[dict]:
    """Restoration is structural work; an unreviewed repair is not source approval."""
    records = []
    for path in sorted((ROOT / 'schema').glob('source-restoration-*.yml')):
        record = yaml.safe_load(path.read_text()) or {}
        if record.get('review_status') != 'reviewed':
            records.append(record)
    return records


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
    excused = load_empty_scales()
    bad = 0
    seen: set[str] = set()
    schema = json.loads((ROOT / 'schema/can-do.schema.json').read_text())
    validator = Draft202012Validator(schema)
    for st in sts:
        for error in validator.iter_errors(st):
            print(f"::error::{st.get('id', '?')}: {error.message}")
            bad += 1
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
        imp = st.get('implements', {})
        if (lv, dom, scale) != (imp.get('level'), imp.get('domain'), imp.get('scale')):
            print(f"::error::{sid}: id disagrees with implements")
            bad += 1
        if st.get('status') == 'deprecated' and st.get('superseded_by') not in {x['id'] for x in sts}:
            print(f"::error::{sid}: superseded_by does not resolve")
            bad += 1
        if (dom, scale) not in reg:
            print(f"::error::{sid} names no scale in scale-registry.yml")
            bad += 1
        if imp.get('source_level', lv).rstrip('+') != lv:
            print(f"::error::{sid}: printed source level disagrees with base level")
            bad += 1
    crosswalk = (ROOT / 'docs/descriptor-crosswalk.md').read_text()
    crosswalk_ids = re.findall(r'^\| `([^`]+)` \|', crosswalk, re.M)
    if set(crosswalk_ids) != seen or len(crosswalk_ids) != len(set(crosswalk_ids)):
        print('::error::descriptor crosswalk must contain each framework ID exactly once')
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
    unresolved = [k for k in empty if excused.get(k, {}).get("status") != "empty-in-cv"]
    for d, scale in unresolved:
        row = excused.get((d, scale), {})
        print(f"::error::{d}.{scale}: unresolved framework coverage ({row.get('status', 'unrecorded')}); {row.get('cite', 'source review required')}")
    bad += len([k for k in unresolved if k not in unrecorded])
    cited = [k for k in empty if excused.get(k, {}).get('status') == 'empty-in-cv']
    for key in cited:
        if not excused[key].get('cite'):
            print(f"::error::{key}: an empty-in-cv exemption requires a source citation")
            bad += 1
    if excused:
        print(f"  {len(cited)} source-verified empty scales; {len(unresolved)} unresolved omissions")
    if bad:
        print(f"\nself-audit FAIL — {bad} problem(s)", file=sys.stderr)
        return 3
    for review in pending_source_reviews():
        print(f"::warning::source restoration {review.get('restoration_date')}: {review.get('review_status', 'review status missing')}")
    print("self-audit OK")
    return 0


# ── resolve: the consumer gate ──────────────────────────────────────────────
def cmd_resolve(a) -> int:
    man_path = Path(a.manifest)
    try:
        man = yaml.safe_load(man_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 2
    if not isinstance(man, dict):
        print("::error::manifest must be a mapping")
        return 2
    schema = json.loads((ROOT / 'schema/conformance.schema.json').read_text())
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(man))
    if errors:
        for error in errors:
            print(f"::error::manifest {list(error.path)}: {error.message}")
        return 2
    declared = man['declared_conformance']
    status = man.get('conformance_status', 'in-progress')
    version = (ROOT / 'VERSION').read_text().strip()
    if man['framework_version'].split('+')[0] != version:
        print(f"::error::manifest pins {man['framework_version']}; framework is {version}")
        return 6
    excluded = set()
    if declared == 'core-restricted':
        if man.get('profile') != 'classical-reception' or man['language'] != 'la':
            print('::error::core-restricted requires the approved Latin classical-reception profile')
            return 2
        profile = yaml.safe_load((ROOT / 'profiles/classical-reception.yml').read_text())
        excluded = {(x['domain'], x['scale']) for x in profile['out_of_scope']}
    elif man.get('profile') or man.get('out_of_scope'):
        print('::error::profile exclusions require core-restricted and an approved profile')
        return 2
    if any((x['domain'], x['scale']) not in excluded for x in man.get('out_of_scope', [])):
        print('::error::out_of_scope includes a scale outside the approved profile')
        return 2
    span = list(SPANS[declared])
    if PREA1 in man.get('levels_claimed', []):
        span.insert(0, PREA1)
    if any(lv not in span for lv in man.get('levels_claimed', [])):
        print('::error::levels_claimed contains a level outside the target span')
        return 2
    if status == 'met':
        for review in pending_source_reviews():
            if any(ID_RE.fullmatch(sid) and ID_RE.fullmatch(sid).group(1) in span
                   and (ID_RE.fullmatch(sid).group(2), ID_RE.fullmatch(sid).group(3)) not in excluded
                   for sid in review.get('new_ids', [])):
                print('::error::restored framework source rows still require recorded source/editorial approval before a met claim')
                return 5
        unresolved = [(key, row) for key, row in load_empty_scales().items()
                      if row.get('status') != 'empty-in-cv' and key not in excluded
                      and set(row.get('source_levels', span)) & set(span)]
        if unresolved:
            for (domain, scale), row in unresolved:
                print(f'::error::{domain}.{scale}: unresolved framework omission prevents a met claim')
            return 5
    valid = {st['id'] for st in load_statements() if st.get('status') == 'active'}
    claimed, pairs, bad = set(), set(), []
    for row in man.get('realizations', []):
        rid, page = row['implements_id'], row.get('page', '')
        match = ID_RE.fullmatch(rid)
        if not match or rid not in valid or match.group(1) not in span:
            bad.append(f'{rid}: malformed, inactive, unresolved or outside the target span')
            continue
        if (match.group(2), match.group(3)) in excluded:
            bad.append(f'{rid}: profile excludes this scale')
        if (page, rid) in pairs:
            bad.append(f'{page}: duplicate realization {rid}')
        if page and (Path(page).is_absolute() or '..' in Path(page).parts or '\\' in page):
            bad.append(f'{page}: page must be a relative content path')
        pairs.add((page, rid))
        claimed.add(rid)
    if bad:
        for error in bad: print(f'::error::{error}')
        return 3
    # Match (page, descriptor) pairs in BOTH directions. IDs in prose do not count.
    content = Path(a.content) if a.content else None
    proposed = []
    if content is not None:
        if not content.is_dir():
            print(f'::error::content directory is missing: {content}')
            return 4
        actual, page_stats, basis_stats = set(), defaultdict(int), defaultdict(int)
        for md in sorted(content.rglob('*.md')):
            text = md.read_text(encoding='utf-8')
            front = re.match(r'\A---\s*\n(.*?)\n---(?:\n|$)', text, re.S)
            try:
                fm = yaml.safe_load(front.group(1)) if front else {}
                block = (fm or {}).get('curriculum') or {}
                ids = block.get('implements') or []
                if not isinstance(ids, list) or any(not isinstance(x, str) for x in ids):
                    raise ValueError('curriculum.implements must be a list of descriptor ids')
            except (yaml.YAMLError, AttributeError, ValueError) as exc:
                print(f'::error::{md}: {exc}')
                return 2
            key = md.relative_to(content).with_suffix('').as_posix()
            if key.endswith('/index'): key = key[:-6]
            if len(ids) != len(set(ids)) or any(x not in valid for x in ids):
                print(f'::error::{md}: duplicate or unresolved descriptor id')
                return 3
            actual.update((key, rid) for rid in ids)
            if ids:
                page_stats[block.get('level')] += 1
                basis_stats[block.get('implements_basis', 'unreviewed')] += 1
                if block.get('implements_basis') != 'asserted': proposed.append(key)
                if any(ID_RE.fullmatch(x).group(1) != block.get('level') for x in ids):
                    print(f'::error::{md}: descriptor level differs from curriculum.level')
                    return 3
        drift = pairs ^ actual
        if drift:
            for page, rid in sorted(drift)[:15]:
                where = 'manifest only' if (page, rid) in pairs else 'content only'
                print(f'::error::{page}: {rid} ({where})')
            print(f'::error::{len(drift)} page/descriptor pairs disagree')
            return 4
        if 'pages' in man and man['pages'] != dict(page_stats):
            print('::error::manifest pages summary disagrees with source')
            return 4
        if 'implements' in man:
            measured = {'distinct_descriptors':len(claimed), 'proposed':basis_stats['proposed'], 'asserted':basis_stats['asserted']}
            if man['implements'] != measured:
                print(f'::error::manifest implements summary disagrees with source: {measured}')
                return 4
    if status == 'in-progress':
        print(f'resolve OK — {len(pairs)} realizations, {len(claimed)} distinct descriptors; target {declared}; coverage not claimed')
        return 0
    if content is None or proposed:
        print(f'::error::met requires source pages and asserted mappings; {len(proposed)} pages remain unreviewed')
        return 5
    pop, _ = cells()
    missing, short = set(), 0
    for lv in span:
        want = pop.get(lv, set()) - excluded
        got = {(ID_RE.fullmatch(c).group(2), ID_RE.fullmatch(c).group(3)) for c in claimed if c.startswith(lv + '.')}
        absent = want - got
        missing.update((lv, dom, scale) for dom, scale in absent)
        need = math.ceil(len(want) * COVERAGE_THRESHOLD)
        # ADR-0013 keeps these domains complete within the restricted profile.
        strict = {'REC', 'MED', 'PLUR', 'LING', 'SOC', 'PRAG'} if excluded else set()
        if len(want & got) < need or any(dom in strict for dom, _ in absent):
            print(f'::error::{lv}: {len(want & got)}/{len(want)} cells; minimum {need}')
            short += 1
    gaps = {(x['level'], x['domain'], x['scale']) for x in man.get('gaps', [])}
    if gaps != missing or len(gaps) != len(man.get('gaps', [])):
        print('::error::gaps must record each uncovered cell exactly once, with reason and scheduled date')
        return 5
    if short: return 5
    print('resolve OK — declared coverage verified against asserted source mappings')
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
        profile_excluded = set()
        if name == 'core-restricted':
            profile = yaml.safe_load((ROOT/'profiles/classical-reception.yml').read_text())
            profile_excluded = {(x['domain'],x['scale']) for x in profile['out_of_scope']}
        doc["spans"][name] = sum(len(pop.get(lv,set()) - set(excused) - profile_excluded) for lv in span)
    out = ROOT / "coverage.yml"
    text = yaml.dump(doc, sort_keys=False, allow_unicode=True)
    if a.check:
        if not out.exists():
            print("::error::coverage.yml missing — run coverage --emit-yaml", file=sys.stderr)
            return 4
        if yaml.safe_load(out.read_text(encoding="utf-8")) != doc:
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
    # A BARE REPO PATH resolves that course. `kit check` hands every gate the
    # repo and nothing else, so a tool whose only entry points were subcommands
    # could not be in the battery — which is why gate A16 sat battery:false with
    # a `runs:` field naming a workflow that never invoked it. It was status:
    # live and had no invocation site anywhere in the organisation.
    argv = sys.argv[1:]
    if argv and not argv[0].startswith("-") and argv[0] not in (
            "self-audit", "resolve", "coverage", "explain", "suggest"):
        repo = Path(argv[0]).resolve()
        if not repo.is_dir():
            print(f"::error::{repo} is not a directory", file=sys.stderr)
            return 2
        manifest = repo / "curriculum.yml"
        if not manifest.exists():
            print(f"A16 n/a — {repo.name} declares no curriculum.yml, so it "
                  f"claims no conformance to resolve.")
            return 0
        sys.argv = [sys.argv[0], "resolve", "--manifest", str(manifest),
                    "--content", str(repo / "content")]

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
