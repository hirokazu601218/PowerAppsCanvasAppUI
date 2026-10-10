import json, hashlib, collections, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
AUDIT=ROOT.parent/'pay-audit-001'
OUT=Path(__file__).resolve().parent
doc=json.loads((AUDIT/'docs-html-matrix.json').read_text())
src=json.loads((AUDIT/'source-data-matrix.json').read_text())
findings=json.loads((AUDIT/'source-findings.json').read_text())
sourceops={x['id']:x for x in src['operations']}
COMMIT='252abe4aa5d3b1d99a584a30c97d9b48153c91f5'
def ev(p,a,b=None):return {'path':p,'line_start':a,'line_end':b or a,'commit':COMMIT,'url':f'https://github.com/hirokazu601218/PowerAppsCanvasAppUI/blob/{COMMIT}/{p}#L{a}'+(f'-L{b}' if b and b!=a else '')}
def group(id,title,status,scope,blockers,prereq,migration,tests,rollback,question,owner,evidence):
 return dict(id=id,title=title,status=status,confirmed_scope=scope,blockers=blockers,prerequisites=prereq,migration=migration,tests=tests,rollback=rollback,smallest_missing_question=question,question_owner=owner,evidence=evidence)
groups=[
group('G01','現行検索・履歴・試算UIの明確な差分','implementnow','既存の検索結果・ページ・職員・月保持、タブ別履歴キー保持、SCR005の固定サマリーと旧算定根拠消去。旧式の単純再利用ではなく最新読戻しとの差分修正。',[],['編集前の同一App IDの最新下書き、ソースSHA、隔離接続先を照合','未保存破棄確認と失敗時入力保持を維持'],'DB移行なし。最小の変更コントロール／依存式だけを保存する。',['検索1/0/複数件・ページ2→005→002','区分別複数履歴の選択→別タブ→復帰','保存失敗・破棄取消・連続操作','未登録月・登録0円・別職員・失敗時に旧数値／根拠なし','幅900/1366/1920・200%・最終行到達'],'変更直前の同一アプリパッケージと対象式を保存し、変更分だけ復元。現在の依頼は同一試験アプリへの公開を明示承認済み。main統合・本番公開は範囲外。','業務質問なし。差分の現行版再現だけが必要。','engineering',[ev('docs/design/detailed/detailed-design.md',97,134),ev('docs/requirements/open-decisions.md',10,17)]),
group('G02','職員基本・組織・予算と履歴の新モデル','designblocked','一人一行、GUID Lookup＋12桁番号、最新基本と有効期間履歴、階層なし組織、所属既定予算と履歴個別予算、住所、採用日給与対象時必須。',['PD-01','D-02','Issue #51'],['新旧列対応と型・精度・既定値・主列・一意制約・保存経路を確定','M_職員基本変更前にIssue #51を再確認し同時処理計画へ組込'],'旧_STUDIOは保持。新モデルの列契約とテスト行移行を独立して読戻し。既存12接続表を完成新モデルとしない。',['12桁先頭0・重複拒否・GUIDと番号不一致','同一人の再雇用・月途中履歴・住所更新','所属予算と個別上書き','Issue #51の実列と独立欠勤単価読戻し'],'マッピングと元テスト行を退避。旧接続へ戻す。新表を即削除せず旧履歴を保持。','新モデルの各列を既存列へ対応させた物理辞書はどれか。未存在なら設計を作りレビューする。','engineering',[ev('docs/design/basic/data-model.md',48,92),ev('docs/requirements/payroll-confirmed-20261007.md',32,43),ev('docs/requirements/open-decisions.md',84,84)]),
group('G03','採用前・発令自動候補の連携','designblocked','発令登録完了時の候補、採用ごとの識別子、番号後反映、採用取消は履歴保持・計算除外。自動連携は実現性確認目標。',['PD-08','PD-01','AD連携方式'],['異動情報アプリ通知／取得仕様と安定採用IDを入手','番号未発行候補と一人一行職員基本の分離・統合契約'],'候補領域を別に設計し、番号未発行行を無条件に職員基本へ作らない。',['重複通知・番号遅延・再採用別ID','確定前・後の取消','給与班修正と外部変更の競合','決裁だけでは候補作成しない'],'取込回／外部IDの対応を保存し再適用可能にする。候補を物理削除しない。','発令登録完了イベントと採用ごとの不変IDをどの正式インターフェースから取得できるか。','source-owner/engineering',[ev('docs/requirements/business-requirements.md',40,67),ev('docs/requirements/open-decisions.md',91,91)]),
group('G04','E専用Excel取込と確認待ち候補','needsbusinessdecision','人単位で一律拒否せず内容重複注意、正常行先行、不備行を給与班が判断、専用画面入口。PoCとは別機能。',['E-03','E-05','PD-01','PD-08'],['異動Excel正式列・不備条件・内容一致／重複可能性基準を入手','行別処理回・確認待ち候補保存設計'],'E用ステージングと判断履歴を設計。SCR003勤怠の全件検証方式をEに流用しない。',['既存人の新履歴は許容','正常行＋重複／不備混在','行見送り／採用・再取込・外部値競合','給与班確定前は計算不可'],'取込回単位に追跡。適用済み行を勝手に取消せず、隔離行のみ元状態へ戻す。','E取込で内容一致／重複可能性と必須不足を判定する列と条件は何か。','business/data-owner',[ev('docs/requirements/business-requirements.md',70,122),ev('docs/requirements/screen-requirements.md',419,425)]),
group('G05','勤務条件・保険・税・固定控除の登録確認','designblocked','実変更は新期間履歴、誤登録は前後記録して訂正、登録→確認待ち→給与班確定・差戻し、未払い再計算。月別住民税・保険確認と控除期間を分離。',['PD-01','PD-04','D-02','PD-02の特殊月・保険例外'],['編集可能列・検証と状態コード・監査前後値・保存先を確定','未払い結果失効と給与班確認経路を設計'],'既存56列の読取接続をそのまま保存対象としない。住民税月列→月別行等は明示変換と行数照合。',['期間変更と誤訂正を分離','未確認／非加入／加入、NULL／0','確認待ちを計算へ使わない','確定後訂正で再確認・未払い失効','保存失敗はドラフト保持'],'変更前後監査とテスト元行を保存。途中反映の再実行契約ができるまで本保存を有効化しない。','新モデルの許可編集列・検証条件・状態／監査の正式保存契約は何か。','engineering; business only for listed policy exceptions',[ev('docs/requirements/payroll-confirmed-20261007.md',44,58),ev('docs/design/detailed/detailed-design.md',112,133),ev('docs/design/basic/data-model.md',55,65)]),
group('G06','通勤届・認定・新ヘッダー経路モデル','designblocked','定期前払い／IC実日数を経路別に混在、提出⇄差戻し→認定、新認定と旧認定保持、一時不支給と終了を区別。既存HTML印刷維持。',['PD-01','PD-09','PD-02','F-02'],['正式ヘッダー／経路列、必須検証・経路数・帳票取得対応を確定','精算・適用期間／不支給計算を業務資料で確定'],'既存4経路を上限と決めない。新旧行のGUID対応を保存し受入済みHTMLを保持。',['新旧認定・複数経路・混合方式','不支給と終了の区別','認定前は計算利用不可','GUIDと職員不一致拒否','71欄・2ページ・NULL/0・印刷枠超過停止'],'旧データ契約・受入済みHTML・通常入口の復元材料を保持。新契約受入前に旧経路を消さない。','新経路テーブルとHTML取得契約を確定する資料はどれか。精算式は別の未決として保留。','engineering + business for calculation',[ev('docs/requirements/business-requirements.md',125,171),ev('docs/requirements/open-decisions.md',85,95),ev('docs/design/basic/data-model.md',61,72)]),
group('G07','勤怠の追加更新・職員行編集・復旧','designblocked','所属×勤務月、掲載行は手修正を上書き／空欄クリア、非掲載行保持、報告済ロック、全件検証・処理中停止・不完全結果除外。',['PD-01の行識別／必須空欄','PD-05','PD-04'],['既存直列フロー／activebatch方式の再利用可能性を設計・検証','正規化12桁職員番号を新要件でも行キーに使う契約とNo再採番等を確定','対象報告の処理中状態・復旧記録・権威ある実行者を確定'],'現行の有効バッチ＋旧バッチ保持は再利用候補。追加更新では旧有効行と正規化入力を合成して新バッチへ、検証後切替。これは設計案であり未承認物理方式。',['掲載A更新・新B追加・非掲載C保持','手修正上書き・空欄クリア・0維持','複数所属同職員の別報告','全件検証前書込なし・999/1000境界','途中失敗／応答喪失／再実行／重複実行／並行編集・提出','報告者／差戻担当Lookup読戻し'],'旧activebatchと版を保存。失敗バッチは利用不可、旧成功分を維持。活性化後の取消は検証済み復旧手順のみ。','新要件の職員行識別・必須空欄・Noの扱いを既存列契約からそのまま採用してよいかを設計根拠で確定する。','engineering first; business only for ambiguous required cells',[ev('docs/design/detailed/detailed-design.md',284,291),ev('docs/requirements/payroll-confirmed-20261007.md',65,70),ev('docs/requirements/payroll-confirmed-20261007.md',108,110),ev('scripts/automation/build_scr003_flow.py',105,163)]),
group('G08','期末勤勉率・単価区分マスタ','designblocked','職員×対象期間の別々の期末・勤勉率。業務管理者が単価・区分等を有効期間管理、給与班兼務可、使用停止で履歴保持。',['PD-01','PD-04','PD-02'],['率の桁・単位・上下限・期間／職員キーと正式保存先を設計','業務管理者の実効認可は今回変更しない'],'現行SCR004はSetのみ。率を永続表に保存した証拠なし。マスタ新旧版は上書きしない。',['別職員／別期間／別率の保存読戻し','未確定値を計算に使わない','マスタ改定前後・使用停止後の過去参照','業務／システム管理ロール混同なし'],'旧率画面とマスタ読取経路を保持し新保存機能を停止可能にする。','別率の正式保存先・精度・入力範囲をどの資料で確定するか。','engineering; business for valid rate domain',[ev('docs/requirements/screen-requirements.md',424,425),ev('docs/requirements/screen-requirements.md',482,489),ev('docs/requirements/payroll-confirmed-20261007.md',71,77)]),
group('G09','外部機関の決定結果登録','designblocked','社会保険／税固定控除タブで担当者が紙電子の決定結果を登録、給与班確認前は計算不可。電子申請・受付進捗・自動取込・採否再判断は作らない。',['PD-01','PD-04','Gの入力／証憑／適用条件'],['決定結果項目・証憑契約・適用日・確認状態の保存先を確定'],'新決定結果を既存保険26列等へ自動対応させない。必要な正式マッピングを作成。',['紙／電子同じ登録経路','担当局外拒否','未確認結果の計算除外','外部結果を給与班独自判断で変更しない'],'テスト決定結果と確認前後を追跡し旧表示契約を保持。','決定結果に必須の登録内容と給与適用時点は何か。','business/data-owner + engineering',[ev('docs/requirements/business-requirements.md',174,235),ev('docs/requirements/screen-requirements.md',403,413)]),
group('G10','支給回・本計算・調整・確定単位','needsbusinessdecision','日額時間額、対象期間と支給日、元データ訂正、理由／処理者付き別調整、計算版根拠、個別／所属一括、差分ゼロ確定。',['PD-02','D9～D12保留','PD-01','PD-05','Q47とI12の個別／全支給回境界'],['現行Excelと業務資料から項目別式・丸め・適用時期・独立期待結果を確定','支給回／計算版／使用値／調整の正式モデル','個別確定と支給回全体検証の関係を決める'],'SCR005仮例は置換前提にしない。計算結果・根拠は版ごと分離、支払済への更新経路を作らない。',['日額時間額・月途中条件・採退境界','二重欠勤減算なし','未確認保険・勤怠失敗・未確定元データは確定不可','支給回全件でゼロ判定・同時更新失効','支払済不変'],'支払済／最終版を不変保持。未払い候補版だけ無効化して直前有効版へ戻す設計。','式精査再開はD9から。先に画面を進めるなら個別／所属一括確定と全支給回差分ゼロ判定の関係のみ確認する。','business; formula review remains on hold',[ev('docs/requirements/payroll-confirmed-20261007.md',71,84),ev('docs/requirements/payroll-interface-decisions-20261008.md',7,36),ev('docs/design/detailed/detailed-design.md',293,305)]),
group('G11','承認済み人給連携のUI単独部分','implementnow','3タブ・支給回コンテキスト、初回全職員と絞込み、手動A/M一括／明細指定、出力前件数確認、差分／全件と指定6列。永続化・業務計算・人給接続から分離できる純粋な表示／ローカル状態。',[],['最新アプリ読戻しと衝突しない最小Canvas差分','明確に架空と表示した入力データ契約。新しい正式物理名／業務状態コードを確定しない','実出力・取込・給与班確定は依存契約完成まで無効。試験完了を業務機能完了としない'],'DB移行なし。新UIローカル状態のみ。内部コントロール名は実装上の名前として記録し正式業務画面IDを勝手に確定しない。',['JLINK-T01の3タブ／コンテキスト部分','JLINK-T02の対象選択・A/M・確認件数部分','JLINK-T04の切替・6列表示部分','0件・多行同職員・取消・再入場・別支給回・Tab順','未接続操作は成功通知や架空の確定状態を出さない'],'追加した最小Canvas subtreeとローカル状態式を直前版へ戻す。既存画面／接続／権限を変更しない。','業務質問なし。正式画面IDと実データadapterは後段の技術設計。試験UIを本機能完成と扱わない。','engineering',[ev('docs/requirements/screen-requirements.md',494,516),ev('docs/design/detailed/payroll-jinkyu-interface.md',93,121),ev('docs/testing/test-specification.md',677,684)]),
group('G12','人給237列xlsxの本出力','designblocked','xlsx、237見出し固定順、見出し1／データ2行目、文字列型・表示形式、11キー、職員判断A/M、指定網掛け列を維持。',['PD-03','全237列の値設定','D9～D12等の式保留'],['ローコードの生成方式・既存接続・保存配布先を確定','各出力列の入力元／文字列整形と最新結果ID・出力履歴を定義','単に237見出しが決まったことを金額マッピング完了としない'],'出力履歴／計算版対応を新設する設計が必要。空欄0化は人給側の動作なので全セルをアプリで0埋めする新ルールを作らない。',['IF-T01/02/03/04/06','237列／固定順／文字列実型／先頭0／日付','11キーと内部GUID分離','約800行の欠落重複／タイムアウト','Excel出力取消・再試行と履歴対応'],'生成候補を識別し未送信ファイル／失敗出力を業務完了扱いにしない。前回出力履歴保持。','承認済み接続だけを用いたxlsx生成・配布方式と、列ごとの値設定マッピングは何か。','engineering/data-owner',[ev('docs/design/detailed/payroll-jinkyu-interface.md',7,48),ev('docs/design/detailed/payroll-jinkyu-interface.md',123,363)]),
group('G13','給与簿CSV取込・最新版照合・再出力','designblocked','固定1～5行、6行目以降、【合計情報】境界、原空欄保持して比較0、未知職員保持／確定阻止、失敗時前回成功保持、最新版照合と旧ゼロ失効、差分対応明細再出力。',['PD-03','PD-05','照合キー／多重行／出力行対応','I8エラー取得方式','差額符号／非数値表現'],['実CSVの文字コード・列・引用符・キー・行対応を確認','最新結果IDと同時更新検出・確定再検証を設計','差分⇔出力明細の多対多対応、エラー源と行IDを定義'],'給与簿は取込回ごとの読み取り専用スナップショット。既存163列と出力237列の1対1一致を仮定しない。',['IF-T07/08/09/12、JLINK-T03/05/06/08','未知／不足／余分／重複／空欄対0','途中失敗で前回成功維持','再計算中／照合中／確定直前の更新','多差分1出力行でも再出力重複なし'],'取込回・照合回を追跡し前回成功分を維持。過去照合を削除せず失効扱い。','通常・追給・控除を含む給与簿CSVと出力明細の対応サンプル／照合キーは何か。','data-owner/engineering',[ev('docs/design/detailed/payroll-jinkyu-interface.md',83,121),ev('docs/requirements/open-decisions.md',102,114)]),
group('G14','追給集約・返納分割回収','needsbusinessdecision','支払済不訂正、月別差額内訳と人給追給行の対応、確認待ち→給与班確定、給与相殺／告知書併用、複数回収・残額。',['PD-02','PD-03','PD-07','PERIOD-05とR10の両立'],['過去複数月集約と対象日のルール','差額式・税保険丸め・相殺限度／取消／過回収／完了条件','案件・月別内訳・回収実績の物理モデル'],'元支払を保持し新案件だけ作る。返納実績と差額確定状態を別保存。',['複数過去月・同月複数支給','分割2回＋相殺／告知併用','負値・過回収・取消・未完了','元支払不変／回収済＋残額整合'],'元給与に書き戻さない。回収実績訂正は未確定のため実績取消機能を勝手に作らない。','複数過去月を1追給行に集約したとき対象年月日はどう決めるか。返納取消等は別の未決として保持。','business',[ev('docs/requirements/payroll-confirmed-20261007.md',98,109),ev('docs/design/detailed/payroll-jinkyu-interface.md',62,77),ev('docs/requirements/open-decisions.md',90,90)]),
group('G15','業務認可・監査主体','designblocked','給与班全局、局担当自局記録と必要共通基本、業務管理者兼務とシステム管理分離。UI確認用変数は認可根拠にしない。',['PD-04','D-01','security changes out of scope'],['権威ある主体／所属／複数役割、所有共有とフロー認可設計','report/reopenの実行者Lookupを信頼できる主体から取得'],'今回ロール・権限設定は変更禁止。将来の試験ロール／所有・共有移行は別権限確認が必要。',['別局直接ID・フロー直呼び・同一人兼務','帳票／照合／CSV出力の全経路','報告者／差戻者が接続所有者に化けない'],'既存権限を拡張しない。別途承認後は最小権限差分と復元手順を保存。','実行者と局・役割を信頼できるどの属性から決定するか。','security-owner/engineering',[ev('docs/requirements/business-requirements.md',241,253),ev('docs/design/detailed/detailed-design.md',307,311)]),
group('G16','保存・障害復旧・非機能／総合受入','needsbusinessdecision','処理中各版、支払後の最終根拠・給与簿・支払実績・全照合回明細保持。架空データとローコード、単体結合の根拠。',['PD-06','D-07','NFR未決目標'],['保存期間・削除責任／復元・業務RTO/RPO・性能合否値','総合シナリオと独立期待結果を確定'],'中間版削除は可能という方針であって削除実行の許可ではない。最終根拠と照合履歴を切り離せる保存設計。',['中間版削除後の最終根拠と双方不一致額参照','復元／障害復旧','改修単位単体・影響結合・同一版読戻し','約800行を測定、未定性能閾値を創作しない'],'削除機能を実装／実行する前に復旧・参照整合と権限を確定。実データ移行は今回対象外。','運用上の保存期間・削除主体と総合試験シナリオ／性能合否値は何か。','business/operations',[ev('docs/requirements/payroll-confirmed-20261007.md',97,117),ev('docs/requirements/non-functional-requirements.md',23,57),ev('docs/requirements/open-decisions.md',90,95)]),
group('G17','現行HTML認定簿と既存読取機能','alreadyimplemented','既存の別タブHTML・ブラウザー印刷、動的163列、4履歴56列読取、ホームと既存勤怠の現行機能。存在と履歴の限定証拠であり全条件PASSではない。',[],['最新保存／公開版との同一性と変更影響範囲を読戻し'],'既存機能維持。新モデルの機能充足へ転用しない。',['現行の選定スモークと変更影響回帰','0/1/複数履歴、同月複数給与、NULL/0/負','HTML71表示・2ページ・GUID'],'直前snapshotと既存受入HTMLを保持。','業務質問なし。残る未照合条件は実機検証。','engineering',[ev('docs/handoff/STATUS.md',22,39),ev('docs/design/basic/data-model.md',29,46)]),
group('G18','レビュー提案・初回対象外','proposal','未承認の具体的動線／配置案と、初回対象外の本人・SKDB・家族・メモ・銀行等。確定した業務目標を撤回する意味ではない。',['explicitly proposed/out of initial scope'],['該当の具体操作が正本で承認されるまで実装対象へ昇格しない'],'なし。',['提案UIを確定要件として自動採用していないこと'],'なし。','この具体動線を採用するか。現在は追加で質問せず保留する。','business if/when selected',[ev('docs/requirements/payroll-confirmed-20261007.md',125,129)])]
G={x['id']:x for x in groups}
# Parent scope decision: no disabled/demo-only screen counts as a usable business feature.
G['G11']['status']='designblocked'
G['G11']['blockers']=['支給回／最新版結果／出力明細／照合結果の正式データadapter不在','正本の正式画面ID・物理列名未入力','全体を業務機能として提供するにはG12/G13/G15が必要']
G['G11']['confirmed_component_status']='implementnow_components_only_not_a_complete_business_feature'
G['G02']['scope_exclusion']='Issue #51の元M_職員基本は今回のsole-trial-app範囲外。実テーブル変更を承認済みと推定しない。'
# Classify all 100 operation records, preserving the original HTML and source labels.
proposal_ids={'OP-IMPORT-RETURN','OP-JLINK-HOME','OP-IMPORT-HOME','OP-001-DIFF','OP-007-HOME'}
fix_ids={'OP-002-TABS','OP-002-HISTORY','OP-002-PAYDETAIL','OP-005-RETURN','OP-005-MONTH','OP-005-DETAILS'}
ops=[]
for x in doc['operations']:
 id=x['operation_id']; s=sourceops[id]; gid='G17';status='alreadyimplemented';note='現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。'
 if s['source_classification']=='not_present_in_snapshot_planned':
  status='designblocked'
  if id in proposal_ids:gid='G18';status='proposal'
  elif id in {'OP-001-IMPORT','OP-IMPORT-VALIDATE','OP-IMPORT-APPLY'}:gid='G04';status='needsbusinessdecision'
  elif id.startswith('OP-AD-'):gid='G03'
  elif id.startswith('OP-E-'):gid='G05'
  elif id.startswith('OP-F-'):gid='G06'
  elif id.startswith('OP-G-'):gid='G09'
  elif id.startswith('OP-003-'):gid='G07'
  elif id.startswith('OP-006-'):gid='G08'
  elif id.startswith('OP-PAY-'):gid='G10';status='needsbusinessdecision'
  elif id.startswith('OP-RETRO-') or id.startswith('OP-REPAY-'):gid='G14';status='needsbusinessdecision'
  elif id in {'OP-001-JLINK','OP-JLINK-SELECT','OP-JLINK-TARGET','OP-JLINK-AM','OP-JLINK-FILTER'}:gid='G11'
  elif id=='OP-JLINK-EXPORT':gid='G12'
  elif id.startswith('OP-JLINK-') or id=='OP-JINKYU-PROCESS':gid='G13'
  else:raise Exception(id)
  note='保存ソースに当該業務操作なし。業務確定と実装可能性を分離し、下記の具体的依存契約が完了するまで本機能化しない。'
 if id in fix_ids:gid='G01';status='implementnow';note='既存ソースの操作は存在。SD-03/04または旧根拠文・固定サマリーの確認済み設計差分を最小修正し現行版で再試験する。'
 if id=='OP-002-SAVE':gid='G05';status='designblocked';note='Basic/Commuteの試験職員保存は部分実装。Work/Social/Tax保存は拒否。5区分保存全体は列・状態・権限設計待ち。'
 if id=='OP-002-EDIT':gid='G05';status='designblocked';note='読取／編集モードとドラフトはあるが、5区分の許可編集列／永続化が未完成。モード切替だけを業務編集完了としない。'
 if id=='OP-003-RETURN':gid='G07';status='designblocked';note='現行reopenは存在。給与班専属、実行者Lookup、未払い計算への失効連携は未完成。'
 if id=='OP-004-RATES':gid='G08';status='designblocked';note='SCR004は変数Setの試作。職員×期間の期末／勤勉別率の永続保存は存在しない。'
 if id in {'OP-F-NOPAY','OP-F-END'}:status='needsbusinessdecision';note='病欠時不支給と認定期間終了の区別は確定。対象期間／支給月対応や入力条件は未確定なので値を推定して保存しない。'
 if id in {'OP-PAY-ADJUST','OP-PAY-PAID','OP-REPAY-METHOD','OP-REPAY-RECORD','OP-RETRO-CONFIRM'}:status='designblocked';note='業務目的は確定済み。HTMLの提案表示だけで未承認業務としない。具体的な保存・識別・状態／例外処理設計が未完成。'
 if id=='OP-PAY-INDIVIDUAL':note='Q47の職員×支給回個別／所属一括確定とI12の支給回全体最新差分ゼロ条件の操作境界が未定。どちらかを捨てる解決は禁止。'
 if id=='OP-003-IMPORT-CURRENT':note='全置換取込の現行実装は存在。Q35/R12/R13の追加更新へ変更済みではない。旧バッチ保持は実装、削除記載はSD-06の文書矛盾。'
 if id=='OP-JINKYU-PROCESS':note='外部人給システムで担当者が行う手順。Canvas内自動実行・接続を依頼された機能と推定しない。取込／給与簿出力の業務接続仕様待ち。'
 g=G[gid]
 ops.append(dict(operation_id=id,title=x['title'],feature_group_id=gid,classification=status,classification_scope=('confirmed_current_fix' if status=='implementnow' else 'current_snapshot_core_only' if status=='alreadyimplemented' else 'whole_business_operation'),html_declared_status=x['declared_status'],source_classification=s['source_classification'],requirement_ids=x['requirement_ids'],readiness_reason=note,prerequisites=g['prerequisites'],migration=g['migration'],required_tests=g['tests'],rollback=g['rollback'],smallest_missing_question=g['smallest_missing_question'],question_owner=g['question_owner'],blocking_ids=g['blockers'] if status not in {'alreadyimplemented','implementnow'} else [],requirement_evidence=x['requirement_evidence'],source_evidence=s.get('source_evidence',[]),source_notes=s.get('notes'),end_to_end_runtime_pass=False))
