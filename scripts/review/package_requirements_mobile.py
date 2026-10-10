#!/usr/bin/env python3
"""Build one static HTML containing requirements and their linked review documents."""
import argparse
from pathlib import Path
import re
from html import escape
from urllib.parse import unquote, urlsplit
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'docs/requirements/standard-template'
REVIEW = ROOT / 'docs/review/pay-html-001'
OUTPUT = BASE / 'index-mobile.html'


def scoped_css(css, scope):
    css = re.sub(r'/\*[\s\S]*?\*/', '', css)
    out = []
    pos = 0
    while pos < len(css):
        start = css.find('{', pos)
        if start < 0:
            out.append(css[pos:])
            break
        pre = css[pos:start].strip()
        depth, end, quote = 1, start + 1, None
        while end < len(css) and depth:
            c = css[end]
            if quote:
                if c == quote and css[end - 1] != '\\': quote = None
            elif c in "\"'": quote = c
            elif c == '{': depth += 1
            elif c == '}': depth -= 1
            end += 1
        inner = css[start + 1:end - 1]
        if pre.startswith(('@media', '@supports', '@layer')):
            out.append(pre + '{' + scoped_css(inner, scope) + '}')
        elif pre.startswith('@'):
            out.append(pre + '{' + inner + '}')
        else:
            selectors = []
            for sel in pre.split(','):
                sel = sel.strip()
                replaced = re.sub(r':root|(?<![\w-])(?:body|html)(?![\w-])', scope, sel)
                selectors.append(replaced if replaced != sel else scope + ' ' + sel)
            out.append(','.join(selectors) + '{' + inner + '}')
        pos = end
    return ''.join(out)


