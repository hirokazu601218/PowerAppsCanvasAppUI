"""Build a self-contained Dataverse HTML resource. No environment URL or data embedded."""
from pathlib import Path
from html import escape
import json
ROOT=Path(__file__).resolve().parent
def f(key,cls=''):
 return f'<span class="value {cls}" data-field="{key}"></span>'
def table(cols,rows,cls=''):
 return '<table class="'+cls+'"><colgroup>'+''.join('<col style="width:'+str(x*100/sum(cols))+'%">' for x in cols)+'</colgroup>'+rows+'</table>'
def td(s='',attrs=''): return '<td '+attrs+'>'+s+'</td>'
def tr(s,cls=''): return '<tr class="'+cls+'">'+s+'</tr>'
css='''
@page{size:A4 landscape;margin:5mm}
*{box-sizing:border-box}html,body{margin:0;padding:0;color:#000;background:#fff;font-family:"Yu Gothic","Meiryo","Noto Sans CJK JP",sans-serif;font-size:8pt}
[hidden]{display:none!important}.page{width:287mm;height:199mm;page-break-inside:avoid;break-inside:avoid;position:relative;padding:1mm 0}.page+.page{break-before:page;page-break-before:always}
h1{text-align:center;font-size:16pt;letter-spacing:3mm;margin:1mm 0 2mm;font-weight:600}.formno{position:absolute;top:5mm;left:2mm;font-size:9pt}
table{break-inside:avoid;page-break-inside:avoid;border-collapse:collapse;width:100%;table-layout:fixed;border:0.45mm solid #000}td,th{border:0.22mm solid #000;padding:0.4mm 0.7mm;vertical-align:middle;font-weight:400;overflow-wrap:anywhere;line-height:1.25}th{text-align:center}td{position:relative}.value{display:block;width:100%;font-size:8pt;font-weight:500;white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.2;max-height:100%;min-height:1em}
.inline{display:inline-block;width:auto;min-width:10mm;vertical-align:bottom}.small{font-size:8pt}.num{text-align:right}.center{text-align:center}.vert{text-align:center;line-height:1.3}.vertical-label{position:absolute;top:50%;left:0;right:0;transform:translateY(-50%)}.diag{background:linear-gradient(to top right,transparent calc(50% - .15mm),#000 50%,transparent calc(50% + .15mm))}.gap{margin-top:1.2mm}.titlebar{border:.45mm solid #000;border-bottom:0;padding:1mm 2mm;font-size:9pt;height:5.5mm}
.head{height:16mm}.head td{height:5mm}.routes thead tr{height:6mm}.routes tbody tr{height:11mm}.routes .value{height:9mm}.routes .period .value,.routes .section .value{height:4mm}.routes tfoot tr{height:7mm}.routes tfoot .value{height:5mm}.routes .remarks .value{font-size:8pt}.auto td{height:13mm}.combined td{height:10mm}
.shinkansen thead tr{height:6mm}.shinkansen tbody td{height:7mm}.shinkansen tfoot td{height:5mm}.parking thead td{height:5mm;font-size:7.5pt}.parking tbody td{height:5mm}.parking tfoot td{height:5mm}.parking-bottom td{height:8mm}.cap td{height:12mm}.monthly th{height:5mm;font-size:7pt}.monthly td{height:8mm}.monthly .value{height:6mm;font-size:8pt}.decision td{height:9mm}.decision .rules{font-size:7.5pt;line-height:1.45;padding:1mm 2mm}.refund{border:0}.refund td,.refund th{font-size:7pt;height:6mm}.refund th{height:11mm}.last td{height:13mm}
.toolbar{padding:12px 20px;background:#f0f4f8;color:#172b4d;position:sticky;top:0;z-index:2;border-bottom:1px solid #bcc8d4;font-size:14px}.toolbar button{padding:9px 20px;margin-right:16px;font:inherit}.toolbar p{margin:5px 0}.print-error{display:none}
@media screen{body{background:#e8edf1}#report{width:287mm;margin:8mm auto}.page{background:#fff;box-shadow:0 1px 8px #aaa;margin-bottom:8mm}.toolbar{min-width:320px}.page{padding-left:0;padding-right:0}}
@media print{.toolbar,noscript{display:none}#report{margin:0}.page{margin:0;box-shadow:none}body:not(.ready) #report{display:none!important}body:not(.ready) .print-error{display:block;font-size:14pt;padding:15mm}}
'''
header=table([21,18,30,14,17],tr(td('氏名 '+f('name'))+td('職員番号 '+f('staff'))+td('組織・所属 '+f('org'))+td('事実発生年月日')+td(f('event')))+tr(td('□ 回数券等を使用して利用する交通機関等がある職員（交替制勤務等）','colspan="2"')+td('（算出式　　　　　　　　　　　　　　　　）','rowspan="2"')+td('届出年月日')+td(f('submitted')))+tr(td('1箇月当たりの平均通勤所要回数　　　　　　　　回','colspan="2"')+td('受理年月日')+td(f('received'))),'head')
rh='<thead>'+tr('<th rowspan="2">区分</th><th rowspan="2">順路</th><th colspan="2">算出の基礎となる普通交通機関等</th><th rowspan="2">定期券<br>回数券<br>その他の別</th><th colspan="2">運賃等の額の算出基礎</th><th colspan="2">運賃等相当額</th><th rowspan="2">1箇月当たりの<br>運賃等相当額</th><th rowspan="2">普通交通機関等の<br>認定期間</th><th rowspan="2">支給月</th><th rowspan="2">備考</th>')+tr('<th>普通交通機関等の名称</th><th>利用区間</th><th>回数券<br>その他</th><th>定期券</th><th>回数券<br>その他</th><th>定期券</th>')+'</thead><tbody>'
for i in range(1,9):
 def rf(k): return f('r'+str(i)+'_'+k) if i<=4 else ''
 cells=td('<span class="vertical-label">'+'<br>'.join('普通交通機関等利用者')+'</span>','rowspan="8" class="vert"') if i==1 else ''
 cells+=td(str(i),'class="center"')+td(rf('operator'))+td(rf('from')+rf('to'),'class="section"')+td(rf('tickettype'))+td(rf('ticketbasis'),'class="num"')+td(rf('distancekm'),'class="num"')+td(rf('ticketamount'),'class="num"')+td(rf('passamount'),'class="num"')+td(rf('amount'),'class="num"')+td(rf('recognitionstart')+rf('passmonths'),'class="period"')+td(rf('paymonth'),'class="center"')+td(rf('remarks'),'class="remarks"')
 rh+=tr(cells)
