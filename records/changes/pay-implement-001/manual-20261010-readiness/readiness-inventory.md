# PAY-IMPLEMENT-001 実装準備インベントリ

基準: main 252abe4aa5d3b1d99a584a30c97d9b48153c91f5。対象は StaffMaster-Automation-Test の単一試験アプリ 204a48dc-7f23-43dd-b934-4654a3cfa306。読取り調査のみ。

## 結論

使える全機能として今進められる範囲は、既存の検索往復・履歴選択保持、試算の旧根拠消去／固定サマリー、既存通勤保存のGUID対象解決などの確定済み差分修正。新しい人給画面を表示のみで完成扱いにしない。
59件の保存ソース未存在操作は個別に点検し、{'needsbusinessdecision': 10, 'designblocked': 44, 'proposal': 5}。確定済みのUI要素は別に残した。業務回答をやり直すための一律保留ではなく、実利用できる操作ごとの最小依存を示す。
最も実装に近い次のまとまりは勤怠追加更新取込。既存20列・職員番号一意・直列フロー・expectedVersion・activebatch切替は再利用できるが、合成時のNo衝突／上限、処理中／失敗と復旧の契約が不足する。
Issue #51の元M_職員基本は今回の試験アプリ範囲外。元表への列追加・型推定・完了処理を行わない。

## 判定の読み方

- **implementnow**: 確定詳細設計と既存物理契約で成立する現行機能の具体的修正／検証。最新読戻し・隔離試験前提。実装完了／runtime PASSではない。
- **designblocked**: 目的／操作は確定。全体として使える業務機能には、記載した物理列／adapter／キー／状態／失敗／同時更新等の設計が必要。既答を再質問しない。
- **needsbusinessdecision**: 確定済みの目的は維持しつつ、式・境界・例外・入力必須条件・運用目標等の未確定な業務判断が不可欠。保留式は再開指示まで触らない。
- **alreadyimplemented**: 保存snapshotまたは対象過去記録に現行coreが存在する。新要件全部・現行live・実効認可・全条件PASSを意味しない。classification_scope/partial_limitsを必ず併読。
- **proposal**: 具体操作がレビュー提案のみ、または初回対象外。後者は承認済みの除外を保つ意味。

100操作、240明示要件、136決定記録を各別に列挙。102件のHTML直接対応なし要件も省略しない。既存機能のalreadyimplementedは現行coreの限定証拠であり、現在公開Sourceの同一性をruntime／全条件PASSへ読み替えない。

現在公開v35の公式Export: package SHA 465dcdc2eec6deb181f8df811558bdade4f0b6494675346e1cac700d90f1a740。全10 Sourceのbyte一致とDataSources一致を検証。runtime全件PASSではない。

現行履歴56列の追加評価: 全56列の物理名・型・更新可能schemaは既知。形式契約42列、領域値未確定12列、Q16入力対象外2列。限定保存は許可列／訂正監査などの契約が未充足。field-readiness-56.md参照。

## 1. 機能グループ別

### G01 現行検索・履歴・試算UIの明確な差分 [implementnow]

既存の検索結果・ページ・職員・月保持、タブ別履歴キー保持、SCR005の固定サマリーと旧算定根拠消去。旧式の単純再利用ではなく最新読戻しとの差分修正。

依存: 業務上の未決なし。最新readbackと試験は必要。
前提: 編集前の同一App IDの最新下書き、ソースSHA、隔離接続先を照合 / 未保存破棄確認と失敗時入力保持を維持
移行: DB移行なし。最小の変更コントロール／依存式だけを保存する。
検証: 検索1/0/複数件・ページ2→005→002 / 区分別複数履歴の選択→別タブ→復帰 / 保存失敗・破棄取消・連続操作 / 未登録月・登録0円・別職員・失敗時に旧数値／根拠なし / 幅900/1366/1920・200%・最終行到達
復元: 変更直前の同一アプリパッケージと対象式を保存し、変更分だけ復元。現在の依頼は同一試験アプリへの公開を明示承認済み。main統合・本番公開は範囲外。
最小の未充足事項（engineering）: 業務質問なし。差分の現行版再現だけが必要。
要件ID: COMMON-CONTEXT-002, COMMON-NAV-003, R20, SCR002-LT-002, SCR002-LT-004, SCR002-LT-005, SCR005-ACT-002, SCR005-ACT-005, SCR005-ACT-006, SCR005-UI-004, SCR005-UI-015
操作ID: OP-002-TABS, OP-002-HISTORY, OP-002-PAYDETAIL, OP-005-MONTH, OP-005-DETAILS, OP-005-RETURN
決定: open:D-05, legacy_app_R:R03, legacy_app_R:R04, legacy_app_R:R05, legacy_app_R:R13
証拠: docs/design/detailed/detailed-design.md:97-134 / docs/requirements/open-decisions.md:10-17

### G02 職員基本・組織・予算と履歴の新モデル [designblocked]

一人一行、GUID Lookup＋12桁番号、最新基本と有効期間履歴、階層なし組織、所属既定予算と履歴個別予算、住所、採用日給与対象時必須。

依存: PD-01、D-02、Issue #51
前提: 新旧列対応と型・精度・既定値・主列・一意制約・保存経路を確定 / M_職員基本変更前にIssue #51を再確認し同時処理計画へ組込
移行: 旧_STUDIOは保持。新モデルの列契約とテスト行移行を独立して読戻し。既存12接続表を完成新モデルとしない。
検証: 12桁先頭0・重複拒否・GUIDと番号不一致 / 同一人の再雇用・月途中履歴・住所更新 / 所属予算と個別上書き / Issue #51の実列と独立欠勤単価読戻し
復元: マッピングと元テスト行を退避。旧接続へ戻す。新表を即削除せず旧履歴を保持。
最小の未充足事項（engineering）: 新モデルの各列を既存列へ対応させた物理辞書はどれか。未存在なら設計を作りレビューする。
要件ID: PAYREQ-01, PAYREQ-02, SCR005-CALC-003
操作ID: 
決定: payroll_Q:Q1, payroll_Q:Q2, payroll_Q:Q3, payroll_Q:Q4, payroll_Q:Q5, payroll_Q:Q6, payroll_Q:Q7, payroll_Q:Q8, payroll_Q:Q9, payroll_Q:Q10, payroll_Q:Q11, payroll_Q:Q12, open:PD-01
証拠: docs/design/basic/data-model.md:48-92 / docs/requirements/payroll-confirmed-20261007.md:32-43 / docs/requirements/open-decisions.md:84-84

### G03 採用前・発令自動候補の連携 [designblocked]

発令登録完了時の候補、採用ごとの識別子、番号後反映、採用取消は履歴保持・計算除外。自動連携は実現性確認目標。

依存: PD-08、PD-01、AD連携方式
前提: 異動情報アプリ通知／取得仕様と安定採用IDを入手 / 番号未発行候補と一人一行職員基本の分離・統合契約
移行: 候補領域を別に設計し、番号未発行行を無条件に職員基本へ作らない。
検証: 重複通知・番号遅延・再採用別ID / 確定前・後の取消 / 給与班修正と外部変更の競合 / 決裁だけでは候補作成しない
復元: 取込回／外部IDの対応を保存し再適用可能にする。候補を物理削除しない。
最小の未充足事項（source-owner/engineering）: 発令登録完了イベントと採用ごとの不変IDをどの正式インターフェースから取得できるか。
要件ID: AD-01, AD-02, AD-03, AD-04, AD-05, AD-06, AD-07, AD-08, AD-09, AD-10, E-01, E-09, FR-AD-01, FR-AD-02, FR-AD-03, FR-AD-04
操作ID: OP-AD-CANDIDATE, OP-AD-NUMBER, OP-AD-CHANGE, OP-AD-CANCEL
決定: open:PD-08
証拠: docs/requirements/business-requirements.md:40-67 / docs/requirements/open-decisions.md:91-91

### G04 E専用Excel取込と確認待ち候補 [needsbusinessdecision]

人単位で一律拒否せず内容重複注意、正常行先行、不備行を給与班が判断、専用画面入口。PoCとは別機能。

依存: E-03、E-05、PD-01、PD-08
前提: 異動Excel正式列・不備条件・内容一致／重複可能性基準を入手 / 行別処理回・確認待ち候補保存設計
移行: E用ステージングと判断履歴を設計。SCR003勤怠の全件検証方式をEに流用しない。
検証: 既存人の新履歴は許容 / 正常行＋重複／不備混在 / 行見送り／採用・再取込・外部値競合 / 給与班確定前は計算不可
復元: 取込回単位に追跡。適用済み行を勝手に取消せず、隔離行のみ元状態へ戻す。
最小の未充足事項（business/data-owner）: E取込で内容一致／重複可能性と必須不足を判定する列と条件は何か。
要件ID: E-02, E-03, E-04, E-05, E-11, FR-E-01, FUT-IMPORT-001
操作ID: OP-001-IMPORT, OP-IMPORT-VALIDATE, OP-IMPORT-APPLY
決定: 
証拠: docs/requirements/business-requirements.md:70-122 / docs/requirements/screen-requirements.md:419-425

### G05 勤務条件・保険・税・固定控除の登録確認 [designblocked]

実変更は新期間履歴、誤登録は前後記録して訂正、登録→確認待ち→給与班確定・差戻し、未払い再計算。月別住民税・保険確認と控除期間を分離。

依存: D-02: 現行列の明示的編集許可・状態別保存契約、Q17/Q18/Q27/R11: 訂正前後監査・再確認・未払い影響失効、PD-04: 現在callerの実効更新権限未検証（権限変更は範囲外）、PD-01/02: 新モデル再構成／特殊月の未確定。現行56物理列は既知。
前提: 編集可能列・検証と状態コード・監査前後値・保存先を確定 / 未払い結果失効と給与班確認経路を設計
移行: 既存56列の読取接続をそのまま保存対象としない。住民税月列→月別行等は明示変換と行数照合。
検証: 期間変更と誤訂正を分離 / 未確認／非加入／加入、NULL／0 / 確認待ちを計算へ使わない / 確定後訂正で再確認・未払い失効 / 保存失敗はドラフト保持
復元: 変更前後監査とテスト元行を保存。途中反映の再実行契約ができるまで本保存を有効化しない。
最小の未充足事項（engineering; business only for listed policy exceptions）: 新モデルの許可編集列・検証条件・状態／監査の正式保存契約は何か。
要件ID: E-06, E-07, E-08, E-10, E-12, FR-E-02, FR-E-03, FUT-STATE-E, PAYREQ-03, PAYREQ-04, SCR002-E-001, SCR002-EDIT-001, SCR002-EDIT-002
操作ID: OP-002-EDIT, OP-002-SAVE, OP-E-PENDING, OP-E-HISTORY, OP-E-CORRECT, OP-E-SUBMIT, OP-E-RETURN, OP-E-CONFIRM
決定: payroll_Q:Q13, payroll_Q:Q14, payroll_Q:Q15, payroll_Q:Q16, payroll_Q:Q17, payroll_Q:Q18, payroll_Q:Q19, payroll_Q:Q20, payroll_Q:Q21, payroll_Q:Q22, payroll_Q:Q23, payroll_Q:Q24, payroll_Q:Q25, payroll_Q:Q26, payroll_Q:Q27, payroll_R:R11, payroll_R:R19, open:D-02
証拠: docs/requirements/payroll-confirmed-20261007.md:44-58 / docs/design/detailed/detailed-design.md:112-133 / docs/design/basic/data-model.md:55-65

### G06 通勤届・認定・新ヘッダー経路モデル [designblocked]

定期前払い／IC実日数を経路別に混在、提出⇄差戻し→認定、新認定と旧認定保持、一時不支給と終了を区別。既存HTML印刷維持。

依存: PD-01、PD-09、PD-02、F-02
前提: 正式ヘッダー／経路列、必須検証・経路数・帳票取得対応を確定 / 精算・適用期間／不支給計算を業務資料で確定
移行: 既存4経路を上限と決めない。新旧行のGUID対応を保存し受入済みHTMLを保持。
検証: 新旧認定・複数経路・混合方式 / 不支給と終了の区別 / 認定前は計算利用不可 / GUIDと職員不一致拒否 / 71欄・2ページ・NULL/0・印刷枠超過停止
復元: 旧データ契約・受入済みHTML・通常入口の復元材料を保持。新契約受入前に旧経路を消さない。
最小の未充足事項（engineering + business for calculation）: 新経路テーブルとHTML取得契約を確定する資料はどれか。精算式は別の未決として保留。
要件ID: F-01, F-02, F-03, F-04, F-07, F-08, FR-F-01, FR-F-02, FR-F-03, FUT-STATE-F, PAYREQ-05, SCR002-F-001
操作ID: OP-F-EDIT, OP-F-SUBMIT, OP-F-RETURN, OP-F-CERTIFY, OP-F-CHANGE, OP-F-NOPAY, OP-F-END
決定: payroll_Q:Q28, payroll_Q:Q29, payroll_Q:Q30, payroll_Q:Q31, payroll_Q:Q32, payroll_Q:Q33, open:D-06, open:PD-09
証拠: docs/requirements/business-requirements.md:125-171 / docs/requirements/open-decisions.md:85-95 / docs/design/basic/data-model.md:61-72

