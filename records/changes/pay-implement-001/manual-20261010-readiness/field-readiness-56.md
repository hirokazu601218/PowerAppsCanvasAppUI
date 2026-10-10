# PAY-IMPLEMENT-001：現行履歴56列の保存準備

勤務15・社会保険26・税固定控除9・住民税6の全56列を個別確認した。物理名・型・親GUIDと表示キーは既知。現在v35の公式Export内DataSourcesとソースを根拠に、btnSave拒否だけでは判断していない。

## 結論

- 物理列既知 56/56、schema IsValidForUpdate=true 56/56、汎用UI入力可 56/56
- 完全な限定保存として実装準備完了：0列。54列は具体的な設計依存、2列の始終業時刻はQ16により入力対象外。
- 最小候補はWorkの辞令案・辞令コメント・その他備考。text4000・行GUID・親・ドラフト／再取得は既知だが、許可列・状態と訂正監査の契約が未指定。
- 既存の隔離fixture訂正と、新モデルの全業務保存を別に判定する。後者の未完成だけを理由に物理列がないとは言わない。
- 列のAuditFlag=trueやIsWritable=trueは、実効権限や監査記録成功の証明ではない。専用利用者は過去Readのみ。権限を変更して迂回しない。

## 入力形式の準備状態

{"format_and_domain_ready": 8, "format_ready": 34, "domain_incomplete": 12, "excluded_by_confirmed_scope": 2}

形式変換の設計が揃っても保存許可を意味しない。多表一括更新を作らず、単一の事前指定架空行・許可列・前値退避・再取得一致を最小単位とする。

## 全56列