O={x['operation_id']:x for x in ops}
# Every named requirement gets an individual row, including IDs without an HTML mapping.
# Broad requirements use the blocking whole contract; ready subclauses are linked separately.
def requirement_group(id):
 if id.startswith(('AD-','FR-AD-')):return 'G03'
 if id in {'AUTH-03','FR-AUTH-03','FUT-AUTH-003'}:return 'G18'
 if id.startswith(('AUTH-','FR-AUTH-','FUT-AUTH-','COMMON-AUTH-')):return 'G15'
 if id.startswith('E-'):
  n=int(id.split('-')[1]);return 'G03' if n in {1,9} else 'G04' if n in {2,3,4,5,11} else 'G05'
 if id=='FR-E-01' or id=='FUT-IMPORT-001':return 'G04'
 if id.startswith('FR-E-') or id in {'FUT-STATE-E','SCR002-E-001','SCR002-EDIT-001','SCR002-EDIT-002'}:return 'G05'
 if id in {'F-05','FR-F-04'}:return 'G17' # rendering exists, role/new-model clauses still not fulfilled
 if id.startswith(('F-','FR-F-')) or id in {'FUT-STATE-F','SCR002-F-001'}:return 'G06'
 if id=='G-03' or id=='FR-G-02':return 'G16'
 if id.startswith(('G-','FR-G-','SCR002-G-')) or id=='FUT-STATE-G':return 'G09'
 if id.startswith('PAYREQ-'):
  return {'01':'G02','02':'G02','03':'G05','04':'G05','05':'G06','06':'G07','07':'G10','08':'G13','09':'G15','10':'G16'}[id[-2:]]
 if id in {'PAY-01','PAY-02','SCR006-RULE-001'}:return 'G08'
 if id.startswith(('PAY-','FR-PAY-')) or id in {'FUT-STATE-PAY','SCR007-DIFF-001'}:return 'G14'
 if id.startswith('PERIOD-'):return 'G14' if id[-2:] in {'04','05'} else 'G10'
 if id.startswith('IF-'):
  n=int(id.split('-')[1]);return 'G11' if n==5 else 'G17' if n==10 else 'G13' if n in {9,11} else 'G16' if n==12 else 'G12'
 if id.startswith('JLINK-UI-'):
  return 'G13' if id[-2:] in {'06','07','09','10','11'} else 'G11'
 if re.fullmatch(r'I\d+',id):return 'G13' if id in {'I5','I7','I8','I9','I10','I12'} else 'G11'
 if id.startswith('NFR-'):return 'G18' if id=='NFR-N' else 'G15' if id=='NFR-J' else 'G16'
 if id.startswith('COMMUTE-'):return 'G17'
 if id in {'SCR002-LT-002','SCR002-LT-004','SCR002-LT-005','COMMON-NAV-003','COMMON-CONTEXT-002','SCR005-ACT-002','SCR005-ACT-005','SCR005-ACT-006','SCR005-UI-004','SCR005-UI-015'}:return 'G01'
 if id in {'R20','SCR002-PERF-001'}:return 'G01'
 if id in {'SCR005-CALC-003'}:return 'G02'
 return 'G17'
