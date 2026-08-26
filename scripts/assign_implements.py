#!/usr/bin/env python3
"""Propose curriculum.implements for every unit and exam page.

    assign_implements.py REPO [--apply] [--limit N]

WHAT THIS IS AND IS NOT. `implements` is the field that turns a level claim
into something checkable, and its value comes from somebody having asserted the
mapping. A script cannot assert; it can rank, and it can guarantee the
structural properties a hand assignment would also have to satisfy:

  * every id resolves to a real catalogue statement at the page's own level
  * 3 to 5 ids, never two from the same scale
  * the breadth rule holds — at least one id from a domain outside the page's
    own skills_focus, so a reading unit cannot implement only REC

So every page written here carries `implements_basis: proposed`, and the
manifest stays `conformance_status: in-progress`. That pairing is the honest
statement: the structure is verified, the judgement is pending. A later pass
confirms a tranche and flips it to `asserted`; nothing here pretends that has
already happened.

Ranking is the same signal `conformance_audit suggest` uses — domain match
against skills_focus, plus term overlap with the page's title, its can-do
statements and the first part of its body — because an author confirming a
ranked list is the difference between ten minutes a page and thirty.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FM = re.compile(r"\A(---\n)(.*?)(\n---\n)", re.S)

SKILL_DOMAIN = {"reading": "REC", "listening": "REC", "speaking_interaction": "INT",
                "speaking_production": "PROD", "writing": "PROD", "mediation": "MED",
                "language_awareness": "LING", "intercultural": "SOC"}
# `speaking` is unsplit on efl. It spans INT and PROD, so both count as the
# page's own domains for the breadth rule — otherwise a speaking unit would
# satisfy breadth with an INT id that is squarely its own subject.
SKILL_SPAN = {"speaking": ("INT", "PROD"), "sprechen": ("INT", "PROD")}

STOP = set("""the a an and or but can i you your with from for of about into
their there this that they them then when what which while your yourself
sich ich kann und oder aber mit von für über eine einen einem der die das
des dem den auf als auch nicht noch nur schon sehr sind wird werden""".split())


def words(t: str) -> set[str]:
    return {w for w in re.findall(r"[\wäöüßéèêàçÄÖÜ]{4,}", (t or "").lower())
            if w not in STOP}


def load_catalogue():
    spec = importlib.util.spec_from_file_location("ca", ROOT / "scripts" / "conformance_audit.py")
    m = importlib.util.module_from_spec(spec)
    argv, sys.argv = sys.argv, ["conformance_audit.py", "coverage"]
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    finally:
        sys.argv = argv
    out = []
    for s in m.load_statements():
        imp = s.get("implements") or {}
        if not imp.get("level"):
            continue
        out.append({"id": s["id"], "level": imp["level"], "domain": imp["domain"],
                    "scale": s["id"].split(".")[2], "text": s.get("can_do", ""),
                    "terms": words(s.get("can_do", ""))})
    return out


def choose(cands, own, n_min=3, n_max=5):
    """Top-ranked, spread across the page's declared skills, then broadened.

    Rank alone produced five PROD ids on a unit called "Interview and Portrait"
    whose skills are speaking, writing and language awareness — every pick was
    a real match, and together they described a writing unit. Term overlap is
    incidental vocabulary; the declared skills are an authored fact, and a page
    claiming three of them should implement across all three.

    So: one id per declared domain first, best-ranked, then fill by rank with
    at most two from any single domain, then force the breadth pick.
    """
    picked, scales, dom = [], set(), Counter()

    for d in sorted(own):
        best = next((c for c in cands
                     if c["domain"] == d and c["scale"] not in scales), None)
        if best and len(picked) < n_max:
            picked.append(best); scales.add(best["scale"]); dom[d] += 1

    for c in cands:
        if len(picked) >= n_max:
            break
        if c["scale"] in scales or dom[c["domain"]] >= 2:
            continue
        picked.append(c); scales.add(c["scale"]); dom[c["domain"]] += 1

    if not picked:
        return []
    # Breadth: force one id from outside the page's own domains. Swapping the
    # LOWEST-ranked pick keeps the strongest matches and costs the weakest.
    if own and all(c["domain"] in own for c in picked):
        outside = next((c for c in cands
                        if c["domain"] not in own and c["scale"] not in scales), None)
        if outside:
            picked[-1] = outside
    return picked if len(picked) >= n_min else picked


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repo", type=Path)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    repo = a.repo.resolve()

    cat = load_catalogue()
    by_level: dict[str, list] = {}
    for c in cat:
        by_level.setdefault(c["level"], []).append(c)

    wrote, skipped, narrow = 0, 0, 0
    no_level, no_cands = [], []
    dom_hist, n_hist = Counter(), Counter()

    pages = sorted(p for p in (repo / "content").rglob("*.md"))
    for md in pages:
        raw = md.read_text(encoding="utf-8")
        m = FM.match(raw)
        if not m:
            continue
        fm = yaml.safe_load(m.group(2)) or {}
        if fm.get("page_type") not in ("unit", "exam"):
            continue
        cur = fm.get("curriculum") or {}
        if cur.get("implements"):
            skipped += 1
            continue
        rel = md.relative_to(repo).as_posix()
        level = cur.get("level")
        if not level:
            no_level.append(rel)
            continue

        skills = [str(x) for x in (fm.get("skills_focus") or [])]
        own = {SKILL_DOMAIN[s] for s in skills if s in SKILL_DOMAIN}
        for s in skills:
            own |= set(SKILL_SPAN.get(s, ()))

        body = re.sub(r"\{\{<.*?>\}\}", " ", raw[m.end():][:6000])
        terms = words(fm.get("title", "")) | words(fm.get("subtitle", "")) | words(body)
        for c in (fm.get("cefr_can_do") or []):
            terms |= words(str(c))

        scored = []
        for c in by_level.get(level, []):
            score = (3 if c["domain"] in own else 0) + len(terms & c["terms"])
            scored.append((score, c["id"], c))
        scored.sort(key=lambda z: (-z[0], z[1]))
        cands = [c for _, _, c in scored]
        picked = choose(cands, own)
        if len(picked) < 3:
            no_cands.append(f"{rel}: only {len(picked)} candidate(s) at {level}")
            continue
        if own and all(c["domain"] in own for c in picked):
            narrow += 1

        for c in picked:
            dom_hist[c["domain"]] += 1
        n_hist[len(picked)] += 1
        wrote += 1

        if a.apply:
            ids = "\n".join(f"    - {c['id']}" for c in picked)
            block = f"  implements:\n{ids}\n  implements_basis: proposed\n"
            body_fm = re.sub(r"(?m)^(  level: .*)$", r"\1\n" + block.rstrip("\n"),
                             m.group(2), count=1)
            md.write_text(m.group(1) + body_fm + m.group(3) + raw[m.end():],
                          encoding="utf-8")
        if a.limit and wrote >= a.limit:
            break

    for x in no_level[:5]:
        print(f"::error::{x}: no curriculum.level — assign levels first")
    for x in no_cands[:5]:
        print(f"::error::{x}")
    if narrow:
        print(f"::warning::{narrow} page(s) could not satisfy the breadth rule — "
              f"no candidate outside their own skill domains had a free scale")
    print(f"  {wrote} page(s) " + ("written" if a.apply else "would change")
          + (f", {skipped} already had implements" if skipped else ""))
    print(f"  ids per page: " + ", ".join(f"{k}:{v}" for k, v in sorted(n_hist.items())))
    print(f"  domains used: " + ", ".join(f"{k} {v}" for k, v in dom_hist.most_common()))
    return 1 if (no_level or no_cands) else 0


if __name__ == "__main__":
    raise SystemExit(main())
