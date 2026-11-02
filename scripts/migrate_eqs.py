#!/usr/bin/env python3
"""Preserve source while keying existing steps and separating assessments.

Dry run by default. Apply writes original sources plus SHA-256 manifest under
course docs/eqs-archive before touching content. Divergent assessment versions
are preserved and flagged for individual reconciliation, never merged by a
similarity guess. No descriptor mapping is asserted by this migration.
"""
from __future__ import annotations
import argparse,copy,hashlib,io,json,re,os,tempfile
from html.parser import HTMLParser
from pathlib import Path
from ruamel.yaml import YAML

STEPS=['activate','input','practise','apply','reflect']
FM=re.compile(r'\A---\n(.*?)\n---\n(.*)\Z',re.S)
H2=re.compile(r'^## (.+)\n',re.M)
Y=YAML();Y.preserve_quotes=True;Y.width=4096


def read(raw):
    m=FM.match(raw)
    if not m:raise ValueError('missing YAML front matter')
    return Y.load(m[1]),m[2]


def write(fm,body):
    buf=io.StringIO();Y.dump(fm,buf);raw='---\n'+buf.getvalue()+'---\n'+body
    check,_=read(raw)
    if check!=fm:raise ValueError('round-trip metadata drift')
    return raw


class Headings(HTMLParser):
    def __init__(self):super().__init__();self.current=None;self.rows={};self.heading_link=False
    def handle_starttag(self,tag,attrs):
        if tag=='h2':self.current=[dict(attrs).get('id'),'']
        if tag=='a' and 'heading-link' in dict(attrs).get('class','').split():self.heading_link=True
    def handle_data(self,data):
        if self.current is not None and not self.heading_link:self.current[1]+=data
    def handle_endtag(self,tag):
        if tag=='a':self.heading_link=False
        if tag=='h2' and self.current:
            key=self.current[1].strip().replace('’', "'")
            if self.current[0]:self.rows[key]=self.current[0]
            self.current=None


def former_anchors(repo,path,fm):
    rel=path.parent.relative_to(repo/'content');parts=list(rel.parts)
    if fm.get('slug'):parts[-1]=str(fm['slug'])
    rendered=repo/'public'/Path(*parts)/'index.html'
    if not rendered.is_file():raise ValueError(f'exact old headings need existing render: {rendered}')
    parser=Headings();parser.feed(rendered.read_text());return parser.rows


def section(body,start):
    match=next((m for m in H2.finditer(body) if start(m[1])),None)
    if not match:return None
    end=H2.search(body,match.end());return match.start(),end.start() if end else len(body),match[1],body[match.end():end.start() if end else len(body)]


def normalize(text):return re.sub(r'\s+',' ',text).strip()


def activation_split(text):
    lines=text.splitlines(keepends=True);offset=0
    for line in lines:
        clean=line.strip().strip('*').strip()
        if len(clean)<180 and re.match(r'(Aktivierungsfragen|Fragen zum|Einstiegsfragen|Leitfragen|Diskutieren Sie|Sprechen Sie|Sprechen wir|Überlegen Sie)',clean):
            return text[:offset],text[offset:]
        offset+=len(line)
    # An actual existing learner list, never a line inside a quoted story.
    m=re.search(r'^(?:- |\d+\. )',text,re.M)
    if m:return text[:m.start()],text[m.start():]
    raise ValueError('no existing activation task boundary; individual authoring required')


def points(body):
    patterns=[r'\*\*(?:Total|Gesamt|Punkte)\.?\*\*\s*(\d+)',r'Barème\s*:\s*(\d+)',r'\|\s*\*?\*?(?:Total|Summe)\*?\*?\s*\|\s*\*?\*?(\d+)',r'(?:insgesamt|Gesamtpunktzahl)\D{0,10}(\d+)']
    for pat in patterns:
        m=re.search(pat,body,re.I)
        if m:return int(m[1])
    return None


