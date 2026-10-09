#!/usr/bin/env python3
"""PAY-HTML-001: deterministic, stdlib-only HTML derivative generator.
The Markdown requirements remain canonical. Generated HTML is deliberately readable.
"""
from pathlib import Path
import argparse
import html
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/review/pay-html-001'
MODEL = OUT / 'data/model.json'
E = lambda value: html.escape(str(value), quote=True)


def load_model():
    return json.loads(MODEL.read_text(encoding='utf-8'))


def relative(target, current):
    return os.path.relpath(OUT / target, (OUT / current).parent).replace(os.sep, '/')


def link(target, text, current, attrs=''):
    return f'<a href="{E(relative(target, current))}" {attrs}>{E(text)}</a>'


def tag(value):
    kinds = {'現行実装':'current', '確定改修要件':'accepted', '提案':'proposed', '未決':'open'}
    return f'<span class="badge {kinds.get(value, "proposed")}">{E(value)}</span>'


def table(headers, rows, caption='', attrs=''):
    return ('<div class="table-scroll" tabindex="0" role="region" aria-label="'+E(caption or '表')+'">\n'
            '<table '+attrs+'>' + ('<caption>'+E(caption)+'</caption>' if caption else '') + '\n<thead><tr>'
            + ''.join('<th scope="col">'+E(x)+'</th>' for x in headers) + '</tr></thead>\n<tbody>\n'
            + '\n'.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in row)+'</tr>' for row in rows)
            + '\n</tbody></table></div>\n')


def sources_html(model, ids, current):
    items=[]
    byid={s['id']:s for s in model['sources']}
    for sid in ids:
        s=byid.get(sid)
        if not s:
            items.append(E(sid)); continue
        target=os.path.relpath(ROOT/s['path'], (OUT/current).parent).replace(os.sep,'/')
        items.append(f'<a href="{E(target)}">{E(s["title"])} {E(s.get("section", ""))}</a>')
    return ' / '.join(items)


def reqs(ids):
    return ' '.join(f'<span class="requirement" data-requirement-id="{E(x)}">{E(x)}</span>' for x in ids)


def page(model, current, title, body, active='', screen=None):
    meta=model['metadata']
    nav=[('index.html','入口'),('navigation.html','① 画面遷移'),('workflows/index.html','② 業務フロー'),('operations/index.html','③ 操作定義'),('wireframes/index.html','④ ワイヤー'),('coverage.html','対応表'),('design-notes.html','設計注記')]
    navhtml='\n'.join(link(p,t,current,'aria-current="page"' if active==p else '') for p,t in nav)
    return f'''<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="非常勤給与アプリ PAY-HTML-001 非正本のレビュー資料">
  <title>{E(title)} | 非常勤給与レビュー</title>
  <link rel="stylesheet" href="{E(relative('assets/review.css',current))}">
  <script src="{E(relative('assets/review.js',current))}" defer></script>
</head>
<body{f' data-screen-id="{E(screen)}"' if screen else ''}>
<a class="skip" href="#main">本文へ移動</a>
<header class="doc-header"><div><strong>非常勤給与アプリ</strong><span>画面・業務レビュー</span></div><p>PAY-HTML-001</p></header>
<nav class="doc-nav" aria-label="資料ナビゲーション">{navhtml}</nav>
<main id="main">
<div class="document-meta"><span>{E(meta['version'])} / {E(meta['updated'])}</span><strong>提案・レビュー用（未承認）</strong><span>元 main：<code>{E(meta['source_sha'])}</code></span></div>
<h1>{E(title)}</h1>
<p class="scope-note">Markdownが正本です。本資料は現行の観測・確定改修要件・提案・未決を分けた確認用HTMLです。画面例はすべて架空です。実アプリ・給与計算・保存・外部送信は実行しません。</p>
{body}
</main>
<footer>PAY-HTML-001 · 静的HTML本文はJavaScript・ネットワークなしで読めます。モックの操作補助のみJavaScriptを使用します。<br>HTML承認と、Power Appsでの実装・権限・性能・業務受入は別の判定です。</footer>
</body>
</html>
'''