| 表 | 順 | 項目 | 物理列／型 | 入力契約の準備 | 保存を止めている具体点 |
|---|---:|---|---|---|---|
| work | 1 | 職員番号 | crb3c_staffnumber / String | format_and_domain_ready | 12桁文字列の検証は設計済み。子の番号を親職員GUIDと異なる値へ変える操作／親付替えは未定。一般入力が見えることを識別キー編集許可とみなさない。 |
| work | 2 | 氏名 | crb3c_fullname / String | format_ready | 200文字の物理text列は既知。職員基本氏名の写し／履歴時点の氏名／独立編集のどれかと、変更の伝播範囲が未定。 |
| work | 3 | 適用開始日 | crb3c_startdate / DateTime | format_ready | DateOnly／有効暦日／任意は既知。開始終了の空欄・重複・訂正か新履歴かの判定と、確認状態・未払い失効への保存連携が未設計。 |
| work | 4 | 適用終了日 | crb3c_enddate / DateTime | format_ready | DateOnly／有効暦日／任意は既知。開始終了の空欄・重複・訂正か新履歴かの判定と、確認状態・未払い失効への保存連携が未設計。 |
| work | 5 | 異動区分 | crb3c_transferkind / String | format_and_domain_ready | 列説明は6候補を列挙。選択UI化は技術的に可能。ただし登録／新履歴／訂正の操作別許可と状態保存が未定。 |
| work | 6 | 発令事由区分 | crb3c_appointmentreason / String | domain_incomplete | 説明は確認値例のみで完全候補集合ではない。正式区分マスタ／廃止候補と新旧履歴への適用契約がない。 |
| work | 7 | 日額単価 | crb3c_dailyrate / Integer | format_ready | 0以上整数の物理列は既知。最新Q40は単価マスタ選択なので、自由数値訂正を本給与条件登録とするにはマスタ対応・訂正／再確認契約が必要。 |
| work | 8 | 勤務時間開始 | crb3c_workstart / String | excluded_by_confirmed_scope | 最新Q16で始業時刻は入力対象外。過去値の表示を維持しても保存解放しない。 |
| work | 9 | 勤務時間終了 | crb3c_workend / String | excluded_by_confirmed_scope | 最新Q16で終業時刻は入力対象外。過去値の表示を維持しても保存解放しない。 |
| work | 10 | １日あたりの勤務時間 | crb3c_dailyhours / Decimal | format_and_domain_ready | 説明は0～24、DB MaxValueは1000000000。アプリ検証は確定説明の24上限・小数2桁を守れる。履歴追加と訂正・再確認の保存契約が未定。 |
| work | 11 | 超勤基礎単価（参考） | crb3c_overtimebaserate / Integer | format_ready | 参考単価の物理整数列は既知だが、参考表示を編集対象にする許可列定義がない。給与使用値か表示専用かの対応が未確定。 |
| work | 12 | 支出科目名 | crb3c_budgetitem / String | format_ready | 文字列名称は既知。Q12の所属既定予算／履歴個別予算の識別子・上書き元を自由名称列から推定できない。 |
| work | 13 | 辞令案 | crb3c_appointmentdraft / String | format_ready | 4000文字・改行の型契約は既知。任意入力を許す列リスト、履歴訂正監査、改行を保持するUI・読戻しが未実装。 |
| work | 14 | 辞令コメント | crb3c_appointmentcomment / String | format_ready | 4000文字・改行の型契約は既知。非計算項目の限定候補だが、既存履歴内での更新許可と訂正前後記録の設計がない。 |
| work | 15 | その他備考 | crb3c_notes / String | format_ready | 4000文字・改行の型契約は既知。最小の保存候補だが、自由備考を履歴訂正監査から除外する根拠も、許可列一覧もない。 |
| social | 1 | 職員番号 | crb3c_staffnumber / String | format_and_domain_ready | 12桁文字列の検証は設計済み。子の番号を親職員GUIDと異なる値へ変える操作／親付替えは未定。一般入力が見えることを識別キー編集許可とみなさない。 |
| social | 2 | 氏名 | crb3c_fullname / String | format_ready | 200文字の物理text列は既知。職員基本氏名の写し／履歴時点の氏名／独立編集のどれかと、変更の伝播範囲が未定。 |
| social | 3 | 職員雇用区分 | crb3c_employmentcategory / String | domain_incomplete | 職員雇用区分は例示値のみ。共通職員基本／条件履歴との役割と正式区分候補が未確定。 |
| social | 4 | 生年月日 | crb3c_birthdate / DateTime | format_ready | DateOnlyと有効暦日は既知。職員基本の生年月日との同期／履歴写し／独立訂正のどれかが未確定。 |
| social | 5 | 4/1時点年齢 | crb3c_ageapril / Integer | format_ready | 整数列は既知。年齢を手修正する列か算出表示か、基準年・生年月日との整合条件が未定。制度判定の自動化は追加しない。 |
| social | 6 | 3/1時点年齢 | crb3c_agemarch / Integer | format_ready | 整数列は既知。年齢を手修正する列か算出表示か、基準年・生年月日との整合条件が未定。制度判定の自動化は追加しない。 |
| social | 7 | 介護徴収該当 | crb3c_carestatus / String | domain_incomplete | N月から等の説明は具体的な全候補と月入力方式を定義しない。確認済み制度判断の登録とQ20の未確認区分の対応が未定。 |
| social | 8 | 厚生年金免除該当 | crb3c_pensionexemption / String | domain_incomplete | N月から等の説明は具体的な全候補と月入力方式を定義しない。給与班確認済み判断の登録契約が必要。 |
| social | 9 | 後期高齢者徴収該当 | crb3c_elderstatus / String | domain_incomplete | N月から等の説明は具体的な全候補と月入力方式を定義しない。未確認と非該当を空欄で混同できない。 |
| social | 10 | 厚生徴収開始月 | crb3c_pensionstart / DateTime | format_ready | DateOnly／有効暦日／任意は既知。この列が資格日・控除期間・改定日のどれかを新モデルへ対応し、開始終了整合と確認状態を保存する契約が未設計。 |
| social | 11 | 厚生徴収終了月日 | crb3c_pensionend / DateTime | format_ready | DateOnly／有効暦日／任意は既知。この列が資格日・控除期間・改定日のどれかを新モデルへ対応し、開始終了整合と確認状態を保存する契約が未設計。 |
| social | 12 | 厚生_級 | crb3c_pensiongrade / Integer | format_ready | 非負数・円／等級・物理桁は既知。Q22で給与班の登録方針は確定だが、対象保険・適用期間・確認状態・訂正前後監査と未払い失効の関連が未設計。 |
| social | 13 | 厚生月額 | crb3c_pensionmonthly / Integer | format_ready | 非負数・円／等級・物理桁は既知。Q22で給与班の登録方針は確定だが、対象保険・適用期間・確認状態・訂正前後監査と未払い失効の関連が未設計。 |
| social | 14 | 二以上_該当 | crb3c_multiemployer / String | format_and_domain_ready | 該当／空欄という旧契約は既知。空欄を未確認・非加入・非該当のどれへ対応させるかは新モデルで未定。 |
| social | 15 | 二以上_通知額_厚生年金保険 | crb3c_multiemployerpensionamount / Decimal | format_ready | 非負数・円／等級・物理桁は既知。Q22で給与班の登録方針は確定だが、対象保険・適用期間・確認状態・訂正前後監査と未払い失効の関連が未設計。 |
| social | 16 | 企業年金_該当 | crb3c_corporatepension / String | format_and_domain_ready | 該当／空欄という旧契約は既知。空欄を未確認・非加入・非該当のどれへ対応させるかは新モデルで未定。 |
| social | 17 | 企業年金通知額 | crb3c_corporatepensionamount / Integer | format_ready | 非負数・円／等級・物理桁は既知。Q22で給与班の登録方針は確定だが、対象保険・適用期間・確認状態・訂正前後監査と未払い失効の関連が未設計。 |
| social | 18 | 短期徴収開始月日 | crb3c_shortstart / DateTime | format_ready | DateOnly／有効暦日／任意は既知。この列が資格日・控除期間・改定日のどれかを新モデルへ対応し、開始終了整合と確認状態を保存する契約が未設計。 |
| social | 19 | 短期徴収終了月日 | crb3c_shortend / DateTime | format_ready | DateOnly／有効暦日／任意は既知。この列が資格日・控除期間・改定日のどれかを新モデルへ対応し、開始終了整合と確認状態を保存する契約が未設計。 |
| social | 20 | 長期徴収開始月 | crb3c_longstart / DateTime | format_ready | DateOnly／有効暦日／任意は既知。この列が資格日・控除期間・改定日のどれかを新モデルへ対応し、開始終了整合と確認状態を保存する契約が未設計。 |
| social | 21 | 長期徴収終了月日 | crb3c_longend / DateTime | format_ready | DateOnly／有効暦日／任意は既知。この列が資格日・控除期間・改定日のどれかを新モデルへ対応し、開始終了整合と確認状態を保存する契約が未設計。 |
| social | 22 | 等級改定日 | crb3c_graderevision / DateTime | format_ready | DateOnly／有効暦日／任意は既知。この列が資格日・控除期間・改定日のどれかを新モデルへ対応し、開始終了整合と確認状態を保存する契約が未設計。 |
| social | 23 | 短期_級 | crb3c_shortgrade / Integer | format_ready | 非負数・円／等級・物理桁は既知。Q22で給与班の登録方針は確定だが、対象保険・適用期間・確認状態・訂正前後監査と未払い失効の関連が未設計。 |
| social | 24 | 短期月額 | crb3c_shortmonthly / Integer | format_ready | 非負数・円／等級・物理桁は既知。Q22で給与班の登録方針は確定だが、対象保険・適用期間・確認状態・訂正前後監査と未払い失効の関連が未設計。 |
| social | 25 | 長期_級 | crb3c_longgrade / Integer | format_ready | 非負数・円／等級・物理桁は既知。Q22で給与班の登録方針は確定だが、対象保険・適用期間・確認状態・訂正前後監査と未払い失効の関連が未設計。 |
| social | 26 | 長期月額 | crb3c_longmonthly / Integer | format_ready | 非負数・円／等級・物理桁は既知。Q22で給与班の登録方針は確定だが、対象保険・適用期間・確認状態・訂正前後監査と未払い失効の関連が未設計。 |
| tax | 1 | 職員番号 | crb3c_staffnumber / String | format_and_domain_ready | 12桁文字列の検証は設計済み。子の番号を親職員GUIDと異なる値へ変える操作／親付替えは未定。一般入力が見えることを識別キー編集許可とみなさない。 |
| tax | 2 | 氏名 | crb3c_fullname / String | format_ready | 200文字の物理text列は既知。職員基本氏名の写し／履歴時点の氏名／独立編集のどれかと、変更の伝播範囲が未定。 |
| tax | 3 | 適用開始日 | crb3c_startdate / DateTime | format_ready | DateOnly／有効暦日／任意は既知。開始終了の空欄・重複・訂正か新履歴かの判定と、確認状態・未払い失効への保存連携が未設計。 |
| tax | 4 | 適用終了日 | crb3c_enddate / DateTime | format_ready | DateOnly／有効暦日／任意は既知。開始終了の空欄・重複・訂正か新履歴かの判定と、確認状態・未払い失効への保存連携が未設計。 |
| tax | 5 | 税表区分 | crb3c_taxtable / String | domain_incomplete | この4表用の列説明では候補値未確認。元の職員基本の甲／乙をこの履歴の全候補と無検証で転用しない。 |
| tax | 6 | 扶養控除対象人数 | crb3c_dependents / Integer | domain_incomplete | 0以上整数は既知、業務上限は未確認。DBの1,000,000,000を扶養人数上限と採用しない。 |
| tax | 7 | 雇用保険加入区分 | crb3c_employmentinsurance / String | domain_incomplete | 設定候補が未確認。新要件の未確認・加入・非加入と旧文字列の対応がない。 |
| tax | 8 | 共済貯金月額 | crb3c_savingsmonthly / Integer | format_ready | 0以上円整数列は既知。Q23の項目別×有効期間行へどう対応し、確認状態・特殊月を扱うか未定。 |
| tax | 9 | 共済貸付月額 | crb3c_loanmonthly / Integer | domain_incomplete | 0以上整数は既知。説明に値域詳細未確認、Q23の項目別履歴対応も未定。 |
| resident | 1 | 職員番号 | crb3c_staffnumber / String | format_and_domain_ready | 12桁文字列の検証は設計済み。子の番号を親職員GUIDと異なる値へ変える操作／親付替えは未定。一般入力が見えることを識別キー編集許可とみなさない。 |
| resident | 2 | 氏名 | crb3c_fullname / String | format_ready | 200文字の物理text列は既知。職員基本氏名の写し／履歴時点の氏名／独立編集のどれかと、変更の伝播範囲が未定。 |
| resident | 3 | 期間区分 | crb3c_periodcategory / String | domain_incomplete | 設定値は元ファイル内とあるだけ。月別住民税Q24の控除年月をこの自由区分から一意解釈できない。 |
| resident | 4 | 住民税月額 | crb3c_monthlyamount / Integer | format_ready | 0以上円整数は既知だが控除年月を特定する新モデルがない。旧期間区分の1行を月別行へ勝手に展開しない。 |
| resident | 5 | 自治体コード | crb3c_municipalitycode / String | domain_incomplete | 物理text200は既知。コード桁／形式・先頭0・空欄許否の業務契約は未確認。 |
| resident | 6 | 納付先自治体 | crb3c_municipalityname / String | domain_incomplete | 物理text200は既知。業務文字数制約未確認、自治体コードとの対応／写し属性の編集可否が未定。 |

