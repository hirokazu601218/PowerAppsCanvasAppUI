/** DOT-002 / PAY-REQ-HTML-REWORK-001. Static derivative only; canonical Markdown is read-only. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {
  pathToFileURL
}
from 'node:url';
const modules=process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
const {
  marked
}
=await import(modules?pathToFileURL(path.join(modules,
'marked/lib/marked.esm.js')).href:'marked');
const root=process.cwd(),
dir='docs/requirements/standard-template',
review='docs/review/pay-html-001';
const baselineData=JSON.parse(fs.readFileSync(`${dir}/requirements-data.json`, 'utf8'));
const sectionSupplements=JSON.parse(fs.readFileSync(`${dir}/section-supplements.json`, 'utf8'));
const publication=baselineData.metadata.publication;
if(publication){
  const raw=fs.readFileSync(publication.record_path);
  const captured=JSON.parse(raw);
  if(crypto.createHash('sha256').update(raw).digest('hex')!==publication.record_sha256
     ||captured.publication.lastPublishTime!==publication.lastPublishTime
     ||captured.publication.download_sha256!==publication.download_sha256
     ||captured.status!==publication.run_status)throw Error('Publication record changed: re-review capture status and digest');
}

const templateSupplements=new Map((sectionSupplements.template_sections||[]).map(item=>[item.id,item]));
// Supplemental summaries are tied to quoted canonical lines. Fail visibly if a
// later Work rebase changes those lines; do not silently reuse an old approval.
for (const supplement of [
  ...sectionSupplements.sections,
  ...(sectionSupplements.template_sections || []),
]) {
  for (const reference of supplement.source_refs) {
    const sourceLines = fs.readFileSync(reference.path, 'utf8').split('\n');
    const actualQuote = sourceLines.slice(reference.line - 1, reference.end_line).join('\n');
    if (actualQuote !== reference.quote || crypto.createHash('sha256').update(fs.readFileSync(reference.path)).digest('hex') !== reference.sha256) {
      throw new Error(
        `Supplement source changed: ${supplement.id}, ${reference.path}:${reference.line}. Re-review the source and summary.`,
      );
    }
  }
}
const data=structuredClone(baselineData);
for (const supplement of sectionSupplements.sections) {
  const section=data.sections.find(item=>item.id===supplement.id);
  if (!section) throw Error(`Unknown supplemental section: ${supplement.id}`);
  section.text=supplement.text;
  section.missing=supplement.missing;
  section.state=supplement.state;
  section.sources=[...new Set([...section.sources, ...supplement.sources])];
  section.supplement=supplement;
}

const model=JSON.parse(fs.readFileSync(`${review}/data/model.json`,
'utf8'));
const templateFile=`${dir}/template-detail-map.json`;
const template=fs.existsSync(templateFile)?JSON.parse(fs.readFileSync(templateFile,
'utf8')):null;
const outlineByLegacy=new Map((template?.core_heading_coverage||[]).map(item=>[item.id,
item]));
const sourceId=section=>outlineByLegacy.get(section.id)?.source_outline_id||section.id;
const sectionLabel=section=>`${sourceId(section)} ${section.title}`;
const HEAD=baselineData.metadata.source_commit,
DATE='2026-10-10',
outputs=new Map();
const E=s=>String(s??'').replace(/[&<>"']/g,
c=>({
  '&':'&amp;',
  '<':'&lt;',
  '>':'&gt;',
  '"':'&quot;',
  "'":'&#39;'
}
[c]));
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const slug=s=>s.replace(/<[^>]*>/g,
'').replace(/[`*]/g,
'').toLowerCase().replace(/[^\p{L}\p{N}_\-\s]/gu,
'').replace(/ /g,
'-');
const sourceName=p=>p.replaceAll('/',
'--').replace(/\.md$/,
'')+'.html';
const rel=(target,
current)=>path.posix.relative(path.posix.dirname(current),
target)||path.posix.basename(target);
const href=(target,
current,
context='')=>{
  const [p,
  hash]=target.split('#');
  return rel(p,
  current)+(context?'?context='+encodeURIComponent(context):'')+(hash?'#'+hash:'');
}
;
const A=(target,
text,
current,
context='',
extra='')=>`<a href="${E(href(target,
current,
context))}" ${extra}>${E(text)}</a>`;
const chip=(target,
text,
current,
context='')=>A(target,
text,
current,
context);
const tag=(text,
type='')=>`<span class="tag ${type}">${E(text)}</span>`;
const ul=values=>`<ul>${values.map(v=>`<li>${E(v)}</li>`).join('')}</ul>`;
const sectionUrl=id=>`sections/${id}.html#section-${id}`;
const reqUrl=id=>`requirements/${id}.html#requirement-${id}`;
const opUrl=id=>`operations/${id}.html#${id}`;
const flowUrl=id=>`workflows/${id}.html#${id}`;
const screenUrl=id=>`screens/${id}.html#${id}`;
const sourceUrl=(p,
line)=>`sources/${sourceName(p)}${line?'#L'+line:''}`;
const sourceMaps=new Map(),
bySource=new Map(model.sources.map(s=>[s.id,
s]));
const S=new Map(data.sections.map(s=>[s.id,
s])),
O=new Map(model.operations.map(o=>[o.id,
o])),
F=new Map(model.workflows.map(f=>[f.id,
f])),
SC=new Map(model.screens.map(s=>[s.id,
s]));
const ids=[...new Set([...model.screens,
...model.operations,
...model.workflows].flatMap(x=>x.requirements||[]))].sort((a,
b)=>a.localeCompare(b,
'en',
{
  numeric:true
}
));
const canonicalPaths=[...new Set([...data.metadata.sources.map(s=>s.path),
...model.sources.map(s=>s.path)])].sort();
const sourceManifest=[];
function routeForRepo(p){
  if(canonicalPaths.includes(p))return sourceUrl(p);
  if(p.startsWith(review+'/'))return '../../review/pay-html-001/'+p.slice(review.length+1);
  return null;
}
// Convert canonical Markdown references into readable local source pages.
// A stale source heading is explicitly disclosed rather than silently broken.
function transformLinks(html, repoPath, current) {
  return html.replace(/href="([^"\n]+)"/g, (_, originalUrl) => {
    if (/^(https?:|mailto:|#)/.test(originalUrl)) {
      return `href="${originalUrl}"`;
    }
    const [file, hash] = originalUrl.split('#');
    const sourcePath = path.posix.normalize(
      path.posix.join(path.posix.dirname(repoPath), file),
    );
    const localTarget = routeForRepo(sourcePath);
    if (!localTarget) {
      return `href="https://github.com/hirokazu601218/PowerAppsCanvasAppUI/blob/${HEAD}/${E(sourcePath)}${hash ? '#' + hash : ''}"`;
    }
    const headingExists = hash && sourceMaps.get(sourcePath)?.blocks.some(
      block => block.token?.type === 'heading'
        && slug(block.token.text) === decodeURIComponent(hash),
    );
    const fragment = headingExists ? '#' + hash : '';
    const explanation = hash && !headingExists
      ? ' title="旧参照先の見出しが現在の資料にないため、資料の先頭を開きます。"'
      : '';
    return `href="${E(href(localTarget + fragment, current))}" data-keep-context${explanation}`;
  });
}
function sourceBlocks(p){
  const content=fs.readFileSync(p,
  'utf8'),
  lines=content.split('\n');
  let blocks=[];
  if(p.endsWith('.md')){
    let cursor=0,
    line=1;
    for(const t of marked.lexer(content,
    {
      gfm:true
    }
    )){
      if(!t.raw||t.type==='space')continue;
      const ix=content.indexOf(t.raw,
      cursor);
      const start=ix<0?cursor:ix;
      line=content.slice(0,
      start).split('\n').length;
      blocks.push({
        line,
        end:line+t.raw.split('\n').length-1,
        raw:t.raw,
        token:t
      }
      );
      cursor=start+t.raw.length;
    }
  }
  else blocks=[{
    line:1,
    end:lines.length,
    raw:content,
    token:null
  }
  ];
  sourceMaps.set(p,
  {
    content,
    lines,
    blocks
  }
  );
  sourceManifest.push({
    path:p,
    sha256:sha(content),
    bytes:Buffer.byteLength(content),
    source_commit:HEAD,
    lines:lines.length,
    scope:p==='docs/handoff/STATUS.md'?'Selected named current/history sections, line ranges listed in generated HTML':'Complete source content'
  }
  );
  return blocks;
}
for(const p of canonicalPaths)sourceBlocks(p);
const sectionOps={
  '1.1.1':['OP-E-CONFIRM',
  'OP-F-CERTIFY',
  'OP-JLINK-CONFIRM'],
  '1.1.2':['OP-E-CONFIRM',
  'OP-PAY-CALCULATE',
  'OP-JLINK-CONFIRM'],
  '1.1.3':['OP-E-CORRECT',
  'OP-F-CERTIFY',
  'OP-G-CONFIRM'],
  '1.1.4':['OP-IMPORT-VALIDATE',
  'OP-JLINK-EXPORT',
  'OP-JLINK-IMPORT'],
  '1.1.5':['OP-E-HISTORY',
  'OP-PAY-CALCULATE',
  'OP-PAY-PAID'],
  '1.3.1':['OP-PAY-PERIOD'],
  '1.5':['OP-JLINK-CONFIRM'],
  '1.6.1':['OP-G-REGISTER',
  'OP-PAY-PAID'],
  '1.8.1':['OP-002-SEARCH',
  'OP-F-HTML'],
  '2.1.1':['OP-E-CONFIRM',
  'OP-PAY-CALCULATE',
  'OP-JLINK-CONFIRM'],
  '2.1.3':['OP-003-IMPORT',
  'OP-JLINK-RECONCILE'],
  '2.2.3':['OP-001-STAFF',
  'OP-002-PAYDETAIL',
  'OP-F-RETURN-HTML',
  'OP-JINKYU-PROCESS'],
  '2.2.4':['OP-002-EDIT',
  'OP-002-SAVE',
  'OP-002-READMODE'],
  '2.3.1':['OP-F-HTML',
  'OP-F-PDF'],
  '2.3.2':['OP-F-PDF'],
  '2.4.1':['OP-E-HISTORY',
  'OP-PAY-CALCULATE'],
  '2.4.2':['OP-E-HISTORY',
  'OP-G-REGISTER'],
  '2.4.3':['OP-E-HISTORY',
  'OP-G-REGISTER'],
  '2.4.4':['OP-PAY-PAID',
  'OP-E-CORRECT'],
  '2.4.5':['OP-JLINK-TARGET'],
  '2.4.6':['OP-E-CONFIRM',
  'OP-F-CERTIFY',
  'OP-PAY-PAID'],
  '2.5.1':['OP-IMPORT-VALIDATE',
  'OP-JLINK-EXPORT',
  'OP-JLINK-IMPORT',
  'OP-JLINK-RECONCILE'],
  '3.1.2':['OP-002-FONT',
  'OP-002-SIDEBAR'],
  '3.5.2':['OP-002-SEARCH',
  'OP-002-SAVE'],
  '3.10.2':['OP-F-HTML'],
  '3.12':['OP-PAY-PAID',
  'OP-JLINK-RECONCILE']
}
;
// Use only identifiers actually present; fail if a authored mapping is mistyped.
for(const [sid,
ops] of Object.entries(sectionOps))for(const id of ops)if(!O.has(id))throw new Error(`Unknown mapped operation ${sid}: ${id}`);
const sectionFlows={
  '1.1.2':model.workflows.map(f=>f.id),
  '2.1.3':['WF-10',
  'WF-13'],
  '2.1.5':['WF-12'],
  '2.2.3':['WF-01',
  'WF-08',
  'WF-13'],
  '2.3.1':['WF-08'],
  '2.3.2':['WF-08'],
  '2.4.4':['WF-05',
  'WF-14'],
  '2.4.6':['WF-05',
  'WF-06',
  'WF-12'],
  '2.5.1':['WF-04',
  'WF-10',
  'WF-13'],
  '3.5.2':['WF-01',
  'WF-10'],
  '3.12':['WF-12',
  'WF-14']
}
;
const sectionScreens={
  '2.2.1':model.screens.map(s=>s.id),
  '2.2.2':model.screens.map(s=>s.id),
  '2.2.3':['SCR-001',
  'SCR-002',
  'SCR-005',
  'FUT-JLINK',
  'EXT-JINKYU'],
  '2.2.4':['SCR-002',
  'SCR-003'],
  '2.3.1':['EXT-COMMUTE'],
  '2.3.2':['EXT-COMMUTE'],
  '2.5.1':['FUT-IMPORT',
  'FUT-JLINK',
  'EXT-JINKYU']
}
;
const parentSection=id=>id.includes('.')?id.split('.').slice(0,
-1).join('.'):null;
const relatedSectionsForReq=id=>data.sections.filter(s=>(sectionOps[s.id]||[]).some(oid=>O.get(oid).requirements.includes(id))||(sectionFlows[s.id]||[]).some(fid=>F.get(fid).requirements.includes(id))||(sectionScreens[s.id]||[]).some(sid=>SC.get(sid).requirements.includes(id))).map(s=>s.id);
const reqEntities=ids.map(id=>{
  const refs=[];
  const re=new RegExp(`(^|[^A-Z0-9-])${id.replace(/[.*+?^${}()|[\]\\]/g,
  '\\$&')}(?=[^A-Z0-9-]|$)`);
  for(const [p,
  src]of sourceMaps){
    if(!p.endsWith('.md')||p==='docs/handoff/STATUS.md')continue;
    for(const b of src.blocks){
      if(b.token?.type==='table'){
        const rows=b.raw.split('\n');
        for(let i=0;
        i<rows.length;
        i++){
          const first=rows[i].split('|')[1]?.replace(/[`*]/g,
          '').trim()||'';
          if(first===id)refs.push({
            path:p,
            line:b.line+i,
            text:rows[i],
            kind:'exact_table_row'
          }
          );
        }
      }
      else if(b.token?.type==='heading'&&re.test(b.raw))refs.push({
        path:p,
        line:b.line,
        text:b.raw,
        kind:'heading'
      }
      );
    }
  }
  if(!refs.length){
    const paths=[...new Set(model.operations.filter(o=>o.requirements.includes(id)).flatMap(o=>o.source_ids).map(s=>bySource.get(s)?.path).filter(Boolean))];
    for(const p of paths){
      const src=sourceMaps.get(p);
      if(!src)continue;
      const b=src.blocks.find(b=>re.test(b.raw));
      if(b)refs.push({
        path:p,
        line:b.line,
        text:b.raw,
        kind:'containing_block'
      }
      );
    }
  }
  if (['SCR005-UI-004','SCR005-UI-015'].includes(id)) {
    const p='docs/requirements/screen-requirements.md', src=sourceMaps.get(p);
    const b=src.blocks.find(b=>b.token?.type==='heading' && b.raw.includes('承認A追補'));
    if(b) {
      const index=src.blocks.indexOf(b); const following=[];
      for(const next of src.blocks.slice(index+1)) { if(next.token?.type==='heading')break; following.push(next.raw); }
      refs.push({path:p,line:b.line,text:b.raw+following.join(''),kind:'approved_addendum'});
    }
  }
  return {
    id,
    source_refs:refs,
    operation_ids:model.operations.filter(o=>o.requirements.includes(id)).map(o=>o.id),
    workflow_ids:model.workflows.filter(f=>f.requirements.includes(id)).map(f=>f.id),
    screen_ids:model.screens.filter(s=>s.requirements.includes(id)).map(s=>s.id),
    section_ids:relatedSectionsForReq(id),
    source_resolved:refs.length>0
  }
  ;
}
);
const R=new Map(reqEntities.map(r=>[r.id,
r]));
const classification=status=>status==='確定改修要件'?'確定':status==='提案'?'提案':status==='未決'?'未決':'既存記録';
function dimensions({
  coverage='本文あり',
  decision='個別出典を参照',
  current=false
}
={
}
){
  return `<dl class="status-grid">
<div>
<dt>記載の充足</dt>
<dd>${E(coverage)}</dd>
</div>
<div>
<dt>要件の判断</dt>
<dd>${E(decision)}</dd>
</div>
<div>
<dt>実装の状態</dt>
<dd>${current?'既存区分・出典時点限定':'この資料では未判定'}</dd>
</div>
<div>
<dt>実機の検証</dt>
<dd>本改訂では未実施</dd>
</div>
</dl>`;
}
const navs=[['index.html',
'入口'],
['journeys.html',
'業務から読む'],
['screens/index.html',
'画面一覧'],
['chapters.html',
'標準の章立て'],
['requirements/index.html',
'要件ID・操作'],
['open-items.html',
'要件未設定'],
['reading-guide.html',
'閲覧方法']];
function shell(current,
title,
body,
{
  active='',
  crumbs=[],
  context=null,
  id=''
}
={
}
){
  const portalRoot=rel('index.html',
  current).replace(/index\.html$/,
  '');
  const breadcrumbs=[['index.html',
  '要件定義'],
  ...crumbs];
  return `<!doctype html>\n<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="非常勤給与アプリの要件定義レビュー。DS120の章、業務、画面、操作、出典を相互参照。Markdownが正本。">
<title>${E(title)} | 非常勤給与 要件定義</title>
<link rel="stylesheet" href="${E(rel('assets/portal.css',
  current))}">
<script src="${E(rel('assets/portal.js',
  current))}" defer>
</script>
<script src="${E(rel('assets/context.js',
  current))}" data-portal-root="${E(portalRoot||'./')}" defer>
</script>
</head>
<body>
<a class="skip" href="#main">本文へ移動</a>
<header class="masthead">
<div class="masthead-inner">${A('index.html',
  '非常勤給与アプリ',
  current,
  '',
  'class="brand"').replace('</a>',
  '<small>要件定義・業務レビュー</small></a>')}<div class="release">DOT-002 / レビュー版<br>${DATE} · Markdownが正本</div>
</div>
</header>
<nav class="topnav" aria-label="主要な資料">
<div>${navs.map(([p,
  t])=>A(p,
  t,
  current,
  '',
  active===p?'aria-current="page"':'')).join('')}</div>
</nav>
<main id="main" class="wrap">
<nav class="breadcrumbs" aria-label="パンくず">${breadcrumbs.map(([p,
  t])=>`<span>${A(p,
  t,
  current)}</span>`).join('')}<span aria-current="page">${E(title)}</span>
</nav>${context?`<a class="context-return" data-context-return href="${E(href(context[0],
  current))}">← ${E(context[1])}</a>`:''}<div${id?` id="${E(id)}"`:''}>${body}</div>
</main>
<footer>
<div>DOT-002 / PAY-REQ-HTML-REWORK-001 · 非正本・確認用。要件の確定、実装、実機検証、業務受入は別の判断です。<br>GitHub資料の基準: PR #136 ${HEAD.slice(0,
  12)}。レビューの業務・画面モデル: ${model.metadata.source_sha.slice(0,
  12)} / ${model.metadata.updated}。DOT-001の承認A・引継ぎLive38観測を反映。正式P/Hはrun 38049776822で採取済み（旧v25 guardでrun FAIL）。選定自動E2E・最終照合は未実施です。 ${A('sources.html',
  '出典と版',
  current)} · ${A('reading-guide.html',
  '閲覧方法',
  current)}</div>
</footer>
</body>
</html>`;
}
function put(p,
title,
body,
opts){
  outputs.set(`${dir}/${p}`,
  shell(p,
  title,
  body,
  opts));
}
function panel(title,
content,
attrs=''){
  return `<section class="panel" ${attrs}>
<h2>${E(title)}</h2>${content}</section>`;
}
function chips(type,
values,
current,
context=''){
  const fn={
    req:reqUrl,
    op:opUrl,
    flow:flowUrl,
    screen:screenUrl,
    section:sectionUrl
  }
  [type];
  return `<div class="chips">${values.map(id=>chip(fn(id),
  id,
  current,
  context)).join('')}</div>`;
}
function sourceLinks(paths,
current,
context=''){
  return `<ul class="list">${[...new Set(paths)].map(p=>`<li>${A(sourceUrl(p),
  path.basename(p),
  current,
  context,
  'data-keep-context')}<div class="meta">${E(p)}</div>
</li>`).join('')}</ul>`;
}
function searchForm(current,
{
  states=true,
  kinds=false,
  placeholder='要件ID、画面、業務、データ名'
}
={
}
){
  return `<form class="toolbar" data-search-form role="search">
<label class="search-field">本文を検索<input type="search" name="q" placeholder="${E(placeholder)}" autocomplete="off">
</label>${states?'<label>記載の充足で絞る<select name="state"><option value="">すべて</option><option value="unset">要件未設定</option><option value="partial">一部設定</option><option value="documented">記載済み</option></select></label>':''}${kinds?'<label>対象<select name="kind"><option value="">すべて</option><option value="requirement">要件ID</option><option value="operation">操作</option></select></label>':''}<button type="submit">検索</button>
<button type="button" data-reset>リセット</button>
</form>
<p class="results" data-result-count role="status" aria-live="polite">
</p>
<p class="empty" data-empty hidden>条件に一致する項目はありません。検索語や状態を変えてください。</p>
<noscript>
<p class="notice info">検索と絞込みにはJavaScriptが必要です。全項目は下に表示しています。ブラウザーのページ内検索も利用できます。</p>
</noscript>`;
}
function opCard(o,
current,
context=''){
  return `<article class="card">
<span class="number">${E(o.id)} · ${E(o.screen_id)}</span>
<h3>${A(opUrl(o.id),
  o.title,
  current,
  context)}</h3>${tag(o.status,
  o.status==='未決'?'amber':o.status==='提案'?'purple':'')}<p>${E(o.process)}</p>
<div class="meta">担当: ${E(o.roles.join(' / '))}</div>
</article>`;
}
function workflowCard(f,
current,
context=''){
  return `<article class="card">
<span class="number">${E(f.id)}</span>
<h3>${A(flowUrl(f.id),
  f.name,
  current,
  context)}</h3>
<p>${E(f.start)} → ${E(f.end)}</p>
<div class="meta">${E(f.actor)}</div>${tag(f.status)}</article>`;
}
function table(headers,
rows,
caption){
  return `<div class="table-wrap" role="region" tabindex="0" aria-label="${E(caption)}">
<table>
<caption>${E(caption)}</caption>
<thead>
<tr>${headers.map(h=>`<th scope="col">${E(h)}</th>`).join('')}</tr>
</thead>
<tbody>${rows.map(r=>`<tr>${r.map(c=>`<td>${c}</td>`).join('')}</tr>`).join('')}</tbody>
</table>
</div>`;
}
function sourceExcerpt(ref,
current,
context=''){
  let html=ref.kind==='exact_table_row'?`<p>${E(ref.text.split('|').filter((s,
  i,
  a)=>i!==0&&i!==a.length-1).map(s=>s.trim().replace(/`/g,
  '')).join(' ｜ '))}</p>`:marked.parse(ref.text,
  {
    gfm:true
  }
  );
  html=transformLinks(html,ref.path,current);
  return `<div class="source-row">${html}<p class="source">${A(sourceUrl(ref.path,
  ref.line),
  `${path.basename(ref.path)} · ${ref.line}行目`,
  current,
  context)} / ${ref.kind==='exact_table_row'?'正本の該当行':'正本の該当箇所'}</p>
</div>`;
}
const counts={
  headings:data.sections.length,
  content:data.sections.filter(s=>s.state!=='章見出し').length,
  documented:data.sections.filter(s=>s.state==='記載済み').length,
  partial:data.sections.filter(s=>s.state.startsWith('一部')).length,
  unset:data.sections.filter(s=>s.state==='要件未設定').length
}
;
const introFlow=[['WF-05',
'給与情報を整える',
'勤務条件・保険・税などを登録し、給与班が確認。未確認の情報は計算に使いません。'],
['WF-10',
'勤務実績をそろえる',
'局・勤務月ごとに報告。取込中・途中失敗を完了扱いにしません。'],
['WF-12',
'計算する',
'認定済み通勤、報告済み勤怠などから計算。使用した条件と結果を版ごとに保持します。'],
['WF-13',
'人給と照合する',
'Excelを人給へ渡し、CSVを戻して最新版と照合。差分は原因の画面へ戻って訂正します。'],
['WF-14',
'確定後の差額を扱う',
'支払済みの元結果は直さず、追給・返納として別に扱います。']];
{
  const cur='index.html';
  let body=`<div class="hero">
<section>
<span class="eyebrow">REQUIREMENTS REVIEW / DS-120</span>
<h1>給与業務を、<br>要件からたどる。</h1>
<p class="lead">業務の流れと画面を確認する方にも、設計・構築の条件を追う方にも。ひとつの要件から、担当・操作・データ・例外・根拠までつなげて読めます。</p>
<div class="actions">${A('journeys.html',
  '業務の流れから読む',
  cur,
  '',
  'class="button primary"')}${A('requirements/index.html',
  '要件IDから探す',
  cur,
  '',
  'class="button"')}</div>
</section>
<aside class="hero-note">
<strong>今回の資料で分かること</strong>
<ul>
<li>誰が、どの画面で、何を確認するか</li>
<li>何が確定し、何がまだ未設定か</li>
<li>設計・試験につなぐ操作条件と出典</li>
</ul>
<p class="meta">アプリの実装や給与計算を実行する資料ではありません。</p>
</aside>
</div>
<section>
<div class="section-head">
<h2>確認したいところから</h2>${A('reading-guide.html',
  'iPhone・PCでの開き方',
  cur)}</div>
<div class="card-grid two">${[ ['screens/index.html',
  '01 / 業務利用者',
  '画面を見ながら確認',
  '入口、表示内容、入力・確認、完了の条件を画面ごとに整理。'],
  ['chapters.html',
  '02 / 設計・構築者',
  '標準の章立てで確認',
  'DS-120第5章の章立てから、業務・機能・非機能へ。'],
  ['requirements/index.html',
  '03 / 条件を追跡',
  '要件・操作を検索',
  '要件IDと操作IDから、役割、データ、例外、関連資料へ。'],
  ['open-items.html',
  '04 / 次の判断',
  '要件未設定を確認',
  '記載の不足と、実装・検証の状況を分けて確認。'] ].map(([p,
  n,
  t,
  d])=>`<a class="card card-link featured" href="${p}">
<span class="number">${n}</span>
<h3>${t} →</h3>
<p>${d}</p>
</a>`).join('')}</div>
</section>
<section class="panel" style="margin-top:24px">
<h2>全体の流れをつかむ</h2>
<ol class="steps">${introFlow.map(([id,
  t,
  d])=>`<li>
<div class="step-title">${A(flowUrl(id),
  t,
  cur)}</div>
<p>${E(d)}</p>
</li>`).join('')}</ol>
<p class="meta">工程順の読み方を示しています。各業務の戻り・分岐・失敗時の経路は、個別フロー図と操作定義で確認できます。</p>
</section>
<section class="panel">
<h2>確定している境界</h2>
<ul>
<li>2026年10月7日の給与確定要件、10月8日の人給連携の決定を優先します。</li>
<li>人給連携は「支給回の状況／出力／取込・照合」の3タブ。最新の全体照合が差分ゼロの場合だけ、給与班が支給回を確定します。</li>
<li>D9以降の計算式、端数、符号などの制度判断は保留です。</li>
</ul>
<div class="chips">${chip(reqUrl('I12'),
  'I12: 支給回の確定条件',
  cur)}${chip(sourceUrl('docs/requirements/payroll-confirmed-20261007.md'),
  '給与確定要件の全文',
  cur)}${chip(sourceUrl('docs/requirements/payroll-interface-decisions-20261008.md'),
  '人給連携の決定・保留',
  cur)}</div>
</section>
<div class="stat-row">
<span>
<strong>148</strong>原本の上位見出し</span>
<span>
<strong>${model.workflows.length}</strong>業務フロー</span>
<span>
<strong>${model.screens.length}</strong>画面・外部境界</span>
<span>
<strong>${model.operations.length}</strong>操作定義</span>
</div>
<p class="meta">本文対象${counts.content}項目の内訳: 記載済み${counts.documented} / 一部設定${counts.partial} / 要件未設定${counts.unset}。この数字は実装率・検証率ではありません。</p>
<p class="notice info">iPhoneの「ファイル」プレビューでは、別ファイルへの移動・検索・図の操作は保証されません。主な閲覧先はSafari等の通常ブラウザーです。現時点では未公開のローカル成果物です。</p>`;
  put(cur,
  '要件定義の入口',
  body,
  {
    active:cur
  }
  );
}
{
  const cur='chapters.html';
  let body=`<span class="eyebrow">STANDARD STRUCTURE</span>
<h1>標準の章立てから読む</h1>
<p class="lead">DS-120第5章の原本階層に、既存の要件IDと具体的な業務を対応させています。従来の140項目に加え、別スタイルで定義された8見出しを補完しています。</p>
<p class="notice info">公式Wordの版は2026-06-12、ZIP掲載更新は2026-07-15。標準の記載例や記入要領は、案件の要件として採用していません。</p>`;
  for(const chapter of data.sections.filter(s=>s.level===1)){
    const groups=data.sections.filter(s=>parentSection(s.id)===chapter.id);
    body+=panel(`${chapter.id} ${chapter.title}`,
    `<ul class="tree">${groups.map(g=>`<li>
<h3>${A(sectionUrl(g.id),
    sectionLabel(g),
    cur)}</h3>${g.text?`<p>${E(g.text)}</p>`:''}<div class="sub">${(template?.additional_outline_items||[]).filter(x=>x.parent_section_id===g.id&&x.type==='template_detail_heading').map(x=>`${A(`template-sections/${x.source_outline_id}.html`,
    `${x.source_outline_id} ${x.title}`,
    cur)} ${tag(templateSupplements.has(x.source_outline_id)?'原本から補完・一部設定':'原本から補完・要件未設定',
    'amber')}<br>`).join('')}${data.sections.filter(x=>parentSection(x.id)===g.id).map(x=>`${A(sectionUrl(x.id),
    sectionLabel(x),
    cur)} ${tag(x.state,
    x.missing?'amber':'')}<br>`).join('')}</div>${g.state!=='章見出し'?tag(g.state,
    g.missing?'amber':''):''}</li>`).join('')}</ul>`);
  }
  body+=`<p>${A('template-details.html',
  '標準テンプレートの補助見出し・表の記入項目',
  cur)} · ${A('open-items.html',
  '要件未設定だけを見る',
  cur)}</p>`;
  put(cur,
  '標準の章立て',
  body,
  {
    active:cur
  }
  );
}
function templateDetails(sid,
current){
  if(!template)return '';
  const details=(template.additional_details||[]).filter(d=>d.parent_section_id===sid),
  outline=(template.additional_outline_items||[]).filter(d=>d.parent_section_id===sid),
  tables=(template.table_schemas||[]).filter(d=>d.parent_section_id===sid),
  guidance=(template.authoring_guidance||[]).filter(d=>d.parent_section_id===sid),
  figures=(template.illustrations||[]).filter(d=>d.parent_section_id===sid);
  if(![details,
  outline,
  tables,
  guidance,
  figures].some(a=>a.length))return '';
  return `<details>
<summary>標準テンプレートの補助項目・記入要領 <small>案件の要件とは別</small>
</summary>
<div>
<p class="notice info">次は公式テンプレートが記入を促す項目です。例文・例示値・推奨条件を、そのまま本アプリの確定要件にしていません。</p>${details.length?`<h3>補助見出し・条文例の論点</h3>
<ul>${details.map(d=>`<li id="${E(d.id||d.html_anchor)}">
<strong>${E(d.type==='template_clause_example'?d.label:d.title||d.label)}</strong> ${tag(d.type==='template_clause_example'?'原本の条文例':'原本の小見出し')} ${d.label&&d.title&&d.label!==d.title?`<p>${E(d.label)}</p>`:''}</li>`).join('')}</ul>`:''}${outline.length?`<h3>本文に指定された補助アウトライン</h3>
<ul>${outline.map(d=>`<li id="${E(d.id||d.html_anchor)}">${E(d.type==='template_clause_example'?d.label:d.title||d.label)} ${tag(d.type==='template_clause_example'?'原本の条文例':'原本の小見出し')}</li>`).join('')}</ul>`:''}${tables.length?`<h3>表の記入項目</h3>${tables.map(t=>`<section id="${E(t.id)}">
<h4>${E(t.caption||t.title||t.id)}</h4>
<p>${E((t.header_rows||[]).map(r=>Array.isArray(r)?r.join(' / '):String(r)).join(' ・ '))}</p>${t.row_prompts?.length?ul(t.row_prompts.map(x=>typeof x==='string'?x:x.label)):''}<p class="meta">表内の見本値は本アプリの要件へ採用していません。</p>
</section>`).join('')}`:''}${figures.length?`<h3>図で示す対象</h3>
<ul>${figures.map(f=>`<li id="${E(f.id)}">${E(f.caption||f.purpose||f.title||f.id)}<p class="meta">原本は例示図です。案件の図に読み替えず、必要な図の論点のみ参照します。</p>
</li>`).join('')}</ul>`:''}${guidance.length?`<h3>原本の記入ガイド</h3>${ul(guidance.map(g=>g.text||g.comment||g.label||JSON.stringify(g)))}`:''}<p>${A('template-details.html',
  'テンプレート照合の全体を見る',
  current)}</p>
</div>
</details>`;
}
for(const s of data.sections){
  const cur=`sections/${s.id}.html`,
  context='section-'+s.id,
  children=data.sections.filter(x=>parentSection(x.id)===s.id),
  parent=parentSection(s.id);
  let body=`<span class="eyebrow">DS-120 / 原本 ${E(sourceId(s))}${sourceId(s)!==s.id?` · 従来ID ${E(s.id)}`:''}</span>
<h1 id="section-${E(s.id)}">${E(sourceId(s))} ${E(s.title)}</h1>`;
  if(sourceId(s)!==s.id)body+=`<p class="notice info">原本の位置は ${E(sourceId(s))} です。従来の資料ID ${E(s.id)} とリンクは「${E(s.title)}」の意味で維持しています。</p>`;
  const additional=(template?.additional_outline_items||[]).filter(x=>x.parent_section_id===s.id&&x.type==='template_detail_heading');
  if(additional.length)body+=panel('原本から補完した見出し',
  `<ul class="list">${additional.map(x=>`<li>${A(`template-sections/${x.source_outline_id}.html`,
  `${x.source_outline_id} ${x.title}`,
  cur)}<p class="meta">${templateSupplements.has(x.source_outline_id)?'正本にある部分条件を記載。残る詳細は未設定。':'案件への対応は未設定。'}記載例を確定要件に採用していません。</p>
</li>`).join('')}</ul>`);
  if(s.id.startsWith('3.14.'))body+=`<p class="notice info">今回の範囲は架空データによる検証です。実データ・本番環境への移行は後段であり、具体的な対象・条件・実施承認は別途必要です。</p>`;
if(s.state!=='章見出し'){
    body+=dimensions({
      coverage:s.state
    }
    );
    if(s.supplement)body+=panel('既存の確定事項から補足した範囲', `<p>${E(s.supplement.reason)}</p><ul>${s.supplement.source_refs.map(ref=>`<li>${A(sourceUrl(ref.path,ref.line),ref.label,cur,context)}</li>`).join('')}</ul>`);
if(s.text)body+=panel('現在の要件',
    `<p class="lead">${E(s.text)}</p>`);
    if(s.missing)body+=panel('要件未設定・判断が必要な内容',
    `<p class="notice">${E(s.missing)}</p>
<p class="meta">具体的な条件・対象範囲・判定基準を未設定のまま表示しています。レイアウト案やテンプレートの例から補いません。</p>`);
  }
  if(children.length)body+=panel('この章・節に含まれる項目',
  `<ul class="list">${children.map(c=>`<li>
<h3>${A(sectionUrl(c.id),
  sectionLabel(c),
  cur)}</h3>${c.text?`<p>${E(c.text)}</p>`:''}${tag(c.state,
  c.missing?'amber':'')}</li>`).join('')}</ul>`);
  if((sectionOps[s.id]||[]).length)body+=panel('操作条件まで確認する',
  `<p class="meta">関連する既存操作モデルの具体内容です。下位仕様や画面配置が提案の場合は、その区分を維持しています。</p>
<div class="card-grid two">${sectionOps[s.id].map(id=>opCard(O.get(id),
  cur,
  context)).join('')}</div>`);
  if((sectionFlows[s.id]||[]).length)body+=panel('関連する業務の流れ',
  `<div class="card-grid two">${sectionFlows[s.id].map(id=>workflowCard(F.get(id),
  cur,
  context)).join('')}</div>`);
  if((sectionScreens[s.id]||[]).length)body+=panel('画面・外部境界',
  `<ul class="list">${sectionScreens[s.id].map(id=>{
    const sc=SC.get(id);
    return `<li>
<h3>${A(screenUrl(id),
    `${id} ${sc.name}`,
    cur,
    context)}</h3>
<p>${E(sc.summary)}</p>${tag(sc.status)} <span class="meta">${E(sc.roles.join(' / '))}</span>
</li>`}).join('')}</ul>`);
    if(s.id==='2.2.3')body+=panel('関係の種類を区別する',
    `<ul>
<li>アプリ内: ホームから各業務画面へ。支給明細は職員詳細から開きます。</li>
<li>通勤認定簿: 別タブで表示し、元の職員詳細タブへ戻ります。</li>
<li>人給: 利用者が別システムへ切り替え、Excel・CSVを受け渡します。自動の画面遷移ではありません。</li>
</ul>
<p>${A('../../review/pay-html-001/navigation.html',
    '全体の1対多・方向別遷移図を開く',
    cur,
    context)}</p>`);
    body+=templateDetails(s.id,
    cur);
    if(s.sources.length)body+=panel('根拠資料と、この節への戻り',
    `<p class="meta">資料は読みやすい別ページで開きます。冒頭の「元の要件へ戻る」でこの節へ戻れます。JavaScriptなしでも資料側の参照元一覧から戻れます。</p>${sourceLinks(s.sources,
    cur,
    context)}`);
    put(cur,
    sectionLabel(s),
    body,
    {
      active:'chapters.html',
      crumbs:[['chapters.html',
      '標準の章立て'],
      ...(parent?[[sectionUrl(parent),
      `${parent} ${S.get(parent).title}`]]:[])],
      context:['chapters.html',
      '標準の章立てへ戻る']
    }
    );
  }
  {
    const cur='journeys.html';
    let body=`<span class="eyebrow">FOR BUSINESS REVIEW</span>
<h1>業務の流れから読む</h1>
<p class="lead">どこから始め、何を入力・確認し、何をもって完了とするか。担当する業務を選んでください。</p>
<p class="notice info">各図は業務の流れを説明するものです。提案の画面配置や未決の方式も含み、アプリ上で全工程が動くことを示していません。</p>`;
    for(const [title,
    wfs]of [['日常の入力・確認',
    ['WF-01',
    'WF-05',
    'WF-06',
    'WF-08',
    'WF-09',
    'WF-10',
    'WF-11']],
    ['給与の計算・人給との照合',
    ['WF-12',
    'WF-13',
    'WF-14']],
    ['受渡し・変更・管理',
    ['WF-02',
    'WF-03',
    'WF-04',
    'WF-07',
    'WF-15']]])body+=`<div class="section-head">
<h2>${title}</h2>
</div>
<div class="card-grid">${wfs.map(id=>workflowCard(F.get(id),
    cur)).join('')}</div>`;
    put(cur,
    '業務の流れ',
    {
      toString:()=>body
    }
    .toString(),
    {
      active:cur
    }
    );
  }
  function figure(f,
  current){
    const legacy=fs.readFileSync(`${review}/workflows/${f.id.toLowerCase()}.html`,
    'utf8');
    let svg=legacy.match(/<svg\b[\s\S]*?<\/svg>/)?.[0];
    if(!svg)throw Error(`Missing connected SVG ${f.id}`);
    svg=svg.replace(/href="([^"]+)"/g,
    (all,
    u)=>{
      if(u.startsWith('#'))return /^#[a-z]+$/.test(u)?`href="#step-${u.slice(1)}"`:all;
      const op=u.match(/#(OP-[A-Z0-9-]+)/)?.[1];
      if(op&&O.has(op))return `href="${E(href(opUrl(op),
      current,
      'flow-'+f.id))}"`;
      const screen=u.match(/wireframes\/([a-z0-9-]+)\.html/)?.[1]?.toUpperCase();
      if(screen&&SC.has(screen))return `href="${E(href(screenUrl(screen),
      current,
      'flow-'+f.id))}"`;
      return all;
    }
    );
    return `<figure data-figure>
<div class="figure-controls">
<button type="button" data-zoom-out aria-label="図を縮小">− 縮小</button>
<output aria-live="polite">100%</output>
<button type="button" data-zoom-in aria-label="図を拡大">＋ 拡大</button>
<button type="button" data-zoom-fit>全体に戻す</button>
</div>
<div class="diagram-viewport" tabindex="0" role="region" aria-label="${E(f.id+' '+f.name)}。拡大後は横・縦にスクロールできます。">
<div class="diagram-canvas">${svg}</div>
</div>
<figcaption class="figure-note">拡大後は指で横・縦へスクロールできます。キーボードは図枠にTabで移動し矢印キー。図の工程名から操作の詳細へ進めます。図の下にも同じ工程と全経路を記載しています。</figcaption>
</figure>`;
  }
  for(const f of model.workflows){
    const cur=`workflows/${f.id}.html`,
    context='flow-'+f.id,
    ops=f.steps.map(s=>O.get(s.operation_id)).filter(Boolean);
    let body=`<span class="eyebrow">BUSINESS FLOW / ${f.id}</span>
<h1 id="${f.id}">${E(f.name)}</h1>
<p class="lead">${E(f.diagram?.summary||`${f.start}から${f.end}まで。`)}</p>${dimensions({
      decision:classification(f.status),
      current:f.status==='現行実装'})}`;
      body+=panel('この業務の確認ポイント',
      `<dl class="contract">
<dt>担当する人</dt>
<dd>${E(f.actor)}</dd>
<dt>どこから始める</dt>
<dd>${E(f.start)}</dd>
<dt>使う画面</dt>
<dd>${chips('screen',
      f.screen_ids,
      cur,
      context)}</dd>
<dt>何をもって完了</dt>
<dd>${E(f.end)}</dd>
</dl>`);
      body+=panel('流れと戻り・分岐',
      figure(f,
      cur)+`<p class="meta">青の実線: 業務の順序。茶色: 訂正・再試行。破線: 外部システムとの受渡し等。内部画面移動、別タブ、利用者による人給への切替を混同しません。</p>`);
      body+=panel('何を入力・確認するか',
      `<ol class="steps">${f.steps.map(st=>`<li id="step-${E(st.id)}">
<div class="step-title">${st.operation_id&&O.has(st.operation_id)?A(opUrl(st.operation_id),
      st.label,
      cur,
      context):E(st.label)}</div>
<p>${E(st.detail)}</p>
<div class="meta">${SC.has(st.screen_id)?A(screenUrl(st.screen_id),
      st.screen_id,
      cur,
      context):'アプリ外・画面未指定'} ${st.operation_id?` / ${E(st.operation_id)}`:''}</div>
</li>`).join('')}</ol>`);
      body+=`<details>
<summary>設計・構築者向け: 役割・データ・処理条件</summary>
<div>${table(['操作',
      '担当・対象範囲',
      '読む情報 → 変更する情報',
      '実行条件・失敗時'],
      ops.map(o=>[A(opUrl(o.id),
      `${o.id} ${o.title}`,
      cur,
      context),
      E(o.roles.join(' / '))+'<br>'+E(o.row_scope),
      E(o.reads.join('、'))+' → '+E(o.writes.length?o.writes.join('、'):'データ更新なし'),
      E(o.preconditions)+'<br>'+E(o.failure)]),
      '業務を構成する操作の契約')}${table(['起点',
      '条件・操作',
      '到達点'],
      f.edges.map(e=>[E(f.steps.find(s=>s.id===e.from)?.label||e.from),
      E(e.label),
      E(f.steps.find(s=>s.id===e.to)?.label||e.to)]),
      '図と同一データの全経路')}</div>
</details>`;
      if(f.diagram?.notes?.length)body+=panel('例外・未決・確認時の注意',
      ul(f.diagram.notes));
      body+=panel('要件と根拠へ戻る',
      chips('section',
      ['1.1.2',
      ...(f.id==='WF-13'?['2.5.1']:[])],
      cur)+`<h3 style="margin-top:18px">関連要件ID</h3>`+chips('req',
      f.requirements,
      cur,
      context)+sourceLinks(f.source_ids.map(s=>bySource.get(s).path),
      cur,
      context));
      put(cur,
      f.name,
      body,
      {
        active:'journeys.html',
        crumbs:[['journeys.html',
        '業務の流れ']],
        context:['journeys.html',
        '業務一覧へ戻る']
      }
      );
    }
    {
      const cur='screens/index.html';
      let body=`<span class="eyebrow">SCREEN CATALOG</span>
<h1>画面一覧</h1>
<p class="lead">画面の目的、表示する内容、入力・確認の流れを見比べます。外部システムと将来の画面は分けて表示しています。</p>
<div class="actions">${A('../../review/pay-html-001/navigation.html',
      '全体画面遷移図',
      cur,
      'section-2.2.3',
      'class="button"')}${A(sectionUrl('2.2.1'),
      '標準要件 画面一覧へ',
      cur,
      '',
      'class="button"')}</div>
<div class="notice">「現行実装」は古い資料にある区分です。DOT-001の引継ぎLive38観測と承認Aを反映したモデルです。今回の実機再試験ではなく、正式P/Hはrun 38049776822で採取済み（旧v25 guardでrun FAIL）。選定自動E2E・最終照合は未実施です。</div>`;
      for(const [title,
      screenIds]of [['アプリ内の画面',
      ['SCR-001',
      'SCR-002',
      'SCR-003',
      'SCR-004',
      'SCR-005',
      'SCR-006']],
      ['将来機能・試作の境界',
      ['FUT-IMPORT',
      'FUT-JLINK',
      'SCR-007',
      'CUR-IMPORT-POC']],
      ['アプリ外',
      ['EXT-COMMUTE',
      'EXT-JINKYU']]])body+=`<div class="section-head">
<h2>${title}</h2>
</div>
<div class="card-grid">${screenIds.map(id=>{
        const s=SC.get(id);
        return `<article class="card">
<span class="number">${s.id}</span>
<h3>${A(screenUrl(id),
        s.name,
        cur)}</h3>${tag(s.status,
        s.status==='提案'?'purple':'')}<p>${E(s.summary)}</p>
<div class="meta">${E(s.roles.join(' / '))}</div>
</article>`}).join('')}</div>`;
        put(cur,
        '画面一覧',
        body,
        {
          active:'screens/index.html'
        }
        );
      }
      for(const s of model.screens){
        const cur=`screens/${s.id}.html`,
        context='screen-'+s.id,
        ops=model.operations.filter(o=>o.screen_id===s.id),
        flows=model.workflows.filter(f=>f.screen_ids.includes(s.id));
        let body=`<span class="eyebrow">SCREEN / ${s.id}</span>
<h1 id="${s.id}">${E(s.name)}</h1>
<p class="lead">${E(s.summary)}</p>${dimensions({
          decision:classification(s.status),
          current:s.status==='現行実装'})}`;
          if(s.id==='SCR-005') {
            const p='docs/requirements/screen-requirements.md',src=sourceMaps.get(p),index=src.blocks.findIndex(b=>b.token?.type==='heading' && b.raw.includes('承認A追補'));
            const chunks=[];for(const b of src.blocks.slice(index+1)){if(b.token?.type==='heading')break;chunks.push(b.raw);}
            body+=panel('SCR005-UI-004／015 承認A（最新の適用範囲）', `${transformLinks(marked.parse(chunks.join('')),p,cur)}${chips('req',['SCR005-UI-004','SCR005-UI-015'],cur,context)}`);
          }
          body+=panel('画面で何をするか',
          `<dl class="contract">
<dt>利用する人</dt>
<dd>${E(s.roles.join(' / '))}</dd>
<dt>どこから開く</dt>
<dd>${model.operations.filter(o=>o.destination_screen_id===s.id&&o.screen_id!==s.id).map(o=>A(opUrl(o.id),
          `${o.screen_id}: ${o.title}`,
          cur,
          context)).join('<br>')||'このモデルには別画面からの直接入口の記録がありません。'}</dd>
<dt>表示する領域</dt>
<dd>${E(s.tabs.length?s.tabs.join(' / '):'各操作に対応する一覧・内容。具体的な領域は画面例と操作定義で確認。')}</dd>
<dt>入力・確認</dt>
<dd>${E(ops.filter(o=>o.writes.length).map(o=>o.title).join(' / ')||'主に情報を参照し、対象業務へ移動します。')}</dd>
</dl>`);
          body+=panel('画面構成を確認する',
          `<div class="screen-layout">
<div class="mock-pane">
<strong>${E(s.id)}</strong>
<p>${E(s.roles.join(' / '))}</p>
<p>対象を選び、内容を確認</p>
</div>
<div class="mock-pane">
<div class="mock-tabs">${s.tabs.map(t=>`<span>${E(t)}</span>`).join('')||'<span>業務の内容</span>'}</div>
<strong>${E(s.name)}</strong>
<p>${E(s.summary)}</p>
<p class="meta">構造を説明する略図です。入力項目・配置の確定度は各操作に従います。</p>
</div>
</div>
<div class="actions">${A(`../../review/pay-html-001/wireframes/${s.id.toLowerCase()}.html`,
          '詳しい画面イメージを開く',
          cur,
          context,
          'class="button primary"')}${A(`../../review/pay-html-001/operations/${s.id.toLowerCase()}.html`,
          '画面内の操作をまとめて読む',
          cur,
          context,
          'class="button"')}</div>
<p class="meta">画面イメージは架空データのHTMLモックです。Power Appsでの実装・アクセシビリティ・保存・認可を検証済みとは扱いません。</p>`);
          body+=panel('この画面の操作',
          `<div class="card-grid two">${ops.map(o=>opCard(o,
          cur,
          context)).join('')}</div>`);
          if(s.notes?.length)body+=panel('境界・未決・注記',
          ul(s.notes));
          body+=panel('この画面を使う業務',
          `<div class="card-grid two">${flows.map(f=>workflowCard(f,
          cur,
          context)).join('')}</div>`);
          body+=panel('要件と出典',
          chips('section',
          ['2.2.1',
          '2.2.2',
          '2.2.3'],
          cur)+`<h3 style="margin-top:18px">関連要件</h3>`+chips('req',
          s.requirements,
          cur,
          context)+sourceLinks(s.source_ids.map(sid=>bySource.get(sid).path),
          cur,
          context));
          put(cur,
          `${s.id} ${s.name}`,
          body,
          {
            active:'screens/index.html',
            crumbs:[['screens/index.html',
            '画面一覧']],
            context:['screens/index.html',
            '画面一覧へ戻る']
          }
          );
        }
        const opFields=[['origin_tab',
        '遷移元タブ'],
        ['origin_mode',
        '遷移元の状態'],
        ['destination_tab',
        '遷移先タブ'],
        ['destination_mode',
        '遷移先の状態'],
        ['control',
        '操作部品'],
        ['method',
        '操作方法'],
        ['row_scope',
        '対象行・データ範囲'],
        ['visible',
        '表示条件'],
        ['enabled',
        '実行できる条件'],
        ['preconditions',
        '実行前提'],
        ['validation',
        '入力検証'],
        ['process',
        '処理する内容'],
        ['retained',
        '保持する情報'],
        ['reset',
        '解除・失効する情報'],
        ['success',
        '成功時'],
        ['failure',
        '失敗・再実行'],
        ['cancel',
        '取消時'],
        ['unsaved',
        '未保存の扱い']];
        for(const o of model.operations){
          const cur=`operations/${o.id}.html`,
          context=o.requirements.length?'req-'+o.requirements[0]:'screen-'+o.screen_id;
          let body=`<span class="eyebrow">OPERATION / ${o.id}</span>
<h1 id="${o.id}">${E(o.title)}</h1>
<p class="lead">${E(o.process)}</p>${dimensions({
            decision:o.status==='提案'?'操作・配置は提案（業務要件は別）':o.status==='未決'?'操作分担は未決（業務要件は別）':classification(o.status),
            current:o.status==='現行実装'})}<p class="meta">関連操作・配置の区分: ${E(o.status)} / 遷移ID: <span id="${E(o.transition_id)}">${E(o.transition_id)}</span>
</p>`;
            body+=panel('利用する場面',
            `<dl class="contract">
<dt>担当</dt>
<dd>${E(o.roles.join(' / '))}</dd>
<dt>操作する画面</dt>
<dd>${A(screenUrl(o.screen_id),
            `${o.screen_id} ${SC.get(o.screen_id)?.name||''}`,
            cur)} → ${A(screenUrl(o.destination_screen_id),
            o.destination_screen_id,
            cur)}</dd>
<dt>何を確認するか</dt>
<dd>${E(o.validation)}</dd>
<dt>完了の確認</dt>
<dd>${E(o.success)}</dd>
</dl>`);
            body+=panel('設計・構築者向けの処理契約',
            `<dl class="contract">${opFields.map(([key,
            title])=>`<dt>${title}</dt>
<dd data-contract-field="${key}">${E(o[key])}</dd>`).join('')}<dt>参照するデータ</dt>
<dd data-contract-field="reads">${o.reads.length?ul(o.reads):'参照データの記録なし'}</dd>
<dt>変更・記録するデータ</dt>
<dd data-contract-field="writes">${o.writes.length?ul(o.writes):'業務データの更新なし'}</dd>
</dl>`);
            body+=panel('受入観点・注記',
            `<h3>確認する観点</h3>${ul(o.acceptance)}<h3>未決・提案・対象範囲</h3>${ul(o.notes)}`);
            body+=panel('要件・業務・出典をたどる',
            `<h3>関連要件ID</h3>${chips('req',
            o.requirements,
            cur)}<h3 style="margin-top:18px">含まれる業務</h3>${chips('flow',
            model.workflows.filter(f=>f.steps.some(st=>st.operation_id===o.id)).map(f=>f.id),
            cur)}${sourceLinks(o.source_ids.map(id=>bySource.get(id).path),
            cur,
            context)}`);
            put(cur,
            `${o.id} ${o.title}`,
            body,
            {
              active:'requirements/index.html',
              crumbs:[['requirements/index.html',
              '要件ID・操作']],
              context:[screenUrl(o.screen_id),
              '操作元の画面へ戻る']
            }
            );
          }
          for(const r of reqEntities){
            const cur=`requirements/${r.id}.html`,
            context='req-'+r.id,
            ops=r.operation_ids.map(id=>O.get(id));
            const decisions=[...new Set(ops.map(o=>o.status))];
            const decision=/^PAYREQ-\d+$/.test(r.id)?'確定（未設定の方式は別記）':/^I(?:[1-9]|1[0-2])$/.test(r.id)?(r.id==='I8'?'表示要件は確定・取得方式未設定':'確定'):r.id==='FR-G-02'?'保留（業務方針のみ）':'正本の該当記述を参照';
            let body=`<span class="eyebrow">REQUIREMENT / ${r.id}</span>
<h1 id="requirement-${r.id}">${E(r.id)}</h1>${dimensions({
              coverage:r.source_resolved?'出典箇所を記載':'出典箇所の特定が必要',
              decision,
              current:ops.length>0&&ops.every(o=>o.status==='現行実装')})}`;
              body+=panel('正本に書かれている内容',
              r.source_resolved?`<p class="meta">出典の要件行・見出し・該当箇所をそのまま示しています。複数の記述がある場合は、文書と時点を確認してください。</p>${/^R\d+$/.test(r.id)&&r.source_refs.length>1?'<p class="notice">同じR番号が現行画面要件と給与決定等で使われる場合があります。番号だけで同一要件と判断せず、文書名と本文を確認してください。</p>':''}${r.source_refs.map(ref=>sourceExcerpt(ref,
              cur,
              context)).join('')}`:`<p class="notice">モデル内の参照IDとしては存在しますが、引用可能な正本の該当箇所をこの抽出では特定できていません。下記の操作と、その引用元を確認してください。未設定の仕様を補完した意味ではありません。</p>`);
              if(ops.length)body+=`<p class="meta">関連操作・配置の区分: ${E(decisions.join(' / '))}。この区分を上記の要件判断へ転記していません。</p>`;
              if(ops.length)body+=panel('この要件が関係する操作',
              `<div class="card-grid two">${ops.map(o=>opCard(o,
              cur,
              context)).join('')}</div>`);
              body+=panel('関連する章・業務・画面',
              `<h3>標準の章・節</h3>${r.section_ids.length?chips('section',
              r.section_ids,
              cur):`<p class="meta">個別の標準節への対応は未入力です。${A(sectionUrl('2.1.1'),
              '機能一覧から確認',
              cur)}</p>`}<h3 style="margin-top:18px">業務</h3>${chips('flow',
              r.workflow_ids,
              cur,
              context)}<h3 style="margin-top:18px">画面</h3>${chips('screen',
              r.screen_ids,
              cur,
              context)}`);
              put(cur,
              r.id,
              body,
              {
                active:'requirements/index.html',
                crumbs:[['requirements/index.html',
                '要件ID・操作']],
                context:['requirements/index.html',
                '要件ID一覧へ戻る']
              }
              );
            }
            {
              const cur='requirements/index.html';
              let body=`<span class="eyebrow">TRACE REQUIREMENTS</span>
<h1>要件ID・操作から探す</h1>
<p class="lead">要件IDから出典と関連操作へ。操作IDから担当・前提・データ・例外まで追えます。</p>
<p class="meta">標準書式の記載充足は${A('open-items.html',
              '「要件未設定」',
              cur)}で確認します。この一覧ではモデルに登場するIDと操作を扱います。</p>${searchForm(cur,
              {
                states:false,
                kinds:true})}<ul class="list">`;
                for(const r of reqEntities){
                  const ops=r.operation_ids.map(id=>O.get(id)),
                  text=[r.id,
                  ...ops.map(o=>o.title),
                  ...r.source_refs.map(s=>s.text)].join(' ');
                  body+=`<li data-search-item data-kind="requirement" data-search-text="${E(text)}">
<h3>${A(reqUrl(r.id),
                  r.id,
                  cur)}</h3>
<p>${E(ops.map(o=>o.title).join(' / ')||'画面・業務から参照される要件')}</p>
<div class="meta-line">${tag('要件ID')}<span>関連操作 ${ops.length}件 / 出典箇所 ${r.source_refs.length}件</span>${!r.source_resolved?tag('出典の特定待ち',
                  'amber'):''}</div>
</li>`;
                }
                for(const o of model.operations)body+=`<li data-search-item data-kind="operation" data-search-text="${E([o.id,
                o.title,
                o.screen_id,
                o.process,
                ...o.roles,
                ...o.reads,
                ...o.writes,
                ...o.requirements].join(' '))}">
<h3>${A(opUrl(o.id),
                `${o.id} ${o.title}`,
                cur)}</h3>
<p>${E(o.process)}</p>
<div class="meta-line">${tag('操作')}${tag(o.status)}<span>${E(o.roles.join(' / '))} · ${E(o.screen_id)}</span>
</div>
</li>`;
                body+='</ul>';
                put(cur,
                '要件ID・操作',
                body,
                {
                  active:cur
                }
                );
              }
              {
                const cur='open-items.html';
                let body=`<span class="eyebrow">DECISION & COVERAGE</span>
<h1>要件未設定・確認すること</h1>
<p class="lead">未設定の仕様を、実装や試験の未完了と混ぜずに確認します。</p>
<div class="stat-row">
<span>
<strong>${counts.documented}</strong>記載済み</span>
<span>
<strong>${counts.partial}</strong>一部設定</span>
<span>
<strong>${counts.unset}</strong>要件未設定</span>
</div>
<p class="notice">上の内訳は標準書式の本文${counts.content}項目についての記載充足です。「記載済み」でも実装・実機確認は別に必要です。D9以降の式は保留を維持します。</p>${searchForm(cur,
                {
                  placeholder:'未設定の条件・章番号で検索'})}<ul class="list">`;
                  for(const s of data.sections.filter(s=>s.state!=='章見出し')){
                    const states=s.state==='記載済み'?'documented':s.state.startsWith('一部')?'partial unset':'unset';
                    body+=`<li data-search-item data-states="${states}">
<h3>${A(sectionUrl(s.id),
                    sectionLabel(s),
                    cur)}</h3>${tag(s.state,
                    s.missing?'amber':'green')}${s.missing?`<p>
<strong>要件未設定:</strong> ${E(s.missing)}</p>`:`<p>${E(s.text)}</p>`}${s.missing&&s.text?`<details>
<summary>すでに記載した範囲</summary>
<div>${E(s.text)}</div>
</details>`:''}</li>`;
                  }
                  body += '</ul><h2>原本から補完した8見出し</h2><p class="meta">旧本文109項目とは別枠です。一部設定7、要件未設定1。原本例を案件の条件へ流用していません。</p><ul class="list">';
for (const extra of template.additional_outline_items.filter(item => item.type === 'template_detail_heading')) {
  const supplement = templateSupplements.get(extra.source_outline_id);
  body += `<li data-search-item data-states="${supplement?'partial unset':'unset'}"><h3>${A(`template-sections/${extra.source_outline_id}.html`, `${extra.source_outline_id} ${extra.title}`, cur)}</h3>${tag(supplement?'一部設定・要件未設定あり':'要件未設定','amber')}<p>${E(supplement?.missing||'公開対象データ、匿名化、公開方式は要件未設定。給与個人情報の公開を推測しません。')}</p>${supplement?`<details><summary>すでに記載した範囲</summary><div>${E(supplement.text)}</div></details>`:''}</li>`;
}
body+='</ul>'+panel('実装・検証の残件は、別の根拠で確認する',
                  `<p>本改訂はHTML資料の改善です。アプリの実装状態や実機の合否は更新していません。未実装・実装差分・未照合・業務判断待ちは正本の未決一覧で区別されています。</p>${sourceLinks(['docs/requirements/open-decisions.md',
                  'docs/testing/test-specification.md'],
                  cur)}`);
                  put(cur,
                  '要件未設定・確認事項',
                  body,
                  {
                    active:cur
                  }
                  );
                }
                for(const p of canonicalPaths){
                  const cur=sourceUrl(p),
                  src=sourceMaps.get(p),
                  headingIds=new Map();
                  let selected=src.blocks,
                  selectionNote='全文のHTML表示（Markdown等の正本は変更していません）';
                  if(p==='docs/handoff/STATUS.md'){
                    const allowed=['2026-10-10 DOT-001', '2026-10-10 DOT-002', '2026-10-08 人給連携モック',
                    '2026-10-08 人給Excel',
                    '2026-10-07 給与要件',
                    '2026-10-01 SCR001'];
                    let include=false;
                    selected=src.blocks.filter(b=>{
                      if(b.token?.type==='heading'&&b.token.depth===2)include=allowed.some(t=>b.token.text.startsWith(t));
                      return include;
                    }
                    );
                    selectionNote='DOT-001・DOT-002最新状態と関連する過去4節の計7節だけの選択抜粋。全履歴はGitHub原文で確認してください。';
                  }
                  let content='';
                  const selectedRanges=[];
                  for(const b of selected){
                    selectedRanges.push([b.line,
                    b.end]);
                    let html;
                    if(!b.token){
                      html=`<pre>
<code>${E(b.raw)}</code>
</pre>`;
                    }
                    else{
                      html=marked.parser([b.token],
                      {
                        gfm:true
                      }
                      );
                      html=html.replace(/<h([1-6])>([\s\S]*?)<\/h\1>/g,
                      (_,
                      n,
                      t)=>{
                        let id=slug(t),
                        i=headingIds.get(id)||0;
                        headingIds.set(id,
                        i+1);
                        if(i)id+='-'+i;
                        return `<h${n} id="${E(id)}">${t}</h${n}>`;
                      }
                      );
                      if(b.token.type==='table'){
                        let row=0;
                        html=html.replace(/<tr>/g,
                        ()=>`<tr id="L${b.line+(row++===0?0:row)}">`);
                        html=`<div class="table-wrap" role="region" tabindex="0" aria-label="${E(path.basename(p))}の表">${html}</div>`;
                      }
                    }
                    html=transformLinks(html,
                    p,
                    cur);
                    html=html.replace(/src="([^"]+)"/g,
                    (all,
                    url)=>{
                      if(/^(https?:|data:)/.test(url))return all;
                      const resolved=path.posix.normalize(path.posix.join(path.posix.dirname(p),
                      url));
                      if(!fs.existsSync(resolved))throw Error(`Missing source image: ${resolved}`);
                      const target='assets/source-'+path.posix.basename(resolved);
                      outputs.set(`${dir}/${target}`,
                      fs.readFileSync(resolved));
                      return `src="${E(rel(target,
                      cur))}"`;
                    }
                    );
                    content+=`<section id="${b.token?.type==='table'?'block-':''}L${b.line}" data-source-start="${b.line}" data-source-end="${b.end}">${html}</section>`;
                  }
                  const sectionRefs=data.sections.filter(s=>s.sources.includes(p)),
                  entityRefs=reqEntities.filter(r=>r.source_refs.some(ref=>ref.path===p));
                  let body=`<span class="eyebrow">SOURCE DOCUMENT</span>
<h1>${E(path.basename(p))}</h1>
<p class="meta">${E(p)}<br>${E(selectionNote)}</p>
<p class="notice info">新旧の記述を保持した出典です。今後の業務仕様は2026-10-07給与確定要件、2026-10-08人給決定を優先します。既存実装記録をLive 38の確認結果へ読み替えません。</p>
<p>
<a href="https://github.com/hirokazu601218/PowerAppsCanvasAppUI/blob/${HEAD}/${E(p)}">この版のGitHub原文</a> / SHA-256: <code>${sha(src.content)}</code>
</p>`;
                  body+=`<details>
<summary>この資料を参照している要件・節</summary>
<div>${chips('section',
                  sectionRefs.map(s=>s.id),
                  cur)}<div style="margin-top:12px">${chips('req',
                  entityRefs.map(r=>r.id),
                  cur)}<div class="chips">${(sectionSupplements.template_sections||[]).filter(item=>item.sources.includes(p)).map(item=>A(`template-sections/${item.id}.html#template-${item.id}`,`原本 ${item.id} ${item.title}`,cur)).join('')}</div></div>
<p class="meta">JavaScriptなしの場合も、この一覧から関連する要件へ戻れます。</p>
</div>
</details>
<article class="panel source-body" id="source-content">${content}</article>`;
                  sourceManifest.find(s=>s.path===p).rendered_line_ranges=selectedRanges;
                  put(cur,
                  path.basename(p),
                  body,
                  {
                    crumbs:[['sources.html',
                    '出典と版']],
                    context:[sectionRefs.length?sectionUrl(sectionRefs[0].id):'sources.html',
                    sectionRefs.length?`関連する要件 ${sectionRefs[0].id} へ戻る`:'出典一覧へ戻る']
                  }
                  );
                }
                {
                  const cur='sources.html';
                  let body=`<span class="eyebrow">PROVENANCE</span>
<h1>出典と版</h1>
<p class="lead">どの時点の何を根拠にしたか。正本とレビュー資料を分けて追跡します。</p>${panel('この版の範囲',
                  `<dl class="contract">
<dt>作業基準</dt>
<dd>PR #136 / ${HEAD}</dd>
<dt>正本</dt>
<dd>GitHub Markdown。PR #137から必要なDOT-001文書差分を選択統合。新しい業務仕様・制度判断は追加していません。</dd>
<dt>画面・操作モデル</dt>
<dd>${model.metadata.source_sha} / ${model.metadata.updated}</dd>
<dt>優先する確定要件</dt>
<dd>2026-10-07給与要件 / 2026-10-08人給決定</dd>
<dt>正式公開日時 P（採取済み）</dt><dd>${E(publication.lastPublishTime)}</dd><dt>独立PACアプリ本体SHA-256 H（採取済み）</dt><dd><code>${E(publication.download_sha256)}</code></dd><dt>採取run／後続試験</dt><dd>38049776822：旧v25画面SHA guard不一致でFAIL。選定E2E・最終照合はNOT_RUN。${A(sourceUrl(publication.record_path),"採取記録",cur)}</dd><dt>DOT-001の反映範囲と限界</dt>
<dd>承認A・Live38引継ぎ観測・記録を選択反映。正式P/Hはrun 38049776822で採取済み（旧v25 guardでrun FAIL）。選定自動E2E・最終照合は未実施。今回のアプリ実装・実機再試験ではありません。</dd>
</dl>`)}`;
                  body+=table(['資料',
                  'HTML表示範囲',
                  'SHA-256'],
                  sourceManifest.map(s=>[A(sourceUrl(s.path),
                  s.path,
                  cur),
                  s.path==='docs/handoff/STATUS.md'?'DOT-001・DOT-002と関連履歴の6節選択抜粋':'全文',
                  `<code>${s.sha256}</code>`]),
                  '基準ソースの一覧');
                  body+=panel('標準テンプレート',
                  `<p>DS-120第5章 要件定義書標準テンプレート。原本Wordの版2026-06-12 / ZIP掲載更新2026-07-15。</p>
<p>
<a href="${E(data.metadata.template_url)}">デジタル庁公式ZIP</a> · <a href="https://www.digital.go.jp/resources/standard_guidelines">公式掲載ページ</a> · ${A('template-details.html',
                  '階層・補助項目の照合',
                  cur)}</p>
<p class="meta">Word SHA-256: ${E(data.metadata.template_sha256)}</p>`);
                  put(cur,
                  '出典と版',
                  body);
                }
                {
                  const cur='template-details.html';
                  let body=`<span class="eyebrow">OFFICIAL TEMPLATE STRUCTURE</span>
<h1>標準テンプレートの階層・補助項目</h1>
<p class="lead">既存140項目のIDを保持し、原本のアウトライン設定から判明した補助見出しと記入項目を補っています。</p>
<p class="notice">140は従来の見出しスタイル1〜3の項目数です。原本には別スタイルの見出し8件もあり、上位3階層は148項目です。3.14の原本(1)は「移行に関する前提条件」で、従来ID 3.14.1「移行計画の作成」は原本(2)です。既存リンクの意味は変えず、原本位置を別に表示します。</p>
<p>Word版: ${E(template?.word_cover_version||'2026/06/12')} / 掲載更新: ${E(template?.official_zip_posted_updated_date||'2026-07-15')}。下位見出し・条文例を含む実効アウトライン${template?.effective_outline?.length||'未確認'}段落、表${template?.table_schemas?.length||0}件、図${template?.illustrations?.length||0}件、原本コメントの記入要領${template?.authoring_guidance?.length||0}件を対応付けています。</p>`;
                  if(template){
                    body+=table(['原本の階層番号',
                    '見出し・論点',
                    '既存IDと移動先'],
                    template.effective_outline.filter(x=>x.level<=3).map(x=>[E(x.source_outline_id),
                    E(x.title),
                    x.legacy_id?A(sectionUrl(x.legacy_id),
                    `既存ID ${x.legacy_id}`,
                    cur):A(`template-sections/${x.source_outline_id}.html`,
                    '補完した原本見出し',
                    cur)]),
                    '原本の上位3階層と既存IDの対応');
                    body+=`<h2>下位項目・表・記入要領（案件要件とは別）</h2>`;
                    for(const s of data.sections){
                      const details=templateDetails(s.id,
                      cur);
                      if(details)body+=`<section id="template-parent-${s.id}">
<h3>${A(sectionUrl(s.id),
                      sectionLabel(s),
                      cur)}</h3>${details}</section>`;
                    }
                  }
                  body+=`<section class="panel">
<h2>出典・利用条件</h2>
<p>${E(template?.license?.attribution||'')}</p>
<p>${E(template?.license?.license||'')}。<a href="${E(template?.license?.policy_url)}">デジタル庁の著作権・利用条件</a> / <a href="${E(template?.license?.license_url)}">PDL1.0</a>
</p>
<p>構造抽出・再整理: dot（DOT-002）。第三者図版・ロゴは再配布していません。</p>
</section>
<p class="meta">原本の例示値・条文を本アプリの確定条件へ自動採用していません。補助項目には対応未設定のものがあります。</p>`;
                  put(cur,
                  'テンプレート階層の照合',
                  body,
                  {
                    active:'chapters.html',
                    crumbs:[['chapters.html',
                    '標準の章立て']]
                  }
                  );
                }
                if (template) {
  for (const extra of template.additional_outline_items.filter(item => item.type === 'template_detail_heading')) {
    const current = `template-sections/${extra.source_outline_id}.html`;
    const supplement = templateSupplements.get(extra.source_outline_id);
    const clauses = template.additional_outline_items.filter(item => item.source_parent_outline_id === extra.source_outline_id);
    let body = `<span class="eyebrow">DS-120 / 原本 ${E(extra.source_outline_id)}</span>
<h1 id="template-${E(extra.source_outline_id)}">${E(extra.source_outline_id)} ${E(extra.title)}</h1>
<p class="notice info">原本の実効アウトラインで確認した見出しです。既存140項目に含まれていなかったため補完しました。原本の例文を案件要件に採用したものではありません。</p>
<p>既存の親節 ${A(sectionUrl(extra.parent_section_id), extra.parent_section_id, current)} に関連付け、既存IDの意味は変更していません。</p>`;
    if (supplement) {
      body += dimensions({coverage: supplement.state});
      body += panel('正本に記載済みの部分条件', `<p>${E(supplement.text)}</p>`);
      body += panel('要件未設定・判断が必要な内容', `<p class="notice">${E(supplement.missing)}</p>`);
      body += panel('確定事項の出典', `<ul>${supplement.source_refs.map(reference => `<li>${A(sourceUrl(reference.path, reference.line), reference.label, current, 'template-'+extra.source_outline_id)}</li>`).join('')}</ul>`);
    } else {
      body += dimensions({coverage:'要件未設定'});
      body += panel('要件未設定', '<p>公開対象データ、匿名化、公開方式の明示された確定条件は確認できていません。給与の個人情報を公開できると推測しません。</p>');
    }
    if (clauses.length) body += panel('原本の記入論点（案件の確定要件ではありません）', ul(clauses.map(item => item.label)));
    body += `<p>${A('template-details.html', '原本階層と既存IDの対応表', current)}</p>`;
    put(current, `${extra.source_outline_id} ${extra.title}`, body, {
      active: 'chapters.html',
      context: [sectionUrl(extra.parent_section_id), '親節へ戻る'],
    });
  }
}
{
                  const cur='reading-guide.html';
                  let body=`<span class="eyebrow">HOW TO READ</span>
<h1>iPhone・PCでの開き方</h1>
<p class="lead">この成果物は、未公開の静的HTML一式です。閲覧環境によって使える機能が異なります。</p>${panel('iPhone: SafariでURLを開く方式が本来の閲覧先',
                  `<ol>
<li>この資料を、承認した閲覧者だけが開けるWeb置場へ配置します。</li>
<li>そのURLをSafariで開きます。</li>
<li>要件・関連資料を通常リンクで移動し、検索・図の拡大を使います。</li>
</ol>
<p class="notice">今回、Web配置・Sites登録・公開・アクセス権変更は実施していません。URLでの提供には、公開先と閲覧範囲の承認が別途必要です。</p>
<p>PCのlocalhostは同じPCだけのアドレスで、iPhoneからそのまま開けるURLではありません。</p>`)}${panel('PC: 展開したフォルダーを通常ブラウザーで開く',
                  `<ol>
<li>配布ZIPを展開し、フォルダーの構造をそのまま保持します。</li>
<li>docs/requirements/standard-template/index.html をChrome・Edge・Safari等で開きます。配布ZIPでは viewer/docs/requirements/standard-template/index.html です。</li>
<li>別ページへのリンク、本文、図を確認します。検索・拡大はJavaScriptを許可した通常ブラウザーで利用します。</li>
</ol>
<p class="meta">外部CDN・ネットワークによる本文取得は不要です。ローカルファイルへの移動が制限される環境では、PC内のHTTPサーバーで一式を配信してください。GitHubのファイル画面はHTMLソースの表示です。</p>`)}${panel('iPhoneの「ファイル」プレビュー: 読むだけの補助資料',
                  `<p>Quick Lookは通常のWebブラウザーではありません。別HTMLへの移動、同一ページのアンカー、JavaScript、検索、拡大ボタン、モック操作を保証できません。</p>
<p>${A('index-mobile.html',
                  '単独ファイルの閲覧用要約',
                  cur)}は、業務の全体像・確定した境界・主な未設定事項を、上から読むために用意しています。別資料や操作機能は含めていません。</p>
<p class="notice">この補助資料だけでは、全要件・全操作を確認したことになりません。詳細レビューには通常ブラウザー版が必要です。iPhone実機／Safariでの動作は未検証です。今回の環境ではブラウザーからローカルHTTPへ到達できず、Chromiumの表示・操作・狭幅描画も未実施です。静的リンク検査やJavaScript単体試験は実ブラウザー試験の代わりにはしていません。</p>`)}${panel('ボタンが動かないとき',
                  `<ul>
<li>「ファイル」内のプレビューであれば、動作不良と決めつけず、まず閲覧方法を確認します。</li>
<li>通常ブラウザーでもJavaScriptを使えない場合、検索と拡大は使えません。本文と普通のリンクは残ります。</li>
<li>図が小さい場合は拡大し、図枠を縦・横へスクロールします。同じ内容は図の下の工程・経路表でも確認できます。</li>
<li>関連資料の冒頭に元要件へのリンクがあります。ブラウザーの「戻る」も使えます。</li>
</ul>`)}`;
                  put(cur,
                  '閲覧方法',
                  body,
                  {
                    active:cur
                  }
                  );
                }
                // A purpose-built linear reading sheet. No script, iframe, external CSS or local file dependency.
                {
                  const cur='index-mobile.html',
                  css=fs.readFileSync('scripts/review/requirements_portal/portal.css',
                  'utf8');
                  const body=`<header class="masthead">
<div class="masthead-inner">
<div class="brand">非常勤給与アプリ<small>iPhoneファイル閲覧用・要約</small>
</div>
</div>
</header>
<main class="wrap reading-sheet">
<span class="eyebrow">DOT-002 / ${DATE}</span>
<h1>業務と要件の全体像</h1>
<p class="notice">このファイルは上から読むための要約です。リンク移動・検索・図の操作・モック操作は含みません。全要件と操作契約は、通常ブラウザー用の資料一式で確認してください。</p>
<section class="panel">
<h2>読む順番</h2>
<p>まず次の流れをつかみ、通常ブラウザー版で担当する業務・画面を選びます。設計担当者は「標準の章立て」「要件ID・操作」から根拠へ進みます。</p>
<ol class="steps">${introFlow.map(([,
                  t,
                  d])=>`<li>
<div class="step-title">${E(t)}</div>
<p>${E(d)}</p>
</li>`).join('')}</ol>
</section>${panel('利用者ごとの役割',
                  `<ul>
<li>会計課給与班: 全局の計算・確認・確定、通勤認定。</li>
<li>局担当者: 自局の勤務・申請・必要な職員情報の登録・訂正。</li>
<li>業務マスタ管理者: 単価・区分等を管理。システム管理権限とは分離。</li>
<li>本人機能: 将来追加。初回の実装済み機能には含めません。</li>
</ul>
<p>実効ロールの取得・物理権限の実装方式は未設定です。</p>`)}${panel('確定している重要な境界',
                  `<ul>
<li>勤務条件などは登録→確認待ち→給与班確定。必要時に差戻し。未確認の情報は給与確定に使いません。</li>
<li>通勤は提出⇄差戻し→認定。認定済み情報を計算が直接参照します。</li>
<li>人給連携は3タブ。Excelを人給へ渡し、戻りCSVと最新版の計算結果を照合します。</li>
<li>支給回全体の最新照合が差分ゼロの場合だけ給与班が確定。表示対象だけに判定を狭めません。</li>
<li>支払済み結果は変更せず、追給・返納を別に処理します。</li>
</ul>`)}${panel('これから決めること',
                  `<ul>
<li>D9以降の計算式、端数、符号等。</li>
<li>人給CSVの照合キー・出力行との対応、I8のエラー取得方法。</li>
<li>正式テーブル・列型、保存・復旧、同時更新の方式。</li>
<li>実効権限、本番運用、規模・性能、保存期間、総合試験D-07。</li>
</ul>
<p>未設定の要件を、一般的な例や仮の画面から補っていません。</p>`)}${panel('画面の見取り図',
                  `<ul>${model.screens.map(s=>`<li>
<strong>${E(s.id)} ${E(s.name)}</strong>
<br>${E(s.summary)}</li>`).join('')}</ul>
<p>将来画面の正式IDは未確定です。外部人給への移動は利用者によるシステム切替で、自動の画面遷移ではありません。</p>`)}${panel('標準の章立てと記載状況',
                  `<p>業務要件／機能要件／非機能要件の3章。既存140見出しを維持し、原本の別スタイルで見つかった8見出しと、下位記入項目を補完しています。</p>
<p>本文対象109項目: 記載済み${counts.documented}、一部設定${counts.partial}、要件未設定${counts.unset}。既存正本にある${sectionSupplements.sections.length}節の確定事項を補足した後の件数です。この数字は実装率・検証率ではありません。</p>`)}${panel('詳細版の閲覧方法',
                  `<p>PCでは配布ZIPを展開し、viewer/docs/requirements/standard-template/index.htmlを通常ブラウザーで開きます。リポジトリではdocs/requirements/standard-template/index.htmlです。iPhoneでは閲覧を許可したWeb置場のURLをSafariで開く方式が適しています。</p>
<p>今回の資料は未公開です。Web配置と閲覧範囲の決定は別途必要です。Quick Lookの機能やiPhone実機動作を確認済みとはしていません。</p>`)}<p class="source-info">正本: GitHub Markdown。基準: PR136 ${HEAD}。モデル: ${model.metadata.source_sha} / ${model.metadata.updated}。2026-10-07給与確定要件・2026-10-08人給決定を優先。DOT-001の承認A・引継ぎLive38観測を反映。正式P/Hはrun 38049776822で採取済み（旧v25 guardでrun FAIL）。選定自動E2E・最終照合は未実施。非正本・確認用。</p>
</main>`;
                  outputs.set(`${dir}/${cur}`,
                  `<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>非常勤給与 業務と要件の要約</title>
<style>${css}</style>
</head>
<body>${body}</body>
</html>`);
                }
                const portalData={
                  metadata:{
                    request_id:'DOT-002',
                    task_id:'PAY-REQ-HTML-REWORK-001',
                    version:baselineData.metadata.version,
                    date:DATE,
                    source_commit:HEAD,
                    app_publication:publication,
                    review_model_commit:model.metadata.source_sha,
                    review_model_date:model.metadata.updated,
                    canonical:'Selected current Markdown; prior P/H-unavailable state retained as history',
                    live38_included:true, live38_scope:"DOT-001 handoff observation only; formal P/H captured, legacy v25 guard failed, E2E and reconciliation NOT_RUN",
                    publication:'Not published'
                  }
                  ,
                  coverage:counts,
 baseline_coverage:{headings:140,content:109,documented:10,partial:38,unset:61},
 applied_supplement_ids:sectionSupplements.sections.map(item=>item.id),
 supplemental_heading_coverage:{content:8,documented:0,partial:7,unset:1},
 template_section_mapping:(sectionSupplements.template_sections||[]).map(item=>({id:item.id,state:item.state,source_refs:item.source_refs,href:`template-sections/${item.id}.html`})),
                  section_mapping:data.sections.map(s=>({
                    id:s.id,
                    source_outline_id:template?.core_heading_coverage?.find(x=>x.id===s.id)?.source_outline_id||s.id,
                    title:s.title,
                    state:s.state,
                    operation_ids:sectionOps[s.id]||[],
                    workflow_ids:sectionFlows[s.id]||[],
                    screen_ids:sectionScreens[s.id]||[],
                    source_paths:s.sources,
                    href:sectionUrl(s.id)
                  }
                  )),
                  requirements:reqEntities,
                  sources:sourceManifest,
                  states:{
                    documentation:['記載済み',
                    '一部設定・要件未設定あり',
                    '要件未設定'],
                    decision:['確定',
                    '提案',
                    '未決',
                    '既存記録'],
                    implementation:'Not reassessed by this HTML task',
                    verification:'Power Apps not tested by this HTML task'
                  }
                }
                ;
                outputs.set(`${dir}/portal-data.json`,
                JSON.stringify(portalData,
                null,
                2)+'\n');
                for(const name of ['portal.css',
                'portal.js',
                'context.js'])outputs.set(`${dir}/assets/${name}`,
                fs.readFileSync(`scripts/review/requirements_portal/${name}`,
                'utf8'));
                // Compatibility: old index.html#section-X links continue to resolve with the same meaning.
                let index=outputs.get(`${dir}/index.html`);
                index=index.replace('</main>',
                `<details class="wrap">
<summary>以前の章・節リンク</summary>
<div class="chips">${data.sections.map(s=>`<a id="section-${s.id}" href="sections/${s.id}.html#section-${s.id}">${E(s.id+' '+s.title)}</a>`).join('')}</div>
</details>
</main>`);
                outputs.set(`${dir}/index.html`,
                index);
                let bad=false;
                for(const [p,
                raw]of outputs){
                  const s=typeof raw==='string'&&p.endsWith('.html')?raw.replace(/>\s*</g,
                  '>\n<').replace(/[ \t]+$/gm,''):raw;
                  if(process.argv.includes('--check')){
                    if(!fs.existsSync(p)||(Buffer.isBuffer(s)?!fs.readFileSync(p).equals(s):fs.readFileSync(p,
                    'utf8')!==s)){
                      console.error('Mismatch:',
                      p);
                      bad=true;
                    }
                  }
                  else{
                    fs.mkdirSync(path.dirname(p),
                    {
                      recursive:true
                    }
                    );
                    fs.writeFileSync(p,
                    s);
                  }
                }
                if(bad)process.exit(1);
                console.log(`${outputs.size} files ${process.argv.includes('--check')?'verified':'generated'}; ${ids.length} requirement IDs, ${counts.headings} legacy headings, ${reqEntities.filter(r=>!r.source_resolved).length} unresolved source references.`);