def svg_lanes(nodes, edges, title):
    """Each edge owns a lane: no crossing connectors or label/box overlap.
    SVG and equivalent table are rendered from exactly the same nodes/edges.
    """
    nmap={n['id']:n for n in nodes}
    rowh=126
    height=50+len(edges)*rowh
    pieces=[f'<svg class="lane-diagram" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 {height}" role="img" aria-label="{E(title)}">',
            '<title>'+E(title)+'</title>',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#0f6cbd"/></marker></defs>']
    def chunks(text,width=18):
        return [text[i:i+width] for i in range(0,len(text),width)] or ['']
    for i,edge in enumerate(edges):
        y=36+i*rowh
        for x,key in ((12,edge['from']),(678,edge['to'])):
            n=nmap[key]
            pieces.append(f'<rect x="{x}" y="{y}" width="310" height="94" rx="6" class="node {E(n.get("kind", "action"))}"/>')
            pieces.append(f'<text x="{x+14}" y="{y+22}" class="node-id">{E(key)}</text>')
            for j,line in enumerate(chunks(n['label'])):
                pieces.append(f'<text x="{x+14}" y="{y+47+j*22}" class="node-label">{E(line)}</text>')
            if n.get('status'):pieces.append(f'<text x="{x+14}" y="{y+85}" class="node-id">{E(n["status"])}</text>')
        pieces.append(f'<path d="M 328 {y+64} H 664" stroke="#0f6cbd" stroke-width="2" marker-end="url(#arrow)"/>')
        for j,line in enumerate(chunks(edge.get('label',''),21)):
            pieces.append(f'<text x="496" y="{y+20+j*20}" text-anchor="middle" class="edge-label">{E(line)}</text>')
        if edge.get('status'):pieces.append(f'<text x="496" y="{y+88}" text-anchor="middle" class="node-id">{E(edge["status"])}</text>')
    pieces.append('</svg>')
    return '<div class="diagram-scroll" tabindex="0" role="region" aria-label="'+E(title)+'。狭い画面では横スクロール">'+''.join(pieces)+'</div>'


def overview_map(model):
    """Compact hub overview using the same canonical screen/transition objects.
    Dense exception routes remain in the generated detailed lanes and table below.
    """
    screens={s['id']:s for s in model['screens']}
    routes={(o['screen_id'],o['destination_screen_id']):o for o in model['operations'] if o['screen_id']!=o['destination_screen_id']}
    positions={'SCR-001':(40,200),'SCR-002':(380,60),'SCR-003':(380,200),'SCR-004':(380,340),'SCR-006':(380,480),'CUR-IMPORT-POC':(380,620),'SCR-005':(850,60),'EXT-COMMUTE':(850,200),'FUT-IMPORT':(40,850),'FUT-JLINK':(425,850),'SCR-007':(850,850),'EXT-JINKYU':(850,1040)}
    parts=['<svg class="overview-diagram" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1160 1190" role="img" aria-label="ホームを起点とした全体配置の概観"><title>全体配置の概観。詳しい方向別操作と例外は下段の同一データ表を参照</title><defs><marker id="overview-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#0f6cbd"/></marker></defs>',
      '<rect x="20" y="35" width="1110" height="690" rx="10" fill="#f7faff" stroke="#cbd5e1"/>',
      '<text x="40" y="22" class="map-heading">現行の入口・画面と別タブ境界</text>',
      '<text x="40" y="120" class="map-note">Microsoftの認証はアプリ外</text>',
      '<rect x="20" y="810" width="1110" height="340" rx="10" fill="#f6f5ff" stroke="#cbd5e1" stroke-dasharray="7 4"/>',
      '<text x="40" y="750" class="map-heading">確定した改修先と配置案（未実装・正式ID未定を含む）</text>']
    def edge(start,end,path,label=None,lx=0,ly=0,reverse=False):
        o=routes.get((start,end))
        if not o:return
        dash=' stroke-dasharray="7 4"' if o['status']=='提案' else ''
        back=' marker-start="url(#overview-arrow)"' if reverse and (end,start) in routes else ''
        parts.append(f'<path d="{path}" fill="none" stroke="#0f6cbd" stroke-width="2" marker-end="url(#overview-arrow)"{back}{dash} data-operation-id="{E(o["id"])}"/>')
        if label:parts.append(f'<text x="{lx}" y="{ly}" class="map-note" text-anchor="middle">{E(label)}</text>')
    # Shared trunk is a visual grouping; each leaf corresponds to a canonical edge.
    parts.append('<path d="M 290 245 H 330 M 330 105 V 665" fill="none" stroke="#0f6cbd" stroke-width="2"/>')
    for sid in ['SCR-002','SCR-003','SCR-004','SCR-006','CUR-IMPORT-POC']:
        y=positions[sid][1]+45
        edge('SCR-001',sid,f'M 330 {y} H 374')
    edge('SCR-002','SCR-005','M 636 105 H 844','支給明細／戻る',740,86,True)
    edge('SCR-002','EXT-COMMUTE','M 636 135 H 720 V 245 H 844','認定簿表示（別タブ）',786,223)
    parts.append('<text x="55" y="342" class="map-note">各画面名の操作で開く</text><text x="55" y="368" class="map-note">ホーム操作で戻る</text>')
    # Target home additions use an isolated lower bus; no current direct trial link.
    parts.append('<path d="M 40 270 H 8 V 770 H 975" fill="none" stroke="#597bb7" stroke-width="2"/>')
    for sid in ['FUT-IMPORT','FUT-JLINK','SCR-007']:
        x=positions[sid][0]+125
        edge('SCR-001',sid,f'M {x} 770 V 844')
    edge('FUT-JLINK','EXT-JINKYU','M 550 942 V 1085 H 844','Excel出力 → 外部処理 → 給与簿CSV',656,1062,True)
    for sid,(x,y) in positions.items():
        if sid not in screens:continue
        screen=screens[sid];external=sid.startswith('EXT-')
        fill='#fff4df' if external else '#eaf3fc' if screen['status']=='現行実装' else '#efedfc'
        dash=' stroke-dasharray="6 3"' if external else ''
        parts.append(f'<a href="wireframes/{sid.lower()}.html"><rect x="{x}" y="{y}" width="250" height="92" rx="6" fill="{fill}" stroke="#6f90b0"{dash}/><text x="{x+12}" y="{y+20}" class="node-id">{E(sid)}</text>')
        title=screen['name']; chunks=[title[n:n+14] for n in range(0,len(title),14)]
        for i,line in enumerate(chunks[:2]):parts.append(f'<text x="{x+12}" y="{y+44+i*21}" class="map-label">{E(line)}</text>')
        parts.append(f'<text x="{x+12}" y="{y+83}" class="node-id">{E(screen["status"])}{ " / アプリ外" if external else ""}</text></a>')
    parts.append('</svg>')
    return '<div class="diagram-scroll" tabindex="0" role="region" aria-label="全体関係図。狭幅は横スクロール">'+''.join(parts)+'</div>'

def op_target(op):
    return 'operations/'+op['screen_id'].lower()+'.html#'+op['id']


def generate(model):
    screens=model['screens']; operations=model['operations']; flows=model['workflows']
    sm={x['id']:x for x in screens}; om={x['id']:x for x in operations}
    results={}
    body='''<p class="lead">画面から業務へ。業務から一つの操作へ。確認したい粒度を選んで進めます。</p>
<div class="review-cards">'''
    for p,t,d in [('navigation.html','01 画面遷移','ホーム・戻り・役割別入口・外部との境界'),('workflows/index.html','02 業務フロー','業務単位の手順、分岐、失敗・再実行'),('operations/index.html','03 操作定義','条件・対象範囲・データ・例外を一か所で確認'),('wireframes/index.html','04 ワイヤーフレーム','架空の画面でタブ、確認、戻りをたどる')]:
        body+=f'<article><h2>{link(p,t,"index.html")}</h2><p>{E(d)}</p></article>'
    body+='</div><h2>読み方と判断の境界</h2><ul><li>画面の既存性と各操作の実装状態は分けて読みます。確定要件は実装済みを意味しません。</li><li>最新の2026-10-07要件と2026-10-08 I1～I12を優先します。D9以降の式は保留です。</li><li>支給回の給与班確定は最新の全体照合が差分ゼロの場合に限り、確認ダイアログは出しません。Excel出力前の確認とは別です。</li><li>未決を補うレイアウト・確認文・模擬操作は提案です。新しい制度判断や計算式は採用しません。</li></ul>'
    body+='<div class="legend">'+''.join(tag(x) for x in ['現行実装','確定改修要件','提案','未決'])+'</div>'
    body+=f'<p>{len(screens)}画面・外部境界 / {len(flows)}業務フロー / {len(operations)}操作。{link("coverage.html","網羅性対応表","index.html")}で相互参照を確認できます。</p>'
    body+='<h2>出典</h2>'+table(['出典ID','Markdown正本・参照節'],[[E(s['id']),sources_html(model,[s['id']],'index.html')] for s in model['sources']],'参照資料')
    results['index.html']=page(model,'index.html','非常勤給与アプリ レビュー資料',body,'index.html')
    # navigation diagrams: each cross-screen operation is one explicit directed edge
    navops=[o for o in operations if o.get('destination_screen_id') in sm and o['destination_screen_id']!=o['screen_id']]
    nodes=[dict(id=s['id'],label=s['name'],status=s['status'],kind='external' if s['id'].startswith('EXT-') else 'action') for s in screens]
    edges=[{'from':o['screen_id'],'to':o['destination_screen_id'],'label':o['title'],'status':o['status']} for o in navops]
    cur='navigation.html'
    body='<p>矢印1本は方向と操作を持つ1経路です。同じ画面を複数のレーンに再掲し、交差・重なりを避けています。画面の縦の並びは連続遷移ではありません。</p><p class="callout">現行ホームは職員マスタ検索・勤務時間報告・期末勤勉支給率登録・メンテナンスの4入口。SCR-005へはSCR-002から進みます。将来の追加入口は確定改修要件として区別します。</p>'
    body+='<h2>全体関係の概観</h2>'+overview_map(model)+'<p>塗りと文字で区分を示し、外部の枠線を破線にしています。画面を選ぶとワイヤーへ進めます。ホーム追加のうちSCR-007への入口は提案です。人給連携と勤務条件・勤怠の訂正往復、追給出力の受渡しは次の詳細経路で確認します。</p><h2>方向別の詳細経路</h2>'+svg_lanes(nodes,edges,'全体画面遷移と外部境界')
    body+=table(['遷移ID／操作','遷移元 → 先','役割・条件','区分','詳細'],[[E(o['transition_id'])+'<br>'+E(o['title']),E(o['screen_id'])+' → '+E(o['destination_screen_id']),E('・'.join(o['roles']))+'<br>'+E(o['enabled']),tag(o['status']),link(op_target(o),'操作定義',cur)+' / '+link('wireframes/'+o['screen_id'].lower()+'.html','画面',cur)] for o in navops],'SVGと同一データの遷移表')
    body+='<h2>画面と入口</h2>'+table(['ID・画面','区分・境界','役割','関連資料'],[[f'<span id="{E(s["id"])}" data-screen-id="{E(s["id"])}">{E(s["id"])} {E(s["name"])}</span>',tag(s['status'])+'<br>'+E(s['summary']),E('・'.join(s['roles'])),link('operations/'+s['id'].lower()+'.html','操作',cur)+' / '+link('wireframes/'+s['id'].lower()+'.html','ワイヤー',cur)+'<br>'+sources_html(model,s['source_ids'],cur)] for s in screens],'画面一覧・正式ID未定は仮識別子')
    body+='<h2>未決事項</h2><p>人給連携・データ一括取込の正式画面ID、遡及差額の最終配置、認証と実効ロールの取得方式は未決。外部Microsoft認証はCanvas内部画面ではありません。別タブ認定簿はアプリ内戻りと区別し、元タブを維持します。</p>'
    results[cur]=page(model,cur,'① 全体画面遷移図',body,cur)
    cur='workflows/index.html'
    body='<p>業務を独立した図に分割しています。各図の番号から操作定義・画面例へ進めます。実線は業務上の流れを示し、実装済みの証明ではありません。</p>'+table(['業務ID・名称','担当／開始→終了','画面','区分'],[[link('workflows/'+f['id'].lower()+'.html',f['id']+' '+f['name'],cur),E(f['actor'])+'<br>'+E(f['start'])+' → '+E(f['end']),E(' / '.join(f['screen_ids'])),tag(f['status'])] for f in flows],'業務フロー一覧')
    results[cur]=page(model,cur,'② 業務フロー一覧',body,'workflows/index.html')
    for flow in flows:
        cur='workflows/'+flow['id'].lower()+'.html'
        body=f'<p>{tag(flow["status"])} 担当：{E(flow["actor"])}</p><dl><dt>開始</dt><dd>{E(flow["start"])}</dd><dt>終了</dt><dd>{E(flow["end"])}</dd></dl>'+reqs(flow['requirements'])
        body+=svg_lanes(flow['steps'],flow['edges'],flow['name'])
        stepmap={x['id']:x for x in flow['steps']}
        body+=table(['起点','条件／操作','到達点'],[[E(x['from'])+' '+E(stepmap[x['from']]['label']),E(x['label']),E(x['to'])+' '+E(stepmap[x['to']]['label'])] for x in flow['edges']],'SVGと同一データの分岐表')
        rows=[]
        for step in flow['steps']:
            o=om.get(step.get('operation_id'))
            refs=(link(op_target(o),o['id'],cur) if o else '業務境界・状態（操作なし）')
            if step.get('screen_id') in sm: refs+=' / '+link('wireframes/'+step['screen_id'].lower()+'.html','画面を開く',cur)
            rows.append([f'<span id="{E(step["id"])}">{E(step["id"])}</span> '+E(step['label']),E(step.get('screen_id',''))+'<br>'+E(step['kind']),E(step['detail']),refs])
        body+=table(['工程','画面・種類','動作・条件','操作定義／画面'],rows,'業務工程の定義')
        body+='<h2>例外・未保存・引継ぎの確認</h2><p>各操作定義の失敗／取消／未保存／保持・解除欄を確認してください。処理中・報告済み・支払済みの編集制限、並行更新、再試行の物理方式は確定業務と未決方式を分けています。モックの再試行成功は実データの復旧保証ではありません。</p>'
        body+='<p>出典：'+sources_html(model,flow['source_ids'],cur)+'</p>'
        results[cur]=page(model,cur,'② '+flow['name'],body,'workflows/index.html')
    cur='operations/index.html'
    body='''<p>短い索引から画面別の詳細定義へ進みます。業務ルール、例外、保持情報の詳細はここへ集約しています。フィルターは閲覧補助であり、権限・確定判定の範囲を変更しません。</p><div class="filters" data-filter-panel>'''
    for field,label,vals in [('screen','画面',[s['id'] for s in screens]),('business','業務',sorted({o['business_id'] for o in operations})),('role','役割',sorted({r for o in operations for r in o['roles']})),('status','区分',['現行実装','確定改修要件','提案','未決'])]:
        body+=f'<label>{label}<select data-filter="{field}"><option value="">すべて</option>'+''.join(f'<option>{E(v)}</option>' for v in vals)+'</select></label>'
    body+='<label>操作名・ID<input data-filter="text" type="search" placeholder="例：照合、保存"></label><button type="button" data-reset-filters>解除</button></div><p data-result-count role="status">全操作を表示</p>'
    body+='<div class="table-scroll" tabindex="0" role="region" aria-label="操作索引"><table><caption>全操作の短い索引</caption><thead><tr><th>操作ID・操作</th><th>画面／業務</th><th>役割</th><th>区分</th><th>画面例</th></tr></thead><tbody>\n'
    for o in operations:
        body+=f'<tr data-operation-row data-screen="{E(o["screen_id"])}" data-business="{E(o["business_id"])}" data-role="{E("|".join(o["roles"]))}" data-status="{E(o["status"])}"><td>{link(op_target(o),o["id"]+" "+o["title"],cur)}</td><td>{E(o["screen_id"])} / {E(o["business_id"])}</td><td>{E("・".join(o["roles"]))}</td><td>{tag(o["status"])}</td><td>{link("wireframes/"+o["screen_id"].lower()+".html","開く",cur)}</td></tr>\n'
    body+='</tbody></table></div>'
    results[cur]=page(model,cur,'③ 操作定義 索引',body,'operations/index.html')
    fields=[('origin_tab','遷移元タブ'),('origin_mode','遷移元モード'),('destination_tab','遷移先タブ'),('destination_mode','遷移先モード'),('control','操作部品'),('method','操作方法'),('row_scope','対象行・データ範囲'),('visible','表示条件'),('enabled','活性条件'),('preconditions','実行前提'),('validation','入力検証・エラー'),('process','処理'),('retained','保持する情報'),('reset','解除する情報'),('success','成功'),('failure','失敗・再実行'),('cancel','取消'),('unsaved','未保存')]
    for s in screens:
        cur='operations/'+s['id'].lower()+'.html'; ops=[o for o in operations if o['screen_id']==s['id']]
        body='<p>'+tag(s['status'])+' '+E(s['summary'])+'</p><p>'+link('wireframes/'+s['id'].lower()+'.html','この画面を操作する',cur)+'</p><nav aria-label="この画面の操作">'+''.join(f'<a href="#{E(o["id"])}">{E(o["title"])}</a> ' for o in ops)+'</nav>'
        for o in ops:
            body+=f'<section class="operation" id="{E(o["id"])}" data-operation-id="{E(o["id"])}" data-screen-id="{E(s["id"])}"><h2>{E(o["id"])} {E(o["title"])}</h2><p>{tag(o["status"])} <span id="{E(o["transition_id"])}">遷移：{E(o["transition_id"])}</span> / 業務：{E(o["business_id"])}</p>'+reqs(o['requirements'])
            rows=[['出典',sources_html(model,o['source_ids'],cur)],['画面',E(o['screen_id'])+' → '+E(o['destination_screen_id'])],['利用可能な役割',E('・'.join(o['roles']))]]+[[title,E(o.get(key,''))] for key,title in fields]+[['参照エンティティ',E('・'.join(o['reads']))],['更新エンティティ',E('・'.join(o['writes']))]]
            body+=table(['定義項目','内容'],rows,o['title']+'の詳細契約')+'<h3>受入観点</h3><ul>'+''.join('<li>'+E(a)+'</li>' for a in o['acceptance'])+'</ul><h3>未決・注記</h3><ul>'+''.join('<li>'+E(n)+'</li>' for n in o['notes'])+'</ul></section>'
        results[cur]=page(model,cur,'③ '+s['id']+' '+s['name']+'の操作定義',body,'operations/index.html',s['id'])
    cur='coverage.html'
    rows=[]
    for s in screens:
        related=[f for f in flows if s['id'] in f['screen_ids']]
        rows.append([E(s['id'])+' '+E(s['name']),link('navigation.html#'+s['id'],'① 画面',cur),'<br>'.join(link('workflows/'+f['id'].lower()+'.html',f['id'],cur) for f in related) or '業務図なし（境界のみ）',link('operations/'+s['id'].lower()+'.html','③ 操作',cur),link('wireframes/'+s['id'].lower()+'.html','④ ワイヤー',cur),reqs(s['requirements'])])
    body=table(['画面・境界','①','② 業務','③','④','要件'],rows,'全画面から4資料への対応')
    body+=table(['業務','① 画面一覧','②','③ 全工程の操作','④'],[[E(f['id'])+' '+E(f['name']),'<br>'.join(link('navigation.html#'+sid,sid,cur) for sid in f['screen_ids'] if sid in sm),link('workflows/'+f['id'].lower()+'.html','フロー',cur),'<br>'.join(link(op_target(om[x['operation_id']]),x['operation_id'],cur) for x in f['steps'] if x.get('operation_id') in om),'<br>'.join(link('wireframes/'+sid.lower()+'.html',sid,cur) for sid in f['screen_ids'] if sid in sm)] for f in flows],'全業務から4資料への対応')
    results[cur]=page(model,cur,'網羅性・相互参照対応表',body,'coverage.html')
    # wireframe rendering is separated for maintainability
    from payroll_wireframes import wireframe_pages
    results.update(wireframe_pages(model,page,table,link,tag,reqs,sources_html))
    return results


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
    data=generate(load_model()); failures=[]
    for filename,content in data.items():
        path=OUT/filename
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8')!=content: failures.append(filename)
        else:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content,encoding='utf-8')
    if failures:
        print('Generated files out of date: '+', '.join(failures));return 1
    print(f'{len(data)} HTML pages '+('verified' if args.check else 'generated'))
    return 0

if __name__=='__main__': sys.exit(main())
