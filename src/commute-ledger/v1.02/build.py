"""Build an independent HTML candidate from a read-back of the working resource.
Never writes to the baseline or deploys. PDF is supplied separately, hash pinned.
"""
import argparse, hashlib, json, re
from pathlib import Path
import fitz
ROOT = Path(__file__).resolve().parent

def digest(b): return hashlib.sha256(b).hexdigest()

def fields():
    out=[]
    def put(key,page,x,y,w,h,size=7,align='left'):
        out.append(dict(key=key,page=page,x=x,y=y,w=w,h=h,size=size,align=align))
    put('name',0,47,83,116,13)
    put('staff',0,218,83,62,13)
    put('org',0,311,83,180,13)
    for k,y in [('event',83),('submitted',100),('received',117)]:
        put(k,0,600,y,198,13,8,'center')
    for i in range(1,5):
        y=190+30.24*(i-1); p=f'r{i}_'
        put(p+'operator',0,52,y,54,27)
        put(p+'from',0,110,y,54,13)
        put(p+'to',0,110,y+13.5,54,13)
        put(p+'tickettype',0,168,y,39,27)
        put(p+'ticketbasis',0,212,y,68,27,7,'right')
        put(p+'distancekm',0,284,y,39,27,7,'right')
        put(p+'ticketamount',0,328,y,39,27,7,'right')
        put(p+'passamount',0,372,y,61,27,7,'right')
        put(p+'amount',0,438,y,39,27,7,'right')
        put(p+'recognitionstart',0,482,y,84,13,7,'center')
        put(p+'passmonths',0,482,y+13.5,84,13,7,'center')
        put(p+'paymonth',0,572,y,81,27,7,'center')
        put(p+'remarks',0,659,y,156,27)
    put('total',0,438,433,39,17,7,'right')
    xs=[207.1,236.6,266.2,293.2,326.2,353.5,383.0,414.0,443.5,473.0,502.6,532.1,561.6]
    for j,m in enumerate(['04','05','06','07','08','09','10','11','12','01','02','03']):
        put('month'+m,1,xs[j]+1,402,xs[j+1]-xs[j]-3,14,6.5,'right')
    return out

def layout(pdf):
    doc=fitz.open(pdf)
    assert len(doc)==2
    shapes=[]
    for i,page in enumerate(doc):
        assert abs(page.rect.width-841.89)<.02 and abs(page.rect.height-595.276)<.02
        svg=page.get_svg_image(text_as_path=True)
        # Inline paths render synchronously; namespace glyph IDs across pages.
        svg=re.sub(r'id="([^"]+)"',lambda m:f'id="p{i}_{m[1]}"',svg)
        svg=re.sub(r'href="#([^"]+)"',lambda m:f'href="#p{i}_{m[1]}"',svg)
        svg=re.sub(r'url\(#([^)]+)\)',lambda m:f'url(#p{i}_{m[1]})',svg)
        svg=svg.replace('<svg ', '<svg class="official-form" aria-hidden="true" ',1)
        cells=[]
        for f in fields():
            if f['page']!=i:continue
            style=f"left:{f['x']}pt;top:{f['y']}pt;width:{f['w']}pt;height:{f['h']}pt;font-size:{f['size']}pt;text-align:{f['align']}"
            cells.append(f'<span class="value official-value" data-field="{f["key"]}" style="{style}"></span>')
        shapes.append(f'<section class="page official-page" aria-label="通勤手当認定簿 {i+1}ページ目">{svg}'+''.join(cells)+'</section>')
    return '<main id="report" hidden>'+''.join(shapes)+'</main>'

CSS='''
/* Official form uses PDF points; page geometry includes the PDF's own margins. */
@page { size:841.89pt 595.276pt; margin:0 }
.page.official-page { position:relative;width:841.89pt;height:595.276pt;box-sizing:border-box;padding:0;margin:0;border:0;break-inside:avoid;page-break-inside:avoid }
.official-page+.official-page { break-before:page;page-break-before:always }
.official-form { position:absolute;left:0;top:0;width:100%;height:100%;display:block }
.official-value { position:absolute;display:block;box-sizing:border-box;padding:0;margin:0;min-height:0;max-height:none;line-height:1.15;font-family:"Noto Sans CJK JP","Yu Gothic",sans-serif;font-weight:400;white-space:pre-wrap;overflow-wrap:anywhere;word-break:normal }
.official-value:not(:empty) { background:white }
@media screen {#report{width:841.89pt;margin:8mm auto}.page.official-page{margin-bottom:8mm}}
@media print {html,body {margin:0!important;padding:0!important} .toolbar{display:none!important} .official-form{print-color-adjust:exact;-webkit-print-color-adjust:exact}}
'''

def build(baseline,pdf):
    source=baseline.read_text(encoding='utf-8')
    old_fields=re.findall(r'data-field="([^"]+)"',source)
    new_fields=[x['key'] for x in fields()]
    if len(old_fields)!=len(set(old_fields)) or sorted(old_fields)!=sorted(new_fields):
        raise ValueError('Baseline field contract differs. Review live mapping before building.')
    main=layout(pdf)
    result,count=re.subn(r'<main\b[^>]*\bid="report"[^>]*>.*?</main>',lambda _:main,source,flags=re.S)
    if count!=1:raise ValueError('Expected exactly one report main.')
    result=result.replace('<strong>通勤手当認定簿 HTML版 1.01</strong>','<strong>通勤手当認定簿 公式様式 1.02（受入テスト用）</strong>',1)
    result=result.replace('</head>','<style>'+CSS+'</style></head>',1)
    if re.findall(r'<script\b[^>]*>.*?</script>',source,re.S)!=re.findall(r'<script\b[^>]*>.*?</script>',result,re.S):
        raise ValueError('Runtime script changed')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--pdf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--expected-baseline-sha256',required=True);p.add_argument('--reference-only',action='store_true');a=p.parse_args()
    meta=json.loads((ROOT/'source.json').read_text())
    if digest(a.pdf.read_bytes())!=meta['pdf_sha256']:raise SystemExit('Official PDF hash mismatch')
    if digest(a.baseline.read_bytes())!=a.expected_baseline_sha256:raise SystemExit('Baseline hash mismatch')
    if a.output.resolve()==a.baseline.resolve():raise SystemExit('Cannot overwrite working baseline')
    html=build(a.baseline,a.pdf);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(html,encoding='utf-8')
    a.output.with_suffix('.build.json').write_text(json.dumps({'reference_only':a.reference_only,'baseline_sha256':digest(a.baseline.read_bytes()),'output_sha256':digest(html.encode()),'pdf_sha256':meta['pdf_sha256'],'runtime_scripts_unchanged':True,'field_count':len(fields()),'deployed':False},indent=2)+'\n')
