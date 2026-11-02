#!/usr/bin/env python3
"""Prepare a source-bound review ledger; never assert mappings or invent reviews."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
import yaml
from conformance_audit import ROOT, SPANS, COVERAGE_THRESHOLD, cells, load_statements


def build(repo: Path) -> dict:
    manifest=yaml.safe_load((repo/'curriculum.yml').read_text())
    catalogue={s['id']:s for s in load_statements() if s.get('status')=='active'}
    pages=[]
    for path in sorted((repo/'content').rglob('*.md')):
        raw=path.read_text();match=re.match(r'\A---\n(.*?)\n---\n(.*)',raw,re.S)
        if not match:continue
        fm=yaml.safe_load(match[1]) or {};cur=fm.get('curriculum') or {}
        if fm.get('page_type') not in {'unit','exam'}:continue
        headings=[{'heading':m[1], 'line':raw[:match.start(2)+m.start()].count('\n')+1} for m in re.finditer(r'^#{2,3}\s+(.+)$',match[2],re.M)]
        pages.append({'page':path.relative_to(repo/'content').with_suffix('').as_posix().removesuffix('/index'),'sha256':hashlib.sha256(raw.encode()).hexdigest(),'type':fm['page_type'],'title':fm.get('title'),'level':cur.get('level'),'skills':fm.get('skills_focus',[]),'headings':headings,'review_status':'pending','reviewer':None,'review_date':None,'mappings':[{'id':sid,'statement':catalogue[sid]['can_do'] if sid in catalogue else None,'current_basis':cur.get('implements_basis','unreviewed'),'task_evidence':None,'fit_explanation':None,'decision':None} for sid in cur.get('implements',[])]})
    proposed={sid for page in pages for sid in [m['id'] for m in page['mappings']]};pop,_=cells();excluded=set()
    if manifest['declared_conformance']=='core-restricted':
        excluded={(x['domain'],x['scale']) for x in yaml.safe_load((ROOT/'profiles/classical-reception.yml').read_text())['out_of_scope']}
    coverage=[]
    for level in SPANS[manifest['declared_conformance']]:
        want=pop[level]-excluded;got={(sid.split('.')[1],sid.split('.')[2]) for sid in proposed if sid.startswith(level+'.')}
        coverage.append({'level':level,'required_cells':math.ceil(len(want)*COVERAGE_THRESHOLD),'populated_cells':len(want),'proposed_cells':len(got&want),'asserted_cells':len({(m['id'].split('.')[1],m['id'].split('.')[2]) for p in pages if p['level']==level for m in p['mappings'] if m['current_basis']=='asserted'}),'missing_cells':[{'domain':domain,'scale':scale,'descriptor_options':[s['id'] for s in catalogue.values() if s['implements']['level']==level and s['implements']['domain']==domain and s['implements']['scale']==scale],'reviewed_task_evidence':None,'action':'review existing tasks or author missing instruction and assessment'} for domain,scale in sorted(want-got)]})
    return {'schema_version':1,'purpose':'Review preparation, not conformance approval','framework_version':(ROOT/'VERSION').read_text().strip(),'target':manifest['declared_conformance'],'coverage':coverage,'pages':pages}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('repo',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    if args.output.exists():raise SystemExit('Refusing to overwrite a ledger that may contain reviewer work; choose a new output path.')
    report=build(args.repo.resolve());args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(f"Prepared {len(report['pages'])} pages; all review decisions remain pending.")


if __name__=='__main__':main()