### G07 勤怠の追加更新・職員行編集・復旧 [designblocked]

所属×勤務月、掲載行は手修正を上書き／空欄クリア、非掲載行保持、報告済ロック、全件検証・処理中停止・不完全結果除外。

依存: PD-01の行識別／必須空欄、PD-05、PD-04
前提: 既存直列フロー／activebatch方式の再利用可能性を設計・検証 / 正規化12桁職員番号を新要件でも行キーに使う契約とNo再採番等を確定 / 対象報告の処理中状態・復旧記録・権威ある実行者を確定
移行: 現行の有効バッチ＋旧バッチ保持は再利用候補。追加更新では旧有効行と正規化入力を合成して新バッチへ、検証後切替。これは設計案であり未承認物理方式。
検証: 掲載A更新・新B追加・非掲載C保持 / 手修正上書き・空欄クリア・0維持 / 複数所属同職員の別報告 / 全件検証前書込なし・999/1000境界 / 途中失敗／応答喪失／再実行／重複実行／並行編集・提出 / 報告者／差戻担当Lookup読戻し
復元: 旧activebatchと版を保存。失敗バッチは利用不可、旧成功分を維持。活性化後の取消は検証済み復旧手順のみ。
最小の未充足事項（engineering first; business only for ambiguous required cells）: 新要件の職員行識別・必須空欄・Noの扱いを既存列契約からそのまま採用してよいかを設計根拠で確定する。
要件ID: PAYREQ-06
操作ID: OP-003-IMPORT, OP-003-RECOVER, OP-003-ROWEDIT, OP-003-RETURN
決定: payroll_Q:Q34, payroll_Q:Q35, payroll_Q:Q36, payroll_Q:Q37, payroll_Q:Q38, payroll_Q:Q39, payroll_R:R12, payroll_R:R13, payroll_R:R14, open:D-04, open:PD-05
証拠: docs/design/detailed/detailed-design.md:284-291 / docs/requirements/payroll-confirmed-20261007.md:65-70 / docs/requirements/payroll-confirmed-20261007.md:108-110 / scripts/automation/build_scr003_flow.py:105-163

### G08 期末勤勉率・単価区分マスタ [designblocked]

職員×対象期間の別々の期末・勤勉率。業務管理者が単価・区分等を有効期間管理、給与班兼務可、使用停止で履歴保持。

依存: PD-01、PD-04、PD-02
前提: 率の桁・単位・上下限・期間／職員キーと正式保存先を設計 / 業務管理者の実効認可は今回変更しない
移行: 現行SCR004はSetのみ。率を永続表に保存した証拠なし。マスタ新旧版は上書きしない。
検証: 別職員／別期間／別率の保存読戻し / 未確定値を計算に使わない / マスタ改定前後・使用停止後の過去参照 / 業務／システム管理ロール混同なし
復元: 旧率画面とマスタ読取経路を保持し新保存機能を停止可能にする。
最小の未充足事項（engineering; business for valid rate domain）: 別率の正式保存先・精度・入力範囲をどの資料で確定するか。
要件ID: PAY-01, PAY-02, SCR006-RULE-001
操作ID: OP-004-RATES, OP-006-RULE, OP-006-END
決定: 
証拠: docs/requirements/screen-requirements.md:424-425 / docs/requirements/screen-requirements.md:482-489 / docs/requirements/payroll-confirmed-20261007.md:71-77

### G09 外部機関の決定結果登録 [designblocked]

社会保険／税固定控除タブで担当者が紙電子の決定結果を登録、給与班確認前は計算不可。電子申請・受付進捗・自動取込・採否再判断は作らない。

依存: PD-01、PD-04、Gの入力／証憑／適用条件
前提: 決定結果項目・証憑契約・適用日・確認状態の保存先を確定
移行: 新決定結果を既存保険26列等へ自動対応させない。必要な正式マッピングを作成。
検証: 紙／電子同じ登録経路 / 担当局外拒否 / 未確認結果の計算除外 / 外部結果を給与班独自判断で変更しない
復元: テスト決定結果と確認前後を追跡し旧表示契約を保持。
最小の未充足事項（business/data-owner + engineering）: 決定結果に必須の登録内容と給与適用時点は何か。
要件ID: FR-G-01, FR-G-03, FR-G-04, FUT-STATE-G, G-01, G-02, G-04, G-05, G-06, SCR002-G-001, SCR002-G-002, SCR002-G-003, SCR002-G-004
操作ID: OP-G-REGISTER, OP-G-CONFIRM
決定: 
証拠: docs/requirements/business-requirements.md:174-235 / docs/requirements/screen-requirements.md:403-413

### G10 支給回・本計算・調整・確定単位 [needsbusinessdecision]

日額時間額、対象期間と支給日、元データ訂正、理由／処理者付き別調整、計算版根拠、個別／所属一括、差分ゼロ確定。

依存: PD-02、D9～D12保留、PD-01、PD-05、Q47とI12の個別／全支給回境界
前提: 現行Excelと業務資料から項目別式・丸め・適用時期・独立期待結果を確定 / 支給回／計算版／使用値／調整の正式モデル / 個別確定と支給回全体検証の関係を決める
移行: SCR005仮例は置換前提にしない。計算結果・根拠は版ごと分離、支払済への更新経路を作らない。
検証: 日額時間額・月途中条件・採退境界 / 二重欠勤減算なし / 未確認保険・勤怠失敗・未確定元データは確定不可 / 支給回全件でゼロ判定・同時更新失効 / 支払済不変
復元: 支払済／最終版を不変保持。未払い候補版だけ無効化して直前有効版へ戻す設計。
最小の未充足事項（business; formula review remains on hold）: 式精査再開はD9から。先に画面を進めるなら個別／所属一括確定と全支給回差分ゼロ判定の関係のみ確認する。
要件ID: PAYREQ-07, PERIOD-01, PERIOD-02, PERIOD-03
操作ID: OP-PAY-PERIOD, OP-PAY-CALCULATE, OP-PAY-ADJUST, OP-PAY-INDIVIDUAL, OP-PAY-PAID
決定: payroll_Q:Q40, payroll_Q:Q41, payroll_Q:Q42, payroll_Q:Q43, payroll_Q:Q44, payroll_Q:Q45, payroll_Q:Q46, payroll_Q:Q47, payroll_R:R20, interface_D:D4, interface_D:D5, interface_D:D6, open:D-03, open:PD-02
証拠: docs/requirements/payroll-confirmed-20261007.md:71-84 / docs/requirements/payroll-interface-decisions-20261008.md:7-36 / docs/design/detailed/detailed-design.md:293-305

### G11 承認済み人給連携のUI単独部分 [designblocked]

3タブ・支給回コンテキスト、初回全職員と絞込み、手動A/M一括／明細指定、出力前件数確認、差分／全件と指定6列。永続化・業務計算・人給接続から分離できる純粋な表示／ローカル状態。

依存: 支給回／最新版結果／出力明細／照合結果の正式データadapter不在、正本の正式画面ID・物理列名未入力、全体を業務機能として提供するにはG12/G13/G15が必要
前提: 最新アプリ読戻しと衝突しない最小Canvas差分 / 明確に架空と表示した入力データ契約。新しい正式物理名／業務状態コードを確定しない / 実出力・取込・給与班確定は依存契約完成まで無効。試験完了を業務機能完了としない
移行: DB移行なし。新UIローカル状態のみ。内部コントロール名は実装上の名前として記録し正式業務画面IDを勝手に確定しない。
検証: JLINK-T01の3タブ／コンテキスト部分 / JLINK-T02の対象選択・A/M・確認件数部分 / JLINK-T04の切替・6列表示部分 / 0件・多行同職員・取消・再入場・別支給回・Tab順 / 未接続操作は成功通知や架空の確定状態を出さない
復元: 追加した最小Canvas subtreeとローカル状態式を直前版へ戻す。既存画面／接続／権限を変更しない。
最小の未充足事項（engineering）: 業務質問なし。正式画面IDと実データadapterは後段の技術設計。試験UIを本機能完成と扱わない。
要件ID: I1, I11, I2, I3, I4, I6, IF-05, JLINK-UI-01, JLINK-UI-02, JLINK-UI-03, JLINK-UI-04, JLINK-UI-05, JLINK-UI-08
操作ID: OP-001-JLINK, OP-JLINK-SELECT, OP-JLINK-TARGET, OP-JLINK-AM, OP-JLINK-FILTER
決定: interface_I:I1, interface_I:I2, interface_I:I3, interface_I:I4, interface_I:I6, interface_I:I11
証拠: docs/requirements/screen-requirements.md:494-516 / docs/design/detailed/payroll-jinkyu-interface.md:93-121 / docs/testing/test-specification.md:677-684

### G12 人給237列xlsxの本出力 [designblocked]

xlsx、237見出し固定順、見出し1／データ2行目、文字列型・表示形式、11キー、職員判断A/M、指定網掛け列を維持。

依存: PD-03、全237列の値設定、D9～D12等の式保留
前提: ローコードの生成方式・既存接続・保存配布先を確定 / 各出力列の入力元／文字列整形と最新結果ID・出力履歴を定義 / 単に237見出しが決まったことを金額マッピング完了としない
移行: 出力履歴／計算版対応を新設する設計が必要。空欄0化は人給側の動作なので全セルをアプリで0埋めする新ルールを作らない。
検証: IF-T01/02/03/04/06 / 237列／固定順／文字列実型／先頭0／日付 / 11キーと内部GUID分離 / 約800行の欠落重複／タイムアウト / Excel出力取消・再試行と履歴対応
復元: 生成候補を識別し未送信ファイル／失敗出力を業務完了扱いにしない。前回出力履歴保持。
最小の未充足事項（engineering/data-owner）: 承認済み接続だけを用いたxlsx生成・配布方式と、列ごとの値設定マッピングは何か。
要件ID: IF-01, IF-02, IF-03, IF-04, IF-06, IF-07, IF-08
操作ID: OP-JLINK-EXPORT
決定: payroll_R:R9, interface_D:D1, interface_D:D2, interface_D:D3
証拠: docs/design/detailed/payroll-jinkyu-interface.md:7-48 / docs/design/detailed/payroll-jinkyu-interface.md:123-363

### G13 給与簿CSV取込・最新版照合・再出力 [designblocked]

固定1～5行、6行目以降、【合計情報】境界、原空欄保持して比較0、未知職員保持／確定阻止、失敗時前回成功保持、最新版照合と旧ゼロ失効、差分対応明細再出力。

依存: PD-03、PD-05、照合キー／多重行／出力行対応、I8エラー取得方式、差額符号／非数値表現
前提: 実CSVの文字コード・列・引用符・キー・行対応を確認 / 最新結果IDと同時更新検出・確定再検証を設計 / 差分⇔出力明細の多対多対応、エラー源と行IDを定義
移行: 給与簿は取込回ごとの読み取り専用スナップショット。既存163列と出力237列の1対1一致を仮定しない。
検証: IF-T07/08/09/12、JLINK-T03/05/06/08 / 未知／不足／余分／重複／空欄対0 / 途中失敗で前回成功維持 / 再計算中／照合中／確定直前の更新 / 多差分1出力行でも再出力重複なし
復元: 取込回・照合回を追跡し前回成功分を維持。過去照合を削除せず失効扱い。
最小の未充足事項（data-owner/engineering）: 通常・追給・控除を含む給与簿CSVと出力明細の対応サンプル／照合キーは何か。
要件ID: I10, I12, I5, I7, I8, I9, IF-09, IF-11, JLINK-UI-06, JLINK-UI-07, JLINK-UI-09, JLINK-UI-10, JLINK-UI-11, PAYREQ-08
操作ID: OP-JINKYU-PROCESS, OP-JLINK-IMPORT, OP-JLINK-RECONCILE, OP-JLINK-CORRECT, OP-JLINK-REEXPORT, OP-JLINK-ERROR, OP-JLINK-CONFIRM, OP-JLINK-HISTORY, OP-JLINK-CORRECT-ATT, OP-JLINK-RETURN, OP-JLINK-RETURN-ATT
決定: payroll_Q:Q48, payroll_Q:Q49, payroll_Q:Q50, payroll_Q:Q51, payroll_Q:Q52, payroll_R:R2, payroll_R:R4, payroll_R:R5, payroll_R:R6, interface_I:I5, interface_I:I7, interface_I:I8, interface_I:I9, interface_I:I10, interface_I:I12, open:PD-03
証拠: docs/design/detailed/payroll-jinkyu-interface.md:83-121 / docs/requirements/open-decisions.md:102-114

### G14 追給集約・返納分割回収 [needsbusinessdecision]

支払済不訂正、月別差額内訳と人給追給行の対応、確認待ち→給与班確定、給与相殺／告知書併用、複数回収・残額。

