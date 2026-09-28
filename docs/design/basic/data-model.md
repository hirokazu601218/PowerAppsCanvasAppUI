# Dataverseデータ設計（職員基本・通勤・基準給与簿）

## 対象と正本

現行単一アプリは隔離された `M_職員基本_STUDIO`、`T_通勤_STUDIO`、`T_基準給与簿_STUDIO` を参照する。以下の元テーブルの設計は親子関係と型を考える根拠であり、`_STUDIO` の物理列・権限・行を読戻した証拠ではない。接続・保存・権限の未確認部分は[未決一覧](../../requirements/open-decisions.md)を参照。

| テーブル | 論理関係と主な契約 | 全列の正本 |
|---|---|---|
| `M_職員基本`（元の `crb3c_staffbasic`） | 職員1人1行。12桁数字の職員番号を文字列の代替キーとし、実体の主キーはGUID。在籍状態は日本時間の日付から導出。 | [移行前の職員基本設計](../../../records/docs/design/dataverse-staff-basic-before-consolidation.md#テーブル)。`_STUDIO`側の列・権限は未照合 |
| `T_通勤`（元の `crb3c_commute`） | 親職員1件に認定0..N件。子の親LookupはGUID、子の職員番号は重複可能。認定GUIDと職員の一致を確認する。 | [機械可読の84列](../../../config/dataverse/commute-columns.json)。原本の型決定・テスト値は[移行前の設計](../../../records/docs/design/dataverse-commute-before-consolidation.md) |
| `T_基準給与簿`（元の `crb3c_payrollledger`） | 親職員1件に履歴0..N件。同月複数行を許容し、各行をGUIDで区別。SCR-002では読取り専用。 | [機械可読の163列](../../../config/dataverse/payrollledger-columns.json)。元の範囲・fixtureは[移行前の設計](../../../records/docs/design/dataverse-payrollledger-before-consolidation.md) |

## 関係と検証の境界

| 関係 | 必要な確認 |
|---|---|
| 職員→通勤 | 職員番号の代替キーから親GUIDを解決して子Lookupへ結ぶ。認定IDだけ、氏名だけでは別人を区別できない。0件、複数件、同姓同名、退職・未来のfixtureを確認 |
| 職員→給与簿 | 親GUIDのLookupと12桁番号の整合を確認。同月複数行、追給・返納の負値、登録済み0円とNULLを区別 |
| 元テーブル→隔離`_STUDIO` | テーブル名の類似だけで列型・権限・データが同一とは判断しない。現行接続先のメタデータと画面での読戻しが必要 |
| 各画面の更新 | 基本情報・通勤を含む5区分の編集可能列、勤務・保険・税の保存先、実効ロールを確定してから書込みを検証。給与簿のSCR-002からの更新は要件外 |

元テーブルでは通勤・給与簿の子Lookupは `ApplicationRequired` だが、任意のAPI経路で非NULLが保証されたわけではない。書込み経路ごとに親子関係を検証する。職員基本の税表は甲／乙、勤務時間は分の整数（例7:45＝465分）、保険は未確認の空欄と未加入を区別する。これらの列挙・型は元テーブルの契約であり、現行隔離テーブルの実測値への転記は保留する。

古いDataverse作成作業の実行手順、7件・6件の投入値、60分制限、旧Canvas接続前提は各[移行前の設計](../../../records/docs/design/)に保存した。現在の自動化フローが使う対象と権限は[単一アプリ運用](../../operations/single-app-workflow.md)と実際の接続設定で確認する。

## SCR-002の4履歴テーブル（2026-09-28）

添付4定義書の列名・型・制約を[機械可読の列契約](../../../config/dataverse/scr002-history-columns.json)に転記した。正式4表と隔離4表のメタデータ、親子関係は[構築Action](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36363649180)で読戻し済み。現行アプリでの全列表示、利用者権限、保存動作は別途検証する。

| タブ | 正式表 / 隔離表（論理名） | 添付列数 |
|---|---|---:|
| 勤務条件 | `crb3c_workcondition` / `crb3c_studioworkcondition` | 15 |
| 社会保険 | `crb3c_socialinsurance` / `crb3c_studiosocialinsurance` | 26 |
| 税固定控除 | `crb3c_taxfixeddeduction` / `crb3c_studiotaxfixeddeduction` | 9 |
| 税固定控除内の住民税 | `crb3c_residenttax` / `crb3c_studioresidenttax` | 6 |

各表は所有者付きで、GUIDの主キー、必須の履歴レコード名、および親職員への必須Lookupを持つ。親は正式表では`M_職員基本`、隔離表では`M_職員基本_STUDIO`。親の削除はRestrict。添付56列はいずれも任意で、日付はDateOnly、数値は整数または小数。元定義の正規表現・候補値など列型だけで表せない条件は列の説明に記録した。正式表に人事行は投入せず、隔離表は架空値だけで試験する。子の職員番号と親GUIDの整合は書込み時に別途検証する。
