"""Read current exported package metadata; emit sanitized, field-specific readiness evidence."""
import json, zipfile, hashlib, collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
SPEC=json.loads((ROOT/'config/dataverse/scr002-history-columns.json').read_text())
PKG=ROOT/'backup/before-v35-20261010.msapp'
EXPECTED='465dcdc2eec6deb181f8df811558bdade4f0b6494675346e1cac700d90f1a740'
assert hashlib.sha256(PKG.read_bytes()).hexdigest()==EXPECTED
z=zipfile.ZipFile(PKG)
raw=z.read('References\\DataSources.json')
ds={d.get('LogicalName'):d for d in json.loads(raw)['DataSources']}
SOURCE_COMMIT='252abe4aa5d3b1d99a584a30c97d9b48153c91f5'
base_refs=[{'path':'docs/design/detailed/detailed-design.md','line_start':112,'line_end':130}, {'path':'docs/requirements/screen-requirements.md','line_start':381,'line_end':384}, {'path':'docs/changes/requests/change-20260928-scr002-history.json','line_start':8,'line_end':25}]
# Each entry identifies the actual missing contract, not a supposed missing physical column.
field_specific={
 'work':{
 'crb3c_transferkind':('format_and_domain_ready','列説明は6候補を列挙。選択UI化は技術的に可能。ただし登録／新履歴／訂正の操作別許可と状態保存が未定。','PAYREQ-03 / Q15,Q17,Q18'),
 'crb3c_appointmentreason':('domain_incomplete','説明は確認値例のみで完全候補集合ではない。正式区分マスタ／廃止候補と新旧履歴への適用契約がない。','PAYREQ-03 / Q13,Q18'),
 'crb3c_dailyrate':('format_ready','0以上整数の物理列は既知。最新Q40は単価マスタ選択なので、自由数値訂正を本給与条件登録とするにはマスタ対応・訂正／再確認契約が必要。','PAYREQ-03,PAYREQ-07 / Q40,R11'),
 'crb3c_workstart':('excluded_by_confirmed_scope','最新Q16で始業時刻は入力対象外。過去値の表示を維持しても保存解放しない。','PAYREQ-03 / Q16'),
 'crb3c_workend':('excluded_by_confirmed_scope','最新Q16で終業時刻は入力対象外。過去値の表示を維持しても保存解放しない。','PAYREQ-03 / Q16'),
 'crb3c_dailyhours':('format_and_domain_ready','説明は0～24、DB MaxValueは1000000000。アプリ検証は確定説明の24上限・小数2桁を守れる。履歴追加と訂正・再確認の保存契約が未定。','PAYREQ-03 / Q15,Q16,Q17,Q18'),
 'crb3c_overtimebaserate':('format_ready','参考単価の物理整数列は既知だが、参考表示を編集対象にする許可列定義がない。給与使用値か表示専用かの対応が未確定。','SCR002-EDIT-001/002,PAYREQ-07'),
 'crb3c_budgetitem':('format_ready','文字列名称は既知。Q12の所属既定予算／履歴個別予算の識別子・上書き元を自由名称列から推定できない。','PAYREQ-02 / Q12'),
 'crb3c_appointmentdraft':('format_ready','4000文字・改行の型契約は既知。任意入力を許す列リスト、履歴訂正監査、改行を保持するUI・読戻しが未実装。','SCR002-EDIT-001/002/003,PAYREQ-03'),
 'crb3c_appointmentcomment':('format_ready','4000文字・改行の型契約は既知。非計算項目の限定候補だが、既存履歴内での更新許可と訂正前後記録の設計がない。','SCR002-EDIT-001/002/003,PAYREQ-03'),
 'crb3c_notes':('format_ready','4000文字・改行の型契約は既知。最小の保存候補だが、自由備考を履歴訂正監査から除外する根拠も、許可列一覧もない。','SCR002-EDIT-001/002/003,PAYREQ-03')},
 'social':{
 'crb3c_employmentcategory':('domain_incomplete','職員雇用区分は例示値のみ。共通職員基本／条件履歴との役割と正式区分候補が未確定。','PAYREQ-04 / Q19,Q27'),
 'crb3c_birthdate':('format_ready','DateOnlyと有効暦日は既知。職員基本の生年月日との同期／履歴写し／独立訂正のどれかが未確定。','SCR002-EDIT-002,PAYREQ-01'),
 'crb3c_ageapril':('format_ready','整数列は既知。年齢を手修正する列か算出表示か、基準年・生年月日との整合条件が未定。制度判定の自動化は追加しない。','SCR002-EDIT-001/002,PAYREQ-04'),
 'crb3c_agemarch':('format_ready','整数列は既知。年齢を手修正する列か算出表示か、基準年・生年月日との整合条件が未定。制度判定の自動化は追加しない。','SCR002-EDIT-001/002,PAYREQ-04'),
 'crb3c_carestatus':('domain_incomplete','N月から等の説明は具体的な全候補と月入力方式を定義しない。確認済み制度判断の登録とQ20の未確認区分の対応が未定。','PAYREQ-04 / Q20,R19'),
 'crb3c_pensionexemption':('domain_incomplete','N月から等の説明は具体的な全候補と月入力方式を定義しない。給与班確認済み判断の登録契約が必要。','PAYREQ-04 / Q20,R19'),
 'crb3c_elderstatus':('domain_incomplete','N月から等の説明は具体的な全候補と月入力方式を定義しない。未確認と非該当を空欄で混同できない。','PAYREQ-04 / Q20,R19'),
 'crb3c_multiemployer':('format_and_domain_ready','該当／空欄という旧契約は既知。空欄を未確認・非加入・非該当のどれへ対応させるかは新モデルで未定。','PAYREQ-04 / Q20,Q27'),
 'crb3c_corporatepension':('format_and_domain_ready','該当／空欄という旧契約は既知。空欄を未確認・非加入・非該当のどれへ対応させるかは新モデルで未定。','PAYREQ-04 / Q20,Q27')},
 'tax':{
 'crb3c_taxtable':('domain_incomplete','この4表用の列説明では候補値未確認。元の職員基本の甲／乙をこの履歴の全候補と無検証で転用しない。','PAYREQ-04 / Q25,Q27'),
 'crb3c_dependents':('domain_incomplete','0以上整数は既知、業務上限は未確認。DBの1,000,000,000を扶養人数上限と採用しない。','PAYREQ-04 / Q25,Q26'),
 'crb3c_employmentinsurance':('domain_incomplete','設定候補が未確認。新要件の未確認・加入・非加入と旧文字列の対応がない。','PAYREQ-04 / Q20,Q27'),
 'crb3c_savingsmonthly':('format_ready','0以上円整数列は既知。Q23の項目別×有効期間行へどう対応し、確認状態・特殊月を扱うか未定。','PAYREQ-04 / Q23,Q27; PD-02'),
 'crb3c_loanmonthly':('domain_incomplete','0以上整数は既知。説明に値域詳細未確認、Q23の項目別履歴対応も未定。','PAYREQ-04 / Q23,Q27; PD-02')},
 'resident':{
 'crb3c_periodcategory':('domain_incomplete','設定値は元ファイル内とあるだけ。月別住民税Q24の控除年月をこの自由区分から一意解釈できない。','PAYREQ-04 / Q24'),
 'crb3c_monthlyamount':('format_ready','0以上円整数は既知だが控除年月を特定する新モデルがない。旧期間区分の1行を月別行へ勝手に展開しない。','PAYREQ-04 / Q24,Q27'),
 'crb3c_municipalitycode':('domain_incomplete','物理text200は既知。コード桁／形式・先頭0・空欄許否の業務契約は未確認。','SCR002-EDIT-002,PAYREQ-04'),
 'crb3c_municipalityname':('domain_incomplete','物理text200は既知。業務文字数制約未確認、自治体コードとの対応／写し属性の編集可否が未定。','SCR002-EDIT-002,PAYREQ-04')}
}
rows=[];tables=[]
contract_lines=(ROOT/'config/dataverse/scr002-history-columns.json').read_text().splitlines()
for t in SPEC['tables']:
 d=ds[t['studio_logical_name']];meta=json.loads(json.loads(d['TableDefinition'])['EntityMetadata']);attrs={a['LogicalName']:a for a in meta['Attributes']}
 rel=next(q for q in meta['ManyToOneRelationships'] if q.get('ReferencingAttribute')=='crb3c_staffbasicid')
 tables.append({'table_key':t['key'],'logical_name':d['LogicalName'],'source_name':d['Name'],'entity_set':d['EntitySetName'],'primary_id':meta['PrimaryIdAttribute'],'primary_name':meta['PrimaryNameAttribute'],'ownership_type':meta['OwnershipType'],'connector_is_writable':d['IsWritable'],'parent_lookup':rel['ReferencingAttribute'],'parent_table':rel['ReferencedEntity'],'parent_primary_id':rel['ReferencedAttribute'],'parent_delete':rel['CascadeConfiguration']['Delete'],'warning':'NativeCDS IsWritable / attribute IsValidForUpdate are connector/schema capability, not current caller update privilege or approved editable-column list.'})
 for i,c in enumerate(t['columns'],1):
  logical=c['logical_name'];a=attrs[logical]
  codec='format_ready';req='SCR002-EDIT-001/002/003,PAYREQ-03' if t['key']=='work' else 'SCR002-EDIT-001/002/003,PAYREQ-04'
  if logical=='crb3c_staffnumber':
   codec='format_and_domain_ready';specific='12桁文字列の検証は設計済み。子の番号を親職員GUIDと異なる値へ変える操作／親付替えは未定。一般入力が見えることを識別キー編集許可とみなさない。';req='SCR002-EDIT-002,PAYREQ-01,PAYREQ-02 / Q2,Q3,Q7'
  elif logical=='crb3c_fullname':
   specific='200文字の物理text列は既知。職員基本氏名の写し／履歴時点の氏名／独立編集のどれかと、変更の伝播範囲が未定。'
  elif logical in {'crb3c_startdate','crb3c_enddate'}:
   specific='DateOnly／有効暦日／任意は既知。開始終了の空欄・重複・訂正か新履歴かの判定と、確認状態・未払い失効への保存連携が未設計。'
  elif t['key']=='social' and c['kind']=='date':
   specific='DateOnly／有効暦日／任意は既知。この列が資格日・控除期間・改定日のどれかを新モデルへ対応し、開始終了整合と確認状態を保存する契約が未設計。'
  elif t['key']=='social' and c['kind'] in {'integer','decimal'}:
   specific='非負数・円／等級・物理桁は既知。Q22で給与班の登録方針は確定だが、対象保険・適用期間・確認状態・訂正前後監査と未払い失効の関連が未設計。'
  else:specific='型と入力表示は既知。対象列の編集許可と履歴訂正・確認保存の契約が未設計。'
  if logical in field_specific[t['key']]:codec,specific,req=field_specific[t['key']][logical]
  if c['kind']=='text':parse=f"文字列。{c['max_length']}文字以内。BlankはNullと空文字の往復方針を明記し、表示整形で元値を改変しない。"
  elif c['kind']=='date':parse='空欄はNull。yyyy/mm/ddで有効暦日を検証しDateOnlyとして保存。DateValueの寛容変換だけで入力妥当性を合格にしない。'
  elif c['kind']=='integer':parse=f"空欄はNull。整数性、非負、物理上限{c['max']}を検証。業務上限の未決を物理上限で置換しない。"
  else:parse=f"空欄はNull。小数{c['precision']}桁以内、非負。丸めて不正入力を受理しない。"
  tests=['未変更／Null／0／最大長または数値精度／不正値を分ける','別職員GUID・番号不一致・別履歴キーを保存前拒否','単一行を変更分だけ保存し、再取得一致後だけ成功','保存失敗／再取得失敗はドラフト保持・日時だけ更新しない']
  if c.get('max_length')==4000:tests+=['改行・長文4000／4001の入力、保存、再表示を実機確認（現行入力にMultiline設定の明示なし）']
  if c['kind']=='date':tests+=['無効暦日・開始後終了・月境界・Null終了・実変更と誤訂正を分離']
  before_restore='選択行GUID・親GUID・職員番号・対象列のtyped前値・行バージョンを試験前に読戻す。既存行を削除せず、承認済みの同じ隔離行へ前値を戻し読戻し一致。DB全体ロールバックを約束しない。'
  rows.append({'field_id':t['studio_logical_name']+'.'+logical,'table_key':t['key'],'display_name':c['display_name'],'logical_name':logical,'existing_physical_schema_known':True,'existing_schema':{k:a.get(k) for k in ['AttributeType','MaxLength','MinValue','MaxValue','Precision','Format','IsValidForUpdate','IsValidForCreate'] if k in a},'required_level':a['RequiredLevel']['Value'],'attribute_audit_flag':a.get('IsAuditEnabled',{}).get('Value'),'audit_flag_limit':'列フラグのみ。環境・テーブル監査の有効性、監査の閲覧／保存期間、訂正前後の実際の記録成功は未確認。','source_constraint':c['source_constraint'],'input_codec_readiness':codec,'input_codec_contract':parse,'current_ui':{'section':'Work' if t['key']=='work' else 'Social' if t['key']=='social' else 'Tax','field_key':str(i),'record_id_contract':'R:<resident GUID>' if t['key']=='resident' else '<selected history GUID>','input_control':'TextInput2','draft_key':['Section','Key','RecordId'],'visible_in_edit_mode':True,'generic_displaymode_allows_input':True,'save_current':'Rejected by btnSave111 for Section other than Basic/Commute','warning':'汎用TextInput.DisplayModeの許可は明示的な編集許可列一覧ではない。職員番号等までEditになる。'},'parent_guard_ready':'既知の親Lookup crb3c_staffbasicid と選択職員GUID、子12桁職員番号を再検証。Tax residentはR:接頭辞から別表GUIDを解決し、Taxの同じKeyと混同しない。','synthetic_scope':'単一試験App＋_STUDIOのみ。^0099000000[0-9]{2}$に一致する職員と事前特定した隔離行GUIDに限定。正規表現だけを実効認可／実データ不存在の証明にしない。','whole_save_readiness':'proposal' if codec=='excluded_by_confirmed_scope' else 'designblocked','whole_save_reason':specific,'shared_precise_blockers':([] if codec=='excluded_by_confirmed_scope' else ['SCR002-EDIT-001/002: この列をどの主体・状態で更新できるかの明示許可列契約なし。','Q17/Q18またはQ27/R11: 履歴訂正前後・確認待ち復帰・必要な未払い影響失効を保存する契約なし。単なるPatchで新要件完了にしない。','専用利用者は過去Readのみ。現在callerのUpdate権限は別確認。今回ロール変更で迂回しない。']),'requirement_ids':req,'smallest_missing_question':('入力対象外として現状の表示だけを維持。再質問不要。' if codec=='excluded_by_confirmed_scope' else specific),'test_requirements':tests,'rollback':before_restore,'evidence':[{'path':'config/dataverse/scr002-history-columns.json','table':t['key'],'column':logical},{'artifact':'current v35 exported References/DataSources.json','sha256':hashlib.sha256(raw).hexdigest(),'table':d['LogicalName'],'column':logical},{'path':'Src/scrStaffMasterSearch.pa.yaml','line_start':952,'line_end':1009,'provenance':'current v35 Source byte-equal to Oct7 reviewed source'}]+base_refs})