def migrate(repo:Path,code:str):
    changes={};ledger=[]
    for path in sorted((repo/'content').rglob('*.md')):
        raw=path.read_text();fm,body=read(raw)
        if fm.get('page_type')!='unit' or fm.get('steps')==STEPS:continue
        original_body=body;anchors=former_anchors(repo,path,fm);aliases={}
        # Promote real activation questions already present in every DaF lead-in.
        if code=='daf':
            lead=section(body,lambda h:h.startswith('Einstieg'))
            if not lead:raise ValueError(f'{path}: missing lead-in')
            story,task=activation_split(lead[3]);body=body[:lead[0]]+'## '+lead[2]+'\n'+story.rstrip()+'\n\n## Aktivieren\n\n'+task.lstrip()+body[lead[1]:]
        labels={'efl':{'activate':'1. Activate','input':'2. Input','practise':'3. Practise','apply':'4. Produce','reflect':'5. Reflect'},'fle':{'activate':'1. Activer','input':'2. Apporter','practise':"3. S'entraîner",'apply':'4. Produire','reflect':'5. Réfléchir'},'daf':{'activate':'Aktivieren','input':'Input','practise':'Üben','apply':'Anwenden','reflect':'Reflexion'}}[code]
        for key,label in labels.items():
            pattern=rf'^## {re.escape(label)}\s*$';found=re.search(pattern,body,re.M)
            if not found:raise ValueError(f'{path}: missing {label}')
            if label not in anchors and not (code=='daf' and key=='activate'):
                raise ValueError(f'{path}: old anchor for {label} is not known')
            if label in anchors and anchors[label]!=key:aliases[key]=[anchors[label]]
            body=re.sub(pattern,'## '+label+' {#'+key+'}',body,count=1,flags=re.M)
        fm['steps']=STEPS.copy();fm['anchor_aliases']=aliases
        teacher={'efl':'Downloads','fle':'Notes pour l\'enseignant·e','daf':'Hinweise für Lehrkräfte'}[code]
        teacher_match=next((m for m in H2.finditer(body) if m[1]==teacher or (code=='fle' and m[1].startswith('Notes pour l'))),None)
        if teacher_match:
            old=teacher_match[1];label='Teacher notes' if code=='efl' else old
            if old in anchors:aliases['teacher-notes']=[anchors[old]]
            body=body[:teacher_match.start()]+'## '+label+' {#teacher-notes}\n'+body[teacher_match.end():]
        # Preserve visible keys but put their content behind the canonical control.
        solution=section(body,lambda h:bool(re.fullmatch(r'Solutions|Lösungen|Corrigé',h)))
        if solution:
            wrapped='## '+solution[2]+'\n\n{{< details summary="'+solution[2]+'" >}}\n'+solution[3].strip()+'\n{{< /details >}}\n\n'
            body=body[:solution[0]]+wrapped+body[solution[1]:]
        exam=section(body,lambda h:h=='Exam example' or h=='Évaluation' or h.startswith('Prüfung'))
        if not exam:raise ValueError(f'{path}: missing embedded assessment')
        suffix='-exam' if code=='efl' else '_exam';exam_path=path.parent.with_name(path.parent.name+suffix)/'index.md'
        identical=False;new_exam=False
        if exam_path.exists():
            exraw=exam_path.read_text();exfm,exbody=read(exraw);identical=normalize(exam[3]) in normalize(exbody)
        else:
            if code!='daf':raise ValueError(f'{path}: missing expected existing exam {exam_path}')
            new_exam=True;exfm=copy.deepcopy(fm)
            for key in ['steps','anchor_aliases','presentation','worksheet','audio','aliases','exam','description']:
                exfm.pop(key,None)
            exfm['page_type']='exam';exfm['title']='Prüfungsübung — '+str(fm['title']);exfm['material_slug']=path.parent.name+'-exam';exfm['assessment_review']='pending'
            if exfm.get('slug'):exfm['slug']=str(exfm['slug'])+'-exam'
            exfm['curriculum']['implements_basis']='proposed';exfm['curriculum']['level_basis']='derived-from-unit'
            exbody='\n'+exam[3].strip()+'\n';changes[exam_path]=(None,write(exfm,exbody))
        key=exam_path.parent.relative_to(repo/'content').as_posix();duration=re.search(r'(\d+)\s*(?:minutes|Minuten)',exbody,re.I)
        meta={'page':key,'format':'module-practice' if new_exam else 'existing-assessment','duration_minutes':int(duration[1]) if duration else None,'points':points(exbody),'skills':copy.deepcopy(fm.get('skills_focus',[]))};fm['exam']=meta
        if exam[2] in anchors and anchors[exam[2]]!='exam':aliases['exam']=[anchors[exam[2]]]
        pending=[]
        # Safe automatic transfer only when exact content is already present or
        # there was no sibling. Divergent tasks stay in the unit pending review.
        if identical or new_exam:
            caption={'efl':'Open the separate assessment','fle':'Ouvrir l’évaluation séparée','daf':'Prüfungsübung öffnen'}[code]
            pointer='## '+exam[2]+' {#exam}\n\n['+caption+']({{< relref "'+key+'" >}}).\n\n'
            body=body[:exam[0]]+pointer+body[exam[1]:]
        else:
            pending.append('embedded and sibling assessment differ; retained both for individual reconciliation')
            body=body[:exam[0]]+'## '+exam[2]+' {#exam}\n'+exam[3]+body[exam[1]:]
        if meta['duration_minutes'] is None:pending.append('duration requires review')
        if meta['points'] is None:pending.append('point total requires review')
        if new_exam:pending.append('transferred module task requires standalone input, rubric and scope review')
        changes[path]=(raw,write(fm,body));ledger.append({'unit':path.relative_to(repo).as_posix(),'exam':exam_path.relative_to(repo).as_posix(),'new_exam':new_exam,'exact_existing_assessment':identical,'pending':pending,'review_status':'pending'})
    return changes,ledger


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('repo',type=Path);ap.add_argument('--code',choices=['efl','fle','daf'],required=True);ap.add_argument('--apply',action='store_true');args=ap.parse_args();repo=args.repo.resolve();changes,ledger=migrate(repo,args.code)
    if args.apply:
        archive=repo/'docs/eqs-archive/2026-10-31'
        if archive.exists():raise SystemExit('Archive exists; inspect prior migration before rerunning')
        # Stage and parse every result before preserving/replacing any source.
        for path,(_,after) in changes.items():read(after)
        archive.mkdir(parents=True);records=[]
        for path,(before,after) in changes.items():
            rel=path.relative_to(repo)
            if before is not None:
                backup=archive/rel;backup.parent.mkdir(parents=True,exist_ok=True);backup.write_text(before)
            records.append({'path':rel.as_posix(),'before_sha256':hashlib.sha256(before.encode()).hexdigest() if before is not None else None,'after_sha256':hashlib.sha256(after.encode()).hexdigest()})
        (archive/'manifest.json').write_text(json.dumps({'schema_version':1,'files':records,'review':ledger},ensure_ascii=False,indent=2)+'\n')
        for path,(_,after) in changes.items():
            path.parent.mkdir(parents=True,exist_ok=True)
            fd,name=tempfile.mkstemp(dir=path.parent,prefix='.eqs-',suffix='.tmp')
            with os.fdopen(fd,'w') as f:f.write(after)
            staged=Path(name);read(staged.read_text());staged.replace(path)
    print(json.dumps({'units':len(ledger),'changed_or_new_files':len(changes),'new_exams':sum(x['new_exam'] for x in ledger),'exact_existing_exams':sum(x['exact_existing_assessment'] for x in ledger),'divergent_existing_exams':sum(not x['new_exam'] and not x['exact_existing_assessment'] for x in ledger),'applied':args.apply},indent=2))


if __name__=='__main__':main()