requirements=[]
for x in doc['requirements_reverse_index']:
 id=x['requirement_id'];gid=requirement_group(id);g=G[gid];status=g['status']
 es=[e for e in x['definition_evidence'] if 'traceability' not in e['path']];e=(es or x['definition_evidence'])[0]
 lines=(ROOT/e['path']).read_text().splitlines();definition=lines[e['line_start']-1]
 note='上位グループの全契約を判定。個別根拠と操作対応を保持。'
 scope='whole_requirement'
 if gid=='G17':
  status='alreadyimplemented';scope='existing_scope_core_only_not_full_acceptance';note='既存保存ソース／既存公開記録に対応する現行機能。現在公開Sourceの同一性は確認済みだが、条件網羅・runtime・全役割の合格を示さない。個別条件は下記partial_limitsで維持。'
 if gid=='G01':note='確定済み詳細設計に沿った修正または改修前後検証を直ちに行える。新しい業務仕様判断は不要。'
 if id in {'G-03','FR-G-02'}:note='二重申請防止方針はあるがアプリ内申請管理は作らない。具体的なアプリ機能／試験対象は未定。'
 if id in {'F-06'}:gid='G15';g=G[gid];status=g['status']
 if id in {'F-08','FR-F-03'}:status='needsbusinessdecision'
 if id in {'FUT-STATE-PAY','SCR007-DIFF-001','PAY-04'}:status='designblocked'
 if id=='COMMUTE-PARALLEL-001':note='並行配置は過去に実施し、後続COMMUTE-CUTOVER-001で撤去済み。再導入する要件ではない。';scope='historical_superseded'
 if id in {'AUTH-03','FR-AUTH-03','FUT-AUTH-003','NFR-N'}:scope='explicit_initial_scope_exclusion';note='初回対象外。proposal分類は確定済み除外を未確定へ戻す意味ではなく、実装バックログから外すため。'
 limits=[]
 if gid=='G17':
  limits=['公開v35のSource10件は公式Exportで再確認済み。最新未公開下書き・現在Dataverse行・実機条件の網羅は別途未確認。']
  if id.startswith('SCR002-') or id in {'R17','R18','R19','R22','R23'}:limits.append('0/1/複数履歴、163列末尾、同月複数、NULL/0/負、全幅／支援操作、失敗条件の未照合を個別に残す。')
  if id.startswith('SCR005-CALC-'):limits.append('内蔵仮例の契約だけ。新給与計算・税保険制度・Excel未精査式へ昇格しない。')
  if id in {'F-05','FR-F-04','SCR002-COM-003'}:limits.append('既存HTML／印刷は存在。給与班全局／局担当自局の実効認可と新モデル取得契約はG15/G06待ち。')
 if id=='IF-10':limits=['SCR002現行給与簿が読取り専用である証拠。新しいCSV取込先と全経路書込み禁止は未実装G13。'];scope='current_ledger_readonly_only'
 requirements.append(dict(requirement_id=id,definition_text=definition,definition_evidence=x['definition_evidence'],feature_group_id=gid,classification=status,classification_scope=scope,readiness_reason=note,partial_limits=limits,operation_ids=x['referencing_operation_ids'],explicit_html_mapping=x['explicit_id_mapped'],blocking_ids=g['blockers'] if status not in {'alreadyimplemented','implementnow'} else [],prerequisites=g['prerequisites'],migration=g['migration'],required_tests=g['tests'],rollback=g['rollback'],smallest_missing_question=g['smallest_missing_question'],question_owner=g['question_owner'],end_to_end_runtime_pass=False))
