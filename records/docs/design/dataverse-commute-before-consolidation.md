# Dataverse 通勤テーブル設計（2026-09-17）

## 依頼・対象

添付 `T_通勤_テーブル定義書.xlsx` の84業務項目を `T_通勤` として追加する。職員基本1件に通勤0件以上を関連付け、既存25名と整合する合成テストデータを登録する。

- 要件ID：COM-DV-001（84項目）、002（親1対子0..N）、003（既存親と整合するテストデータ）。
- 対象：既存隔離テスト環境、既存 `StaffMasterAutomation` ソリューション。環境識別は `config/apps/staff-master.json` を参照。
- 原本SHA256：`d960e4de97bbb9adccdf1e500827abdaf5b6f888f8634833bddc00093620d40a`。定義書と「作成条件」を確認。全84項目は任意と記載。
- 公開Canvasアプリv1.17、YAML／Fx、内蔵通勤データ、既存親レコードは今回変更しない。アプリの取得元切替は別工程。

## 親子関係

| 対象 | 設定 |
|---|---|
| 親 | `M_職員基本` / `crb3c_staffbasic` |
| 子 | `T_通勤` / `crb3c_commute` |
| 職員番号 | 親の既存12桁文字列・一意代替キー `crb3c_staffnumber_key` で照合 |
| 関連 | `crb3c_staffbasic_commute`、親1件に子0..N件 |
| 子の参照列 | `crb3c_staffbasicid`、表示名「職員基本」、ApplicationRequired |
| 内部参照 | 職員番号で親を特定してLookupに関連付ける。Dataverse内部の外部参照は親GUID |
| 主キー | Dataverseが管理する `crb3c_commuteid` GUID。職員番号には子側で一意制約を設定しない |
| 主列 | 補助列 `crb3c_name`「通勤レコード名」。認定ID＋職員番号 |
| 親の削除 | 子がある親の削除を制限（Restrict）。連鎖削除しない |
| 所有権・共有 | UserOwned。Assign/Reparent/Share/Unshare/Merge/RollupViewはNoCascade |

原本の「職員番号」「氏名」はそのまま文字列列として残す。登録時点の値であり、Lookupが実際の親子関係を保持する。親の改名に伴う文字列の自動同期は今回実装しない。

LookupのApplicationRequiredはアプリ向け必須設定であり、任意API経由の空参照をサーバーで完全に禁止するものではない。今回の投入処理は参照・職員番号・氏名の一致を必須検証する。任意の将来書込経路についても同じ検証を行うこと。IDの正規表現・日付間整合・親との値の整合は投入時検証であり、汎用サーバープラグインは追加しない。

参照方式：[Microsoft Lookup作成仕様](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/create-update-entity-relationships-using-web-api)、[代替キーによる参照](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-alternate-key-reference-record)。

## 型・制約の扱い

- 原本の全84業務項目を任意として保持。GUID、主列、親Lookup、Dataverse標準列は別途追加される。
- 日付はDateOnly、金額・月は整数。非負整数の上限は2,147,483,647。月は1..12、方式フラグは0..1。
- 小数は原本で桁精度指定がないため小数4桁、0..1,000,000,000とした。文字列は原本の上限を優先し、未指定は200文字。
- 支給方式は文字列。業務上の選択肢や複合方式を勝手に閉じたChoiceへ変更しない。
- `2_2箇月当たり…` / `3_3箇月当たり…` / `4_4箇月当たり…` は原本表記を保持。意味を推測した集計式は追加しない。
- 「氏名」の全角想定は正規化で既存親を変更せず、実際の親氏名を空白も含めて複写する。
- 通勤認定IDには原本にない一意制約を追加しない。投入処理は決定的GUIDで重複作成を防ぐ。

## テストデータ

| 職員番号 | 通勤認定ID | 適用期間 | 支給方式 | 確認するケース |
|---|---|---|---|---|
| 009900000003 | TK-910001 | 2026-04-01～09-30 | 半年定期 | 同一親の前期間、半年7,800円 |
| 009900000003 | TK-910002 | 2026-10-01～2027-03-31 | 半年定期 | 同一親の次期間、半年8,400円 |
| 009900000004 | TK-910003 | 2025-04-01～2026-03-31 | 毎月精算 | 退職日以内、IC420円×40回=16,800円 |
| 009900000011 | TK-910004 | 2026-04-01～2027-03-31 | 支給なし | 同姓同名でも職員番号で紐付け |
| 009900000013 | TK-910005 | 2026-04-01～2027-03-31 | 支給なし | 0円と空欄を区別 |
| 009900000025 | TK-910006 | 2099-04-01～2100-03-31 | 支給なし | 未来採用日からの予定期間 |

25名中5名へ6件。残り20名は子0件。009900000011と同姓同名の009900000012には子を作らない。親の既存通勤方式・金額が設定済みなら一致させ、未設定の003/004に有料の合成ケースを置く。親の通勤登録状態を更新しないため、将来アプリ切替時の集約・表示方針は別途扱う。