依存: PD-02、PD-03、PD-07、PERIOD-05とR10の両立
前提: 過去複数月集約と対象日のルール / 差額式・税保険丸め・相殺限度／取消／過回収／完了条件 / 案件・月別内訳・回収実績の物理モデル
移行: 元支払を保持し新案件だけ作る。返納実績と差額確定状態を別保存。
検証: 複数過去月・同月複数支給 / 分割2回＋相殺／告知併用 / 負値・過回収・取消・未完了 / 元支払不変／回収済＋残額整合
復元: 元給与に書き戻さない。回収実績訂正は未確定のため実績取消機能を勝手に作らない。
最小の未充足事項（business）: 複数過去月を1追給行に集約したとき対象年月日はどう決めるか。返納取消等は別の未決として保持。
要件ID: FR-PAY-01, FR-PAY-02, FUT-STATE-PAY, PAY-03, PAY-04, PAY-05, PERIOD-04, PERIOD-05, SCR007-DIFF-001
操作ID: OP-RETRO-CALCULATE, OP-RETRO-CONFIRM, OP-RETRO-EXPORT, OP-REPAY-METHOD, OP-REPAY-RECORD
決定: payroll_Q:Q53, payroll_R:R3, payroll_R:R10, payroll_R:R18, interface_D:D7, interface_D:D8, interface_D:D9, interface_D:D10, interface_D:D11, interface_D:D12, open:D-08, open:PD-07
証拠: docs/requirements/payroll-confirmed-20261007.md:98-109 / docs/design/detailed/payroll-jinkyu-interface.md:62-77 / docs/requirements/open-decisions.md:90-90

### G15 業務認可・監査主体 [designblocked]

給与班全局、局担当自局記録と必要共通基本、業務管理者兼務とシステム管理分離。UI確認用変数は認可根拠にしない。

依存: PD-04、D-01、security changes out of scope
前提: 権威ある主体／所属／複数役割、所有共有とフロー認可設計 / report/reopenの実行者Lookupを信頼できる主体から取得
移行: 今回ロール・権限設定は変更禁止。将来の試験ロール／所有・共有移行は別権限確認が必要。
検証: 別局直接ID・フロー直呼び・同一人兼務 / 帳票／照合／CSV出力の全経路 / 報告者／差戻者が接続所有者に化けない
復元: 既存権限を拡張しない。別途承認後は最小権限差分と復元手順を保存。
最小の未充足事項（security-owner/engineering）: 実行者と局・役割を信頼できるどの属性から決定するか。
要件ID: AUTH-01, AUTH-02, AUTH-04, COMMON-AUTH-001, COMMON-AUTH-002, F-06, FR-AUTH-01, FR-AUTH-02, FR-AUTH-04, FUT-AUTH-001, FUT-AUTH-002, FUT-AUTH-004, NFR-J, PAYREQ-09
操作ID: 
決定: payroll_Q:Q54, payroll_Q:Q55, payroll_Q:Q56, payroll_Q:Q57, payroll_R:R15, payroll_R:R21, open:D-01, open:PD-04
証拠: docs/requirements/business-requirements.md:241-253 / docs/design/detailed/detailed-design.md:307-311

### G16 保存・障害復旧・非機能／総合受入 [needsbusinessdecision]

処理中各版、支払後の最終根拠・給与簿・支払実績・全照合回明細保持。架空データとローコード、単体結合の根拠。

依存: PD-06、D-07、NFR未決目標
前提: 保存期間・削除責任／復元・業務RTO/RPO・性能合否値 / 総合シナリオと独立期待結果を確定
移行: 中間版削除は可能という方針であって削除実行の許可ではない。最終根拠と照合履歴を切り離せる保存設計。
検証: 中間版削除後の最終根拠と双方不一致額参照 / 復元／障害復旧 / 改修単位単体・影響結合・同一版読戻し / 約800行を測定、未定性能閾値を創作しない
復元: 削除機能を実装／実行する前に復旧・参照整合と権限を確定。実データ移行は今回対象外。
最小の未充足事項（business/operations）: 運用上の保存期間・削除主体と総合試験シナリオ／性能合否値は何か。
要件ID: FR-G-02, G-03, IF-12, NFR-A, NFR-B, NFR-C, NFR-D, NFR-E, NFR-F, NFR-G, NFR-H, NFR-I, NFR-K, NFR-L, NFR-M, NFR-O, NFR-P, NFR-Q, NFR-R, PAYREQ-10
操作ID: 
決定: payroll_Q:Q58, payroll_Q:Q59, payroll_Q:Q60, payroll_R:R1, payroll_R:R7, payroll_R:R8, payroll_R:R16, payroll_R:R17, open:D-07, open:PD-06
証拠: docs/requirements/payroll-confirmed-20261007.md:97-117 / docs/requirements/non-functional-requirements.md:23-57 / docs/requirements/open-decisions.md:90-95

### G17 現行HTML認定簿と既存読取機能 [alreadyimplemented]

既存の別タブHTML・ブラウザー印刷、動的163列、4履歴56列読取、ホームと既存勤怠の現行機能。存在と履歴の限定証拠であり全条件PASSではない。

依存: 業務上の未決なし。最新readbackと試験は必要。
前提: 最新保存／公開版との同一性と変更影響範囲を読戻し
移行: 既存機能維持。新モデルの機能充足へ転用しない。
検証: 現行の選定スモークと変更影響回帰 / 0/1/複数履歴、同月複数給与、NULL/0/負 / HTML71表示・2ページ・GUID
復元: 直前snapshotと既存受入HTMLを保持。
最小の未充足事項（engineering）: 業務質問なし。残る未照合条件は実機検証。
要件ID: COMMON-CONTEXT-001, COMMON-LAYOUT-001, COMMON-NAV-001, COMMON-NAV-002, COMMON-SCREEN-001, COMMUTE-CUTOVER-001, COMMUTE-OFFICIAL-001, COMMUTE-PARALLEL-001, F-05, FR-F-04, IF-10, R15, R16, R17, R18, R19, R21, R22, R23, SCR001-UI-001, SCR001-UI-002, SCR002-COM-001, SCR002-COM-002, SCR002-COM-003, SCR002-COM-004, SCR002-COM-005, SCR002-EDIT-003, SCR002-EDIT-004, SCR002-LT-001, SCR002-LT-003, SCR002-LT-006, SCR002-LT-007, SCR002-PAY-001, SCR002-PAY-002, SCR002-PAY-003, SCR002-PAY-004, SCR002-PAY-005, SCR002-PAY-006, SCR002-PAY-007, SCR002-PAY-008, SCR002-UI-001, SCR002-UI-002, SCR002-UI-003, SCR002-UI-004, SCR002-UI-005, SCR002-UI-006, SCR002-UI-007, SCR002-UI-008, SCR002-UI-009, SCR002-UI-010, SCR003-IMPORT-001, SCR005-ACT-001, SCR005-ACT-003, SCR005-ACT-004, SCR005-ACT-007, SCR005-ACT-008, SCR005-CALC-001, SCR005-CALC-002, SCR005-CALC-004, SCR005-CALC-005, SCR005-CALC-006, SCR005-CALC-007, SCR005-CALC-008, SCR005-UI-001, SCR005-UI-002, SCR005-UI-003, SCR005-UI-005, SCR005-UI-006, SCR005-UI-007, SCR005-UI-008, SCR005-UI-009, SCR005-UI-010, SCR005-UI-011, SCR005-UI-012, SCR005-UI-013, SCR005-UI-014
操作ID: OP-001-STAFF, OP-001-ATTENDANCE, OP-001-RATES, OP-001-MAINTENANCE, OP-002-SEARCH, OP-002-SELECT, OP-002-SIDEBAR, OP-002-READMODE, OP-002-CANCEL, OP-002-DISCARD, OP-002-LEDGER, OP-002-HOME, OP-003-HOME, OP-004-HOME, OP-005-HOME, OP-006-HOME, OP-003-SELECT, OP-003-EDIT, OP-003-SAVE, OP-003-READMODE, OP-003-IMPORT-CURRENT, OP-003-REPORT, OP-005-RECALC, OP-006-MONTH, OP-F-HTML, OP-F-PDF, OP-F-RETURN-HTML, OP-002-CLEAR, OP-002-FONT, OP-001-POC, OP-POC-HOME
決定: legacy_app_R:R01, legacy_app_R:R02, legacy_app_R:R06, legacy_app_R:R07, legacy_app_R:R08, legacy_app_R:R09, legacy_app_R:R10, legacy_app_R:R11, legacy_app_R:R12, legacy_app_R:R14
証拠: docs/handoff/STATUS.md:22-39 / docs/design/basic/data-model.md:29-46

### G18 レビュー提案・初回対象外 [proposal]

未承認の具体的動線／配置案と、初回対象外の本人・SKDB・家族・メモ・銀行等。確定した業務目標を撤回する意味ではない。

依存: explicitly proposed/out of initial scope
前提: 該当の具体操作が正本で承認されるまで実装対象へ昇格しない
移行: なし。
検証: 提案UIを確定要件として自動採用していないこと
復元: なし。
最小の未充足事項（business if/when selected）: この具体動線を採用するか。現在は追加で質問せず保留する。
要件ID: AUTH-03, FR-AUTH-03, FUT-AUTH-003, NFR-N
操作ID: OP-IMPORT-RETURN, OP-JLINK-HOME, OP-IMPORT-HOME, OP-001-DIFF, OP-007-HOME
決定: 
証拠: docs/requirements/payroll-confirmed-20261007.md:125-129

## 2. 今すぐ進められる既存機能修正

### READY-01 検索結果・ページ・職員・月の往復保持
SCR002-LT-002, COMMON-NAV-003, COMMON-CONTEXT-002, SCR005-ACT-002
既存動作修正。新スキーマ・業務ルールなし。

### READY-02 タブ別履歴選択保持
SCR002-LT-004, SCR002-LT-005, SCR002-EDIT-003
既存History.RecordIdを区分別に保持。選択職員／取得版が変わった時だけ妥当性再検証。

### READY-03 試算旧根拠消去と固定サマリー
SCR005-ACT-005, SCR005-ACT-006, SCR005-UI-004, SCR005-UI-015
既存内蔵仮例の表示修正。本給与計算式・制度判断は変更しない。

### READY-04 現行通勤保存のGUID対象解決
SCR002-EDIT-002, SCR002-EDIT-003
既存通勤の許可列・試験職員ゲートを保持し、Title解析による対象解決を既存RecordIdのGUID照合へ限定修正。5区分保存全体の完成ではない。

試験: 同職員内の重複認定ID／同じTitleを別GUIDで作る / Title変更後も正しいGUID1件だけ保存 / 別職員GUID・不存在・不正GUID・旧選択はPatchなし / 既存試験番号ゲート維持・入力失敗時保持・保存後再取得
復元: 対象式の直前版と隔離テスト行の前値を保持。5区分解放・列追加・実データは行わない。

### READY-05 勤怠旧バッチ保持の文書矛盾解消
SCR003-IMPORT-001
config import_contract.replacementのthen remove superseded rowsを、実装・テスト・現行データ設計の旧バッチ保持へ整合。追加更新機能の実装完了を意味しない。

試験: tests/automation/test_scr003_flow.pyの非破壊条件とフローDeleteRecord不存在を照合 / 将来追加更新要件と現行全置換を別記
復元: この文言差分のみ復元。

## 3. 確定済みだが単独リリースしない部品

- COMP-01 JLINK-UI-01, JLINK-UI-02, I3: 同一画面3タブ・支給回コンテキスト保持・計算版選択なし。未充足: 支給回の正式データadapter未定。
- COMP-02 JLINK-UI-03, JLINK-UI-04, JLINK-UI-05, I1, I2, I4, IF-05: 初回全職員・対象変更・一括／行別A/M・出力前4件数確認。未充足: 出力明細ID／最新版結果／生成／出力履歴が未設計。
- COMP-03 JLINK-UI-08, I6, I11: 差分のみ初期表示、全件切替、指定6列。未充足: 比較行adapter・差額符号／非数値表示未定。
- COMP-04 IF-01, IF-02, IF-03, IF-04, IF-07, IF-08: 237見出しと11キー、1行目見出し／2行目から文字列・日付形式。未充足: 列ごとの値設定・低コードxlsx生成／配布経路未定。
- COMP-05 PAYREQ-06: 掲載行上書き・非掲載保持・空欄消去／0区別のmerge意味論。未充足: 行No衝突・合成上限・処理中／失敗状態・再実行契約未完成。

## 4. 全100操作の列挙