R={x['requirement_id']:x for x in requirements}
# Decision namespaces are retained: Q/R business answers, interface D/I, open IDs, and legacy app R do not alias.
def decision_group(x):
 ns=x['namespace'];id=x['id'];n=int(re.sub(r'\D','',id) or 0)
 if ns=='payroll_Q':
  return 'G02' if n<=12 else 'G05' if n<=27 else 'G06' if n<=33 else 'G07' if n<=39 else 'G10' if n<=47 else 'G13' if n<=52 else 'G14' if n==53 else 'G15' if n<=57 else 'G16'
 if ns=='payroll_R':return {1:'G16',2:'G13',3:'G14',4:'G13',5:'G13',6:'G13',7:'G16',8:'G16',9:'G12',10:'G14',11:'G05',12:'G07',13:'G07',14:'G07',15:'G15',16:'G16',17:'G16',18:'G14',19:'G05',20:'G10',21:'G15'}[n]
 if ns=='interface_D':return 'G12' if n<=3 else 'G10' if n<=6 else 'G14'
 if ns=='interface_I':return R[id]['feature_group_id']
 if ns=='legacy_app_R':return 'G01' if n in {3,4,5,13} else 'G17'
 if ns=='open':return {'D-01':'G15','D-02':'G05','D-03':'G10','D-04':'G07','D-05':'G01','D-06':'G06','D-07':'G16','D-08':'G14','PD-01':'G02','PD-02':'G10','PD-03':'G13','PD-04':'G15','PD-05':'G07','PD-06':'G16','PD-07':'G14','PD-08':'G03','PD-09':'G06'}[id]
 raise Exception(ns)
