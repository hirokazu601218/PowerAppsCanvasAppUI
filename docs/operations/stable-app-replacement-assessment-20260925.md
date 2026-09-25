# 安定版アプリの置換・旧版削除判断（2026-09-25 読取り調査）

対象環境：`StaffMaster-Automation-Test`。旧安定版 `362ac991-eead-4f07-8373-afdb3ebfdba1` と編集用 `204a48dc-7f23-43dd-b934-4654a3cfa306` の現在公開パッケージをMakerから読み取り、ソリューション画面と照合した。アプリ・テーブル・ソリューションの変更、削除、公開は行っていない。今後の安定版として編集用アプリを初回コピーするというユーザー方針を前提とする。

## 「10部品」の意味

`StaffMasterAutomation`（表示名：職員マスタ自動化）の**ソリューションのルート構成要素**が10件。キャンバス画面のコントロール数ではない。編集用アプリ自体はこの10件に含まれない。

|種類|内訳|件数|
|---|---|---:|
|Canvasアプリ|自動開発_職員マスタ検索（旧安定版）|1|
|本番側Dataverseテーブル|M_職員基本、T_基準給与簿、T_通勤|3|
|編集隔離側Dataverseテーブル|M_職員基本_STUDIO、T_基準給与簿_STUDIO、T_通勤_STUDIO|3|
|HTML Webリソース|HTML帳票PoC（固定値）、通勤手当認定簿（正式2ページ）、通勤認定簿 Studio隔離版|3|
|合計||10|

[読取り専用Actions run 36083565028](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36083565028)でRootComponentはCanvas type 300=1、Table type 1=6、Web Resource type 61=3と確認。表示名はMakerのソリューションObjects画面で確認。既存Solutionの10件をそのままimportする経路と、Canvas 1件だけの隔離配布経路は対象範囲が異なる。

## 公開アプリ本体の比較

|項目|旧安定版|編集用|
|---|---|---|
|App ID|`362ac991-eead-4f07-8373-afdb3ebfdba1`|`204a48dc-7f23-43dd-b934-4654a3cfa306`|
|Maker版履歴|v61 Live、v62未公開|v8 Live|
|公開msapp SHA256|`4078adc1c7e3c4a7122b2fe8731bb4a3904061f33272ebbb99259bd46e995518`|`d3063eac783580e2d089c93254fcf0c3d1f4dca977cb27da8538697a42c024ee`|
|画面と実行コントロール|6画面・244個|6画面・244個|
|所有者|PowerAppsCanvasAppUI-Automation|山下 浩和|
|共有|山下 浩和、Power Apps 自動テストが共同所有者|Power Apps 自動テストが共同所有者|
|MakerのConnections／Flowsタブ|いずれも「なし」の表示|いずれも「なし」の表示|

公開msappを展開した8つのSource Code形式YAMLでは、`scrAttendance`、`scrBonus`、`scrMaintenance`、`scrPayroll`、`_EditorState` がバイト一致。変更は `App.Formulas` 1件、`scrStaffMasterSearch` の式5件（テーブル名・レコードID・HTML参照先）、`scrHome.ContentLanguage` 1件（編集用に `=Blank()` が追加）。コントロール名は各244個のうち通常名237個が共通、内部生成GUID 7個はコピーごとに相違。見かけの画面構造が近くても、データ参照の相違は機能・安全性に直結する。現在のGitHub上の追加UI変更がこれら公開版へ反映済みであることは、この比較だけでは証明しない。

|用途|旧安定版が参照するテーブル|編集用が参照するテーブル|
|---|---|---|
|職員基本|`M_職員基本` / `crb3c_staffbasics`|`M_職員基本_STUDIO` / `crb3c_studiostaffbasics`|
|通勤|`T_通勤` / `crb3c_commutes`|`T_通勤_STUDIO` / `crb3c_studiocommutes`|
|給与簿|`T_基準給与簿` / `crb3c_payrollledgers`|`T_基準給与簿_STUDIO` / `crb3c_studiopayrollledgers`|
|通勤認定簿HTML|`crb3c_reports/commute-ledger.html`|`crb3c_reports/commute-ledger-studio.html`|

したがって**編集用アプリをSave asしただけでは本番データ用の安定版にはならない**。新コピーは編集用の隔離テーブルと隔離HTML参照を持ち込む。利用者が新アプリIDを利用するには、そのアプリ固有の共有・所有権・URLも切り替える必要がある。Maker画面では旧安定版が自動化主体所有、編集用が山下 浩和所有。既存のGitHub `config/apps/staff-master.json`、Actions、e2e等には旧App ID参照が残る。

## 削除判断

**現時点では旧安定版の削除を推奨しない。** 新しい安定版コピーは未作成であり、コピー後の本番3テーブルへの切替、正式HTML参照、版の公開、実利用画面、共有・権限、URL/自動化の移行が未検証。旧安定版にはライブv61と未公開v62の履歴があり、現在の復旧点でもある。

削除を検討できる条件：

1. 編集用アプリから作った新コピーを特定し、**本番用3テーブルと正式HTML**へ切り替え、指定した差分以外の全ソース・実行定義・3参照を確認する。編集用のテストレコードへの書込みをそのまま本番用へ通さない。
2. 新コピーの共有先・データアクセス権、Playerの検索・給与・帳票などの受入、改訂配布と切り戻しを確認する。import直後にライブになった隔離試験の観測も考慮する。
3. アプリID・URLを参照するGitHub設定、Actions、E2E、配布済みリンクや他の外部導線を新App IDへ切り替え、旧App IDを使う処理が残っていないことを確認する。リポジトリ外の利用状況は現時点で未確認。
4. 旧安定版の公開物・履歴・設定を復旧可能な形で保全し、新版を実際に運用して問題がないことを確認した後、ユーザーが**旧アプリ単体**の削除を判断する。ソリューション、6テーブル、3 Webリソースは別の対象として扱う。

Power Appsの「Delete from cloud」は共有先の利用者のアプリも削除する。未管理ソリューションの削除は構成要素を削除しないが、アプリ単体・ソリューション・テーブルの削除は別操作なので混同しない。関連するMicrosoft Learn：[キャンバスアプリ削除](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/delete-app)、[ソリューション作成・削除](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/create-solution)。