| 操作ID | 内容 | 判定 | 群 | 最小依存・確認 |
|---|---|---|---|---|
| OP-001-STAFF | 職員マスタ検索 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-001-ATTENDANCE | 勤務時間報告 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-001-RATES | 期末勤勉支給率登録 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-001-MAINTENANCE | メンテナンス | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-001-IMPORT | データ一括取込み | needsbusinessdecision | G04 | E取込で内容一致／重複可能性と必須不足を判定する列と条件は何か。 |
| OP-001-JLINK | 人給連携 | designblocked | G11 | 支給回と最新版結果を読み出す正式データ源／識別子を定義する。3タブ自体を再質問しない。 |
| OP-002-SEARCH | 職員を検索 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-002-SELECT | 職員を選択 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-002-SIDEBAR | 検索欄を開閉 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-002-TABS | 詳細タブを切替 | implementnow | G01 | 既存ソースの操作は存在。SD-03/04または旧根拠文・固定サマリーの確認済み設計差分を最小修正し現行版で再試験する。 |
| OP-002-HISTORY | 履歴を選択 | implementnow | G01 | 既存ソースの操作は存在。SD-03/04または旧根拠文・固定サマリーの確認済み設計差分を最小修正し現行版で再試験する。 |
| OP-002-EDIT | 編集モードへ | designblocked | G05 | 新モデルの許可編集列・検証条件・状態／監査の正式保存契約は何か。 |
| OP-002-SAVE | 変更を保存 | designblocked | G05 | 新モデルの許可編集列・検証条件・状態／監査の正式保存契約は何か。 |
| OP-002-READMODE | 読取りモードへ | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-002-CANCEL | 破棄確認を取消 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-002-DISCARD | 破棄して続行 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-002-LEDGER | 給与簿の月範囲変更 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-002-PAYDETAIL | 支給明細へ | implementnow | G01 | 既存ソースの操作は存在。SD-03/04または旧根拠文・固定サマリーの確認済み設計差分を最小修正し現行版で再試験する。 |
| OP-002-HOME | ホームへ戻る | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-003-HOME | ホームへ戻る | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-004-HOME | ホームへ戻る | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-005-HOME | ホームへ戻る | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-006-HOME | ホームへ戻る | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-003-SELECT | 局・月・報告を選択 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-003-EDIT | 勤務実績を一覧編集 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-003-SAVE | 勤務実績を保存 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-003-READMODE | 勤怠編集を取り消す | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-003-IMPORT-CURRENT | 現行Excel全置換取込 | alreadyimplemented | G17 | 全置換取込の現行実装は存在。Q35/R12/R13の追加更新へ変更済みではない。旧バッチ保持は実装、削除記載はSD-06の文書矛盾。 |
| OP-003-IMPORT | 勤務実績を追加更新取込 | designblocked | G07 | 旧有効バッチと入力の合成時、職員番号キー・No衝突・合成後999上限・必須空欄・対象報告処理中状態を既存契約にどう対応させるか。 |
| OP-003-RECOVER | 取込失敗を復旧・再実行 | designblocked | G07 | 応答喪失／ステージング途中／活性化直後を識別する処理ID・状態・再実行契約は何か。 |
| OP-003-ROWEDIT | 職員行を追加・削除 | designblocked | G07 | 職員行追加の既定値・No割当て・最後の行削除の扱いを既存20列契約でどう定義するか。 |
| OP-003-REPORT | 勤務時間を報告 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-003-RETURN | 報告を差し戻す | designblocked | G07 | 給与班主体をどこから信頼して取得し、差戻者Lookupと未払い再計算対象へどう結ぶか。 |
| OP-004-RATES | 期末・勤勉率を登録 | designblocked | G08 | 職員×対象期間の2率を保存する正式テーブル／列、精度と入力範囲は何か。 |
| OP-005-MONTH | 試算対象月を変更 | implementnow | G01 | 既存ソースの操作は存在。SD-03/04または旧根拠文・固定サマリーの確認済み設計差分を最小修正し現行版で再試験する。 |
| OP-005-RECALC | 内蔵仮例を再計算 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-005-DETAILS | 支給・控除内訳を開閉 | implementnow | G01 | 既存ソースの操作は存在。SD-03/04または旧根拠文・固定サマリーの確認済み設計差分を最小修正し現行版で再試験する。 |
| OP-005-RETURN | 職員詳細へ戻る | implementnow | G01 | 既存ソースの操作は存在。SD-03/04または旧根拠文・固定サマリーの確認済み設計差分を最小修正し現行版で再試験する。 |
| OP-006-MONTH | 勤務報告対象月を設定 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-006-RULE | 業務マスタを登録・改定 | designblocked | G08 | 単価／区分マスタの正式項目と適用期間・改定対象の契約は何か。 |
| OP-006-END | マスタを使用停止 | designblocked | G08 | 使用停止／終了日をどの既存または新規正式列で保存し、過去参照を維持するか。 |
| OP-AD-CANDIDATE | 発令情報から候補作成 | designblocked | G03 | 発令登録完了イベントと採用ごとの不変IDをどの正式インターフェースから取得できるか。 |
| OP-AD-NUMBER | 発行職員番号を反映 | designblocked | G03 | 発令登録完了イベントと採用ごとの不変IDをどの正式インターフェースから取得できるか。 |
| OP-AD-CHANGE | 前工程変更の差異確認 | designblocked | G03 | 発令登録完了イベントと採用ごとの不変IDをどの正式インターフェースから取得できるか。 |
| OP-AD-CANCEL | 採用取消を反映 | designblocked | G03 | 発令登録完了イベントと採用ごとの不変IDをどの正式インターフェースから取得できるか。 |
| OP-IMPORT-VALIDATE | Excelの行を検証 | needsbusinessdecision | G04 | E取込で内容一致／重複可能性と必須不足を判定する列と条件は何か。 |
| OP-IMPORT-APPLY | 行別に取込を判断 | needsbusinessdecision | G04 | E取込で内容一致／重複可能性と必須不足を判定する列と条件は何か。 |
| OP-IMPORT-RETURN | 確認待ち候補を開く | proposal | G18 | この具体動線を採用するか。現在は追加で質問せず保留する。 |
| OP-E-PENDING | 確認待ちで絞り込む | designblocked | G05 | 確認待ち対象を判定する正式状態列と候補／職員への対応は何か。 |
| OP-E-HISTORY | 実際の条件変更を登録 | designblocked | G05 | 新履歴の編集許可列・有効期間検証・親GUIDと番号対応・前履歴を保持する保存経路は何か。 |
| OP-E-CORRECT | 誤登録を訂正 | designblocked | G05 | 訂正前後監査と確認待ちへの復帰、影響未払い結果の失効をどの保存処理で一貫させるか。 |
| OP-E-SUBMIT | 内容を確認待ちにする | designblocked | G05 | 確認待ちに移す必須列検証・正式状態コード・同時更新条件は何か。 |
| OP-E-RETURN | 給与情報を差し戻す | designblocked | G05 | 差戻し状態と戻し主体の保存先、元入力を失わず再提出する経路は何か。 |
| OP-E-CONFIRM | 給与情報を確定・再確定 | designblocked | G05 | 確定／再確定の許可条件と必要情報検証、権威ある給与班主体、未払い結果失効の契約は何か。 |
| OP-F-EDIT | 通勤届を入力 | designblocked | G06 | ヘッダー／経路の入力列・必須検証・保存先は何か。 |
| OP-F-SUBMIT | 通勤届を提出・再提出 | designblocked | G06 | 提出を許可する必須項目・検証条件と新認定への状態保存契約は何か。 |
| OP-F-RETURN | 通勤届を差し戻す | designblocked | G06 | 差戻しの正式状態・担当主体・提出者対応をどこへ保存するか。理由連絡をアプリ外から変更しない。 |
| OP-F-CERTIFY | 通勤手当を認定 | designblocked | G06 | 認定状態の保存先と認定期間／登録額の検証、給与計算の認定済参照契約は何か。 |
| OP-F-CHANGE | 変更届から新認定へ | designblocked | G06 | 新旧認定GUID・期間・精算案件を関連付ける正式契約は何か。 |
| OP-F-NOPAY | 一時不支給期間を確認 | needsbusinessdecision | G06 | 病気／欠勤のどの期間をどの支給月・経路へ対応させるか。精算式は推測しない。 |
| OP-F-END | 認定期間の終了を確定 | needsbusinessdecision | G06 | 認定期間終了日の境界と届出・給与班確認に必要な入力は何か。独立終了状態は追加しない。 |
| OP-F-HTML | 認定簿を表示 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-F-PDF | ブラウザー印刷でPDF保存 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-F-RETURN-HTML | 元の通勤タブへ戻る | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-G-REGISTER | 外部決定結果を登録 | designblocked | G09 | 各外部決定の必須登録内容・証憑の扱い・給与への適用日を示す資料は何か。 |
| OP-G-CONFIRM | 外部決定結果を確認確定 | designblocked | G09 | 外部決定結果の正式状態と確定後適用時点をどの列／計算版へ結ぶか。 |
| OP-PAY-PERIOD | 支給回・対象期間を設定 | needsbusinessdecision | G10 | 対象年月日の具体日と採用日境界、支給日の例外設定ルールは何か。 |
| OP-PAY-CALCULATE | 給与を計算・再計算 | needsbusinessdecision | G10 | 式精査再開はD9から。先に画面を進めるなら個別／所属一括確定と全支給回差分ゼロ判定の関係のみ確認する。 |
| OP-PAY-ADJUST | 例外調整を記録 | designblocked | G10 | 理由・処理者・対象項目・調整額を結果本体と分離して保存し、最新結果／照合を失効させる正式契約は何か。 |
| OP-PAY-INDIVIDUAL | 個別・所属一括確定の境界 | needsbusinessdecision | G10 | Q47の職員単位／所属一括確定とI12の支給回全体最新差分ゼロを、同じ確定操作のどの単位で両立させるか。 |
| OP-PAY-PAID | 支払い済みを記録 | designblocked | G10 | 支払い済みの記録項目・実施証拠・状態保存と最終根拠の凍結契約は何か。支払い実行機能は追加しない。 |
| OP-JLINK-SELECT | 支給回・タブを選択 | designblocked | G11 | 選択支給回・支給日・期間・状態の実データadapterをどの正式モデルで提供するか。 |
| OP-JLINK-TARGET | 出力対象を選択 | designblocked | G11 | 出力明細IDと職員、差分行の対応は何か。初回全職員／絞込みは確定済み。 |
| OP-JLINK-AM | A/Mを指定 | designblocked | G11 | 一括／明細別A/Mを保持する出力明細の安定IDと出力履歴adapterは何か。手動判断の方針は再確認しない。 |
| OP-JLINK-EXPORT | 確認してExcel出力 | designblocked | G12 | 237列の値設定元／整形、低コード生成方式、保存配布先と出力処理履歴を定義する。 |
| OP-JINKYU-PROCESS | 人給取込・給与簿出力 | designblocked | G13 | 通常・追給・控除を含む給与簿CSVと出力明細の対応サンプル／照合キーは何か。 |
| OP-JLINK-IMPORT | 給与簿CSVを取り込む | designblocked | G13 | 給与簿CSVの文字コード・ヘッダー列・行識別・成功版切替を確定できるサンプルは何か。 |
| OP-JLINK-RECONCILE | 最新版と照合 | designblocked | G13 | 給与簿側の照合キー／多重行対応と最新結果ID・更新検知・差分明細保存の正式契約は何か。 |
| OP-JLINK-FILTER | 差分・全件表示を切替 | designblocked | G11 | 比較結果の実データ源、差額符号と非数値差分の表示値契約を定義する。6列と差分既定は確定済み。 |
| OP-JLINK-CORRECT | 差分原因の入力画面へ | designblocked | G13 | 差分原因を勤務条件／通勤等の正しい職員・履歴へ結ぶIDと、戻り支給回コンテキストの契約は何か。 |
| OP-JLINK-REEXPORT | 差分対応明細を再出力 | designblocked | G13 | 複数差分項目と1出力明細を重複なく対応させるキー／集約契約は何か。A/Mは自動変更しない。 |
| OP-JLINK-ERROR | 人給エラー行を確認 | designblocked | G13 | 人給インポートエラーをどの形式・取得方法・行IDで受け取れるか（I8）。 |
| OP-JLINK-CONFIRM | 給与班が支給回を確定 | designblocked | G13 | 全支給回の最新結果IDと照合回を確定時に再検証し、同時更新・未解決行を拒否する保存契約は何か。 |
| OP-JLINK-HISTORY | 処理回の履歴を確認 | designblocked | G13 | 処理回の日時・実行者・件数・版／取込ID・不一致双方額を、中間版削除後も残す物理保存契約は何か。 |
| OP-JLINK-HOME | ホームへ戻る | proposal | G18 | この具体動線を採用するか。現在は追加で質問せず保留する。 |
| OP-RETRO-CALCULATE | 過去月との差額を計算 | needsbusinessdecision | G14 | 複数過去月を1追給行に集約したとき対象年月日はどう決めるか。返納取消等は別の未決として保持。 |
| OP-RETRO-CONFIRM | 差額内訳を確認・確定 | designblocked | G14 | 選択差額結果・内訳・確認主体・確定状態を支給／返納実績と分離する正式保存契約は何か。 |
| OP-RETRO-EXPORT | 追給を人給出力へ渡す | needsbusinessdecision | G14 | 複数過去月の追給を集約した行の対象年月日と月別内訳対応をどう両立させるか。 |
| OP-REPAY-METHOD | 返納方法を決定 | designblocked | G14 | 返納案件と給与班指定の相殺／告知書方法を複数回収へ結ぶ保存契約は何か。 |
| OP-REPAY-RECORD | 回収実績と残額を記録 | designblocked | G14 | 回収日・方法・額の保存先と、取消／過回収／完了判定／相殺限度をどう扱うか。 |
| OP-002-CLEAR | 検索条件をクリア | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-002-FONT | 文字サイズを切替 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-IMPORT-HOME | ホームへ戻る | proposal | G18 | この具体動線を採用するか。現在は追加で質問せず保留する。 |
| OP-001-DIFF | 遡及差額を開く | proposal | G18 | この具体動線を採用するか。現在は追加で質問せず保留する。 |
| OP-007-HOME | ホームへ戻る | proposal | G18 | この具体動線を採用するか。現在は追加で質問せず保留する。 |
| OP-JLINK-CORRECT-ATT | 勤怠の差分訂正へ | designblocked | G13 | 勤怠差分を局×月の報告ID／職員行へ結ぶ対応と、戻り支給回コンテキストの契約は何か。 |
| OP-JLINK-RETURN | 人給連携へ戻る | designblocked | G13 | 入力画面から返す安定支給回ID／職員IDと訂正後失効の通知契約は何か。 |
| OP-JLINK-RETURN-ATT | 人給連携へ戻る | designblocked | G13 | 勤怠画面から返す安定支給回ID／職員IDと訂正後失効の通知契約は何か。 |
| OP-001-POC | PoCデータ一括取込 | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |
| OP-POC-HOME | ホームへ戻る | alreadyimplemented | G17 | 現在公開v35のSourceはOct7解析Sourceと10件すべてbyte一致。現行操作の存在判定であり、全要件／runtime／権限の合格ではない。 |