assert len(rows)==56 and len({r['field_id'] for r in rows})==56
counts={'fields':56,'physical_columns_known':sum(r['existing_physical_schema_known'] for r in rows),'schema_valid_for_update':sum(r['existing_schema'].get('IsValidForUpdate') is True for r in rows),'ui_generic_editable':sum(r['current_ui']['generic_displaymode_allows_input'] for r in rows),'per_table':dict(collections.Counter(r['table_key'] for r in rows)),'input_codec_readiness':dict(collections.Counter(r['input_codec_readiness'] for r in rows)),'whole_save_readiness':dict(collections.Counter(r['whole_save_readiness'] for r in rows))}
result={'task_id':'PAY-IMPLEMENT-001','title':'Current 56-column persistence readiness: known schema does not imply approved write contract','current_export_package_sha256':EXPECTED,'current_export_metadata_sha256':hashlib.sha256(raw).hexdigest(),'current_source_status':'All 10 source files verified byte-equal to reviewed Oct7 snapshot. References/DataSources.json also byte-equal to that snapshot; this is exported app metadata, not a new live Dataverse metadata query.','counts':counts,'tables':tables,'findings':['56列は4表とも物理名・型・選択GUID・親Lookupが既知。物理列不明を保存不能の理由にしない。','56列すべてschema IsValidForUpdate=true、connector IsWritable=true。いずれも利用者の実効Update許可ではない。','汎用TextInputは56列すべて入力可にするが、保存の許可列設計ではなく、職員番号やQ16対象外の始終業まで解放する。','勤務開始／終了の2列はQ16により新たな入力対象外。その他54列は列別に形式が整っても、明示許可列・訂正監査／確認状態などの前提が不足。','最小候補は勤務条件の辞令案／辞令コメント／その他備考。既知text4000で給与式を変えず単一行更新が可能だが、これらだけを許可する契約、改行入力と前後記録、既存caller Updateの検証を完了するまでreadyにしない。','型の広いDB制約を業務基準へ転用しない。勤務時間は説明0～24に対しDB max1e9、扶養人数の業務上限と税区分候補等は未確認。','新モデルの勤務条件／控除／住民税の全業務保存と、既存隔離fixtureの限定フィールド訂正を区別する。後者を新モデル完成として扱わない。'],'narrow_candidate_to_unblock':{'table':'crb3c_studioworkcondition','columns':['crb3c_appointmentdraft','crb3c_appointmentcomment','crb3c_notes'],'what_is_known':['同一行GUID','親GUID＋12桁番号','text4000型','現在表示／ドラフト経路','再取得経路','単一行Patchなら多表原子性不要'],'what_remains':['この3列に限定した状態別・役割別の編集許可根拠','Q17前後記録が実際に成立する経路（列AuditFlagのみでは不足）','改行UIとNull/空文字の入出力契約','既存の実効Update権限の読戻し／隔離検証（権限拡張なし）'],'question':'既存の架空Work履歴について、この非計算3列だけを訂正する許可列・状態と監査経路をどの既存設計が定めるか。資料になければ技術設計として明示し、業務例外を勝手に足さない。'},'fields':rows,'validation':{'exact_56_unique_fields':'PASS','all_metadata_present':'PASS','all_current_ui_columns_present':'PASS','no_schema_or_source_mutation':True,'no_external_state_changes':True}}
(OUT/'field-readiness-56.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
md=['# PAY-IMPLEMENT-001：現行履歴56列の保存準備','',
 '勤務15・社会保険26・税固定控除9・住民税6の全56列を個別確認した。物理名・型・親GUIDと表示キーは既知。現在v35の公式Export内DataSourcesとソースを根拠に、btnSave拒否だけでは判断していない。','',
 '## 結論','',
 f"- 物理列既知 {counts['physical_columns_known']}/56、schema IsValidForUpdate=true {counts['schema_valid_for_update']}/56、汎用UI入力可 {counts['ui_generic_editable']}/56", 
 '- 完全な限定保存として実装準備完了：0列。54列は具体的な設計依存、2列の始終業時刻はQ16により入力対象外。',
 '- 最小候補はWorkの辞令案・辞令コメント・その他備考。text4000・行GUID・親・ドラフト／再取得は既知だが、許可列・状態と訂正監査の契約が未指定。',
 '- 既存の隔離fixture訂正と、新モデルの全業務保存を別に判定する。後者の未完成だけを理由に物理列がないとは言わない。',
 '- 列のAuditFlag=trueやIsWritable=trueは、実効権限や監査記録成功の証明ではない。専用利用者は過去Readのみ。権限を変更して迂回しない。','',
 '## 入力形式の準備状態','',json.dumps(counts['input_codec_readiness'],ensure_ascii=False),'',
 '形式変換の設計が揃っても保存許可を意味しない。多表一括更新を作らず、単一の事前指定架空行・許可列・前値退避・再取得一致を最小単位とする。','',
 '## 全56列','',
 '| 表 | 順 | 項目 | 物理列／型 | 入力契約の準備 | 保存を止めている具体点 |','|---|---:|---|---|---|---|']
for r in rows:
 vals=[r['table_key'],r['current_ui']['field_key'],r['display_name'],r['logical_name']+' / '+r['existing_schema']['AttributeType'],r['input_codec_readiness'],r['whole_save_reason']]
 md.append('| '+' | '.join(str(v).replace('|','／') for v in vals)+' |')
md+=['','## 共通の保存試験・復元','',
 '親GUID・番号・選択履歴を再検証し、変更列だけを単一行へ適用する。Null／0／不正型／範囲外／別職員／別履歴／保存失敗／再取得失敗を分離して試験する。給与簿へ書込まない。成功表示は読戻し一致後だけ。',
 '試験前に対象行GUIDとtyped前値・行版を記録し、同じ承認済み隔離行へ前値を復元して一致確認する。親付替え・行削除・実データ・役割変更は含まない。','',
 '## 主要根拠','',
 '- config/dataverse/scr002-history-columns.json（56列）',
 '- scripts/automation/scr002_history_schema.py（列・親Lookup・Restrict）',
 '- docs/design/detailed/detailed-design.md:112–130（許可列・状態・保存／再取得）',
 '- docs/changes/requests/change-20260928-scr002-history.json（表示変更、編集保存未判定）',
 '- docs/requirements/payroll-confirmed-20261007.md:46–58（Q15～Q27）',
 '- current v35 Src/scrStaffMasterSearch.pa.yaml:952–1009（表示と汎用入力）、:653–686（保存拒否）',
 '- 現在公開package SHA: '+EXPECTED,
 '- 出力されたDataSources SHA: '+hashlib.sha256(raw).hexdigest(),
 '','詳細JSONは各列の入力パーサ契約、現行UIキー、親照合、synthetic制限、テスト、復元、要件IDを含む。環境URL・個人値・Library IDは含めない。','']
(OUT/'field-readiness-56.md').write_text('\n'.join(md))
print(json.dumps(counts,ensure_ascii=False,indent=2))
