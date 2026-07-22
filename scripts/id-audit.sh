#!/usr/bin/env bash
#
# id-audit.sh — verify Boulingua descriptor IDs across the level files.
#
# Checks, for every Can-Do statement in levels/*.md (YAML front-matter blocks):
#   1. id matches {LEVEL}.{DOMAIN}.{SCALE}.{SEQ}
#   2. ids are globally unique
#   3. every implements:.scale exists in schema/scale-registry.yml (in-scope)
#   4. implements:.level and the id's LEVEL agree
#   5. every statement has a resolvable implements: block (source/scale/level/ordinal)
#
# Exit non-zero on any violation. Requires python3 + pyyaml.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$here"

python3 - "$here" <<'PY'
import sys, os, re, glob
sys.path  # noqa
try:
    import yaml
except ImportError:
    sys.exit("id-audit: pyyaml required (pip install pyyaml)")

root = sys.argv[1]
ID_RE = re.compile(r'^(preA1|A1|A2|B1|B2|C1|C2)\.(REC|PROD|INT|MED|PLUR|LING|SOC|PRAG)\.[a-z0-9-]+\.[0-9]{2}$')

reg = yaml.safe_load(open(os.path.join(root, "schema/scale-registry.yml"))) or []
inscope = {e["scale"] for e in reg if e.get("in_scope")}

errors = []
seen = {}
count = 0

def statements_from(path):
    """Yield can-do dicts from a level markdown file's ```yaml blocks."""
    txt = open(path, encoding="utf-8").read()
    for m in re.finditer(r'```ya?ml\n(.*?)```', txt, re.S):
        try:
            block = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            errors.append(f"{os.path.basename(path)}: YAML parse error: {e}")
            continue
        items = block if isinstance(block, list) else block.get("can_dos", []) if isinstance(block, dict) else []
        for it in items or []:
            if isinstance(it, dict) and "id" in it:
                yield path, it

for path in sorted(glob.glob(os.path.join(root, "levels/*.md"))):
    for p, s in statements_from(path):
        count += 1
        sid = s.get("id", "")
        f = os.path.basename(p)
        if not ID_RE.match(sid):
            errors.append(f"{f}: malformed id '{sid}'")
            continue
        if sid in seen:
            errors.append(f"{f}: duplicate id '{sid}' (also {seen[sid]})")
        seen[sid] = f
        lvl, dom, scale, seq = sid.split(".")
        imp = s.get("implements")
        if not isinstance(imp, dict):
            errors.append(f"{f}: {sid} missing implements: block"); continue
        for k in ("source", "domain", "scale", "level", "descriptor_ordinal"):
            if k not in imp:
                errors.append(f"{f}: {sid} implements: missing '{k}'")
        if imp.get("scale") != scale:
            errors.append(f"{f}: {sid} implements.scale '{imp.get('scale')}' != id scale '{scale}'")
        if imp.get("level") != lvl:
            errors.append(f"{f}: {sid} implements.level '{imp.get('level')}' != id level '{lvl}'")
        if imp.get("scale") not in inscope:
            errors.append(f"{f}: {sid} scale '{imp.get('scale')}' not an in-scope registry scale")

print(f"id-audit: checked {count} statement(s) across levels/, {len(inscope)} in-scope scales")
if errors:
    print(f"\nFAIL — {len(errors)} problem(s):")
    for e in errors[:200]:
        print("  -", e)
    sys.exit(1)
print("OK — all ids well-formed, unique, and resolve to registry scales.")
PY