decisions=[]
for x in doc['decision_and_open_question_index']:
 gid=decision_group(x);g=G[gid];status=g['status']; note='確定済み回答を再質問しない。分類は回答の承認状態でなく、それを実現する全契約の準備状態。'
 if x['namespace']=='interface_D' and int(x['id'][1:])>=9:status='needsbusinessdecision';note='利用者指示で保留・未回答。今回式を選択せず、式精査再開時にD9から確認。'
 if x['namespace']=='legacy_app_R':note='旧25名／旧版固有条件は履歴のまま。後続の12桁番号、単一アプリ、10月1日ホーム4入口、10月7日通勤切替を優先。'
 if x['namespace']=='open' and x['id']=='D-05':status='designblocked';note='旧操作名未決の記述と、後続で実装されたSCR002支給明細入口を照合。既存遷移保持の修正をこの旧未決だけで止めない。'
 if x['namespace']=='open' and x['id']=='D-08':status='designblocked';note='独立画面先行は確定。最終的なタブ統合未決を理由に独立画面設計まで止めないが、計算／保存契約は別途必要。'
 decisions.append({**x,'feature_group_id':gid,'implementation_classification':status,'implementation_note':note,'blocking_ids':g['blockers'],'smallest_missing_question':g['smallest_missing_question'],'question_owner':g['question_owner']})
# Known legacy fields and new model must not be conflated.
G['G05']['known_current_56_columns']='現行4隔離表の15/26/9/6列の正式物理名・型・主キー・親Lookupは確認済み。field-readiness-56を参照。'
G['G05']['blockers']=['D-02: 現行列の明示的編集許可・状態別保存契約','Q17/Q18/Q27/R11: 訂正前後監査・再確認・未払い影響失効','PD-04: 現在callerの実効更新権限未検証（権限変更は範囲外）','PD-01/02: 新モデル再構成／特殊月の未確定。現行56物理列は既知。']
for item in ops:
 if item['feature_group_id']=='G05':item['blocking_ids']=G['G05']['blockers']
for item in requirements:
 if item['feature_group_id']=='G05':item['blocking_ids']=G['G05']['blockers'];item['partial_limits'].append(G['G05']['known_current_56_columns'])
for item in decisions:
 if item['feature_group_id']=='G05':item['blocking_ids']=G['G05']['blockers']
current_verification=json.loads((OUT/'current-source-verification.json').read_text())
issue51=json.loads((OUT/'issue51-readonly.json').read_text())
field_appendix_summary=json.loads((OUT/'field-readiness-56.json').read_text())['counts']