全データは合成であり正式な通勤認定ではない。2～4経路目は任意NULLのケースを保持する。テストデータの固定JSONは `tests/fixtures/commute-6.json`、実環境投入直前には親を読んで再生成・検査する。

## 実行と再開

`automation/commute-run.json` のmodeを preflight → provision → seed / verify の順で指定。既存OIDC認証を利用し、テナント・環境・親25件・代替キーを検査する。権限、ライセンス、課金、アプリ接続を変更しない。

既存の子レコードを上書きしない。既存GUIDを読戻し、想定値と違えば停止する。作成はIf-None-Matchで保護。途中失敗時は実環境を再読し、作成済みテーブルを削除・再作成しない。起算時刻を修復で更新せず、60分前に停止する。

公開Canvasアプリ用の利用者ロールへ新しい通勤テーブル権限は付与しない。アプリ接続を追加するときに必要な権限を確認し、権限変更が必要ならユーザーへ確認する。

## 84項目対応表

機械可読の正本は `config/dataverse/commute-columns.json`。下表の型・長さはその内容から作成した。

| # | 原本項目名 | Dataverse論理名 | 型・範囲 |
|---|---|---|---|
| 1 | 通勤認定ID | `crb3c_recognitionid` | 文字列 9文字 |
| 2 | 職員番号 | `crb3c_staffnumber` | 文字列 12文字 |
| 3 | 氏名 | `crb3c_fullname` | 文字列 50文字 |
| 4 | 適用開始日 | `crb3c_startdate` | 日付のみ |
| 5 | 適用終了日 | `crb3c_enddate` | 日付のみ |
| 6 | 支給方式 | `crb3c_method` | 文字列 200文字 |
| 7 | 通勤4月 | `crb3c_month04` | 整数 0..2147483647 |
| 8 | 通勤5月 | `crb3c_month05` | 整数 0..2147483647 |
| 9 | 通勤6月 | `crb3c_month06` | 整数 0..2147483647 |
| 10 | 通勤7月 | `crb3c_month07` | 整数 0..2147483647 |
| 11 | 通勤8月 | `crb3c_month08` | 整数 0..2147483647 |
| 12 | 通勤9月 | `crb3c_month09` | 整数 0..2147483647 |
| 13 | 通勤10月 | `crb3c_month10` | 整数 0..2147483647 |
| 14 | 通勤11月 | `crb3c_month11` | 整数 0..2147483647 |
| 15 | 通勤12月 | `crb3c_month12` | 整数 0..2147483647 |
| 16 | 通勤1月 | `crb3c_month01` | 整数 0..2147483647 |
| 17 | 通勤2月 | `crb3c_month02` | 整数 0..2147483647 |
| 18 | 通勤3月 | `crb3c_month03` | 整数 0..2147483647 |
| 19 | 通勤毎月 | `crb3c_monthly` | 整数 0..2147483647 |
| 20 | 通勤IC運賃 | `crb3c_icfare` | 整数 0..2147483647 |
| 21 | 半年定期 | `crb3c_sixmonthpass` | 整数 0..1 |
| 22 | 毎月固定 | `crb3c_monthlyfixed` | 整数 0..1 |
| 23 | 毎月精算 | `crb3c_monthlyactual` | 整数 0..1 |
| 24 | 該当数 | `crb3c_matchcount` | 整数 0..2147483647 |
| 25 | 支給対象1 | `crb3c_target1` | 文字列 200文字 |
| 26 | 支給対象2 | `crb3c_target2` | 文字列 200文字 |
| 27 | 支給対象3 | `crb3c_target3` | 文字列 200文字 |
| 28 | 支給対象結合 | `crb3c_targetcombined` | 文字列 200文字 |
| 29 | 事実発生年月日 | `crb3c_eventdate` | 日付のみ |
| 30 | 提出年月日 | `crb3c_submitteddate` | 日付のみ |
| 31 | 受理年月日 | `crb3c_receiveddate` | 日付のみ |
| 32 | 1_交通機関 | `crb3c_route1_operator` | 文字列 100文字 |
| 33 | 1_利用区間発 | `crb3c_route1_from` | 文字列 100文字 |
| 34 | 1_利用区間着 | `crb3c_route1_to` | 文字列 100文字 |
| 35 | 1_定期等別 | `crb3c_route1_tickettype` | 文字列 200文字 |
| 36 | 1_回数券他_算定基礎 | `crb3c_route1_ticketbasis` | 小数4桁 0..1000000000 |
| 37 | 1_定期券(km)_算定基礎 | `crb3c_route1_distancekm` | 小数4桁 0..1000000000 |
| 38 | 1_回数券他_相当額 | `crb3c_route1_ticketamount` | 整数 0..2147483647 |
| 39 | 1_定期券_相当額 | `crb3c_route1_passamount` | 整数 0..2147483647 |
| 40 | 1_定期箇月 | `crb3c_route1_passmonths` | 整数 1..12 |
| 41 | 1_１箇月当たりの運賃等相当額 | `crb3c_route1_amount` | 整数 0..2147483647 |
| 42 | 1_認定期間始 | `crb3c_route1_recognitionstart` | 日付のみ |
| 43 | 1_支給月 | `crb3c_route1_paymonth` | 整数 1..12 |
| 44 | 1_備考 | `crb3c_route1_remarks` | 文字列 255文字 |
| 45 | 2_交通機関 | `crb3c_route2_operator` | 文字列 100文字 |
| 46 | 2_利用区間発 | `crb3c_route2_from` | 文字列 100文字 |
| 47 | 2_利用区間着 | `crb3c_route2_to` | 文字列 100文字 |
| 48 | 2_定期等別 | `crb3c_route2_tickettype` | 文字列 200文字 |
| 49 | 2_回数券他_算定基礎 | `crb3c_route2_ticketbasis` | 小数4桁 0..1000000000 |
| 50 | 2_定期券(km)_算定基礎 | `crb3c_route2_distancekm` | 小数4桁 0..1000000000 |
| 51 | 2_回数券他_相当額 | `crb3c_route2_ticketamount` | 整数 0..2147483647 |
| 52 | 2_定期券_相当額 | `crb3c_route2_passamount` | 整数 0..2147483647 |
| 53 | 2_定期箇月 | `crb3c_route2_passmonths` | 整数 1..12 |
| 54 | 2_2箇月当たりの運賃等相当額 | `crb3c_route2_amount` | 整数 0..2147483647 |
| 55 | 2_認定期間始 | `crb3c_route2_recognitionstart` | 日付のみ |
| 56 | 2_支給月 | `crb3c_route2_paymonth` | 整数 1..12 |
| 57 | 2_備考 | `crb3c_route2_remarks` | 文字列 255文字 |
| 58 | 3_交通機関 | `crb3c_route3_operator` | 文字列 100文字 |
| 59 | 3_利用区間発 | `crb3c_route3_from` | 文字列 100文字 |
| 60 | 3_利用区間着 | `crb3c_route3_to` | 文字列 100文字 |
| 61 | 3_定期等別 | `crb3c_route3_tickettype` | 文字列 200文字 |
| 62 | 3_回数券他_算定基礎 | `crb3c_route3_ticketbasis` | 小数4桁 0..1000000000 |
| 63 | 3_定期券(km)_算定基礎 | `crb3c_route3_distancekm` | 小数4桁 0..1000000000 |
| 64 | 3_回数券他_相当額 | `crb3c_route3_ticketamount` | 整数 0..2147483647 |
| 65 | 3_定期券_相当額 | `crb3c_route3_passamount` | 整数 0..2147483647 |
| 66 | 3_定期箇月 | `crb3c_route3_passmonths` | 整数 1..12 |
| 67 | 3_3箇月当たりの運賃等相当額 | `crb3c_route3_amount` | 整数 0..2147483647 |
| 68 | 3_認定期間始 | `crb3c_route3_recognitionstart` | 日付のみ |
| 69 | 3_支給月 | `crb3c_route3_paymonth` | 整数 1..12 |
| 70 | 3_備考 | `crb3c_route3_remarks` | 文字列 255文字 |
| 71 | 4_交通機関 | `crb3c_route4_operator` | 文字列 100文字 |
| 72 | 4_利用区間発 | `crb3c_route4_from` | 文字列 100文字 |
| 73 | 4_利用区間着 | `crb3c_route4_to` | 文字列 100文字 |
| 74 | 4_定期等別 | `crb3c_route4_tickettype` | 文字列 200文字 |
| 75 | 4_回数券他_算定基礎 | `crb3c_route4_ticketbasis` | 小数4桁 0..1000000000 |
| 76 | 4_定期券(km)_算定基礎 | `crb3c_route4_distancekm` | 小数4桁 0..1000000000 |
| 77 | 4_回数券他_相当額 | `crb3c_route4_ticketamount` | 整数 0..2147483647 |
| 78 | 4_定期券_相当額 | `crb3c_route4_passamount` | 整数 0..2147483647 |
| 79 | 4_定期箇月 | `crb3c_route4_passmonths` | 整数 1..12 |
| 80 | 4_4箇月当たりの運賃等相当額 | `crb3c_route4_amount` | 整数 0..2147483647 |
| 81 | 4_認定期間始 | `crb3c_route4_recognitionstart` | 日付のみ |
| 82 | 4_支給月 | `crb3c_route4_paymonth` | 整数 1..12 |
| 83 | 4_備考 | `crb3c_route4_remarks` | 文字列 255文字 |
| 84 | １箇月当たりの運賃等相当額の合計額 | `crb3c_monthlytotal` | 整数 0..2147483647 |
