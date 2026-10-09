"""Screen-specific static wireframes. No network or real business transaction.
Every source description is emitted as HTML; JS only enhances mock interactions.
"""
from html import escape as E
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[2]

# name, UI type, requiredness, editable mode, fictional value. Physical schemas stay undecided.
FIELDS={
'SCR-002':{
'基本情報':[
('職員番号','文字列12桁','給与対象時必須','参照','009900009901'),('氏名','文字列','詳細検証未決','編集候補','架空 花子'),('氏名カナ','文字列','未決','編集候補','カクウ ハナコ'),('所属','候補選択','給与対象時必要','編集候補','架空総務局'),('住所','文字列','未決','編集候補','架空市例示町1-2-3'),('採用日','日付','採用前空欄可／計算対象時必須','編集候補','2026-04-01'),('在籍状態','候補選択','未決','参照','在籍'),('給与支払グループ','文字列','所属から決定','参照','架空総務局')],
'勤務条件':[
('適用開始日','日付','有効期間に必要','編集候補','2026-04-01'),('適用終了日','日付','終了未定時の検証未決','編集候補','2027-03-31'),('発令事由','候補選択','未決','編集候補','任期更新'),('給与区分','候補選択','日額／時間額','編集候補','日額'),('単価','数値','給与計算に必要','マスタから選択','9750'),('一日当たり勤務時間','数値','給与計算に必要／型精度未決','編集候補','7.75'),('個別予算','候補選択','任意：所属既定を上書き','編集候補','架空予算A'),('確認状態','候補選択','確認前は給与確定不可','参照','確認待ち')],
'通勤':[
('認定ID','文字列','選択時必要','参照','TK-990001'),('認定期間開始','日付','認定期間に必要','編集候補','2026-04-01'),('認定期間終了','日付','期間で終了を管理','編集候補','2026-09-30'),('状態','候補選択','提出／差戻し／認定','参照','認定'),('経路番号','整数','経路の識別','参照','1'),('経路','文字列','詳細検証未決','編集候補','架空駅A → 架空駅B'),('支給方式','候補選択','経路ごと：定期／IC','編集候補','定期券前払い'),('定期額・IC運賃','数値','方式による／精度未決','編集候補','6250')],
'社会保険':[
('保険区分','候補選択','保険ごとの登録','編集候補','健康保険'),('加入状況','候補選択','未確認／加入／非加入','編集候補','加入'),('資格取得日','日付','資格に応じて必要','編集候補','2026-04-01'),('資格喪失日','日付','終了条件は未決','編集候補',''),('控除開始','年月','資格日と区別','編集候補','2026-04'),('控除終了','年月','資格日と区別','編集候補',''),('等級','文字列','詳細検証未決','編集候補','例示等級'),('標準報酬月額','数値','詳細検証未決','編集候補','200000'),('登録控除額','数値','未確認時は確定不可','編集候補','10000'),('決定結果確認','文字列','給与影響前に給与班確認','参照','確認待ち')],
'税固定控除':[
('所得税区分','候補選択','詳細検証未決','編集候補','甲欄'),('扶養控除人数','整数','家族個別情報は対象外','編集候補','0'),('適用開始日','日付','履歴期間','編集候補','2026-04-01'),('適用終了日','日付','検証未決','編集候補','2027-03-31'),('固定控除項目','候補選択','項目別の行','編集候補','例示控除'),('固定控除額','数値','精度・特殊月未決','編集候補','1000'),('住民税控除年月','年月','職員×月の行','編集候補','2026-09'),('住民税額','数値','未確認時は確定不可','編集候補','5000'),('確認状態','文字列','給与班確認前は使用不可','参照','確認待ち')],
'給与簿':[]},
'SCR-003':{'勤務時間報告':[
('所属','候補選択','必須','所属範囲内','架空総務局'),('勤務月','年月','必須','入力中のみ','2026-09'),('報告状態','文字列','入力中／報告済み','参照','入力中'),('職員番号','文字列12桁','必須','入力中のみ','009900009901'),('勤務日数','数値','検証範囲未決','入力中のみ','20'),('通勤日数','数値','検証範囲未決','入力中のみ','18'),('超過勤務時間','小数3桁','必要に応じ登録','入力中のみ','2.125'),('欠勤時間','整数時間','必要に応じ登録','入力中のみ','1'),('備考','文字列','任意','入力中のみ','架空の勤務実績')]},
'SCR-004':{'支給率':[
('職員番号','文字列12桁','必須','参照','009900009901'),('対象期間開始','日付','必須','編集候補','2026-04-01'),('対象期間終了','日付','必須','編集候補','2026-09-30'),('期末支給率','数値','別々に登録／精度未決','編集候補','1.000'),('勤勉支給率','数値','別々に登録／精度未決','編集候補','0.900')]},
'SCR-006':{'業務マスタ':[
('マスタ区分','候補選択','選択必須','業務管理者','日額単価'),('名称','文字列','検証未決','業務管理者','例示単価A'),('金額・区分値','文字列','検証未決','業務管理者','9750'),('適用開始日','日付','有効期間','業務管理者','2026-04-01'),('適用終了日','日付','終了で履歴保持','業務管理者','2027-03-31'),('使用状態','候補選択','使用／停止','業務管理者','使用')]},
'SCR-007':{'差額・回収':[
('職員番号','文字列12桁','対象選択必須','参照','009900009901'),('元の支給回','文字列','支払済み結果参照','参照','例示2026年8月通常'),('対象過去月','年月','月別内訳保持','参照','2026-07'),('差額','数値','算定式未決','参照','1000'),('調整理由','文字列','調整記録に必要','編集候補','勤務条件の誤登録訂正'),('処理者','文字列','記録に必要','参照','架空給与担当'),('回収方法','候補選択','給与相殺／納入告知書・併用','編集候補','給与相殺'),('回収済額','数値','回収実績から管理','参照','0'),('残額','数値','完了・過回収の条件未決','参照','1000')]}}