# Operation-specific unblockers are narrower than the group-level question.
q={
'OP-003-IMPORT':('engineering','旧有効バッチと入力の合成時、職員番号キー・No衝突・合成後999上限・必須空欄・対象報告処理中状態を既存契約にどう対応させるか。'),
'OP-003-RECOVER':('engineering','応答喪失／ステージング途中／活性化直後を識別する処理ID・状態・再実行契約は何か。'),
'OP-003-ROWEDIT':('engineering/business for boundary only','職員行追加の既定値・No割当て・最後の行削除の扱いを既存20列契約でどう定義するか。'),
'OP-003-RETURN':('engineering','給与班主体をどこから信頼して取得し、差戻者Lookupと未払い再計算対象へどう結ぶか。'),
'OP-004-RATES':('engineering','職員×対象期間の2率を保存する正式テーブル／列、精度と入力範囲は何か。'),
'OP-006-RULE':('engineering/business for rule applicability','単価／区分マスタの正式項目と適用期間・改定対象の契約は何か。'),
'OP-006-END':('engineering','使用停止／終了日をどの既存または新規正式列で保存し、過去参照を維持するか。'),
'OP-E-PENDING':('engineering','確認待ち対象を判定する正式状態列と候補／職員への対応は何か。'),
'OP-E-HISTORY':('engineering','新履歴の編集許可列・有効期間検証・親GUIDと番号対応・前履歴を保持する保存経路は何か。'),
'OP-E-CORRECT':('engineering','訂正前後監査と確認待ちへの復帰、影響未払い結果の失効をどの保存処理で一貫させるか。'),
'OP-E-SUBMIT':('engineering','確認待ちに移す必須列検証・正式状態コード・同時更新条件は何か。'),
'OP-E-RETURN':('engineering','差戻し状態と戻し主体の保存先、元入力を失わず再提出する経路は何か。'),
'OP-E-CONFIRM':('engineering','確定／再確定の許可条件と必要情報検証、権威ある給与班主体、未払い結果失効の契約は何か。'),
'OP-F-EDIT':('engineering/business for input rules','ヘッダー／経路の入力列・必須検証・保存先は何か。'),
'OP-F-SUBMIT':('engineering/business for validation','提出を許可する必須項目・検証条件と新認定への状態保存契約は何か。'),
'OP-F-RETURN':('engineering','差戻しの正式状態・担当主体・提出者対応をどこへ保存するか。理由連絡をアプリ外から変更しない。'),
'OP-F-CERTIFY':('engineering','認定状態の保存先と認定期間／登録額の検証、給与計算の認定済参照契約は何か。'),
'OP-F-CHANGE':('engineering','新旧認定GUID・期間・精算案件を関連付ける正式契約は何か。'),
'OP-F-NOPAY':('business','病気／欠勤のどの期間をどの支給月・経路へ対応させるか。精算式は推測しない。'),
'OP-F-END':('business','認定期間終了日の境界と届出・給与班確認に必要な入力は何か。独立終了状態は追加しない。'),
'OP-G-REGISTER':('business/data-owner','各外部決定の必須登録内容・証憑の扱い・給与への適用日を示す資料は何か。'),
'OP-G-CONFIRM':('engineering/business for application date','外部決定結果の正式状態と確定後適用時点をどの列／計算版へ結ぶか。'),
'OP-PAY-PERIOD':('business','対象年月日の具体日と採用日境界、支給日の例外設定ルールは何か。'),
'OP-PAY-INDIVIDUAL':('business','Q47の職員単位／所属一括確定とI12の支給回全体最新差分ゼロを、同じ確定操作のどの単位で両立させるか。'),
'OP-PAY-ADJUST':('engineering','理由・処理者・対象項目・調整額を結果本体と分離して保存し、最新結果／照合を失効させる正式契約は何か。'),
'OP-PAY-PAID':('engineering','支払い済みの記録項目・実施証拠・状態保存と最終根拠の凍結契約は何か。支払い実行機能は追加しない。'),
'OP-001-JLINK':('engineering','支給回と最新版結果を読み出す正式データ源／識別子を定義する。3タブ自体を再質問しない。'),
'OP-JLINK-SELECT':('engineering','選択支給回・支給日・期間・状態の実データadapterをどの正式モデルで提供するか。'),
'OP-JLINK-TARGET':('engineering/data-owner','出力明細IDと職員、差分行の対応は何か。初回全職員／絞込みは確定済み。'),
'OP-JLINK-AM':('engineering','一括／明細別A/Mを保持する出力明細の安定IDと出力履歴adapterは何か。手動判断の方針は再確認しない。'),
'OP-JLINK-EXPORT':('engineering/data-owner','237列の値設定元／整形、低コード生成方式、保存配布先と出力処理履歴を定義する。'),
'OP-JLINK-IMPORT':('data-owner/engineering','給与簿CSVの文字コード・ヘッダー列・行識別・成功版切替を確定できるサンプルは何か。'),
'OP-JLINK-RECONCILE':('data-owner/engineering','給与簿側の照合キー／多重行対応と最新結果ID・更新検知・差分明細保存の正式契約は何か。'),
'OP-JLINK-FILTER':('engineering/business for display convention','比較結果の実データ源、差額符号と非数値差分の表示値契約を定義する。6列と差分既定は確定済み。'),
'OP-JLINK-CORRECT':('engineering','差分原因を勤務条件／通勤等の正しい職員・履歴へ結ぶIDと、戻り支給回コンテキストの契約は何か。'),
'OP-JLINK-CORRECT-ATT':('engineering','勤怠差分を局×月の報告ID／職員行へ結ぶ対応と、戻り支給回コンテキストの契約は何か。'),
'OP-JLINK-RETURN':('engineering','入力画面から返す安定支給回ID／職員IDと訂正後失効の通知契約は何か。'),
'OP-JLINK-RETURN-ATT':('engineering','勤怠画面から返す安定支給回ID／職員IDと訂正後失効の通知契約は何か。'),
'OP-JLINK-REEXPORT':('data-owner/engineering','複数差分項目と1出力明細を重複なく対応させるキー／集約契約は何か。A/Mは自動変更しない。'),
'OP-JLINK-ERROR':('data-owner/engineering','人給インポートエラーをどの形式・取得方法・行IDで受け取れるか（I8）。'),
'OP-JLINK-CONFIRM':('engineering','全支給回の最新結果IDと照合回を確定時に再検証し、同時更新・未解決行を拒否する保存契約は何か。'),
'OP-JLINK-HISTORY':('engineering','処理回の日時・実行者・件数・版／取込ID・不一致双方額を、中間版削除後も残す物理保存契約は何か。'),
'OP-RETRO-EXPORT':('business','複数過去月の追給を集約した行の対象年月日と月別内訳対応をどう両立させるか。'),
'OP-RETRO-CONFIRM':('engineering','選択差額結果・内訳・確認主体・確定状態を支給／返納実績と分離する正式保存契約は何か。'),
'OP-REPAY-METHOD':('engineering','返納案件と給与班指定の相殺／告知書方法を複数回収へ結ぶ保存契約は何か。'),
'OP-REPAY-RECORD':('business/engineering','回収日・方法・額の保存先と、取消／過回収／完了判定／相殺限度をどう扱うか。')}
for id,(owner,question) in q.items():O[id]['question_owner']=owner;O[id]['smallest_missing_question']=question
ready_actions=[
 {'id':'READY-01','title':'検索結果・ページ・職員・月の往復保持','requirement_ids':['SCR002-LT-002','COMMON-NAV-003','COMMON-CONTEXT-002','SCR005-ACT-002'],'finding_ids':['SD-04'],'classification':'implementnow','scope':'既存動作修正。新スキーマ・業務ルールなし。','group_id':'G01'},
 {'id':'READY-02','title':'タブ別履歴選択保持','requirement_ids':['SCR002-LT-004','SCR002-LT-005','SCR002-EDIT-003'],'finding_ids':['SD-03'],'classification':'implementnow','scope':'既存History.RecordIdを区分別に保持。選択職員／取得版が変わった時だけ妥当性再検証。','group_id':'G01'},
 {'id':'READY-03','title':'試算旧根拠消去と固定サマリー','requirement_ids':['SCR005-ACT-005','SCR005-ACT-006','SCR005-UI-004','SCR005-UI-015'],'finding_ids':[],'classification':'implementnow','scope':'既存内蔵仮例の表示修正。本給与計算式・制度判断は変更しない。','group_id':'G01'},
 {'id':'READY-04','title':'現行通勤保存のGUID対象解決','requirement_ids':['SCR002-EDIT-002','SCR002-EDIT-003'],'finding_ids':['SD-12'],'classification':'implementnow','scope':'既存通勤の許可列・試験職員ゲートを保持し、Title解析による対象解決を既存RecordIdのGUID照合へ限定修正。5区分保存全体の完成ではない。','prerequisites':['現行ソースでRecordId=Text(p.T_通勤_STUDIO)を再確認','保存前に対象GUID・職員番号・親職員／取得対象の対応を検証','対象違いは保存前に拒否。既存の部分保存問題や監査不足を成功に読み替えない'],'migration':'なし。既存_GUID／既存列のみ。','required_tests':['同職員内の重複認定ID／同じTitleを別GUIDで作る','Title変更後も正しいGUID1件だけ保存','別職員GUID・不存在・不正GUID・旧選択はPatchなし','既存試験番号ゲート維持・入力失敗時保持・保存後再取得'],'rollback':'対象式の直前版と隔離テスト行の前値を保持。5区分解放・列追加・実データは行わない。','source_evidence':[{'path':'Src/scrStaffMasterSearch.pa.yaml','line_start':1318,'provenance':'SHA-verified Oct7 source snapshot'},{'path':'Src/scrStaffMasterSearch.pa.yaml','line_start':686,'provenance':'SHA-verified Oct7 source snapshot'},ev('docs/design/detailed/detailed-design.md',119,132)]},
 {'id':'READY-05','title':'勤怠旧バッチ保持の文書矛盾解消','requirement_ids':['SCR003-IMPORT-001'],'finding_ids':['SD-06'],'classification':'implementnow','scope':'config import_contract.replacementのthen remove superseded rowsを、実装・テスト・現行データ設計の旧バッチ保持へ整合。追加更新機能の実装完了を意味しない。','migration':'なし。文書契約だけ。','required_tests':['tests/automation/test_scr003_flow.pyの非破壊条件とフローDeleteRecord不存在を照合','将来追加更新要件と現行全置換を別記'],'rollback':'この文言差分のみ復元。','group_id':'G07'}]