## 共通の保存試験・復元

親GUID・番号・選択履歴を再検証し、変更列だけを単一行へ適用する。Null／0／不正型／範囲外／別職員／別履歴／保存失敗／再取得失敗を分離して試験する。給与簿へ書込まない。成功表示は読戻し一致後だけ。
試験前に対象行GUIDとtyped前値・行版を記録し、同じ承認済み隔離行へ前値を復元して一致確認する。親付替え・行削除・実データ・役割変更は含まない。

## 主要根拠

- config/dataverse/scr002-history-columns.json（56列）
- scripts/automation/scr002_history_schema.py（列・親Lookup・Restrict）
- docs/design/detailed/detailed-design.md:112–130（許可列・状態・保存／再取得）
- docs/changes/requests/change-20260928-scr002-history.json（表示変更、編集保存未判定）
- docs/requirements/payroll-confirmed-20261007.md:46–58（Q15～Q27）
- current v35 Src/scrStaffMasterSearch.pa.yaml:952–1009（表示と汎用入力）、:653–686（保存拒否）
- 現在公開package SHA: 465dcdc2eec6deb181f8df811558bdade4f0b6494675346e1cac700d90f1a740
- 出力されたDataSources SHA: 6d6508e38a84eeffbe2e6c3101b7769b97f925dc2dcf50917494800ad12ef7d7

詳細JSONは各列の入力パーサ契約、現行UIキー、親照合、synthetic制限、テスト、復元、要件IDを含む。環境URL・個人値・Library IDは含めない。