def wireframe_pages(model,page,table,link,tag,reqs,sources_html):
    screens=model['screens']; ops=model['operations']; results={}; scmap={s['id']:s for s in screens}
    def op(screen, pattern='', destination=None):
        candidates=[o for o in ops if o['screen_id']==screen]
        if destination: candidates=[o for o in candidates if o['destination_screen_id']==destination]
        if pattern:
            matches=[o for o in candidates if re.search(pattern,o['title']+' '+o['control'],re.I)]
            if matches:return matches[0]
        return candidates[0] if candidates else None
    def button(screen,label,action,pattern='',extra='',primary=False):
        action_ids={
          'SCR-002':{'edit':'OP-002-EDIT','save':'OP-002-SAVE','read':'OP-002-READMODE','font':'OP-002-FONT','sidebar':'OP-002-SIDEBAR','search':'OP-002-SEARCH','clear':'OP-002-CLEAR','ledger-range':'OP-002-LEDGER','submit':'OP-F-SUBMIT','return':'OP-E-RETURN','certify':'OP-F-CERTIFY','staff-confirm':'OP-E-CONFIRM','decision-register':'OP-G-REGISTER','decision-confirm':'OP-G-CONFIRM','adoption-cancel':'OP-AD-CANCEL','new-history':'OP-E-HISTORY','correct-history':'OP-E-CORRECT','pending':'OP-E-SUBMIT','commute-change':'OP-F-CHANGE','commute-end':'OP-F-END','commute-nopay':'OP-F-NOPAY','assign-number':'OP-AD-NUMBER','upstream-change':'OP-AD-CHANGE'},
          'SCR-003':{'edit':'OP-003-EDIT','save':'OP-003-SAVE','read':'OP-003-READMODE','add-row':'OP-003-ROWEDIT','remove-row':'OP-003-ROWEDIT','attendance-import':'OP-003-IMPORT','report':'OP-003-REPORT','reopen':'OP-003-RETURN','recover-import':'OP-003-RECOVER'},
          'SCR-004':{'edit':'OP-004-RATES','save':'OP-004-RATES','read':'OP-004-RATES'},
          'SCR-005':{'trial':'OP-005-RECALC'},
          'SCR-006':{'edit':'OP-006-RULE','save':'OP-006-RULE','read':'OP-006-RULE','master-new':'OP-006-RULE','master-stop':'OP-006-END','report-month':'OP-006-MONTH'},
          'FUT-IMPORT':{'candidate-import':'OP-IMPORT-VALIDATE','candidate-accept':'OP-IMPORT-APPLY','candidate-review':'OP-IMPORT-APPLY'},
          'FUT-JLINK':{'target-visible':'OP-JLINK-TARGET','target-all':'OP-JLINK-TARGET','calculate':'OP-PAY-CALCULATE','finalize':'OP-JLINK-CONFIRM','mark-paid':'OP-PAY-PAID','apply-am':'OP-JLINK-AM','export-review':'OP-JLINK-EXPORT','ledger-import':'OP-JLINK-IMPORT','reconcile':'OP-JLINK-RECONCILE','reexport':'OP-JLINK-REEXPORT','period':'OP-PAY-PERIOD','adjust':'OP-PAY-ADJUST'},
          'SCR-007':{'retro-review':'OP-RETRO-CONFIRM','retro-confirm':'OP-RETRO-CONFIRM','recovery':'OP-REPAY-RECORD','retro-calculate':'OP-RETRO-CALCULATE','repay-method':'OP-REPAY-METHOD'},
          'EXT-COMMUTE':{'print-guide':'OP-F-PDF'}}
        exact=action_ids.get(screen,{}).get(action)
        if screen=='SCR-002' and action=='return' and '通勤' in pattern: exact='OP-F-RETURN'
        o=next((x for x in ops if x['id']==exact),None) if exact else None
        o=o or op(screen,pattern or label)
        attrs=(f'data-operation-id="{E(o["id"])}" ' if o else '')
        role_names=' '.join(o['roles']) if o else ''
        allowed=[]
        if '給与班' in role_names:allowed.append('payroll')
        if '局担当' in role_names:allowed.append('bureau')
        if '業務マスタ' in role_names:allowed.append('master')
        if 'ログイン' in role_names or '同一部署' in role_names:allowed+=['payroll','bureau','master','system']
        if '管理者' in role_names and '業務マスタ' not in role_names:allowed+=['master','system']
        attrs+=f'data-allowed-roles="{E(" ".join(sorted(set(allowed))))}" '
        return f'<button type="button" {attrs}data-action="{E(action)}" class="{"primary" if primary else "secondary"}" {extra}>{E(label)}</button>'
    def nav(screen,target,label,current,pattern='',extra=''):
        o=op(screen,pattern,destination=target)
        attrs=(f'data-operation-id="{E(o["id"])}" ' if o else '')+'data-mock-nav '+extra
        if target in ('FUT-IMPORT','FUT-JLINK','SCR-007'):attrs+=' data-entry-roles="payroll"'
        return link('wireframes/'+target.lower()+'.html',label,current,attrs)
    def fields(screen,tab):
        rows=FIELDS.get(screen,{}).get(tab,[]); out='<div class="field-grid">'
        for idx,(name,kind,required,edit,value) in enumerate(rows):
            fid=f'field-{screen.lower()}-{list(FIELDS.get(screen,{})).index(tab)}-{idx}'
            typ='date' if kind=='日付' else 'month' if kind=='年月' else 'text'
            editable=edit!='参照'
            out+=f'<label class="field-cell" for="{fid}"><span>{E(name)}</span><input id="{fid}" type="{typ}" value="{E(value)}" data-editable="{str(editable).lower()}" readonly aria-describedby="{fid}-note"></label>'
        out+='</div>'
        return out
    def statetable(screen,current):
        rows=[]
        for tab,fs in FIELDS.get(screen,{}).items():
            for idx,(name,kind,required,edit,value) in enumerate(fs):
                fid=f'field-{screen.lower()}-{list(FIELDS.get(screen,{})).index(tab)}-{idx}'
                rows.append([E(tab),f'<span id="{fid}-note">{E(name)}</span>',E(kind)+'（UI例。物理型未決）',E(required),E(edit),tag('提案')+' 項目名は確定要件参照。個別制約は未決'])
        if screen=='SCR-002':
            ledger=json.loads((ROOT/'config/dataverse/payrollledger-columns.json').read_text())['fields']
            for field in ledger:
                rows.append(['給与簿',E(field['display_name']),E(field.get('kind','未定義'))+'（既存表示定義）',E(field.get('source_required','未決')),'常に読み取り専用',sources_html(model,['SRC-LEDGER-FIELDS'],current)+'。変更後CSVの物理設計は別途。'])
        return table(['区分','項目','型','必須性','編集可否','根拠・未決'],rows,'項目・入力部品のレビュー台帳') if rows else ''
    def standard_context(screen):
        return '''<div class="mock-context"><div><strong>選択職員</strong><br><span data-context-staff>009900009901 架空 花子</span></div><div><strong>対象勤務月</strong><br><span data-context-month>2026/09</span></div><div><strong>支給回</strong><br><span data-context-run>例示2026年10月通常</span></div><div><strong>状態</strong><br><span data-mode-label>読み取り</span></div></div>'''
    def toolbar(screen,edit=True):
        out='<div class="mock-toolbar">'
        if edit: out+=button(screen,'編集モード','edit','編集')+button(screen,'保存','save','保存',extra='data-write-control disabled',primary=True)
        out+=button(screen,'読み取りモード','read','読取|読み取り')+'</div>'
        return out
    def statusblock():return '<div class="mock-status" role="status" aria-live="polite" data-mock-status>表示内容は架空の例です。</div>'
    cur='wireframes/index.html'
    body='<p>PCの業務画面構成を確認するワイヤーフレームです。資料そのものはスマートフォンで読めます。PC画面例は狭幅では横スクロールし、モバイルアプリ設計と混同しません。</p>'+table(['画面','区分','確認すること'],[[link('wireframes/'+s['id'].lower()+'.html',s['id']+' '+s['name'],cur),tag(s['status']),E(s['summary'])] for s in screens],'クリックできる画面一覧')
    results[cur]=page(model,cur,'④ ワイヤーフレーム一覧',body,'wireframes/index.html')
    for s in screens:
        sid=s['id']; cur='wireframes/'+sid.lower()+'.html'; content=''; tabs=s.get('tabs',[])
        intro=f'<p>{tag(s["status"])} {E(s["summary"])}</p><p>{link("operations/"+sid.lower()+".html","この画面の操作定義",cur)} / {link("design-notes.html#mock-design","設計・状態の注記",cur)}</p>'
        # reviewer controls are deliberately outside user-facing operational canvas
        controls='''<section class="review-controls" aria-label="レビュー用の条件切替"><p>レビュー用の条件切替（業務画面外）。権限変更・実データ更新は行いません。操作で現れる文言・モーダル配置は提案です。</p><label>役割<select data-review-role><option value="payroll">給与班</option><option value="bureau">局担当者</option><option value="master">業務マスタ管理者</option><option value="system">システム管理者</option><option value="self">職員本人（将来）</option></select></label><label>状態<select data-review-state><option value="normal">通常</option><option value="initial">初期・未選択</option><option value="zero">検索・履歴0件</option><option value="loading">処理中</option><option value="error">エラー</option><option value="readonly">報告済み・読み取り</option><option value="difference">照合差分あり</option><option value="clean">全体差分ゼロ</option><option value="stale">計算更新後</option><option value="unknown">未知職員あり</option><option value="paid">支払い済み</option></select></label><label>次の模擬保存<select data-save-result><option value="success">成功</option><option value="failure">失敗</option></select></label><button type="button" data-review-reset>初期化</button></section>'''
        header_target='SCR-002' if sid=='EXT-COMMUTE' else 'FUT-JLINK' if sid=='EXT-JINKYU' else 'SCR-001'
        header_label='通勤へ戻る' if sid=='EXT-COMMUTE' else '人給連携へ戻る' if sid=='EXT-JINKYU' else 'ホーム'
        header='<header class="mock-header"><div><h2>'+E(s['name'])+'</h2><span class="context-name">架空総務局 · 架空担当者</span></div><div class="header-actions">'+(nav(sid,header_target,header_label,cur) if sid!='SCR-001' else '')+('<span data-acquired-time>取得日時：2026/10/09 09:00（表示例）</span>' if sid=='SCR-002' else '')+'<span>'+E(sid if sid.startswith('SCR-') and sid!='SCR-007' else '画面例')+'</span></div></header>'
        if sid=='SCR-001':
            content='<p>今日の業務を選んでください。</p><div class="mock-grid">'
            for dest,label in [('SCR-002','職員マスタ検索'),('SCR-003','勤務時間報告'),('SCR-004','期末勤勉支給率登録'),('SCR-006','メンテナンス')]:
                content+=nav(sid,dest,label,cur,extra='data-master-entry' if dest=='SCR-006' else '')
            content+='</div><div class="mock-secondary">'
            if 'CUR-IMPORT-POC' in scmap:content+=nav(sid,'CUR-IMPORT-POC','PoCデータ一括取込',cur)
            for dest,label in [('FUT-IMPORT','データ一括取込み'),('FUT-JLINK','人給連携'),('SCR-007','遡及差額・返納')]:
                if dest in scmap:content+=nav(sid,dest,label,cur)
            content+='</div>'+statusblock()
        elif sid=='SCR-002':
            content=nav(sid,'FUT-JLINK','人給連携へ戻る',cur,extra='data-return-jlink')+toolbar(sid)+statusblock()+ '<div class="mock-toolbar">'+nav(sid,'SCR-005','支給明細画面',cur)+' '+button(sid,'文字を大きく','font','文字')+' '+button(sid,'検索を閉じる','sidebar','検索')+'</div>'
            content+='<div class="mock-layout"><aside class="search-sidebar" aria-label="職員検索"><label>職員を検索<input type="search" data-operation-id="OP-002-SEARCH" data-staff-search placeholder="氏名・職員番号"></label><label>給与情報の確認<select data-pending-filter data-operation-id="OP-E-PENDING"><option>すべて</option><option>確認待ち</option></select></label>'+button(sid,'検索','search','検索',primary=True)+button(sid,'クリア','clear','クリア')+'<p data-search-count>3件</p><div data-staff-results>'
            for n,name in [('009900009901','架空 花子'),('009900009902','架空 太郎'),('009900009903','架空 他局子')]:
                content+=f'<button type="button" class="staff-row" data-action="staff" data-staff="{n}" data-bureau="{'other' if n.endswith('03') else 'own'}" data-name="{name}" aria-pressed="{str(n.endswith("01")).lower()}" data-operation-id="{E(op(sid,"選択|検索")["id"])}">{name}<small>{n}　<span>在籍</span></small><small>{'架空他局' if n.endswith('03') else '架空総務局'}</small></button>'
            content+='</div></aside><div data-staff-detail>'+standard_context(sid)+'<div class="tabs" role="tablist" aria-label="職員情報">'
            for i,t in enumerate(['基本情報','勤務条件','通勤','社会保険','税固定控除','給与簿']):content+=f'<button role="tab" type="button" id="tab-{i}" aria-controls="panel-{i}" aria-selected="{str(i==0).lower()}" data-tab="panel-{i}" data-operation-id="{E(op(sid,"タブ")["id"])}">{t}</button>'
            content+='</div>'
            for i,t in enumerate(['基本情報','勤務条件','通勤','社会保険','税固定控除','給与簿']):
                content+=f'<section class="mock-panel" id="panel-{i}" role="tabpanel" aria-labelledby="tab-{i}"><h3>{t}</h3>'
                if i not in (0,5):content+='<label>履歴を選択<select data-history data-operation-id="OP-002-HISTORY"><option>現行 2026/04/01〜2027/03/31</option><option>過去 2025/04/01〜2026/03/31</option><option>予定 2027/04/01〜</option><option>登録なし</option></select></label>'
                if t=='給与簿':
                    content+='<p>給与簿は常に読み取り専用です。</p><div class="mock-toolbar"><label>表示開始月<input type="month" value="2026-08" data-ledger-from></label><label>表示終了月<input type="month" value="2026-10" data-ledger-to></label>'+button(sid,'期間を適用','ledger-range','給与簿|表示期間')+'</div>'
                    ledger=json.loads((ROOT/'config/dataverse/payrollledger-columns.json').read_text())['fields']
                    rows=[]
                    for j,f in enumerate(ledger):
                        vals=['—','—','—']
                        if j==0:vals=['令和08年']*3
                        elif j==3:vals=['2026/08/25','2026/09/25','2026/09/30']
                        elif j==6:vals=['009900009901']*3
                        elif j in (7,8):vals=['架空値']*3
                        elif f.get('kind') in ('integer','decimal','money'):vals=['0','-100','']
                        rows.append([E(f['display_name'])]+[E(v) for v in vals])
                    content+=table(['項目','2026/08/25 通常（例示L1）','2026/09/25 通常（例示L2）','2026/09/30 追給（例示L3）'],rows,'架空給与簿：同月複数行・0・負数・空欄を保持','data-ledger-table')
                else:content+=fields(sid,t)
                if t=='通勤':content+='<div class="mock-actions">'+button(sid,'提出','submit','提出')+button(sid,'差戻し','return','通勤届を差し戻す')+button(sid,'認定','certify','認定',extra='data-payroll-only')+nav(sid,'EXT-COMMUTE','認定簿表示（別タブ）',cur,extra='target="_blank" rel="noopener" data-new-tab')+'</div>'
                if t in ('基本情報','勤務条件','社会保険','税固定控除'):content+='<div class="mock-actions">'+button(sid,'給与情報を確定','staff-confirm','確定',extra='data-payroll-only')+button(sid,'差戻し','return','差戻')+'</div>'
                if t=='基本情報':content+='<p>採用前候補の番号発行・採用取消は前工程の情報を受け取って反映します。手動で紐付ける操作は置きません。</p>'+button(sid,'前工程の変更を確認','upstream-change','前工程')
                if t in ('勤務条件','社会保険','税固定控除'):content+='<div class="mock-actions">'+button(sid,'新しい条件履歴を追加','new-history','実際の条件変更')+button(sid,'誤登録を訂正','correct-history','誤登録')+button(sid,'確認待ちにする','pending','確認待ち')+'</div>'
                if t=='通勤':content+='<div class="mock-actions">'+button(sid,'変更届を作成','commute-change','変更届')+button(sid,'認定期間の終了を確認','commute-end','認定期間')+button(sid,'一時不支給を確認','commute-nopay','一時不支給')+'</div>'
                if t in ('社会保険','税固定控除'):content+='<p>外部機関の手続きはアプリ外で行います。</p>'+button(sid,'決定結果を登録','decision-register','決定結果|登録')+button(sid,'決定結果を確定','decision-confirm','確認確定',extra='data-payroll-only')
                content+='</section>'
            content+='</div></div>'
        elif sid=='SCR-003':
            content=nav(sid,'FUT-JLINK','人給連携へ戻る',cur,extra='data-return-jlink')+standard_context(sid)+toolbar(sid)+statusblock()+fields(sid,'勤務時間報告')
            content+=table(['職員番号・氏名','勤務日数','通勤日数','超勤時間','欠勤時間','備考'],[['009900009901 架空 花子','20','18','2.125','1','例示'],['009900009902 架空 太郎','18','16','0.000','0','例示']],'所属×勤務月の職員別集計')
            content+='<div class="mock-actions">'+button(sid,'職員行を追加','add-row','追加',extra='data-write-control disabled')+button(sid,'末尾の職員行を削除','remove-row','削除',extra='data-write-control disabled')+button(sid,'Excelを取り込む','attendance-import','取込')+button(sid,'報告する','report','報告|提出',primary=True)+button(sid,'入力中に戻す','reopen','差戻|入力中',extra='data-payroll-only')+button(sid,'取込の復旧・再実行','recover-import','復旧')+'</div><p>取込処理中・報告済みは編集と提出を停止します。</p>'
        elif sid=='SCR-004':
            content=standard_context(sid)+toolbar(sid)+statusblock()+fields(sid,'支給率')+'<p>期末と勤勉の率を別々に登録します。</p>'
        elif sid=='SCR-005':
            content=standard_context(sid)+'<label>支給対象月<input type="month" value="2026-09" data-trial-month data-operation-id="OP-005-MONTH"></label><div class="mock-toolbar">'+nav(sid,'SCR-002','職員マスタ検索',cur)+button(sid,'再計算','trial','再計算')+'</div><p>画面確認用の仮例｜金額・料率・適用区分は未確定</p>'+statusblock()+'<div class="mock-summary"><span>給与支給総額<br>200,000円</span><span>− 控除額計<br>48,200円</span><span>＝ 現金支給額<br>151,800円</span></div><div class="pay-breakdown"><details open><summary data-operation-id="OP-005-DETAILS">支給の内訳（開閉）　200,000円</summary><h3>給与支給総額の内訳</h3><p>俸給支給額 193,750円 ＋ 通勤手当 6,250円 ＝ 200,000円</p><h3>俸給支給額</h3><p>固定額 195,000円 − 欠勤減額 1,250円 ＝ 193,750円</p><p>固定額：日額単価 9,750円 × 20日 ＝ 195,000円</p><p>欠勤減額：欠勤時間単価 1,250円 × 1時間 ＝ 1,250円</p><p>全日欠勤は勤務日数・欠勤減額に含めません</p><h3>通勤手当　6,250円</h3><p>毎月固定（既存試算の仮例）。変更後の初回対象方式は定期券前払い／ICです。</p><p>適用期間：2026/04/01〜2026/09/30</p></details><details open><summary data-operation-id="OP-005-DETAILS">控除の内訳（開閉）　48,200円</summary><h3>控除額計の内訳（当給与期間分）</h3><h3>社会保険関係</h3>'
            content+=table(['項目名','算出根拠','金額'],[['健康保険','登録額（仮例）','10,000円'],['介護保険','登録額（仮例）','0円'],['厚生年金','登録額（仮例）','18,000円'],['共済','登録額（仮例）','0円'],['雇用保険','仮例','200円'],['社会保険料計','上記5項目','28,200円']],'社会保険関係')+'<h3>税・その他</h3>'+table(['項目名','算出根拠','金額'],[['所得税','仮例','5,000円'],['住民税','登録額（仮例）','10,000円'],['貯金預入','登録額（仮例）','5,000円']],'税・その他')+'</details></div>'
        elif sid=='SCR-006':
            content='<p>業務マスタの単価・区分・有効期間を管理します。</p><label>勤務報告対象月<input type="month" value="2026-09"></label>'+button(sid,'勤務報告対象月を設定','report-month','勤務報告対象月')+toolbar(sid)+statusblock()+fields(sid,'業務マスタ')+'<div class="mock-actions">'+button(sid,'新しい改定を登録','master-new','登録|改定',extra='data-master-only')+button(sid,'使用を停止','master-stop','停止',extra='data-master-only')+'</div>'
        elif sid=='FUT-IMPORT':
            content='<p>異動情報のExcelから職員候補を取り込みます。</p>'+statusblock()+'<div class="mock-toolbar">'+button(sid,'Excelを選ぶ','candidate-import','取込',primary=True)+'</div>'
            content+=table(['選択','候補','取込結果','確認する内容'],[['<input type="checkbox" checked aria-label="架空花子を選択">','架空 花子','正常','不足なし（架空）'],['<input type="checkbox" checked aria-label="架空太郎を選択">','架空 太郎','正常・番号発行待ち','番号未発行でも候補作成・確認は可能'],['<input type="checkbox" aria-label="架空次郎を選択">','架空 次郎','重複候補','勤務条件の内容が既存の取込済み候補と重複する可能性']],'候補ごとの検証・判断')+'<div class="mock-actions">'+button(sid,'正常行を取り込む','candidate-accept','正常|取込',primary=True)+button(sid,'注意行の取込可否を確認','candidate-review','注意|確認')+nav(sid,'SCR-002','給与情報の確認へ',cur)+'</div>'
        elif sid=='FUT-JLINK':
            content='''<div class="mock-context"><label>支給回<select data-run data-operation-id="OP-JLINK-SELECT"><option value="DEMO-RUN-01">例示2026年10月通常</option><option value="DEMO-RUN-02">例示2026年10月追給</option></select></label><div><strong>支給日</strong><br>2026/10/23</div><div><strong>対象期間</strong><br>2026/09/01〜2026/09/30</div><div><strong>状態</strong><br><span data-pay-status>照合中</span></div></div>'''+statusblock()+'<div class="mock-status mock-warning" data-stale-message hidden>出力後に計算結果が変更されています。最新版との再照合が必要です。</div><div class="tabs" role="tablist" aria-label="人給連携">'
            for i,t in enumerate(['支給回の状況','出力','取込・照合']):content+=f'<button type="button" role="tab" id="tab-j{i}" aria-controls="panel-j{i}" aria-selected="{str(i==0).lower()}" data-tab="panel-j{i}" data-operation-id="{E(op(sid,"タブ|状況|支給回")["id"])}">{t}</button>'
            content+='</div><section class="mock-panel" id="panel-j0" role="tabpanel" aria-labelledby="tab-j0"><h3>支給回の状況</h3><p>全体の対象：2人・3明細（架空）。画面の絞込みと確定判定は別です。</p><p>計算結果：最新の結果を使用します。</p><p data-reconcile-summary>全体差分：1件。未知職員：0件。</p><div class="mock-actions">'+button(sid,'支給回・期間を設定','period','支給回・対象期間',extra='data-payroll-only')+button(sid,'計算する','calculate','計算',extra='data-payroll-only')+button(sid,'例外調整を記録','adjust','例外調整',extra='data-payroll-only')+button(sid,'給与班確定','finalize','確定',extra='data-payroll-only disabled',primary=True)+button(sid,'支払い済みを記録','mark-paid','支払',extra='data-payroll-only disabled')+'</div><h3>処理履歴</h3><p>例示：計算1回／出力0回／給与簿取込0回／照合0回</p><ol data-mock-history><li>確認用の初期状態</li></ol></section>'
            content+='''<section class="mock-panel" id="panel-j1" role="tabpanel" aria-labelledby="tab-j1"><h3>出力対象</h3><label>職員で表示を絞り込む<input type="search" data-operation-id="OP-JLINK-TARGET" data-output-filter placeholder="氏名・職員番号"></label><div class="mock-toolbar"><label>更新区分の一括指定<select data-bulk-am><option>A</option><option>M</option></select></label>'''+button(sid,'選択明細へ適用','apply-am','更新区分|A/M')+button(sid,'表示中だけを選択','target-visible','出力対象')+button(sid,'全明細を選択','target-all','出力対象')+'</div>'
            rows=[]
            for idx,(n,name,period,kind) in enumerate([('009900009901','架空 花子','2026/09','通常'),('009900009901','架空 花子','2026/07','追給'),('009900009902','架空 太郎','2026/09','通常')]):
                rows.append([f'<input type="checkbox" checked data-operation-id="OP-JLINK-TARGET" data-output-row="{idx}" data-staff-number="{n}" aria-label="{name} {period} {kind}を出力">',n+' '+name,period,kind,f'<select data-operation-id="OP-JLINK-AM" data-row-am="{idx}" aria-label="{name} {period} 更新区分"><option>A</option><option>M</option></select>'])
            content+=table(['出力対象','職員','対象期間','明細','更新区分'],rows,'初回は全職員の明細を選択')+'<p>A：新規／M：更新。職員が判断して指定します。出力対象はチェックで指定し、表示の絞込みだけではチェックを解除しません。</p><div class="mock-actions">'+button(sid,'Excel出力前確認','export-review','出力前|出力',primary=True)+'</div></section>'
            content+='<section class="mock-panel" id="panel-j2" role="tabpanel" aria-labelledby="tab-j2"><h3>給与簿の取込・照合</h3><div class="mock-toolbar">'+button(sid,'給与簿CSVを取り込む','ledger-import','給与簿|取込')+button(sid,'最新結果と照合','reconcile','照合',primary=True)+'<label class="inline-check"><input type="checkbox" data-operation-id="OP-JLINK-FILTER" data-all-diffs>全件を表示</label></div>'
            content+=table(['職員','対象期間','項目','アプリ値','給与簿値','差額'],[['009900009901 架空 花子','2026/09','俸給','193,750','193,000','750'],['009900009902 架空 太郎','2026/09','通勤','5,000','5,000','0']],'差分一覧（6列）','data-diff-table')+'<p class="mock-error" data-unresolved-row hidden>未知職員の原行：009900009999（架空）。行を保持して確認し、未解決の間は確定できません。</p>'
            content+='<div class="mock-actions">'+nav(sid,'SCR-002','勤務条件・通勤を訂正',cur,extra='data-target-tab="勤務条件"')+nav(sid,'SCR-003','勤怠を訂正',cur)+button(sid,'差分の明細を再出力','reexport','再出力')+'</div><h3>人給のエラー行</h3><p>人給側のエラー情報を確認します。</p><p>通常状態では取得済みエラーはありません。</p><p class="mock-error" data-jinkyu-error hidden>架空のエラー表示例：職員009900009902／明細例3／必須項目不足。人給側の対象行を確認してください。</p></section>'
        elif sid=='SCR-007':
            content=standard_context(sid)+statusblock()+fields(sid,'差額・回収')+table(['対象月','元の結果','訂正後の結果','差額'],[['2026/07','193,000','194,000','1,000'],['2026/08','193,000','192,000','−1,000']],'月別の差額内訳（架空・算定なし）')+'<div class="mock-actions">'+button(sid,'差額を計算','retro-calculate','過去月との差額',extra='data-payroll-only')+button(sid,'差額を確認','retro-review','確認')+button(sid,'差額を確定','retro-confirm','確定',extra='data-payroll-only')+button(sid,'返納方法を選ぶ','repay-method','返納方法',extra='data-payroll-only')+button(sid,'回収実績を記録','recovery','回収',extra='data-payroll-only')+nav(sid,'FUT-JLINK','追給を人給出力へ',cur,extra='data-retro-output')+'</div><p>元の支払い済み給与は変更しません。追給・返納は別に扱います。</p>'
        elif sid=='EXT-COMMUTE':
            content='<h3>通勤手当認定簿（確認用）</h3><p>架空 花子／009900009901／TK-990001</p><p>適用期間：2026/04/01〜2026/09/30</p>'+table(['経路','方式','認定内容'],[['架空駅A → 架空駅B','定期券前払い','6,250円（架空）'],['架空停留所C → 架空停留所D','IC','日数に応じる（計算なし）']],'認定ヘッダーに対応する経路')+'<p>実装ではA4横2ページをブラウザー印刷から1PDFに保存します。本画面は帳票レイアウトの再実装ではありません。</p>'+button(sid,'印刷の案内','print-guide','印刷')+'<p>別タブを閉じると元の職員マスタ画面に戻れます。</p>'
        elif sid=='CUR-IMPORT-POC':
            content='<p>現行のPoCデータ一括取込の入口を記録する確認用表示です。将来のデータ一括取込み画面とは別です。</p>'+statusblock()+'<p>既存のPoC機能は読み取り参照のみとし、この資料からファイル・Dataverseへ送信しません。業務利用・復旧・権限の完成を意味しません。</p>'
        elif sid.startswith('EXT-'):
            content='<h3>アプリ外で行う作業</h3><p>人給へのExcel取込 → 人給の計算処理 → 給与簿CSVの出力。</p><p>このHTMLから人給へ接続したり、取込成功を記録することはありません。</p>'+nav(sid,'FUT-JLINK','給与簿の取込・照合へ戻る',cur)+statusblock()
        else:content=statusblock()+'<p>具体的な配置は未決です。操作定義を参照してください。</p>'
        dialog='''<dialog class="mock-dialog" data-mock-dialog aria-labelledby="dialog-title"><h3 id="dialog-title" data-dialog-title>操作の確認</h3><div data-dialog-body></div><div class="mock-actions"><button type="button" data-dialog-cancel>キャンセル</button><button type="button" class="primary" data-dialog-confirm>続行</button></div></dialog>'''
        shell='<section class="mock-boundary" aria-label="PC業務画面例"><div class="mock-caption">PCレイアウトの画面例 · 架空データ · 実処理は行いません · 狭い画面はこの枠内を横スクロール</div><div class="mock-app" data-mock-screen="'+sid+'">'+header+'<p class="mock-status mock-warning" data-role-warning hidden>この業務は給与班が担当します。現在の役割では対象データを表示しません。</p><div class="mock-body" data-business-content>'+content+'</div></div></section>'
        static='''<noscript><p class="no-js-message">JavaScriptは無効です。全タブと仕様本文をそのまま表示しています。モックの保存・確認操作は動きません。</p></noscript><section class="static-states"><h2>状態と操作の静的定義</h2><ul><li>初期・未選択：対象を選ぶ案内を表示し、旧職員・旧履歴・旧金額を残しません。</li><li>0件：対象がない旨を表示。以前の詳細・認定ID・金額を利用しません。</li><li>処理中：重複実行・編集・提出を停止。完了または失敗の通知を待ちます。</li><li>エラー：原因と再試行への案内を表示。失敗時は成功したように扱いません。編集中の入力は維持します。</li><li>未保存：SCR-002のタブ変更では保持。別職員／画面／読み取りへの変更時に「変更を破棄して移動しますか」。続行だけ破棄、キャンセルは現状保持。その他画面への共通適用は提案です。</li><li>役割：給与班の全対象・局担当の自局・将来本人の自己分と、業務マスタ／システム管理を区別します。確認用の役割切替は実際の認可ではありません。</li><li>人給連携：出力前確認には支給回・人数・明細数・A/M件数。給与班確定はダイアログなし。選択支給回の全対象について最新照合が差分ゼロで未解決行がない場合だけ確定できます。表示フィルターで判定を狭めません。</li></ul></section>'''
        modal_rows=[]
        if sid in ('SCR-002','SCR-003','SCR-004','SCR-006'):
            modal_rows.append(['変更を破棄して移動しますか','職員・画面・読取への移動で未保存入力が失われる場合。SCR-002タブ移動では出さず保持。','キャンセル：現在の入力を保持／破棄して続行：入力を復元して移動','SCR-002の業務条件は確定。その他への共通適用は提案'])
        if sid=='FUT-JLINK':
            modal_rows.append(['Excel出力前確認','選択支給回・人数・明細数・A件数・M件数。架空の初期例は2人・3明細・A3件・M0件。選択変更に応じて表示する。','キャンセル：出力しない／Excel出力：出力動線のみ模擬','I4確定。ダイアログの形状と文言は提案'])
            modal_rows.append(['給与班確定','確認ダイアログを出さず、ボタン操作時に権限・最新結果・全対象差分ゼロ・未解決行なしを再確認。','条件不成立：確定しない／条件成立：給与班確定へ','I12確定。支払い済みの記録は別操作'])
            modal_rows.append(['支給回・期間／例外調整の確認','対象期間と支給日を区別する。例外調整には理由・処理者を持つ。','キャンセル／内容を確認','この画面への配置と確認部品は提案。計算・金額更新はしない'])
        if sid=='SCR-003':
            modal_rows.extend([['勤務時間を報告しますか','報告後は編集・取込をロックし、訂正には給与班の差戻しが必要。','キャンセル／報告する','業務状態と確認契約を操作定義で確認'],['勤怠Excelの取込','全件検証後に追加更新。未掲載行保持、掲載行の手修正上書き、空欄クリア。処理中停止。','キャンセル／取込を開始','改修要件。復旧・原子性の物理方式は未決'],['職員行を削除しますか','このモックでは末尾行を明示して削除。実データは削除しない。','キャンセル／削除','選択方式・確認文言は提案']])
        if sid=='SCR-006':modal_rows.append(['使用を停止しますか','終了を記録し、過去の履歴を残す。','キャンセル／使用停止','物理削除ではない'])
        if sid=='FUT-IMPORT':modal_rows.append(['注意行の取込可否を確認','内容の不備・重複可能性を確認し、正常行と分けて判断。番号未発行だけでは不備にしない。','キャンセル／判断内容を確認','候補と職員基本の物理接続は未決'])
        if sid=='SCR-007':modal_rows.append(['返納方法／回収実績の確認','給与相殺・納入告知書の併用、案件別の回収実績と残額。','キャンセル／内容を確認','返納操作の配置は提案。取消・過回収の詳細は未決'])
        if modal_rows:static+='<h2>確認・モーダルの静的仕様</h2>'+table(['名称','表示内容・前提','選択肢と結果','区分・境界'],modal_rows,'JavaScriptなしで読める確認仕様')
        mapping=table(['操作ID','業務操作','区分','定義'],[[E(o['id']),E(o['title']),tag(o['status']),link('operations/'+sid.lower()+'.html#'+o['id'],'条件・例外を読む',cur)] for o in ops if o['screen_id']==sid],'この画面の操作対応（業務画面外）')
        body=intro+controls+shell+dialog+static+statetable(sid,cur)+'<h2>操作と仕様の対応</h2>'+mapping+'<p>出典：'+sources_html(model,s['source_ids'],cur)+'</p><h2>未決・実装上の注記</h2><ul>'+''.join('<li>'+E(n)+'</li>' for n in s['notes'])+'</ul>'
        results[cur]=page(model,cur,'④ '+sid+' '+s['name'],body,'wireframes/index.html',sid)
    cur='design-notes.html'
    body='''<h2 id="mock-design">実装と仕様管理の注記</h2><p>この領域はレビュー担当者向けです。職員が使う業務画面の中に仕様ID・実装管理の説明を混ぜません。モックの架空値とデモ操作は業務決定ではありません。</p><h2>適用順序と状態</h2><ul><li>最新mainの2026-10-07確定要件、2026-10-08 I決定を改修先として優先。古いスクリーンショットの金額・方式を新要件へ昇格しません。</li><li>現行実装は資料上の観測範囲に限ります。今回Power Appsに接続して再検証はしていません。</li><li>未決を埋める確認文、モーダル形状、読取／編集操作の共通化、仮画面IDの導線は提案です。</li><li>I8のエラー取得方式、給与簿行の照合キー、最新結果の物理識別、Excel生成方式、D9以降の計算式は決めません。</li></ul><h2>表示・アクセシビリティ</h2><ul><li>B案のFluent 2業務密度とDADSの案内方針を参考に、ヘッダー#073B78、主操作#0F6CBD、本文#242424、44px以上のボタン、フォーカス・文字による状態を使用。</li><li>文書はレスポンシブ。表と図だけ局所横スクロール。PCモックは最小900px、1366px級の構成確認用で、スマートフォン用アプリの完成を意味しません。</li><li>SCR-002は固定ヘッダー／本文全体の縦スクロール、給与簿163項目は同じ本文の中で到達。SCR-005は対象・上部サマリーを保ち、内訳本文を縦スクロールする提案構成。</li><li>タブはaria-selectedと下線、フォームはlabelと対応付け。JavaScript無効時はすべてのタブと定義を読み取れます。</li><li>SVGはテキストと矩形・矢印で構成。1経路1レーンに分け、同じ共通データから生成する表を併記。</li></ul><h2>Power Appsへの移植上の制約</h2><p>これはHTMLのレビュー資料です。HTMLをCanvasアプリの代替実装にしません。Power Appsではモダンコントロールを優先し、Sizeの単位・コントロール版・対応プロパティ・権限・委任・並行処理をStudioと隔離データで別途検証します。JavaScriptのdialog、DOM、sessionStorage、タイマーはモック専用で、Power FxやPower Automateの実装方式として承認しません。</p><h2>安全性</h2><p>ネットワーク呼出し、実ファイル読込、Dataverse更新、Power Automate起動、実給与計算・振込、権限変更はありません。モックの一時状態だけを同一タブのsessionStorageへ保存し、初期化で削除します。ブラウザーによってfile://の状態共有が制限される場合はURLパラメーターで職員・月・支給回・戻り先を引き継ぎます。架空値以外を入力しないでください。</p><h2>未決の業務</h2><p>年末調整、制度改正の適用詳細、随時・定時決定、住民税年度更新の詳細、期末勤勉の式等は本資料で制度判断を追加しません。既存の未決一覧を参照します。</p>'''
    body+='<h2>正本と関連設計</h2><p>'+sources_html(model,[x['id'] for x in model['sources']],cur)+'</p>'
    results[cur]=page(model,cur,'設計注記・未決・制約',body,cur)
    return results