component_only=[
 {'id':'COMP-01','requirement_ids':['JLINK-UI-01','JLINK-UI-02','I3'],'confirmed':'同一画面3タブ・支給回コンテキスト保持・計算版選択なし','not_ready_because':'支給回の正式データadapter未定','deliver_as_feature':False},
 {'id':'COMP-02','requirement_ids':['JLINK-UI-03','JLINK-UI-04','JLINK-UI-05','I1','I2','I4','IF-05'],'confirmed':'初回全職員・対象変更・一括／行別A/M・出力前4件数確認','not_ready_because':'出力明細ID／最新版結果／生成／出力履歴が未設計','deliver_as_feature':False},
 {'id':'COMP-03','requirement_ids':['JLINK-UI-08','I6','I11'],'confirmed':'差分のみ初期表示、全件切替、指定6列','not_ready_because':'比較行adapter・差額符号／非数値表示未定','deliver_as_feature':False},
 {'id':'COMP-04','requirement_ids':['IF-01','IF-02','IF-03','IF-04','IF-07','IF-08'],'confirmed':'237見出しと11キー、1行目見出し／2行目から文字列・日付形式','not_ready_because':'列ごとの値設定・低コードxlsx生成／配布経路未定','deliver_as_feature':False},
 {'id':'COMP-05','requirement_ids':['PAYREQ-06'],'decision_keys':['payroll_Q:Q35','payroll_R:R12','payroll_R:R13'],'confirmed':'掲載行上書き・非掲載保持・空欄消去／0区別のmerge意味論','not_ready_because':'行No衝突・合成上限・処理中／失敗状態・再実行契約未完成','deliver_as_feature':False}]
for g in groups:
 g['operation_ids']=[o['operation_id'] for o in ops if o['feature_group_id']==g['id']]
 g['requirement_ids']=[r['requirement_id'] for r in requirements if r['feature_group_id']==g['id']]
 g['decision_keys']=[r['decision_key'] for r in decisions if r['feature_group_id']==g['id']]
future=[o for o in ops if o['source_classification']=='not_present_in_snapshot_planned']
counts={
 'feature_groups':len(groups),'operations':len(ops),'named_requirements':len(requirements),'decision_records':len(decisions),
 'future_source_absent_operations':len(future),'operation_classification':dict(collections.Counter(o['classification'] for o in ops)),
 'future_operation_classification':dict(collections.Counter(o['classification'] for o in future)),
 'requirement_classification':dict(collections.Counter(o['classification'] for o in requirements)),
 'decision_implementation_classification':dict(collections.Counter(o['implementation_classification'] for o in decisions)),
 'ready_current_correction_actions':len(ready_actions),'confirmed_nonreleasable_components':len(component_only),
 'unmapped_named_requirements_preserved':sum(not r['explicit_html_mapping'] for r in requirements)}
assert len(ops)==100 and len(requirements)==240 and len(decisions)==136 and len(future)==59
assert len(O)==100 and len(R)==240 and len({x['decision_key'] for x in decisions})==136
assert {x['requirement_id'] for x in requirements}=={x['requirement_id'] for x in doc['requirements_reverse_index']}
assert all(o['feature_group_id'] in G for o in ops)
result={
 'task_id':'PAY-IMPLEMENT-001','artifact_type':'read_only_implementation_readiness_inventory','generated_at_utc':'2026-10-10T00:33:00Z',
 'target':{'environment':'StaffMaster-Automation-Test','app_id':'204a48dc-7f23-43dd-b934-4654a3cfa306'},
 'baseline_main_commit':COMMIT,'source_provenance':{k:v for k,v in src['provenance'].items() if k not in {'recovery_library_id','warning'}},'current_source_verification':current_verification,'issue51_readonly':issue51,'field_readiness_56':field_appendix_summary,
 'scope_exclusions':['本番・安定版・実データ','本番公開／main統合','新たな業務・制度判断','セキュリティ／共有／ロール設定','Issue #51元M_職員基本への変更'],
 'classification_definitions':{
  'implementnow':'確定詳細設計と既存物理契約で成立する現行機能の具体的修正／検証。最新読戻し・隔離試験前提。実装完了／runtime PASSではない。',
  'designblocked':'目的／操作は確定。全体として使える業務機能には、記載した物理列／adapter／キー／状態／失敗／同時更新等の設計が必要。既答を再質問しない。',
  'needsbusinessdecision':'確定済みの目的は維持しつつ、式・境界・例外・入力必須条件・運用目標等の未確定な業務判断が不可欠。保留式は再開指示まで触らない。',
  'alreadyimplemented':'保存snapshotまたは対象過去記録に現行coreが存在する。新要件全部・現行live・実効認可・全条件PASSを意味しない。classification_scope/partial_limitsを必ず併読。',
  'proposal':'具体操作がレビュー提案のみ、または初回対象外。後者は承認済みの除外を保つ意味。'},
 'methodology':['100操作・240明示要件・136名前空間付き決定を別々に全数列挙。I1～I12は元監査の要件集合にも含まれるため決定集合との単純合算はしない。','「future」やHTML declared_statusから一律に分類せず、確定要件・設計・現行コードを照合した。','表示だけ／無効ボタンだけのJLINK shellを使える新業務機能として数えない。UI純粋部分はconfirmed_component_onlyへ分離。','一般の技術設計は資料と既存契約から進められる。未入力の業務状態・権限・制度規則を任意に埋めない。現行56列の物理名・型・GUIDは既知としてfield-readiness-56で個別評価し、新モデル未設計と混同しない。','公式Exportで現在公開v35 package SHAと対象Source10件を検証。Oct7保存Sourceとのbyte一致により静的所見を現行公開Sourceへ対応づける。保存package SHAと公開package SHAはなお異なる。実機動作／実効権限の合格にはしない。','新たなreadinessの判定を旧受入PASSへ転記しない。未照合は未実装と断定しない。'],
 'input_files':[{'audit_artifact':f,'sha256':hashlib.sha256((AUDIT/f).read_bytes()).hexdigest()} for f in ['docs-html-matrix.json','source-data-matrix.json','source-findings.json']],
 'counts':counts,'feature_groups':groups,'ready_current_corrections':ready_actions,'confirmed_component_only':component_only,
 'operations':ops,'requirements':requirements,'decisions':decisions,'source_findings':findings,
 'closest_next_full_feature':{'group_id':'G07','title':'勤怠追加更新取込','existing_reusable_design':['20列と型／NULL／番号正規化','報告×局×月','同一フロー直列化','expectedVersion','ステージング全件検証→activebatch切替→旧バッチ保持'],
 'specific_design_work':['新要件での職員番号キー採用を明記','保持行と入力行のNo衝突・合成件数上限を解決','対象報告の処理中・不完全状態と共有UI停止','処理ID／活性化前後失敗／応答喪失の復旧','監査主体と将来未払い結果失効の境界'],
 'do_not_invent':['合成時に黙ってNoを再採番','999を超える行を切捨て','途中成功を利用可にする','UI選択局を実効認可にする']},
 'validation':{'coverage_counts':'PASS','unique_ids':'PASS','no_source_edits':True,'remote_writes':False,'live_tests_run':False,'current_published_source_byte_comparison':'PASS: 10/10','field_readiness_56':'PASS: 56/56, no inferred permissions'}}