## 5. 全240明示要件の列挙

各行の要件原文・全定義リンク・操作対応・前提・移行・試験・復元はreadiness-inventory.jsonに完全収録。未対応IDを機能欠落と短絡しない。

| 要件ID | 判定 | 群 | 証拠 | 対応操作 |
|---|---|---|---|---|
| AD-01 | designblocked | G03 | docs/requirements/business-requirements.md:45 | OP-AD-CANDIDATE |
| AD-02 | designblocked | G03 | docs/requirements/business-requirements.md:46 | OP-AD-CANDIDATE |
| AD-03 | designblocked | G03 | docs/requirements/business-requirements.md:47 | OP-AD-CANDIDATE |
| AD-04 | designblocked | G03 | docs/requirements/business-requirements.md:48 | OP-AD-NUMBER |
| AD-05 | designblocked | G03 | docs/requirements/business-requirements.md:49 | OP-AD-NUMBER |
| AD-06 | designblocked | G03 | docs/requirements/business-requirements.md:50 | OP-AD-CANCEL |
| AD-07 | designblocked | G03 | docs/requirements/business-requirements.md:51 | OP-AD-CANCEL |
| AD-08 | designblocked | G03 | docs/requirements/business-requirements.md:52 | OP-AD-CHANGE |
| AD-09 | designblocked | G03 | docs/requirements/business-requirements.md:53 | OP-AD-CANDIDATE |
| AD-10 | designblocked | G03 | docs/requirements/business-requirements.md:54 | HTML直接対応なし。正本個別確認 |
| AUTH-01 | designblocked | G15 | docs/requirements/business-requirements.md:245 | HTML直接対応なし。正本個別確認 |
| AUTH-02 | designblocked | G15 | docs/requirements/business-requirements.md:246 | HTML直接対応なし。正本個別確認 |
| AUTH-03 | proposal | G18 | docs/requirements/business-requirements.md:247 | HTML直接対応なし。正本個別確認 |
| AUTH-04 | designblocked | G15 | docs/requirements/business-requirements.md:248 | HTML直接対応なし。正本個別確認 |
| COMMON-AUTH-001 | designblocked | G15 | docs/requirements/traceability-matrix.md:155 | HTML直接対応なし。正本個別確認 |
| COMMON-AUTH-002 | designblocked | G15 | docs/requirements/traceability-matrix.md:156 | HTML直接対応なし。正本個別確認 |
| COMMON-CONTEXT-001 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:153 | OP-001-STAFF, OP-001-ATTENDANCE, OP-001-RATES, OP-001-MAINTENANCE, OP-002-HOME, OP-003-HOME, OP-004-HOME, OP-005-HOME, OP-006-HOME, OP-JLINK-HOME, OP-IMPORT-HOME, OP-007-HOME, OP-POC-HOME |
| COMMON-CONTEXT-002 | implementnow | G01 | docs/requirements/traceability-matrix.md:154 | OP-002-PAYDETAIL |
| COMMON-LAYOUT-001 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:231 | HTML直接対応なし。正本個別確認 |
| COMMON-NAV-001 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:150 | OP-001-STAFF, OP-001-ATTENDANCE, OP-001-RATES, OP-001-MAINTENANCE, OP-001-POC |
| COMMON-NAV-002 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:151 | OP-002-HOME, OP-003-HOME, OP-004-HOME, OP-005-HOME, OP-006-HOME |
| COMMON-NAV-003 | implementnow | G01 | docs/requirements/traceability-matrix.md:152 | OP-002-PAYDETAIL, OP-005-RETURN |
| COMMON-SCREEN-001 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:149 | HTML直接対応なし。正本個別確認 |
| COMMUTE-CUTOVER-001 | alreadyimplemented | G17 | docs/requirements/requirements.md:186 | HTML直接対応なし。正本個別確認 |
| COMMUTE-OFFICIAL-001 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:365 | HTML直接対応なし。正本個別確認 |
| COMMUTE-PARALLEL-001 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:366 | HTML直接対応なし。正本個別確認 |
| E-01 | designblocked | G03 | docs/requirements/business-requirements.md:99 | HTML直接対応なし。正本個別確認 |
| E-02 | needsbusinessdecision | G04 | docs/requirements/business-requirements.md:100 | OP-IMPORT-VALIDATE |
| E-03 | needsbusinessdecision | G04 | docs/requirements/business-requirements.md:101 | OP-IMPORT-VALIDATE |
| E-04 | needsbusinessdecision | G04 | docs/requirements/business-requirements.md:102 | OP-IMPORT-VALIDATE, OP-IMPORT-APPLY |
| E-05 | needsbusinessdecision | G04 | docs/requirements/business-requirements.md:103 | OP-IMPORT-VALIDATE |
| E-06 | designblocked | G05 | docs/requirements/business-requirements.md:104 | OP-E-CORRECT |
| E-07 | designblocked | G05 | docs/requirements/business-requirements.md:105 | OP-E-SUBMIT, OP-E-RETURN, OP-E-CONFIRM |
| E-08 | designblocked | G05 | docs/requirements/business-requirements.md:106 | OP-E-CORRECT, OP-E-CONFIRM |
| E-09 | designblocked | G03 | docs/requirements/business-requirements.md:107 | OP-AD-CHANGE |
| E-10 | designblocked | G05 | docs/requirements/business-requirements.md:108 | OP-E-CONFIRM |
| E-11 | needsbusinessdecision | G04 | docs/requirements/business-requirements.md:109 | OP-IMPORT-APPLY |
| E-12 | designblocked | G05 | docs/requirements/business-requirements.md:110 | OP-E-SUBMIT, OP-E-RETURN |
| F-01 | designblocked | G06 | docs/requirements/business-requirements.md:154 | OP-F-EDIT, OP-F-SUBMIT |
| F-02 | designblocked | G06 | docs/requirements/business-requirements.md:155 | OP-F-EDIT, OP-F-SUBMIT |
| F-03 | designblocked | G06 | docs/requirements/business-requirements.md:156 | OP-F-SUBMIT, OP-F-RETURN |
| F-04 | designblocked | G06 | docs/requirements/business-requirements.md:157 | OP-F-CERTIFY |
| F-05 | alreadyimplemented | G17 | docs/requirements/business-requirements.md:158 | OP-F-PDF |
| F-06 | designblocked | G15 | docs/requirements/business-requirements.md:159 | HTML直接対応なし。正本個別確認 |
| F-07 | designblocked | G06 | docs/requirements/business-requirements.md:160 | OP-F-CHANGE |
| F-08 | needsbusinessdecision | G06 | docs/requirements/business-requirements.md:161 | OP-F-NOPAY, OP-F-END |
| FR-AD-01 | designblocked | G03 | docs/requirements/requirements.md:49 | OP-AD-CANDIDATE |
| FR-AD-02 | designblocked | G03 | docs/requirements/requirements.md:50 | OP-AD-NUMBER |
| FR-AD-03 | designblocked | G03 | docs/requirements/requirements.md:51 | OP-AD-CANCEL |
| FR-AD-04 | designblocked | G03 | docs/requirements/requirements.md:52 | OP-AD-CANDIDATE |
| FR-AUTH-01 | designblocked | G15 | docs/requirements/requirements.md:99 | HTML直接対応なし。正本個別確認 |
| FR-AUTH-02 | designblocked | G15 | docs/requirements/requirements.md:100 | HTML直接対応なし。正本個別確認 |
| FR-AUTH-03 | proposal | G18 | docs/requirements/requirements.md:101 | HTML直接対応なし。正本個別確認 |
| FR-AUTH-04 | designblocked | G15 | docs/requirements/requirements.md:102 | HTML直接対応なし。正本個別確認 |
| FR-E-01 | needsbusinessdecision | G04 | docs/requirements/requirements.md:58 | OP-001-IMPORT, OP-IMPORT-VALIDATE, OP-IMPORT-APPLY |
| FR-E-02 | designblocked | G05 | docs/requirements/requirements.md:59 | HTML直接対応なし。正本個別確認 |
| FR-E-03 | designblocked | G05 | docs/requirements/requirements.md:60 | OP-AD-CHANGE |
| FR-F-01 | designblocked | G06 | docs/requirements/requirements.md:66 | HTML直接対応なし。正本個別確認 |
| FR-F-02 | designblocked | G06 | docs/requirements/requirements.md:67 | HTML直接対応なし。正本個別確認 |
| FR-F-03 | needsbusinessdecision | G06 | docs/requirements/requirements.md:68 | OP-F-NOPAY |
| FR-F-04 | alreadyimplemented | G17 | docs/requirements/requirements.md:69 | OP-F-HTML |
| FR-G-01 | designblocked | G09 | docs/requirements/requirements.md:77 | HTML直接対応なし。正本個別確認 |
| FR-G-02 | needsbusinessdecision | G16 | docs/requirements/requirements.md:78 | HTML直接対応なし。正本個別確認 |
| FR-G-03 | designblocked | G09 | docs/requirements/requirements.md:79 | HTML直接対応なし。正本個別確認 |
| FR-G-04 | designblocked | G09 | docs/requirements/requirements.md:80 | HTML直接対応なし。正本個別確認 |
| FR-PAY-01 | needsbusinessdecision | G14 | docs/requirements/requirements.md:86 | OP-RETRO-CALCULATE |
| FR-PAY-02 | needsbusinessdecision | G14 | docs/requirements/requirements.md:87 | HTML直接対応なし。正本個別確認 |
| FUT-AUTH-001 | designblocked | G15 | docs/requirements/screen-requirements.md:435 | HTML直接対応なし。正本個別確認 |
| FUT-AUTH-002 | designblocked | G15 | docs/requirements/screen-requirements.md:436 | HTML直接対応なし。正本個別確認 |
| FUT-AUTH-003 | proposal | G18 | docs/requirements/screen-requirements.md:437 | HTML直接対応なし。正本個別確認 |
| FUT-AUTH-004 | designblocked | G15 | docs/requirements/screen-requirements.md:438 | HTML直接対応なし。正本個別確認 |
| FUT-IMPORT-001 | needsbusinessdecision | G04 | docs/requirements/traceability-matrix.md:329 | OP-001-IMPORT, OP-IMPORT-RETURN, OP-IMPORT-HOME |
| FUT-STATE-E | designblocked | G05 | docs/requirements/traceability-matrix.md:330 | OP-E-PENDING |
| FUT-STATE-F | designblocked | G06 | docs/requirements/traceability-matrix.md:331 | OP-F-RETURN, OP-F-END |
| FUT-STATE-G | designblocked | G09 | docs/requirements/traceability-matrix.md:332 | HTML直接対応なし。正本個別確認 |
| FUT-STATE-PAY | designblocked | G14 | docs/requirements/traceability-matrix.md:333 | OP-RETRO-CONFIRM |
| G-01 | designblocked | G09 | docs/requirements/business-requirements.md:202 | OP-G-REGISTER |
| G-02 | designblocked | G09 | docs/requirements/business-requirements.md:203 | OP-G-REGISTER |
| G-03 | needsbusinessdecision | G16 | docs/requirements/business-requirements.md:204 | HTML直接対応なし。正本個別確認 |
| G-04 | designblocked | G09 | docs/requirements/business-requirements.md:205 | OP-G-REGISTER |
| G-05 | designblocked | G09 | docs/requirements/business-requirements.md:206 | OP-G-CONFIRM |
| G-06 | designblocked | G09 | docs/requirements/business-requirements.md:207 | OP-G-REGISTER |
| I1 | designblocked | G11 | docs/requirements/payroll-interface-decisions-20261008.md:46 | OP-JLINK-TARGET |
| I10 | designblocked | G13 | docs/requirements/payroll-interface-decisions-20261008.md:55 | OP-JINKYU-PROCESS, OP-JLINK-IMPORT |
| I11 | designblocked | G11 | docs/requirements/payroll-interface-decisions-20261008.md:56 | OP-JLINK-FILTER |
| I12 | designblocked | G13 | docs/requirements/payroll-interface-decisions-20261008.md:57 | OP-PAY-INDIVIDUAL, OP-JLINK-CONFIRM |
| I2 | designblocked | G11 | docs/requirements/payroll-interface-decisions-20261008.md:47 | OP-JLINK-AM, OP-JLINK-REEXPORT |
| I3 | designblocked | G11 | docs/requirements/payroll-interface-decisions-20261008.md:48 | OP-001-JLINK, OP-JLINK-SELECT |
| I4 | designblocked | G11 | docs/requirements/payroll-interface-decisions-20261008.md:49 | OP-JLINK-EXPORT, OP-JLINK-REEXPORT |
| I5 | designblocked | G13 | docs/requirements/payroll-interface-decisions-20261008.md:50 | OP-JLINK-SELECT, OP-JLINK-IMPORT, OP-JLINK-RECONCILE |
| I6 | designblocked | G11 | docs/requirements/payroll-interface-decisions-20261008.md:51 | OP-JLINK-FILTER |
| I7 | designblocked | G13 | docs/requirements/payroll-interface-decisions-20261008.md:52 | OP-JLINK-RECONCILE |
| I8 | designblocked | G13 | docs/requirements/payroll-interface-decisions-20261008.md:53 | OP-JLINK-ERROR |
| I9 | designblocked | G13 | docs/requirements/payroll-interface-decisions-20261008.md:54 | OP-JLINK-TARGET, OP-JLINK-REEXPORT |
| IF-01 | designblocked | G12 | docs/design/detailed/payroll-jinkyu-interface.md:11 | OP-JLINK-EXPORT, OP-JINKYU-PROCESS |
| IF-02 | designblocked | G12 | docs/design/detailed/payroll-jinkyu-interface.md:12 | OP-JLINK-EXPORT |
| IF-03 | designblocked | G12 | docs/design/detailed/payroll-jinkyu-interface.md:13 | OP-JLINK-EXPORT |
| IF-04 | designblocked | G12 | docs/design/detailed/payroll-jinkyu-interface.md:14 | OP-JLINK-EXPORT |
| IF-05 | designblocked | G11 | docs/design/detailed/payroll-jinkyu-interface.md:15 | OP-JLINK-AM |
| IF-06 | designblocked | G12 | docs/design/detailed/payroll-jinkyu-interface.md:16 | OP-JLINK-EXPORT |
| IF-07 | designblocked | G12 | docs/design/detailed/payroll-jinkyu-interface.md:17 | OP-JLINK-EXPORT |
| IF-08 | designblocked | G12 | docs/design/detailed/payroll-jinkyu-interface.md:18 | OP-JLINK-EXPORT |
| IF-09 | designblocked | G13 | docs/design/detailed/payroll-jinkyu-interface.md:19 | OP-JINKYU-PROCESS, OP-JLINK-IMPORT |
| IF-10 | alreadyimplemented | G17 | docs/design/detailed/payroll-jinkyu-interface.md:20 | OP-JLINK-IMPORT, OP-JLINK-CORRECT |
| IF-11 | designblocked | G13 | docs/design/detailed/payroll-jinkyu-interface.md:21 | OP-JLINK-ERROR |
| IF-12 | needsbusinessdecision | G16 | docs/design/detailed/payroll-jinkyu-interface.md:22 | OP-JLINK-HISTORY |
| JLINK-UI-01 | designblocked | G11 | docs/requirements/screen-requirements.md:502 | OP-001-JLINK, OP-JLINK-SELECT, OP-JLINK-HOME |
| JLINK-UI-02 | designblocked | G11 | docs/requirements/screen-requirements.md:503 | OP-JLINK-SELECT |
| JLINK-UI-03 | designblocked | G11 | docs/requirements/screen-requirements.md:504 | OP-JLINK-TARGET, OP-JLINK-REEXPORT |
| JLINK-UI-04 | designblocked | G11 | docs/requirements/screen-requirements.md:505 | OP-JLINK-AM |
| JLINK-UI-05 | designblocked | G11 | docs/requirements/screen-requirements.md:506 | OP-JLINK-EXPORT |
| JLINK-UI-06 | designblocked | G13 | docs/requirements/screen-requirements.md:507 | OP-JLINK-IMPORT, OP-JLINK-RECONCILE |
| JLINK-UI-07 | designblocked | G13 | docs/requirements/screen-requirements.md:508 | OP-JLINK-RECONCILE |
| JLINK-UI-08 | designblocked | G11 | docs/requirements/screen-requirements.md:509 | OP-JLINK-FILTER |
| JLINK-UI-09 | designblocked | G13 | docs/requirements/screen-requirements.md:510 | OP-JLINK-CORRECT, OP-JLINK-CORRECT-ATT, OP-JLINK-RETURN, OP-JLINK-RETURN-ATT |
| JLINK-UI-10 | designblocked | G13 | docs/requirements/screen-requirements.md:511 | OP-JLINK-ERROR |
| JLINK-UI-11 | designblocked | G13 | docs/requirements/screen-requirements.md:512 | OP-PAY-INDIVIDUAL, OP-JLINK-CONFIRM |
| NFR-A | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:57 | HTML直接対応なし。正本個別確認 |
| NFR-B | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:58 | HTML直接対応なし。正本個別確認 |
| NFR-C | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:59 | HTML直接対応なし。正本個別確認 |
| NFR-D | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:60 | HTML直接対応なし。正本個別確認 |
| NFR-E | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:61 | HTML直接対応なし。正本個別確認 |
| NFR-F | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:62 | HTML直接対応なし。正本個別確認 |
| NFR-G | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:63 | HTML直接対応なし。正本個別確認 |
| NFR-H | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:64 | HTML直接対応なし。正本個別確認 |
| NFR-I | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:65 | HTML直接対応なし。正本個別確認 |
| NFR-J | designblocked | G15 | docs/requirements/open-decisions.md:66 | HTML直接対応なし。正本個別確認 |
| NFR-K | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:67 | HTML直接対応なし。正本個別確認 |
| NFR-L | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:68 | HTML直接対応なし。正本個別確認 |
| NFR-M | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:69 | HTML直接対応なし。正本個別確認 |
| NFR-N | proposal | G18 | docs/requirements/open-decisions.md:70 | HTML直接対応なし。正本個別確認 |
| NFR-O | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:71 | HTML直接対応なし。正本個別確認 |
| NFR-P | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:72 | HTML直接対応なし。正本個別確認 |
| NFR-Q | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:73 | HTML直接対応なし。正本個別確認 |
| NFR-R | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:74 | HTML直接対応なし。正本個別確認 |
| PAY-01 | designblocked | G08 | docs/requirements/business-requirements.md:258 | OP-006-RULE |
| PAY-02 | designblocked | G08 | docs/requirements/business-requirements.md:259 | OP-006-RULE |
| PAY-03 | needsbusinessdecision | G14 | docs/requirements/business-requirements.md:260 | OP-RETRO-CALCULATE |
| PAY-04 | designblocked | G14 | docs/requirements/business-requirements.md:261 | OP-RETRO-CONFIRM |
| PAY-05 | needsbusinessdecision | G14 | docs/requirements/business-requirements.md:262 | OP-REPAY-METHOD, OP-REPAY-RECORD |
| PAYREQ-01 | designblocked | G02 | docs/requirements/payroll-confirmed-20261007.md:17 | OP-AD-NUMBER, OP-E-HISTORY |
| PAYREQ-02 | designblocked | G02 | docs/requirements/payroll-confirmed-20261007.md:18 | OP-AD-NUMBER, OP-E-HISTORY |
| PAYREQ-03 | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:19 | OP-E-HISTORY, OP-E-CORRECT, OP-E-SUBMIT, OP-E-RETURN, OP-E-CONFIRM |
| PAYREQ-04 | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:20 | OP-E-HISTORY, OP-E-CORRECT, OP-E-SUBMIT, OP-E-RETURN, OP-E-CONFIRM, OP-G-CONFIRM |
| PAYREQ-05 | designblocked | G06 | docs/requirements/payroll-confirmed-20261007.md:21 | OP-F-EDIT, OP-F-CERTIFY, OP-F-CHANGE |
| PAYREQ-06 | designblocked | G07 | docs/requirements/payroll-confirmed-20261007.md:22 | OP-003-SELECT, OP-003-EDIT, OP-003-SAVE, OP-003-READMODE, OP-003-IMPORT-CURRENT, OP-003-IMPORT, OP-003-RECOVER, OP-003-ROWEDIT, OP-003-REPORT, OP-003-RETURN, OP-006-MONTH, OP-JLINK-CORRECT-ATT, OP-JLINK-RETURN-ATT |
| PAYREQ-07 | needsbusinessdecision | G10 | docs/requirements/payroll-confirmed-20261007.md:23 | OP-003-RETURN, OP-004-RATES, OP-E-CORRECT, OP-E-CONFIRM, OP-PAY-PERIOD, OP-PAY-CALCULATE, OP-PAY-ADJUST, OP-PAY-INDIVIDUAL, OP-JLINK-CORRECT, OP-JLINK-CONFIRM, OP-JLINK-CORRECT-ATT |
| PAYREQ-08 | designblocked | G13 | docs/requirements/payroll-confirmed-20261007.md:24 | OP-PAY-CALCULATE, OP-PAY-PAID, OP-JINKYU-PROCESS, OP-JLINK-RECONCILE, OP-JLINK-CONFIRM, OP-JLINK-HISTORY, OP-RETRO-CALCULATE, OP-RETRO-EXPORT, OP-REPAY-METHOD, OP-REPAY-RECORD |
| PAYREQ-09 | designblocked | G15 | docs/requirements/payroll-confirmed-20261007.md:25 | OP-006-RULE, OP-006-END |
| PAYREQ-10 | needsbusinessdecision | G16 | docs/requirements/payroll-confirmed-20261007.md:26 | OP-003-RECOVER, OP-PAY-CALCULATE, OP-PAY-PAID, OP-JLINK-HISTORY |
| PERIOD-01 | needsbusinessdecision | G10 | docs/design/detailed/payroll-jinkyu-interface.md:66 | OP-PAY-PERIOD |
| PERIOD-02 | needsbusinessdecision | G10 | docs/design/detailed/payroll-jinkyu-interface.md:67 | OP-PAY-PERIOD |
| PERIOD-03 | needsbusinessdecision | G10 | docs/design/detailed/payroll-jinkyu-interface.md:68 | HTML直接対応なし。正本個別確認 |
| PERIOD-04 | needsbusinessdecision | G14 | docs/design/detailed/payroll-jinkyu-interface.md:69 | OP-RETRO-EXPORT |
| PERIOD-05 | needsbusinessdecision | G14 | docs/design/detailed/payroll-jinkyu-interface.md:70 | OP-RETRO-EXPORT |
| R15 | alreadyimplemented | G17 | docs/requirements/requirements.md:17 | HTML直接対応なし。正本個別確認 |
| R16 | alreadyimplemented | G17 | docs/requirements/requirements.md:18 | HTML直接対応なし。正本個別確認 |
| R17 | alreadyimplemented | G17 | docs/requirements/requirements.md:19 | HTML直接対応なし。正本個別確認 |
| R18 | alreadyimplemented | G17 | docs/requirements/requirements.md:20 | HTML直接対応なし。正本個別確認 |
| R19 | alreadyimplemented | G17 | docs/requirements/requirements.md:21 | HTML直接対応なし。正本個別確認 |
| R20 | implementnow | G01 | docs/requirements/requirements.md:22 | HTML直接対応なし。正本個別確認 |
| R21 | alreadyimplemented | G17 | docs/requirements/requirements.md:23 | HTML直接対応なし。正本個別確認 |
| R22 | alreadyimplemented | G17 | docs/requirements/requirements.md:24 | HTML直接対応なし。正本個別確認 |
| R23 | alreadyimplemented | G17 | docs/requirements/requirements.md:25 | HTML直接対応なし。正本個別確認 |
| SCR001-UI-001 | alreadyimplemented | G17 | docs/requirements/screen-requirements.md:318 | HTML直接対応なし。正本個別確認 |
| SCR001-UI-002 | alreadyimplemented | G17 | docs/requirements/screen-requirements.md:319 | HTML直接対応なし。正本個別確認 |
| SCR002-COM-001 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:74 | HTML直接対応なし。正本個別確認 |
| SCR002-COM-002 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:75 | HTML直接対応なし。正本個別確認 |
| SCR002-COM-003 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:76 | OP-F-HTML, OP-F-PDF, OP-F-RETURN-HTML |
| SCR002-COM-004 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:77 | HTML直接対応なし。正本個別確認 |
| SCR002-COM-005 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:78 | HTML直接対応なし。正本個別確認 |
| SCR002-E-001 | designblocked | G05 | docs/requirements/screen-requirements.md:421 | OP-IMPORT-RETURN, OP-E-PENDING |
| SCR002-EDIT-001 | designblocked | G05 | docs/requirements/traceability-matrix.md:87 | OP-002-EDIT |
| SCR002-EDIT-002 | designblocked | G05 | docs/requirements/traceability-matrix.md:88 | OP-002-SAVE |
| SCR002-EDIT-003 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:89 | OP-002-SELECT, OP-002-TABS, OP-002-SAVE, OP-002-READMODE, OP-002-CANCEL, OP-002-DISCARD |
| SCR002-EDIT-004 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:90 | OP-002-READMODE |
| SCR002-F-001 | designblocked | G06 | docs/requirements/screen-requirements.md:423 | OP-F-SUBMIT |
| SCR002-G-001 | designblocked | G09 | docs/requirements/screen-requirements.md:408 | OP-G-REGISTER |
| SCR002-G-002 | designblocked | G09 | docs/requirements/screen-requirements.md:409 | OP-G-REGISTER |
| SCR002-G-003 | designblocked | G09 | docs/requirements/screen-requirements.md:410 | HTML直接対応なし。正本個別確認 |
| SCR002-G-004 | designblocked | G09 | docs/requirements/screen-requirements.md:411 | OP-G-CONFIRM |
| SCR002-LT-001 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:57 | HTML直接対応なし。正本個別確認 |
| SCR002-LT-002 | implementnow | G01 | docs/requirements/traceability-matrix.md:58 | OP-002-SELECT, OP-002-SIDEBAR, OP-002-CLEAR |
| SCR002-LT-003 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:59 | OP-002-TABS |
| SCR002-LT-004 | implementnow | G01 | docs/requirements/traceability-matrix.md:60 | OP-002-HISTORY |
| SCR002-LT-005 | implementnow | G01 | docs/requirements/traceability-matrix.md:61 | HTML直接対応なし。正本個別確認 |
| SCR002-LT-006 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:62 | HTML直接対応なし。正本個別確認 |
| SCR002-LT-007 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:63 | OP-002-SEARCH |
| SCR002-PAY-001 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:79 | HTML直接対応なし。正本個別確認 |
| SCR002-PAY-002 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:80 | HTML直接対応なし。正本個別確認 |
| SCR002-PAY-003 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:81 | HTML直接対応なし。正本個別確認 |
| SCR002-PAY-004 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:82 | HTML直接対応なし。正本個別確認 |
| SCR002-PAY-005 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:83 | OP-002-LEDGER |
| SCR002-PAY-006 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:84 | OP-002-LEDGER |
| SCR002-PAY-007 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:85 | HTML直接対応なし。正本個別確認 |
| SCR002-PAY-008 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:86 | OP-002-LEDGER |
| SCR002-UI-001 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:64 | HTML直接対応なし。正本個別確認 |
| SCR002-UI-002 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:65 | HTML直接対応なし。正本個別確認 |
| SCR002-UI-003 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:66 | OP-002-FONT |
| SCR002-UI-004 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:67 | OP-002-SEARCH, OP-002-CLEAR |
| SCR002-UI-005 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:68 | HTML直接対応なし。正本個別確認 |
| SCR002-UI-006 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:69 | HTML直接対応なし。正本個別確認 |
| SCR002-UI-007 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:70 | HTML直接対応なし。正本個別確認 |
| SCR002-UI-008 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:71 | HTML直接対応なし。正本個別確認 |
| SCR002-UI-009 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:72 | HTML直接対応なし。正本個別確認 |
| SCR002-UI-010 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:73 | HTML直接対応なし。正本個別確認 |
| SCR003-IMPORT-001 | alreadyimplemented | G17 | docs/requirements/requirements.md:120 | HTML直接対応なし。正本個別確認 |
| SCR005-ACT-001 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:121 | HTML直接対応なし。正本個別確認 |
| SCR005-ACT-002 | implementnow | G01 | docs/requirements/traceability-matrix.md:122 | OP-005-RETURN |
| SCR005-ACT-003 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:123 | OP-005-MONTH |
| SCR005-ACT-004 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:124 | OP-005-RECALC |
| SCR005-ACT-005 | implementnow | G01 | docs/requirements/traceability-matrix.md:125 | OP-005-MONTH |
| SCR005-ACT-006 | implementnow | G01 | docs/requirements/traceability-matrix.md:126 | OP-005-MONTH |
| SCR005-ACT-007 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:127 | OP-005-DETAILS |
| SCR005-ACT-008 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:128 | HTML直接対応なし。正本個別確認 |
| SCR005-CALC-001 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:113 | HTML直接対応なし。正本個別確認 |
| SCR005-CALC-002 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:114 | HTML直接対応なし。正本個別確認 |
| SCR005-CALC-003 | designblocked | G02 | docs/requirements/traceability-matrix.md:115 | HTML直接対応なし。正本個別確認 |
| SCR005-CALC-004 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:116 | HTML直接対応なし。正本個別確認 |
| SCR005-CALC-005 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:117 | HTML直接対応なし。正本個別確認 |
| SCR005-CALC-006 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:118 | HTML直接対応なし。正本個別確認 |
| SCR005-CALC-007 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:119 | HTML直接対応なし。正本個別確認 |
| SCR005-CALC-008 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:120 | OP-005-RECALC |
| SCR005-UI-001 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:98 | HTML直接対応なし。正本個別確認 |
| SCR005-UI-002 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:99 | HTML直接対応なし。正本個別確認 |
| SCR005-UI-003 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:100 | HTML直接対応なし。正本個別確認 |
| SCR005-UI-004 | implementnow | G01 | docs/requirements/traceability-matrix.md:101 | HTML直接対応なし。正本個別確認 |
| SCR005-UI-005 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:102 | HTML直接対応なし。正本個別確認 |
| SCR005-UI-006 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:103 | HTML直接対応なし。正本個別確認 |
| SCR005-UI-007 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:104 | HTML直接対応なし。正本個別確認 |
| SCR005-UI-008 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:105 | HTML直接対応なし。正本個別確認 |
| SCR005-UI-009 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:106 | HTML直接対応なし。正本個別確認 |
| SCR005-UI-010 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:107 | HTML直接対応なし。正本個別確認 |
| SCR005-UI-011 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:108 | HTML直接対応なし。正本個別確認 |
| SCR005-UI-012 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:109 | HTML直接対応なし。正本個別確認 |
| SCR005-UI-013 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:110 | HTML直接対応なし。正本個別確認 |
| SCR005-UI-014 | alreadyimplemented | G17 | docs/requirements/traceability-matrix.md:111 | HTML直接対応なし。正本個別確認 |
| SCR005-UI-015 | implementnow | G01 | docs/requirements/traceability-matrix.md:112 | OP-005-DETAILS |
| SCR006-RULE-001 | designblocked | G08 | docs/requirements/screen-requirements.md:424 | OP-006-RULE |
| SCR007-DIFF-001 | designblocked | G14 | docs/requirements/screen-requirements.md:425 | OP-RETRO-CONFIRM, OP-001-DIFF, OP-007-HOME |

