# 基準給与簿 Dataverse作成・検証結果

実施日: 2026-09-17。対象は既存の隔離テスト環境。依頼されたテーブル・リレーション・テストデータの作成を完了した。

| 工程 | 結果 | 証跡 |
|---|---|---|
| ①定義・環境確認 | PASS | preflight [35179428426](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35179428426)。親25名、職員番号代替キーActive、新テーブルなし |
| ②列・関連作成 | PASS | provision [35179675557](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35179675557)。163業務列、名称・型・任意指定・上限・小数精度を照合、親Lookup作成 |
| ③データ登録 | PASS | seed [35179933809](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35179933809)。7件新規登録、全163値と親の氏名・所属・在職期間を照合 |
| ④整合性・読取り権限 | PASS | verify [35180031165](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35180031165)。再読込で追加0件、全値一致、権限変更0件、各行ReadAccessのみ |
| ⑤GitHub記録 | PASS | 設計・163項目対応表・合成7件・実行スクリプト・結果JSON・STATUS・原本索引を[PR #48](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/48)へ保存 |

## 作成内容

- `T_基準給与簿` / `crb3c_payrollledger` / Web API EntitySet `crb3c_payrollledgers`。
- 親 `M_職員基本`、関連 `crb3c_staffbasic_payrollledger`。既存職員番号の代替キーで親GUIDのLookupを解決して登録。
- 親25名のうち20名は子0件、4名は1件、1名は3件。合計7件。同姓同名2名は別の職員番号・親GUIDで関連付けた。
- 親25件の照合対象（ID・職員番号・氏名・所属・採用日・退職日）は処理前後で不変。親を更新するAPIは実行していない。
- 7件のfixtureは実環境読戻しとGitHub `tests/fixtures/payrollledger-7.json` が一致。

## 権限変更

ユーザー承認の範囲で、既存の専用ロール`StaffMaster Test Reader`に本テーブルのRead=Globalを1件追加した。変更前に対象が専用テストユーザー1名、チーム0件であることを確認。他の権限が不変であることを比較した。

全7行に対しDataverseのRetrievePrincipalAccessでReadAccessのみを確認。Write/Delete/Assign/Share/Append/AppendTo権限なし。これはDataverseの有効アクセス権検証であり、Canvasの給与画面に接続したE2E試験ではない。

## 試験と限界

ローカルおよびActionsの5テストが合格。163項目の型構成、0/1/N、孤児・親不一致・氏名/所属不一致、採用前/退職後、負数調整、円金額の小数拒否、時間の小数、合計・振込の不一致を検証した。実環境では163列・7行×163項目=1,141値を照合し、追加の表示名とLookupも確認した。

給与額・所得税は任意の合成値であり法定計算ではない。日付は原本指定の和暦文字列を維持。LookupのApplicationRequiredはAPIのNOT NULL制約ではなく、投入処理で親と職員番号を検証している。

アプリへのデータソース追加、内蔵Payroll削除、画面/帳票表示検証、再公開は今回対象外。公開アプリv1.18の給与は引き続き内蔵データを利用する。テーブルを使用するアプリ改修は後続依頼で実施する。

## 変更範囲と時間

料金・ライセンス・課金設定の変更なし。Power Apps編集ロックの上書き操作なし。
Workの起算は2026-09-17T03:41:43.436Z。最終Dataverse検証は60分の期限内に完了。全段階で同じ開始時刻を引継いだ。

詳細: [機械可読証跡](payrollledger-dataverse-evidence.json)、[設計・受入条件](../design/dataverse-payrollledger.md)。