(OUT/'readiness-inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(OUT/'future-operations-59.json').write_text(json.dumps(future,ensure_ascii=False,indent=2)+'\n')
# Human-readable group-first report and explicit row inventories.
def compact(s):return str(s).replace('|','／').replace('\n',' ')
md=['# PAY-IMPLEMENT-001 実装準備インベントリ','',
 '基準: main '+COMMIT+'。対象は StaffMaster-Automation-Test の単一試験アプリ 204a48dc-7f23-43dd-b934-4654a3cfa306。読取り調査のみ。','',
 '## 結論','',
 '使える全機能として今進められる範囲は、既存の検索往復・履歴選択保持、試算の旧根拠消去／固定サマリー、既存通勤保存のGUID対象解決などの確定済み差分修正。新しい人給画面を表示のみで完成扱いにしない。',
 '59件の保存ソース未存在操作は個別に点検し、'+str(counts['future_operation_classification'])+'。確定済みのUI要素は別に残した。業務回答をやり直すための一律保留ではなく、実利用できる操作ごとの最小依存を示す。',
 '最も実装に近い次のまとまりは勤怠追加更新取込。既存20列・職員番号一意・直列フロー・expectedVersion・activebatch切替は再利用できるが、合成時のNo衝突／上限、処理中／失敗と復旧の契約が不足する。',
 'Issue #51の元M_職員基本は今回の試験アプリ範囲外。元表への列追加・型推定・完了処理を行わない。','',
 '## 判定の読み方','']
for k,v in result['classification_definitions'].items():md.append('- **'+k+'**: '+v)
md+=['','100操作、240明示要件、136決定記録を各別に列挙。102件のHTML直接対応なし要件も省略しない。既存機能のalreadyimplementedは現行coreの限定証拠であり、現在公開Sourceの同一性をruntime／全条件PASSへ読み替えない。','',
 '現在公開v35の公式Export: package SHA 465dcdc2eec6deb181f8df811558bdade4f0b6494675346e1cac700d90f1a740。全10 Sourceのbyte一致とDataSources一致を検証。runtime全件PASSではない。', '', '現行履歴56列の追加評価: 全56列の物理名・型・更新可能schemaは既知。形式契約42列、領域値未確定12列、Q16入力対象外2列。限定保存は許可列／訂正監査などの契約が未充足。field-readiness-56.md参照。', '', '## 1. 機能グループ別','']
for g in groups:
 md+=['### '+g['id']+' '+g['title']+' ['+g['status']+']','',g['confirmed_scope'],'',
 '依存: '+('、'.join(g['blockers']) or '業務上の未決なし。最新readbackと試験は必要。'),
 '前提: '+' / '.join(g['prerequisites']),
 '移行: '+g['migration'],
 '検証: '+' / '.join(g['tests']),
 '復元: '+g['rollback'],
 '最小の未充足事項（'+g['question_owner']+'）: '+g['smallest_missing_question'],
 '要件ID: '+', '.join(g['requirement_ids']),
 '操作ID: '+', '.join(g['operation_ids']),
 '決定: '+', '.join(g['decision_keys']),
 '証拠: '+' / '.join(f"{e['path']}:{e['line_start']}-{e['line_end']}" for e in g['evidence']),'']
md+=['## 2. 今すぐ進められる既存機能修正','']
for a in ready_actions:
 md+=['### '+a['id']+' '+a['title'],', '.join(a['requirement_ids']),a['scope'],'']
 if 'required_tests' in a:md+=['試験: '+' / '.join(a['required_tests']),'復元: '+a['rollback'],'']
md+=['## 3. 確定済みだが単独リリースしない部品','']
for a in component_only:md+=['- '+a['id']+' '+', '.join(a['requirement_ids'])+': '+a['confirmed']+'。未充足: '+a['not_ready_because']+'。']
md+=['','## 4. 全100操作の列挙','', '| 操作ID | 内容 | 判定 | 群 | 最小依存・確認 |','|---|---|---|---|---|']
for o in ops:md.append('| '+' | '.join(compact(v) for v in [o['operation_id'],o['title'],o['classification'],o['feature_group_id'],o['smallest_missing_question'] if o['classification'] not in {'alreadyimplemented','implementnow'} else o['readiness_reason']])+' |')
md+=['','## 5. 全240明示要件の列挙','', '各行の要件原文・全定義リンク・操作対応・前提・移行・試験・復元はreadiness-inventory.jsonに完全収録。未対応IDを機能欠落と短絡しない。','', '| 要件ID | 判定 | 群 | 証拠 | 対応操作 |','|---|---|---|---|---|']
for r in requirements:
 e=r['definition_evidence'][0]
 md.append('| '+' | '.join(compact(v) for v in [r['requirement_id'],r['classification'],r['feature_group_id'],e['path']+':'+str(e['line_start']),', '.join(r['operation_ids']) or 'HTML直接対応なし。正本個別確認'])+' |')
md+=['','## 6. 全136決定記録の列挙','', '決定の承認状態と実装準備状態は別。Q/R回答を再質問しない。D9以降の保留を維持する。','', '| 名前空間付きID | 原決定状態 | 実装準備 | 群 | 正本 |','|---|---|---|---|---|']
for d in decisions:md.append('| '+' | '.join(compact(v) for v in [d['decision_key'],d['state'],d['implementation_classification'],d['feature_group_id'],d['source']['path']+':'+str(d['source']['line_start'])])+' |')
md+=['','## 7. 証拠の境界と検証','',
 '- 保存snapshot: '+src['provenance']['saved_at_utc']+'。SHA '+src['provenance']['after_msapp_sha256'],
 '- 過去公開package SHA: '+src['provenance']['publication_package_sha256']+'。保存SHAと同一視しない。',
 '- 現在公開v35の公式Export・Source10件・DataSourcesの一致を確認。最新未公開下書き・現在Dataverse行・操作時認可・Studio/Playerの実機試験は別途未確認。',
 '- ソース編集、ブラウザー操作、外部更新、公開、main統合は実施していない。manual-20261010-readiness配下の成果物のみ。',
 '- カバレッジ: 100/100操作、59/59未来操作、240/240要件、136/136決定。ID重複なし。','',
 '## 8. 成果物','',
 '- readiness-inventory.json: 詳細な全件台帳',
 '- future-operations-59.json: 保存ソース未存在59操作の抽出',
 '- build_readiness_inventory.py: 台帳再生成と全件数検証',
 '- readiness-summary.json: 件数・coverage検証', '- field-readiness-56.json / .md: 現行56列の個別保存準備', '- current-source-verification.json: 公式v35 ExportのSourceとDataSources一致', '- issue51-readonly.json: Issue #51 / ABS-RATE-001の最新読取、型等は未定', '']
(OUT/'readiness-inventory.md').write_text('\n'.join(md))
(OUT/'readiness-summary.json').write_text(json.dumps({'task_id':'PAY-IMPLEMENT-001','counts':counts,'validation':result['validation']},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(counts,ensure_ascii=False,indent=2))