def build():
    req = BASE / 'index.html'
    primary = [REVIEW/'navigation.html', REVIEW/'coverage.html', req,
               REVIEW/'workflows/index.html', REVIEW/'operations/index.html', REVIEW/'wireframes/index.html']
    paths = primary + [p for p in sorted(REVIEW.rglob('*.html')) + sorted((BASE/'sources').glob('*.html')) if p not in primary]
    paths = [p.resolve() for p in paths]
    ids = {p:'doc-' + str(p.relative_to(ROOT)).replace('/', '-').replace('.', '-') for p in paths}
    trees = {p:html.fromstring(p.read_text()) for p in paths}
    original_ids = {p:set(t.xpath('//@id')) for p,t in trees.items()}
    css_review = scoped_css((REVIEW/'assets/review.css').read_text(), '.review-doc')
    css_req = scoped_css(''.join(trees[req.resolve()].xpath('//head/style/text()')), '.requirements-doc')
    sections = []
    for p in paths:
        tree = trees[p]
        body = tree.find('body')
        title = tree.xpath('string(//title)')
        for img in body.xpath('.//img[@src]'):
            src=img.get('src'); u=urlsplit(src)
            if u.scheme in ('data',): continue
            target=(p.parent/unquote(u.path)).resolve()
            if not u.scheme and target.is_file():
                import base64, mimetypes
                mime=mimetypes.guess_type(str(target))[0] or 'application/octet-stream'
                img.set('src','data:'+mime+';base64,'+base64.b64encode(target.read_bytes()).decode())
            else:
                alt=html.Element('p');alt.text='参考画像：'+img.get('alt','原本を参照')
                img.getparent().replace(img,alt)
        for el in body.xpath('.//script|.//dialog|.//iframe|.//template'):
            el.getparent().remove(el)
        # Do not expose controls whose behavior needs JavaScript in a static preview.
        for el in body.xpath('.//button|.//input|.//select|.//textarea'):
            el.set('disabled','disabled')
        for el in body.xpath('.//*[@hidden]'):
            del el.attrib['hidden']
        for el in body.iter():
            if not isinstance(el.tag,str): continue
            for attr,val in list(el.attrib.items()):
                if attr.lower().startswith('on'):
                    del el.attrib[attr]
                    continue
                if attr == 'id':
                    el.set(attr,ids[p]+'--'+val)
                elif attr in ('for','aria-labelledby','aria-describedby','aria-controls'):
                    el.set(attr,' '.join(ids[p]+'--'+v for v in val.split()))
                elif 'url(#' in val:
                    el.set(attr,re.sub(r'url\(#([^)]*)\)',lambda m:'url(#'+ids[p]+'--'+m[1]+')',val))
                elif attr in ('href','{http://www.w3.org/1999/xlink}href'):
                    u=urlsplit(val)
                    if u.scheme or u.netloc: continue
                    target=(p.parent/unquote(u.path)).resolve() if u.path else p
                    if target == OUTPUT.resolve():
                        el.set(attr,'#mobile-top')
                        continue
                    if target in ids:
                        frag=unquote(u.fragment)
                        el.set(attr,'#'+ids[target]+('--'+frag if frag in original_ids[target] else ''))
                        el.attrib.pop('target',None)
                        el.attrib.pop('data-preview',None)
                    else:
                        # Nonbundled material remains an explicitly external repository reference.
                        try: rel=target.relative_to(ROOT)
                        except ValueError: continue
                        el.set(attr,'https://github.com/hirokazu601218/PowerAppsCanvasAppUI/blob/252abe4aa5d3b1d99a584a30c97d9b48153c91f5/'+str(rel)+(('#'+u.fragment) if u.fragment else ''))
        cls='review-doc' if p.is_relative_to(REVIEW) else 'requirements-doc'
        # Header is repeated only at document boundaries; all content remains readable without links.
        rendered=''.join(etree.tostring(c,encoding='unicode',method='html') for c in body)
        sections.append(f'<section id="{ids[p]}" class="mobile-document {cls}"><div class="mobile-section-bar"><strong>{escape(title)}</strong><a href="#mobile-top">資料の先頭へ戻る</a></div>{rendered}</section>')
    links=[('画面遷移図',primary[0]),('画面一覧',primary[1]),('要件定義書',primary[2]),('業務別フロー',primary[3]),('操作一覧',primary[4]),('画面イメージ',primary[5])]
    nav=''.join(f'<a href="#{ids[p.resolve()]}">{escape(t)}</a>' for t,p in links)
    css_mobile='''body{margin:0;background:#f4f7fb;color:#172c45;font:16px/1.8 system-ui,-apple-system,sans-serif}.mobile-top{padding:20px;background:#102d4e;color:white}.mobile-top h1{font-size:25px;line-height:1.5}.mobile-top p{margin:12px 0}.mobile-nav{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.mobile-nav a{padding:13px;background:white;color:#0759a8;border-radius:6px}.mobile-document{margin:20px 0;border-top:3px solid #b9cde0;background:white;overflow-wrap:anywhere;min-width:0}.mobile-section-bar{padding:14px;background:#e7eef7;display:flex;flex-wrap:wrap;gap:10px;justify-content:space-between}.mobile-section-bar a{color:#0759a8}.mobile-document .toolbar,.mobile-document .diagram-tools,.mobile-document .doc-nav,.mobile-document .skip,.mobile-document .filter-bar,.mobile-document .wf-modal,.mobile-document .wf-demo-log{display:none!important}.mobile-document .sidebar{position:static;max-height:none}.mobile-document .layout{display:block}.mobile-document [hidden]{display:block!important}.mobile-document .workflow-scroll{max-height:none!important}.mobile-document svg{height:auto;max-width:100%}.mobile-document .table-scroll,.mobile-document .table-wrap{overflow:auto}.mobile-document .doc-header{padding:16px;flex-wrap:wrap}.mobile-document .doc-header span{margin-left:0;display:block}.mobile-document .wf-shell{overflow:auto;max-width:100%}.mobile-document .wf-panel{display:block!important}.mobile-document main{padding:16px;min-width:0}.mobile-document details{margin:12px 0}.mobile-document .tab-panel,.mobile-document [data-panel]{display:block!important}.mobile-document button{cursor:default}a{overflow-wrap:anywhere}'''
    result='<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>非常勤給与 要件と画面資料 iPhone閲覧版</title><style>'+css_review+css_req+css_mobile+'</style></head><body><header id="mobile-top" class="mobile-top"><h1>非常勤給与 要件と画面資料<br>iPhone閲覧版</h1><p>関連資料をすべてこのファイルに収めました。画面遷移図はこの案内のすぐ下にあります。</p><nav class="mobile-nav">'+nav+'</nav><p>リンクを押すと同じファイル内の資料へ移動します。プレビューでリンクが反応しない場合も、そのまま下へスクロールして読めます。</p><p>この版は閲覧用です。入力・保存などの模擬操作はPC版で確認してください。要件未設定・未承認の区分は元資料を維持しています。</p></header>'+''.join(sections)+'</body></html>'
    # Every bundled link must resolve; ensure no scripts, frames or local resources are left.
    doc=html.fromstring(result)
    allids=doc.xpath('//@id')
    assert len(allids)==len(set(allids)), 'duplicate IDs'
    assert not doc.xpath('//script|//iframe|//link[@href]')
    assert all(u.startswith('data:') for u in doc.xpath('//@src')), 'external local resources'
    known=set(allids)
    broken=[u for u in doc.xpath('//@href') if u.startswith('#') and unquote(u[1:]) not in known]
    assert not broken, broken[:10]
    return result,len(paths)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    text,count=build()
    if args.check:
        assert OUTPUT.read_text()==text,'mobile HTML regeneration mismatch'
    else: OUTPUT.write_text(text)
    print(f'{count} documents in one HTML; {len(text.encode())} bytes; '+('verified' if args.check else 'generated'))

if __name__=='__main__':main()
