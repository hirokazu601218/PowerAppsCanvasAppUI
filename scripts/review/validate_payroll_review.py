#!/usr/bin/env python3
"""Static validation of PAY-HTML-001 canonical model and generated artifacts."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/review/pay-html-001'
class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.ids=[];self.links=[];self.resources=[];self.operations=[];self.reqs=[];self.tags=[];self.labels=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs);self.tags.append(tag)
        if 'id' in d:self.ids.append(d['id'])
        if 'href' in d:self.links.append(d['href'])
        if tag in ('script','img','iframe','link'):
            for key in ('src','href'):
                if key in d:self.resources.append(d[key])
        if 'data-operation-id' in d:self.operations.append(d['data-operation-id'])
        if 'data-requirement-id' in d:self.reqs.extend(d['data-requirement-id'].split())
        if tag=='label' and 'for' in d:self.labels.append(d['for'])

def validate():
    errors=[];d=json.loads((OUT/'data/model.json').read_text());screens={s['id']:s for s in d['screens']};ops={o['id']:o for o in d['operations']};sources={s['id']:s for s in d['sources']}
    def require(test,message):
        if not test:errors.append(message)
    require(len(screens)==len(d['screens']),'Duplicate screen IDs')
    require(len(ops)==len(d['operations']),'Duplicate operation IDs')
    require(len({o['transition_id'] for o in ops.values()})==len(ops),'Duplicate transition IDs')
    require(re.fullmatch(r'[0-9a-f]{40}',d['metadata']['source_sha']), 'Source SHA must be full')
    for s in sources.values():require((ROOT/s['path']).is_file(),f'Missing source: {s["path"]}')
    for o in ops.values():
        for key in ('screen_id','destination_screen_id'):require(o[key] in screens,f'{o["id"]} invalid {key}: {o[key]}')
        for key in ('requirements','source_ids','roles','acceptance'):require(bool(o.get(key)),f'{o["id"]} empty {key}')
        for key in ('visible','enabled','validation','process','retained','reset','success','failure','cancel','unsaved'):require(bool(o.get(key)),f'{o["id"]} empty {key}')
        for src in o['source_ids']:require(src in sources,f'{o["id"]} unknown source {src}')
    for f in d['workflows']:
        nodes={s['id']:s for s in f['steps']}
        require(len(nodes)==len(f['steps']),f'{f["id"]} duplicate nodes')
        for e in f['edges']:
            require(e['from'] in nodes and e['to'] in nodes,f'{f["id"]} invalid edge')
        for step in f['steps']:
            if step.get('operation_id'):require(step['operation_id'] in ops,f'{f["id"]} invalid operation {step["operation_id"]}')
            if step.get('screen_id'):require(step['screen_id'] in screens,f'{f["id"]} invalid screen')
    docs={}
    for p in OUT.rglob('*.html'):
        doc=Document();doc.feed(p.read_text());docs[p.resolve()]=doc
        require(len(doc.ids)==len(set(doc.ids)),f'{p.relative_to(ROOT)} duplicate HTML IDs')
        require('h1' in doc.tags and 'main' in doc.tags,f'{p.name} missing semantic page structure')
        require(d['metadata']['source_sha'] in p.read_text(),f'{p.name} missing SHA')
        for op in doc.operations:require(op in ops,f'{p.name} unknown operation mapping {op}')
        for value in doc.resources:require(not urlsplit(value).scheme and not value.startswith('//'),f'{p.name} external dependency {value}')
        for label in doc.labels:require(label in doc.ids,f'{p.name} label target missing {label}')
    linkcount=0
    for p,doc in docs.items():
        for value in doc.links:
            u=urlsplit(value)
            if u.scheme or value.startswith('//'):continue
            target=(p.parent/unquote(u.path)).resolve() if u.path else p
            require(target.is_file(),f'{p.name} missing link {value}')
            if target in docs and u.fragment:require(unquote(u.fragment) in docs[target].ids,f'{p.name} missing anchor {value}')
            linkcount+=1
    js=(OUT/'assets/review.js').read_text()
    for forbidden in ('fetch(', 'XMLHttpRequest', 'WebSocket(', 'sendBeacon(', 'eval('):require(forbidden not in js,f'Forbidden runtime API {forbidden}')
    require(len(docs)>=30,'Must split screen and business docs')
    require('D9' in (OUT/'design-notes.html').read_text(),'Missing calculation deferral')
    if errors:
        print('\n'.join(errors));return 1
    print(json.dumps({'status':'PASS','screens':len(screens),'operations':len(ops),'workflows':len(d['workflows']),'html_pages':len(docs),'relative_links_checked':linkcount},ensure_ascii=False))
    return 0
if __name__=='__main__':sys.exit(validate())