## 6. 全136決定記録の列挙

決定の承認状態と実装準備状態は別。Q/R回答を再質問しない。D9以降の保留を維持する。

| 名前空間付きID | 原決定状態 | 実装準備 | 群 | 正本 |
|---|---|---|---|---|
| payroll_Q:Q1 | 確定回答/承認済み（実装未検証） | designblocked | G02 | docs/requirements/payroll-confirmed-20261007.md:32 |
| payroll_Q:Q2 | 確定回答/承認済み（実装未検証） | designblocked | G02 | docs/requirements/payroll-confirmed-20261007.md:33 |
| payroll_Q:Q3 | 確定回答/承認済み（実装未検証） | designblocked | G02 | docs/requirements/payroll-confirmed-20261007.md:34 |
| payroll_Q:Q4 | 確定回答/承認済み（実装未検証） | designblocked | G02 | docs/requirements/payroll-confirmed-20261007.md:35 |
| payroll_Q:Q5 | 確定回答/承認済み（実装未検証） | designblocked | G02 | docs/requirements/payroll-confirmed-20261007.md:36 |
| payroll_Q:Q6 | 確定回答/承認済み（実装未検証） | designblocked | G02 | docs/requirements/payroll-confirmed-20261007.md:37 |
| payroll_Q:Q7 | 確定回答/承認済み（実装未検証） | designblocked | G02 | docs/requirements/payroll-confirmed-20261007.md:38 |
| payroll_Q:Q8 | 確定回答/承認済み（実装未検証） | designblocked | G02 | docs/requirements/payroll-confirmed-20261007.md:39 |
| payroll_Q:Q9 | 確定回答/承認済み（実装未検証） | designblocked | G02 | docs/requirements/payroll-confirmed-20261007.md:40 |
| payroll_Q:Q10 | 確定回答/承認済み（実装未検証） | designblocked | G02 | docs/requirements/payroll-confirmed-20261007.md:41 |
| payroll_Q:Q11 | 確定回答/承認済み（実装未検証） | designblocked | G02 | docs/requirements/payroll-confirmed-20261007.md:42 |
| payroll_Q:Q12 | 確定回答/承認済み（実装未検証） | designblocked | G02 | docs/requirements/payroll-confirmed-20261007.md:43 |
| payroll_Q:Q13 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:44 |
| payroll_Q:Q14 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:45 |
| payroll_Q:Q15 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:46 |
| payroll_Q:Q16 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:47 |
| payroll_Q:Q17 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:48 |
| payroll_Q:Q18 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:49 |
| payroll_Q:Q19 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:50 |
| payroll_Q:Q20 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:51 |
| payroll_Q:Q21 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:52 |
| payroll_Q:Q22 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:53 |
| payroll_Q:Q23 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:54 |
| payroll_Q:Q24 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:55 |
| payroll_Q:Q25 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:56 |
| payroll_Q:Q26 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:57 |
| payroll_Q:Q27 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:58 |
| payroll_Q:Q28 | 確定回答/承認済み（実装未検証） | designblocked | G06 | docs/requirements/payroll-confirmed-20261007.md:59 |
| payroll_Q:Q29 | 確定回答/承認済み（実装未検証） | designblocked | G06 | docs/requirements/payroll-confirmed-20261007.md:60 |
| payroll_Q:Q30 | 確定回答/承認済み（実装未検証） | designblocked | G06 | docs/requirements/payroll-confirmed-20261007.md:61 |
| payroll_Q:Q31 | 確定回答/承認済み（実装未検証） | designblocked | G06 | docs/requirements/payroll-confirmed-20261007.md:62 |
| payroll_Q:Q32 | 確定回答/承認済み（実装未検証） | designblocked | G06 | docs/requirements/payroll-confirmed-20261007.md:63 |
| payroll_Q:Q33 | 確定回答/承認済み（実装未検証） | designblocked | G06 | docs/requirements/payroll-confirmed-20261007.md:64 |
| payroll_Q:Q34 | 確定回答/承認済み（実装未検証） | designblocked | G07 | docs/requirements/payroll-confirmed-20261007.md:65 |
| payroll_Q:Q35 | 確定回答/承認済み（実装未検証） | designblocked | G07 | docs/requirements/payroll-confirmed-20261007.md:66 |
| payroll_Q:Q36 | 確定回答/承認済み（実装未検証） | designblocked | G07 | docs/requirements/payroll-confirmed-20261007.md:67 |
| payroll_Q:Q37 | 確定回答/承認済み（実装未検証） | designblocked | G07 | docs/requirements/payroll-confirmed-20261007.md:68 |
| payroll_Q:Q38 | 確定回答/承認済み（実装未検証） | designblocked | G07 | docs/requirements/payroll-confirmed-20261007.md:69 |
| payroll_Q:Q39 | 確定回答/承認済み（実装未検証） | designblocked | G07 | docs/requirements/payroll-confirmed-20261007.md:70 |
| payroll_Q:Q40 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G10 | docs/requirements/payroll-confirmed-20261007.md:71 |
| payroll_Q:Q41 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G10 | docs/requirements/payroll-confirmed-20261007.md:72 |
| payroll_Q:Q42 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G10 | docs/requirements/payroll-confirmed-20261007.md:73 |
| payroll_Q:Q43 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G10 | docs/requirements/payroll-confirmed-20261007.md:74 |
| payroll_Q:Q44 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G10 | docs/requirements/payroll-confirmed-20261007.md:75 |
| payroll_Q:Q45 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G10 | docs/requirements/payroll-confirmed-20261007.md:76 |
| payroll_Q:Q46 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G10 | docs/requirements/payroll-confirmed-20261007.md:77 |
| payroll_Q:Q47 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G10 | docs/requirements/payroll-confirmed-20261007.md:78 |
| payroll_Q:Q48 | 確定回答/承認済み（実装未検証） | designblocked | G13 | docs/requirements/payroll-confirmed-20261007.md:79 |
| payroll_Q:Q49 | 確定回答/承認済み（実装未検証） | designblocked | G13 | docs/requirements/payroll-confirmed-20261007.md:80 |
| payroll_Q:Q50 | 確定回答/承認済み（実装未検証） | designblocked | G13 | docs/requirements/payroll-confirmed-20261007.md:81 |
| payroll_Q:Q51 | 確定回答/承認済み（実装未検証） | designblocked | G13 | docs/requirements/payroll-confirmed-20261007.md:82 |
| payroll_Q:Q52 | 確定回答/承認済み（実装未検証） | designblocked | G13 | docs/requirements/payroll-confirmed-20261007.md:83 |
| payroll_Q:Q53 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G14 | docs/requirements/payroll-confirmed-20261007.md:84 |
| payroll_Q:Q54 | 確定回答/承認済み（実装未検証） | designblocked | G15 | docs/requirements/payroll-confirmed-20261007.md:85 |
| payroll_Q:Q55 | 確定回答/承認済み（実装未検証） | designblocked | G15 | docs/requirements/payroll-confirmed-20261007.md:86 |
| payroll_Q:Q56 | 確定回答/承認済み（実装未検証） | designblocked | G15 | docs/requirements/payroll-confirmed-20261007.md:87 |
| payroll_Q:Q57 | 確定回答/承認済み（実装未検証） | designblocked | G15 | docs/requirements/payroll-confirmed-20261007.md:88 |
| payroll_Q:Q58 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G16 | docs/requirements/payroll-confirmed-20261007.md:89 |
| payroll_Q:Q59 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G16 | docs/requirements/payroll-confirmed-20261007.md:90 |
| payroll_Q:Q60 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G16 | docs/requirements/payroll-confirmed-20261007.md:91 |
| payroll_R:R1 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G16 | docs/requirements/payroll-confirmed-20261007.md:97 |
| payroll_R:R2 | 確定回答/承認済み（実装未検証） | designblocked | G13 | docs/requirements/payroll-confirmed-20261007.md:98 |
| payroll_R:R3 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G14 | docs/requirements/payroll-confirmed-20261007.md:99 |
| payroll_R:R4 | 確定回答/承認済み（実装未検証） | designblocked | G13 | docs/requirements/payroll-confirmed-20261007.md:100 |
| payroll_R:R5 | 確定回答/承認済み（実装未検証） | designblocked | G13 | docs/requirements/payroll-confirmed-20261007.md:101 |
| payroll_R:R6 | 確定回答/承認済み（実装未検証） | designblocked | G13 | docs/requirements/payroll-confirmed-20261007.md:102 |
| payroll_R:R7 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G16 | docs/requirements/payroll-confirmed-20261007.md:103 |
| payroll_R:R8 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G16 | docs/requirements/payroll-confirmed-20261007.md:104 |
| payroll_R:R9 | 確定回答/承認済み（実装未検証） | designblocked | G12 | docs/requirements/payroll-confirmed-20261007.md:105 |
| payroll_R:R10 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G14 | docs/requirements/payroll-confirmed-20261007.md:106 |
| payroll_R:R11 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:107 |
| payroll_R:R12 | 確定回答/承認済み（実装未検証） | designblocked | G07 | docs/requirements/payroll-confirmed-20261007.md:108 |
| payroll_R:R13 | 確定回答/承認済み（実装未検証） | designblocked | G07 | docs/requirements/payroll-confirmed-20261007.md:109 |
| payroll_R:R14 | 確定回答/承認済み（実装未検証） | designblocked | G07 | docs/requirements/payroll-confirmed-20261007.md:110 |
| payroll_R:R15 | 確定回答/承認済み（実装未検証） | designblocked | G15 | docs/requirements/payroll-confirmed-20261007.md:111 |
| payroll_R:R16 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G16 | docs/requirements/payroll-confirmed-20261007.md:112 |
| payroll_R:R17 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G16 | docs/requirements/payroll-confirmed-20261007.md:113 |
| payroll_R:R18 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G14 | docs/requirements/payroll-confirmed-20261007.md:114 |
| payroll_R:R19 | 確定回答/承認済み（実装未検証） | designblocked | G05 | docs/requirements/payroll-confirmed-20261007.md:115 |
| payroll_R:R20 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G10 | docs/requirements/payroll-confirmed-20261007.md:116 |
| payroll_R:R21 | 確定回答/承認済み（実装未検証） | designblocked | G15 | docs/requirements/payroll-confirmed-20261007.md:117 |
| interface_D:D1 | 確定回答/承認済み（実装未検証） | designblocked | G12 | docs/requirements/payroll-interface-decisions-20261008.md:9 |
| interface_D:D2 | 確定回答/承認済み（実装未検証） | designblocked | G12 | docs/requirements/payroll-interface-decisions-20261008.md:10 |
| interface_D:D3 | 確定回答/承認済み（実装未検証） | designblocked | G12 | docs/requirements/payroll-interface-decisions-20261008.md:11 |
| interface_D:D4 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G10 | docs/requirements/payroll-interface-decisions-20261008.md:12 |
| interface_D:D5 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G10 | docs/requirements/payroll-interface-decisions-20261008.md:13 |
| interface_D:D6 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G10 | docs/requirements/payroll-interface-decisions-20261008.md:14 |
| interface_D:D7 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G14 | docs/requirements/payroll-interface-decisions-20261008.md:15 |
| interface_D:D8 | 確定回答/承認済み（実装未検証） | needsbusinessdecision | G14 | docs/requirements/payroll-interface-decisions-20261008.md:16 |
| interface_D:D9 | 保留・未回答 | needsbusinessdecision | G14 | docs/requirements/payroll-interface-decisions-20261008.md:17 |
| interface_D:D10 | 保留・未回答 | needsbusinessdecision | G14 | docs/requirements/payroll-interface-decisions-20261008.md:18 |
| interface_D:D11 | 保留・未回答 | needsbusinessdecision | G14 | docs/requirements/payroll-interface-decisions-20261008.md:19 |
| interface_D:D12 | 保留・未回答 | needsbusinessdecision | G14 | docs/requirements/payroll-interface-decisions-20261008.md:20 |
| interface_I:I1 | 確定回答/承認済み（実装未検証） | designblocked | G11 | docs/requirements/payroll-interface-decisions-20261008.md:46 |
| interface_I:I2 | 確定回答/承認済み（実装未検証） | designblocked | G11 | docs/requirements/payroll-interface-decisions-20261008.md:47 |
| interface_I:I3 | 確定回答/承認済み（実装未検証） | designblocked | G11 | docs/requirements/payroll-interface-decisions-20261008.md:48 |
| interface_I:I4 | 確定回答/承認済み（実装未検証） | designblocked | G11 | docs/requirements/payroll-interface-decisions-20261008.md:49 |
| interface_I:I5 | 確定回答/承認済み（実装未検証） | designblocked | G13 | docs/requirements/payroll-interface-decisions-20261008.md:50 |
| interface_I:I6 | 確定回答/承認済み（実装未検証） | designblocked | G11 | docs/requirements/payroll-interface-decisions-20261008.md:51 |
| interface_I:I7 | 確定回答/承認済み（実装未検証） | designblocked | G13 | docs/requirements/payroll-interface-decisions-20261008.md:52 |
| interface_I:I8 | 確定回答/承認済み（実装未検証） | designblocked | G13 | docs/requirements/payroll-interface-decisions-20261008.md:53 |
| interface_I:I9 | 確定回答/承認済み（実装未検証） | designblocked | G13 | docs/requirements/payroll-interface-decisions-20261008.md:54 |
| interface_I:I10 | 確定回答/承認済み（実装未検証） | designblocked | G13 | docs/requirements/payroll-interface-decisions-20261008.md:55 |
| interface_I:I11 | 確定回答/承認済み（実装未検証） | designblocked | G11 | docs/requirements/payroll-interface-decisions-20261008.md:56 |
| interface_I:I12 | 確定回答/承認済み（実装未検証） | designblocked | G13 | docs/requirements/payroll-interface-decisions-20261008.md:57 |
| open:D-01 | 未決または一部確定・詳細残件 | designblocked | G15 | docs/requirements/open-decisions.md:42 |
| open:D-02 | 未決または一部確定・詳細残件 | designblocked | G05 | docs/requirements/open-decisions.md:43 |
| open:D-03 | 未決または一部確定・詳細残件 | needsbusinessdecision | G10 | docs/requirements/open-decisions.md:44 |
| open:D-04 | 未決または一部確定・詳細残件 | designblocked | G07 | docs/requirements/open-decisions.md:45 |
| open:D-05 | 未決または一部確定・詳細残件 | designblocked | G01 | docs/requirements/open-decisions.md:46 |
| open:D-06 | 未決または一部確定・詳細残件 | designblocked | G06 | docs/requirements/open-decisions.md:47 |
| open:D-07 | 未決または一部確定・詳細残件 | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:48 |
| open:D-08 | 未決または一部確定・詳細残件 | designblocked | G14 | docs/requirements/open-decisions.md:49 |
| open:PD-01 | 未決または一部確定・詳細残件 | designblocked | G02 | docs/requirements/open-decisions.md:84 |
| open:PD-02 | 未決または一部確定・詳細残件 | needsbusinessdecision | G10 | docs/requirements/open-decisions.md:85 |
| open:PD-03 | 未決または一部確定・詳細残件 | designblocked | G13 | docs/requirements/open-decisions.md:86 |
| open:PD-04 | 未決または一部確定・詳細残件 | designblocked | G15 | docs/requirements/open-decisions.md:87 |
| open:PD-05 | 未決または一部確定・詳細残件 | designblocked | G07 | docs/requirements/open-decisions.md:88 |
| open:PD-06 | 未決または一部確定・詳細残件 | needsbusinessdecision | G16 | docs/requirements/open-decisions.md:89 |
| open:PD-07 | 未決または一部確定・詳細残件 | needsbusinessdecision | G14 | docs/requirements/open-decisions.md:90 |
| open:PD-08 | 未決または一部確定・詳細残件 | designblocked | G03 | docs/requirements/open-decisions.md:91 |
| open:PD-09 | 未決または一部確定・詳細残件 | designblocked | G06 | docs/requirements/open-decisions.md:92 |
| legacy_app_R:R01 | 履歴・回帰根拠。現行要件への適用は個別判断 | alreadyimplemented | G17 | records/docs/requirements/requirements-before-consolidation.md:36 |
| legacy_app_R:R02 | 履歴・回帰根拠。現行要件への適用は個別判断 | alreadyimplemented | G17 | records/docs/requirements/requirements-before-consolidation.md:37 |
| legacy_app_R:R03 | 履歴・回帰根拠。現行要件への適用は個別判断 | implementnow | G01 | records/docs/requirements/requirements-before-consolidation.md:38 |
| legacy_app_R:R04 | 履歴・回帰根拠。現行要件への適用は個別判断 | implementnow | G01 | records/docs/requirements/requirements-before-consolidation.md:39 |
| legacy_app_R:R05 | 履歴・回帰根拠。現行要件への適用は個別判断 | implementnow | G01 | records/docs/requirements/requirements-before-consolidation.md:40 |
| legacy_app_R:R06 | 履歴・回帰根拠。現行要件への適用は個別判断 | alreadyimplemented | G17 | records/docs/requirements/requirements-before-consolidation.md:41 |
| legacy_app_R:R07 | 履歴・回帰根拠。現行要件への適用は個別判断 | alreadyimplemented | G17 | records/docs/requirements/requirements-before-consolidation.md:42 |
| legacy_app_R:R08 | 履歴・回帰根拠。現行要件への適用は個別判断 | alreadyimplemented | G17 | records/docs/requirements/requirements-before-consolidation.md:43 |
| legacy_app_R:R09 | 履歴・回帰根拠。現行要件への適用は個別判断 | alreadyimplemented | G17 | records/docs/requirements/requirements-before-consolidation.md:44 |
| legacy_app_R:R10 | 履歴・回帰根拠。現行要件への適用は個別判断 | alreadyimplemented | G17 | records/docs/requirements/requirements-before-consolidation.md:45 |
| legacy_app_R:R11 | 履歴・回帰根拠。現行要件への適用は個別判断 | alreadyimplemented | G17 | records/docs/requirements/requirements-before-consolidation.md:46 |
| legacy_app_R:R12 | 履歴・回帰根拠。現行要件への適用は個別判断 | alreadyimplemented | G17 | records/docs/requirements/requirements-before-consolidation.md:47 |
| legacy_app_R:R13 | 履歴・回帰根拠。現行要件への適用は個別判断 | implementnow | G01 | records/docs/requirements/requirements-before-consolidation.md:48 |
| legacy_app_R:R14 | 履歴・回帰根拠。現行要件への適用は個別判断 | alreadyimplemented | G17 | records/docs/requirements/requirements-before-consolidation.md:49 |