rh+='</tbody><tfoot>'+tr(td('1箇月当たりの運賃等相当額の合計額','colspan="9" class="num"')+td(f('total'),'class="num"')+td('','colspan="3" class="diag"'))+'</tfoot>'
routes=table([2,2,9,10,6,8,7,8,8,8,12,5,15],rh,'routes')
auto=table([52,6,12,11,19],tr(td('自動車等の額<br>（法第12条第2項第2号の額）（自動車等の使用距離　　　　　　km）')+td()+td()+td('','class="diag"')+td()),'auto gap')
combined=table([26,26,6,42],tr(td('普通交通機関等と自動車等の併用者<br>規則第8条の4　□第1号　□第2号　□第3号')+td('1箇月当たりの運賃等相当額と<br>自動車等の額の合計額')+td()+td('','class="diag"')),'combined gap')
p1='<section class="page" aria-label="通勤手当認定簿 1ページ目"><span class="formno">別紙第2</span><h1>通勤手当認定簿</h1>'+header+routes+auto+combined+'</section>'
sh='<thead>'+tr('<th rowspan="2">順路</th><th colspan="2">算出の基礎となる新幹線鉄道等</th><th rowspan="2">定期券<br>回数券<br>その他の別</th><th colspan="2">特別料金等の額の算出基礎</th><th colspan="2">特別料金等相当額</th><th rowspan="2">1箇月当たりの<br>特別料金等相当額</th><th rowspan="2">新幹線鉄道等の<br>認定期間</th><th rowspan="2">支給月</th><th rowspan="2">備考</th>')+tr('<th>新幹線鉄道等の名称</th><th>利用区間</th><th>回数券その他</th><th>定期券</th><th>回数券その他</th><th>定期券</th>')+'</thead><tbody>'
for i in range(1,5): sh+=tr(td(str(i),'class="center"')+td()*11)
sh+='</tbody><tfoot>'+tr(td('1箇月当たりの特別料金等相当額の合計額','colspan="8" class="num"')+td()+td('','colspan="3" class="diag"'))+'</tfoot>'
sh=table([2,9,10,7,8,8,8,8,9,12,6,13],sh,'shinkansen')
park='<thead>'+tr(td('使用<br>駐車場','rowspan="2" class="center"')+td('算出の基礎となる駐車場等','colspan="2" class="center"')+td('1箇月当たりの駐車場等の料金に相当する額','rowspan="2" class="center"')+td('1箇月当たりの平均通勤所要回数','rowspan="2" class="center small"')+td('備考（回数券等の場合の駐車場等の料金の算出基礎等）','rowspan="2" class="center"'))+tr(td('駐車場等の利用形態','class="center"')+td('駐車場等の料金','class="center"'))+'</thead><tbody>'
for i in range(1,4): park+=tr(td(str(i),'class="center"')+td()*5)
park+='</tbody><tfoot>'+tr(td('1箇月当たりの駐車場等の料金に相当する額の合計額','colspan="3"')+td()+td('','colspan="2" class="diag"'))+'</tfoot>'
park=table([5,10,12,12,8,53],park,'parking')
pb=table([23,8,10,5,10,44],tr(td('駐車場等に係る通勤手当の額（上限5,000円）')+td()+td('駐車場等の認定期間')+td()+td('決定事項<br>（手当額の決定）')+td('規則第18条　□第1号イ　□第1号ロ<br>□第1号ハ（1箇月当たりの平均通勤所要回数　　回） □第2号')),'parking-bottom')
cap=table([27,26,47],tr(td('1箇月当たりの運賃等相当額、自動車等の額、1箇月当たりの特別料金等相当額の合計額及び駐車場等に係る通勤手当の額の合計額が150,000円を超えるとき','class="small"')+td('150,000円 × ［　　 箇月 ］＝　　　 円')+td('','class="diag"')),'cap gap')
monthcols=[13]+[5]*12+[17,10]
mr='<thead>'+tr('<th class="diag"></th>'+''.join('<th>'+str(int(m))+'月</th>' for m in ['04','05','06','07','08','09','10','11','12','01','02','03'])+'<th>各庁の長の確認・決定欄</th><th>備考</th>')+'</thead>'+tr(td('支　給　額','class="center"')+''.join(td(f('month'+m),'class="num"') for m in ['04','05','06','07','08','09','10','11','12','01','02','03'])+td('令和　　年　月　日<br>官職<br>氏名','class="small"')+td())
monthly=table(monthcols,mr,'monthly gap')
refund=table([3,17,10,20,21,14,15],tr('<th></th><th>返納事由<br>規則第21条第1項</th><th>返納事由<br>発生年月</th><th>返納対象普通交通機関等<br>及び新幹線鉄道等</th><th>払戻金相当額の算出基礎</th><th>払戻金相当額</th><th>備考</th>')+''.join(tr(td(str(i),'class="center"')+td('□第1号　□第3号<br>□第2号　□第4号')+td()*5) for i in range(1,4)),'refund')
rules='法第12条第1項　該当・非該当<br>　□該当　（□ 規則第5条）<br>　□非該当<br>理由（　　　　　　　　　　　　　　　）<hr>手当額の決定<br>法第12条第2項　□第1号　□第2号　□第3号<br>　□規則第8条の3（通勤所要回数　　回）<br>□規則第8条の4　□第1号　□第2号　□第3号<br>法第12条　□第3項　□第4項　□第5項<br>　（□規則第15条第1項第3号・第4号）'
decision=table([2,28,70],tr(td('<span class="vertical-label">'+'<br>'.join('決定事項')+'</span>','class="vert" rowspan="2"')+td(rules,'rowspan="2" class="rules"')+td(refund,'style="padding:0"'))+tr(td(table([53,20,27],tr(td('1箇月当たりの運賃等相当額及び1箇月当たりの特別料金等相当額が150,000円を超えている場合<br>規則第21条第2項第2号の月数と人事院の定める額（算出基礎）','class="small"')+td('（算出基礎）')+td('　　　　　　　　　円')),'last'),'style="padding:0"')),'decision gap')
p2='<section class="page" aria-label="通勤手当認定簿 2ページ目"><div class="titlebar">□ 新幹線鉄道等利用者</div>'+sh+'<div class="titlebar gap">□ 駐車場等利用者</div>'+park+pb+cap+monthly+decision+'</section>'
body='<div class="toolbar"><button id="print" disabled>印刷／PDF保存</button><strong>通勤手当認定簿 HTML版 1.01</strong><p id="status" role="status" aria-live="polite">認定データを読み込んでいます…</p><p>氏名・所属は現在の職員マスタ。未定義欄は空欄です。保存前に対象と内容を確認してください。</p></div><noscript>JavaScriptが無効のため帳票を表示できません。</noscript><p class="print-error">帳票を印刷できません。画面のエラーを確認してください。</p><main id="report" hidden>'+p1+p2+'</main>'
html='<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><title>通勤手当認定簿</title><style>'+css+'</style></head><body>'+body+'<script>'+ROOT.joinpath('report.js').read_text()+'</script></body></html>'
ROOT.joinpath('commute-ledger.html').write_text(html)
ROOT.joinpath('layout.html').write_text('<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>固定架空データ・レイアウト検証</title><style>'+css+'</style></head><body class="ready">'+body.replace(' id="report" hidden',' id="report"')+'</body></html>')
print('Built',len(html),'characters')