## 7. 証拠の境界と検証

- 保存snapshot: 2026-10-07T01:14:44Z。SHA 5a36daff99deff627e10a868c7f48b059cf29cedfee98c033d8713ddd336de42
- 過去公開package SHA: 465dcdc2eec6deb181f8df811558bdade4f0b6494675346e1cac700d90f1a740。保存SHAと同一視しない。
- 現在公開v35の公式Export・Source10件・DataSourcesの一致を確認。最新未公開下書き・現在Dataverse行・操作時認可・Studio/Playerの実機試験は別途未確認。
- ソース編集、ブラウザー操作、外部更新、公開、main統合は実施していない。manual-20261010-readiness配下の成果物のみ。
- カバレッジ: 100/100操作、59/59未来操作、240/240要件、136/136決定。ID重複なし。

## 8. 成果物

- readiness-inventory.json: 詳細な全件台帳
- future-operations-59.json: 保存ソース未存在59操作の抽出
- build_readiness_inventory.py: 台帳再生成と全件数検証
- readiness-summary.json: 件数・coverage検証
- field-readiness-56.json / .md: 現行56列の個別保存準備
- current-source-verification.json: 公式v35 ExportのSourceとDataSources一致
- issue51-readonly.json: Issue #51 / ABS-RATE-001の最新読取、型等は未定
