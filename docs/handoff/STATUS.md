# 現在の作業と読取り対象：Studio安全編集モードの隔離CRUD

- 編集コピー `自動開発_職員マスタ検索_STUDIO_EDIT`（App ID `204a48dc-7f23-43dd-b934-4654a3cfa306`）は開発環境 `StaffMaster-Automation-Test` で保存・公開済み。画面の3データ接続は `crb3c_studiostaffbasic` / `crb3c_studiocommute` / `crb3c_studiopayrollledger` に切替済み。Studio App checkerの数式問題0件、プレビューで職員・通勤・給与を確認。
- 編集用3テーブルの合成fixtureは25／6／7件。専用ユーザー `powerapps-test@govaca.onmicrosoft.com` には既存の `StaffMaster Test Reader` ロールで編集用3テーブルのCRUD/Append/AppendToを付与。元3テーブルの作成・更新・削除権限なし。[権限検証run](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35858002859)。
- [代理実行CRUD検証run](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35930141288) で、専用ユーザーの実効権限として隔離テーブルへ合成行を作成・更新・削除し読戻し済み。これはDataverse APIの `MSCRMCallerID` による検証であり、専用アカウントのブラウザでのアプリ操作試験とは区別する。既存の `009900009999` 行の作成者は専用ユーザーと一致しなかったため、前回の画面操作を作成成功の根拠にしない。
- 2026-09-24、ユーザーの明示承認を受けてMakerの所有者セッションをサインアウトし、新規タブで専用ユーザー `Power Apps 自動テスト` と開発環境 `StaffMaster-Automation-Test` の `M_職員基本_STUDIO` を画面確認。新しい行の操作で入力用の空行が表示されたが、案内ダイアログを閉じるブラウザ操作が応答せず、値の入力・保存・更新・削除は未実施。既存fixtureへの変更は観測していないが、最終件数の再読戻しは未実施。代理実行APIの合格を画面操作の合格に読み替えない。再開時はまず隔離テーブルの件数・試験番号の不在を確認し、専用アカウント画面で合成行の作成・更新・削除と後片付けを行う。
- 元の安定版アプリと元3テーブルは無変更。元件数25／6／7件をCRUD検証runで確認。編集コピーの安定版への反映は実施していない。
- [後片付けrun](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35930232601) で作業中の合成行 `009900009999` と未割当て試作ロール `StaffMaster Studio CRUD` を削除し、不在を読戻し確認。編集用のfixture25／6／7件を維持。
- `pac canvas download` によるサービスプリンシパルの保存パッケージ取得は[run 35854544372](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35854544372)で「No canvas apps in the selected environment」となり未成立。失敗するワークフローは削除し、保存版の読戻し合格を主張しない。再構築時はアプリへのサービスプリンシパルアクセスとライセンス要件を別途判断する。
- 読取り対象：`scripts/automation/studio_edit_{schema,fixtures,access,cleanup,dataverse}.py`、`.github/workflows/studio-edit-dataverse.yml`、`automation/studio-edit-run.json`、関連Actionsログ。このWorkの次回再開時は60分制限を新たに起算する。職員基本**元テーブル**を編集する次回はIssue #51を確認。

---

# 通勤手当認定簿HTML版1.01（別Workの引継ぎ）

- ユーザーの再開指示で**今回の60分制限を解除**。A4横2ページ・JavaScript＋Dataverse読取り・指定対象の公開は承認済み。
- 指定検証アプリは**バージョン26がライブ**。MakerのPublish successful（2026-09-21 06:23:37 JST）とバージョン一覧を確認。追加は`conLedgerHeader111/btnLedgerHtmlReport`、同ヘッダー高+52のみ。旧PoC・既存子コントロールは保持。
- 新規Webリソース`crb3c_reports/commute-ledger.html`は**動的HTML版1.01を公開済み**。保存後のコード読戻しがソースと完全一致。以前の固定架空版ではない。
- **実環境での帳票表示・Web API接続/実権限・Windows/Edgeの2ページ1PDF保存は未確認**。クラウドブラウザのURL安全ポリシー拒否を回避していない。ユーザーの架空データ受入を待つ。公開成功を正式業務受入完了と扱わない。
- 試験: Node10試験群PASS（HTTP/DOMはモック）。ローカル組版は架空6件＋4明細でA4横2ページ。最大長の経路・備考はあふれ検出・出力停止。Studioは0件、復帰、職員切替、認定なし、既存帳票表示、新ボタン表示を確認。
- 読取り対象: [最新版README](../../src/staff-master/candidates/commute-html-v1.01/README.md)、[設計・項目対応・試験・受入/復旧手順](../../src/staff-master/candidates/commute-html-v1.01/docs/release-1.01.md)、同ディレクトリのソースと要件、`config/dataverse/commute-columns.json`、`tests/fixtures/commute-6.json`。PoCの経緯は`docs/poc/html-report-launch-poc.md`。
- 業務精査は[Issue #68](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/68)を継続。現在氏名・所属、期間単位、未定義欄、長文時の運用など。実データ・認証情報・環境固有URLをGitHubへ追加しない。
- 再開時: まずユーザーのWindows/Edgeで架空004/TK-910003のHTML版と2ページPDFを確認。必要な修正は最新の実アプリ／リソースを読んでから行う。版1.00候補は旧中断記録として保持。
- 下記は過去経緯・他Workの引継ぎ。最新状態は本節を優先し、他Workの残件を完了扱いにしない。職員基本テーブル編集時はIssue #51を引き続き確認する。

---

# 通勤手当認定簿HTML版：2026-09-20 中断引継ぎ

## 現在の作業と読取り対象（今回ユーザー依頼）

- A4横2ページ、JavaScript＋Dataverse Web API読取り、公開は承認済み。項目対応の後日精査はIssue #68。
- **未完成**。新規 `crb3c_reports/commute-ledger.html` に固定架空データ版のみ保存・公開（Maker成功通知確認）。動的版と新ボタンは未配置、アプリは変更・保存・公開していない。既存PoCは保持。
- 候補ソース／設計／試験／再開位置: [中断記録](../../src/staff-master/candidates/commute-html-v1.00/docs/implementation-status.md)。単体6試験グループPASS、実接続・実権限・A4横2ページPDF・既存機能スモークは未完了。
- 読取り対象: 上記中断記録、`docs/poc/html-report-launch-poc.md`、`config/dataverse/commute-columns.json`、`tests/fixtures/commute-6.json`、`assets/commute-ledger/ledger-page{1,2}-template.png`、対象候補ソース、最新の検証専用アプリとWebリソース。
- 作業開始14:23 UTC頃、17:43 UTCの確認で60分停止期限超過を認識。新規実装を止めて状態保存。再開指示後に固定版の描画・印刷確認から再開する。期限内に停止できなかったことも記録する。
- 下記は他Workの引継ぎを保存したもの。今回作業で上書き・完了扱いにしない。Issue #51のテーブル編集時確認ルールも引き継ぐ。

---

# 現在の作業と読取り対象：台帳・全6画面二形式・289表示値照合を実施

- [今回結果と再現手順](../testing/automatable-20260919/README.md)を読む。準備不足だった台帳/二形式比較/統合表示値照合を実施。
- 現行6画面816部品/11型をStudioから読戻し、全6画面の管理/貼付形式が構造一致。部品重複0。過去814部品の結果と混同しない。
- 220項目の見出し/式参照先＋認定簿69項目の参照先、fixture1645値の型、公開011の289表示値に不一致0。
- 合成履歴の日本語見出し/順序の独立業務辞書、公式版別対応プロパティ台帳、指定実行環境などは未充足。**全件完了ではない。** 累積67 PASS /14 BLOCKED /5 FAIL /9 EXCLUDED据置。NOT_RUN0を全実施完了の意味で使わない。
- PATCH-02の二形式準備不足は解消。現行プロパティ更新方式の独立コンテキスト全SMK-01は残る。[95項目](../testing/override-20260918/spec-case-audit.json)。
- 今回製品定義の編集・公開・Dataverse書込みなし。0件検索とクリア7件004を確認、公開コピーは通常ホームへ復帰。既知不具合記録のみ、PDF/HTML帳票PoC除外、時間制約解除、背景ジョブなし。
- **Issue #51：欠勤時間単価の実テーブル反映は未実施。次回実テーブル編集時に対応。**

---

# 現在の作業と読取り対象：14項目を実施・実行条件不足を記録

- **全実機試験は完了していない。** 今回14項目は合格1/導入診断不合格1/過去既知失敗継承2/前提不足10。NOT_RUN0は状態整理であり未完了解消を意味しない。
- 累積 **PASS67 / NOT_RUN0 / BLOCKED14 / FAIL5 / EXCLUDED9**。旧版の継承結果を含む。
- [14項目の結果・各停止条件](../testing/remaining14-20260919/results.md)、[今回実測](../testing/remaining14-20260919/evidence.json)、[95項目](../testing/override-20260918/spec-case-audit.json)、[適用プロファイル](../testing/current-v126-20260919/profile.md)を読む。
- DEP-03は現行別コピー共存の合格。DEP-01はApp checker診断#67を記録してFAIL。LED-05/ACC-03は#62のv1.25既知失敗を継承し分類を訂正、今回Tab再試験なし。
- D2単一プロパティ適用20031文字読戻し一致、Screen1全1444226文字・657部品の基準SHA一致。基準19443文字へ完全復元保存済み（8:28:58 AM）。今回公開なし、公開版は変更していない。
- 残りは指定2viewport/独立context環境、独立部品・項目台帳/現行二形式、人の可読性/スマホ等。条件緩和して合格にしない。追加許可待ちではなく試験前提不足。
- 元アプリ・Dataverse変更なし。#62/#64/#66/#67は記録のみ。PDF/HTML帳票PoC除外、時間制約解除。バックグラウンド実行なし。
- **Issue #51：欠勤時間単価の実テーブル反映は未実施。次回実テーブル編集時に対応。**

---

# 現在の作業と読取り対象：現行v1.26で3項目追加合格・復元済み

- 最新ユーザー「作業すすめて」により現行版プロファイル追加の確認待ちは解除。旧仕様は保持し現行プロファイルを追加した。
- 累積 **PASS66 / NOT_RUN14 / BLOCKED4 / FAIL2 / EXCLUDED9**。全件完了ではない。旧版の継承合格を含む。
- DATA-04、PATCH-03、PATCH-04を追加PASS。給与負数/0/空/備考300文字全文、単一プロパティ差分の二重適用停止、基準復元を確認。任意YAML置換や旧v1.11貼付の合格には読み替えない。
- 給与163項目は独立項目定義・fixtureと全一致。DATA-05全セクション統合は未完。
- [現行プロファイル](../testing/current-v126-20260919/profile.md)、[今回結果・残18項目](../testing/current-v126-20260919/results.md)、[実測](../testing/current-v126-20260919/evidence.json)、[95項目](../testing/override-20260918/spec-case-audit.json)。
- 元App.Formulas19443文字・Screen1全文一致へ復元保存、公開Player通常7件004・011検索1件を確認。後続二重適用試験は非公開で元式へ再復元保存。現在は通常データ・一般・03会計課ホーム。保全済みの公開基準版を維持。
- 自動承認の未保存状態リスクは保全式読戻し確認と直接保存で解消。追加許可待ちなし。
- 元アプリ・Dataverse・権限・課金変更なし。#62/#64/#66記録のみ、PDF/HTML帳票PoC除外、時間制約解除を維持。バックグラウンド実行なし。
- 残件：全プロパティ独立台帳、導入/併存/完全版比較、独立起動、全セクション照合、8表示条件、Notify幅変異。人の可読性/支援技術/スマホ確認と画像承認を自動PASSにしない。
- **Issue #51：欠勤時間単価の実テーブル反映は未実施。次回実テーブル編集時に対応。**

---

# 現在の作業と読取り対象：現行v1.26基準で検証再開

- 2026-09-19「作業すすめて」により現行版プロファイル追加案の確認待ちを解除。
- [適用基準とD2試験データ](../testing/current-v126-20260919/profile.md)。旧仕様を保存し、現行プロファイルで判定する。累積63/16/5/2/9は開始時点のまま。
- 検証コピー内のローカルレコード合成で給与の負数・0・空・長文fixtureを準備。元式を保全し試験後復元する。元アプリ・Dataverse変更なし。
- 不具合は記録のみ。PDF/HTML帳票PoC除外、時間制約解除を継続。
- **Issue #51：欠勤時間単価の実テーブル反映は未実施。次回実テーブル編集時に対応。**

---

# 現在の作業と読取り対象：公開コピー追加検証・基準復元済み

- 累積 **PASS63 / NOT_RUN16 / BLOCKED5 / FAIL2 / EXCLUDED9**。全件完了ではなく旧版証跡を含む。
- PAGE-05/HAR-01/HAR-02/ACC-01/DATA-03を追加合格。公開コピーで故障注入・検出・復元公開、4名5履歴229セル一致と20組合せの最右到達を確認。
- ACC-05のフォーカス枠コントラスト1.48:1を[Issue #66](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/66)へ記録のみ。#62/#64も修正しない。
- [今回結果](../testing/published-copy-20260918/results.md)、[実測](../testing/published-copy-20260918/evidence.json)、[95項目](../testing/override-20260918/spec-case-audit.json)。
- 検証コピーの全試験変異を復元・保存・公開済み。元アプリ定義・Dataverse変更なし。次は現行v1.26と配布ソースの対応確定、導入・差分・表示条件等の残件。
- 現行Screen1は保存v1.24から4プロパティ差分のみと逆適用Git blobハッシュで確認。全6画面の同一性は未確定。
- 残件には旧v1.11仕様と現行v1.26の基準差がある。[具体的な差・現行プロファイル案・残21項目](../testing/published-copy-20260918/remaining-profile-proposal.md)を記録。基準変更案は未承認で、合否基準へ未反映。
- HAR-03の見出し重なり検出と復元は完了。標準Notify過大幅の注入条件は未確立。
- PDF・HTML帳票PoC除外、時間制約解除、検証コピー保存・公開・復元公開の許可を継続。
- **Issue #51：欠勤時間単価の実テーブル反映は未実施、次回実テーブル編集時に対応。**

---

# 現在の作業と読取り対象：公開Player復旧・19件境界合格

- Microsoft認証後、Makerと公開検証コピーの起動・検索を確認。前回HTTP 0取得障害は今回は再現せず。元アプリのホームv1.26も目視確認。
- PAGE-05不足の19件を公開コピーで検証。全19番号順序一致、1/1、前後無効、末尾019と右サマリー一致。元App.Formulas 19443文字へ完全復元・保存・公開済み。Playerで通常7件004選択・011検索1件に復帰。
- 累積 **PASS59 / NOT_RUN19 / BLOCKED7 / FAIL1 / EXCLUDED9**。全件完了ではなく、旧版証跡を含む。
- 継続検証：[95項目](../testing/override-20260918/spec-case-audit.json)。次は検証コピーでHAR-01の公開故障検出・復元。コピー試験用保存/公開/復元公開は許可済み。
- 元アプリ定義・Dataverse変更なし。製品不具合 #62/#64 は記録のみ。PDF・HTML帳票PoC除外。時間制約解除を維持。
- **Issue #51：欠勤時間単価の実テーブル反映は未実施、次回実テーブル編集時に対応。**

---

# 現在の作業と読取り対象：コピー公開済み・Player取得障害

- ユーザーは検証専用コピーの試験用変更保存・公開・復元公開を許可済み。以前の公開許可待ちは解消。基準版の Publish successful を確認（画面時刻2026/9/19 6:16:17）。追加の故障注入はまだ行っていない。
- Microsoft認証は安全な入力でアカウント選択・パスワード送信・組織確認まで進行。その後、同じコピーのPlayerを新しいタブで確認すると「アプリを取得できませんでした」、詳細 `Launch App failed with Http status code of 0`。認証済みアプリ画面は未確認。パスワード不正とは判定しない。
- [Issue #65の追記](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/65#issuecomment-5736866601)に記録。式復元の完了は維持。新たな停止理由はPlayer取得障害。認証の再要求ループを行わない。
- 累積 PASS58 / NOT_RUN20 / BLOCKED7 / FAIL1 / EXCLUDED9 を維持。全件完了ではない。実機確認再開時はコピーの取得・基準正常系から確認。
- 元公開アプリ・Dataverse変更なし。製品不具合 #62/#64 は記録のみ。PDF関連・HTML帳票PoC除外。時間制約解除・コピー公開許可は維持。バックグラウンド処理なし。
- **Issue #51：欠勤時間単価の実テーブル反映は未実施、次回実テーブル編集時に対応。**

---

# 現在の作業と読取り対象：コピー復旧完了・試験コピー公開の明示許可待ち

- オーバーライドは許可済み・実行済み。Issue #65解消。検索式1536文字、App.Formulas19443文字の保存後読戻し一致。数式エラー0。
- [今回結果](../testing/override-20260918/results.md)、[95項目](../testing/override-20260918/spec-case-audit.json)、[実測](../testing/override-20260918/evidence.json)を読む。
- 全件完了ではない。累積 PASS58 / NOT_RUN20 / BLOCKED7 / FAIL1 / EXCLUDED9。4名5履歴229セル一致、003の105セル列位置一致。HAR-01と19件はStudioプレビューで確認しただけで、公開Eの代替PASSにしない。
- **自動承認レビューが検証コピーの公開を拒否**。オーバーライド許可だけでは公開許可に当たらないとの理由。公開未実行、ダイアログをキャンセル。許可を求める範囲は検証専用コピーのみの試験用変更保存・公開・試験後復元公開。
- コピーは未公開・元定義へ復元保存済み。元公開版は03会計課・一般・ホームへ復帰。Dataverse変更なし、新規リモートジョブ・バックグラウンド処理なし。製品不具合 #62/#64 は記録のみ。PDF関連・HTML帳票PoC除外、時間制約解除を継続。
- 人による見やすさ/読上げ/スマホ確認、基準画像承認、独立コンテキスト/200%環境は別の未充足条件。
- **Issue #51：欠勤時間単価の実テーブル反映は未実施、次回実テーブル編集時に対応。**

---

# 現在の作業と読取り対象：専用コピー復旧済み・残件検証継続

- オーバーライドはユーザー許可済み、実行して編集権取得。保存後読戻しでFill正常、検索式1536文字一致、数式エラー0。Issue #65解消。
- [今回途中記録](../testing/override-20260918/results.md)、[95項目](../testing/override-20260918/spec-case-audit.json)、[実測](../testing/override-20260918/evidence.json)を読む。
- 全件完了ではない。累積 PASS58 / NOT_RUN20 / BLOCKED7 / FAIL1 / EXCLUDED9。HAR-01正常/異常対照とPAGE-05の19件をStudioプレビューで追加確認。公開E全面合格にはしない。
- 公開v1.26の4名・5履歴229セル一致。末尾到達・全表示条件は部分実施。コピーの19件fixtureは元定義へ完全復元、保存操作後読戻しは残件。
- 元アプリ公開版・Dataverseを変更しない。製品不具合 #62/#64 は記録のみ。PDF関連・HTML帳票PoC対象外。時間制約解除を継続。
- **Issue #51：欠勤時間単価の実テーブル反映は未実施、次回実テーブル編集時に対応。**

---

# 現在の作業と読取り対象：専用検証コピーの編集ロック・復元確認待ち

- 未完了全件の検証依頼、時間制約解除を継続。**全件完了ではない。PASS58／NOT_RUN20／BLOCKED7／FAIL1／EXCLUDED9のまま。**
- [今回の途中記録](../testing/remaining-all-20260918/results.md)、[95項目JSON](../testing/remaining-all-20260918/spec-case-audit.json)、[証跡](../testing/remaining-all-20260918/evidence.json)、[Issue #65](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/65)を読む。
- 通常Playerのキーボード検索→行選択→詳細表示は追加確認。全フォーカス校正は未完。
- 「検証専用_職員マスタ_20260918_残件」をコピー作成。試験編集で意図しないScreen1.Fillの数式診断61件を観測し復元を試行。再読込後に編集ロック。**コピーは未公開・復元未確認・使用不可。元アプリは編集・公開していない。**
- **確認待ち：当該コピーの編集ロックのオーバーライドを許可するか。**許可後は今回の試験変更の復元を最優先。保全検索式は上記フォルダclone-search-backup.fx。元アプリや他者編集は上書きしない。
- #62/#64と製品の追加不具合は記録のみ。既存不具合の修正許可は求めない。PDF関連・HTML帳票PoCは継続除外。Dataverse変更なし、バックグラウンド処理なし。
- **Issue #51：欠勤時間単価の実テーブル反映は未実施。次回実テーブル編集時に対応。**

---

# 現在の作業と読取り対象：不具合は記録のみ・その他の残件を検証（2026-09-18）

- 最新ユーザー指示「不具合は記録のみで良いです」を確認。**#62/#64および追加発見不具合は記録のみ。修正・再検証・そのための再公開は実施しない。修正許可の確認待ちは解除。**
- 不具合はPASSへ書き換えず、未解決／対応対象外として明記する。OUT-04のFAIL1は保持。LED-05/ACC-03の既知Tab不具合も合格へ変更しない。
- 現在の累積はPASS58／未完了20／前提未整備7／FAIL1／対象外9。全件合格は宣言しない。不具合の修正を要しない未完了項目と前提整備を検証対象として続ける。
- 読取り：[残30項目の確認・実測](../testing/remaining-30-20260918/results.md)、[95項目JSON](../testing/remaining-30-20260918/spec-case-audit.json)、[証跡](../testing/remaining-30-20260918/evidence.json)。同記録の修正方針確認待ちは本指示で解消。
- 人による見やすさ・読み上げ・スマホ閲覧、比較画像承認は本人確認が必要。AIの代替判定でPASSにしない。
- 今回の継続依頼に対する60分制約解除は維持。PDF関連とHTML帳票PoCは継続除外。バックグラウンド処理なし。
- **Issue #51：欠勤時間単価の実テーブル反映は未実施。次回実テーブル編集時に対応。**

---

# 現在の作業と読取り対象：残30項目の検証・方針確認待ち（2026-09-18）

- 今回はユーザー指示で60分制約を解除。INIT-03/VIS-03を追加PASS。累積 **PASS58／未完了20／前提未整備7／FAIL1／対象外9**。全件合格ではなく、過去版の合格を含む。
- [今回結果・全30項目の処置](../testing/remaining-30-20260918/results.md)、[95項目JSON](../testing/remaining-30-20260918/spec-case-audit.json)、[実測](../testing/remaining-30-20260918/evidence.json)を読む。
- **確認待ち**：以前の「記録のみ」指定を変更し、#62/#64の修正・再検証・必要な試作アプリ再公開まで実施するか。VIS-05/06、ACC-06、OPS-02には比較画像承認・人による見やすさ／読み上げ・スマホ閲覧確認が必要。
- 3モーダルの背面クリック防止・選択保持は確認したが、#62を未解決のままLED-05/ACC-03を全面合格にしない。
- 検証用複製、19件fixture、独立セッション、200%・全8条件等の前提も残る。通常データ・一般表示のホームに復帰。アプリ編集・公開、Dataverse書込み、PRマージ、新規Actionsなし。バックグラウンド処理なし。
- PDF関連とHTML帳票PoCは継続除外。**Issue #51の欠勤時間単価実テーブル反映は未実施。次回実テーブル編集時に対応。**

---

# 現在の作業と読取り対象：2026-09-18 v1.26表示・残件追加検証

- 今回INIT-01、SEL-02、SEL-04（非PDF）を追加PASS。累積 **PASS56／FAIL1／未完了22／前提未整備7／対象外9**。旧版の結果を継承し、v1.26全56項目の再合格を意味しない。
- 初期7件・基本9と5履歴、ページ2職員040の全履歴、職員004→011の認定簿69項目を照合。詳細は[今回結果](../testing/resume-20260918-v126-followup/results.md)、[95項目表](../testing/resume-20260918-v126-followup/spec-case-audit.md)、[証跡](../testing/resume-20260918-v126-followup/evidence.json)。
- 公開版ソース全体の読戻し一致は未確定。キーボード入力を含む一連の試験は部分実施。19件fixture、長文備考全文、各表示条件、独立コンテキスト／専用複製などは残件。
- #62/#64は修正・再検証しない。PDF生成・保存・出力・印刷とHTML帳票PoCは実施なし。通常データ・一般表示へ復帰。アプリ編集・公開、Dataverse書込み、PR #60/#61マージ、新規Actionsなし。
- **Issue #51：欠勤時間単価の実テーブル反映は次回実テーブル編集時。今回変更なし。**

---

# 現在の作業と読取り対象：2026-09-18 検証再開・表示v1.26

- 正規のMicrosoftサインインを完了し、新規Playerのホーム／職員画面で **v1.26** 表示を確認。過去STATUSの公開版未確認を更新。PR #61は未マージ。公開ソース全体の読戻し・バイト一致は未実施。
- 95項目の累積：**PASS53／FAIL1／部分実施・未実施25／前提未整備7／対象外9**。過去版の47PASSを継承し、今回はOUT-02、LED-01、LED-04、DETAIL-06、SEL-01、ZERO-03の6件を追加確認。現行v1.26を53項目再合格させた記録ではない。
- OUT-04：163見出しと順序一致、161値一致。減額時間2項目が `0.`。**[Issue #64](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/64)へ記録のみ。ユーザー指示により修正・再検証しない。**
- PDF生成・保存・出力・印刷とHTML帳票PoCは実施しない。#62のTab不具合も修正・再検証しない。
- 読取り：[今回の結果](../testing/resume-20260918-v126/results.md)、[95項目表](../testing/resume-20260918-v126/spec-case-audit.md)、[実測証跡](../testing/resume-20260918-v126/evidence.json)。独立fixture参照SHAはPR #61 head `1dd489a6da91c3753798d466d3caa65a4577b80c`。過去のv1.25成功証跡と混同しない。
- 次回は公開版とソースの対応確定、長文備考の全文到達、19件fixtureなどの不足条件から再開。通常データ・一般表示へ復帰済み。今回アプリ変更／公開、Dataverse書込み、新規Actions、#60/#61マージなし。背景の新規処理なし。
- **Issue #51 ABS-RATE-001：実テーブルの欠勤時間単価は未反映。次回の実テーブル編集で同時対応。今回テーブル編集なし。**

---

# 現在の作業と読取り対象：v1.25 95項目再監査・実機認証待ち

- 2026-09-18 11:34:23 UTC再開、停止期限12:34:23 UTC。今回、公開アプリの再読込がMicrosoftサインインへ移行し、自動セキュリティ審査が認証originへのアクセスを拒否。迂回せず実機操作を停止。ユーザーの認証アクセス承認待ち。
- 最新ユーザー指示を優先：PDF生成・保存・出力・印刷は除外。追加のTab背面移動は[Issue #62](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/62)へ記録のみとし、修正・再検証しない。
- [95項目再監査](../testing/regression-v125-review/spec-case-audit.md)：合格47／部分実施・未実施32／前提未整備7／対象外9＝95。47/86=54.7%。既知のTab不具合は2項目に注記、解消・合格ではない。
- v1.25 run35326181907は41/41成功。今回の新規実機試験ではない。PAGE-04/SIDE-03/ZERO-01/PERF-01と非PDF部分のZERO-02/LED-06を再判定。PAGE-05は19件不足のためPASSから部分実施へ訂正。
- 読取り：[再開結果と次の処置](../testing/regression-v125-review/results.md)、上記監査、試験対象SHA e6b107dece981b21e41cad94c3700f909b6c739d の関連テスト。ローカルe2eとsource-auditにはv1.26候補が混在するためv1.25成功根拠に流用しない。
- この作業ではアプリ変更・公開・新規Actions起動をしていない。PR #60（v1.25）と#61（v1.26候補）のマージ・公開はこの文書更新に混ぜない。直前の実機表示は古いタブのv1.22で、再読込後の現在公開版は未確認。v1.25は過去の成功runの対象版として扱う。
- **Issue #51 ABS-RATE-001：実テーブルの欠勤時間単価は未反映。次回の実テーブル編集で同時対応。今回Dataverse変更なし。**

---

# 現在の作業と読取り対象：v1.23 回帰残件を追加検証・不合格2件

- ユーザー「残件を実施して」により2026-09-18 05:26:19 UTC再開。今回の停止期限06:26:19 UTC。起算変更なし。
- TEST-PDF-001解消：実PDF421567 bytes、A4横2ページを取得・描画・文字照合。基本9項目×5名、帳票69項目×6、コピー拒否通知等も追加検証。
- 全29件実行と追加/対象再試験を統合した33自動ケースの最新観測は31 PASS / 2 FAIL。同一runで33件全合格ではない。職員8表示条件×5往復と追加5画面×4幅の20表示はPASS。基盤単体50/50 PASS。
- 95仕様ケースは38 PASS / 4 FAIL / 21 BLOCKED / 32 NOT_RUN。全残件完了・CORE/REPORT全面合格は宣言しない。
- 公開版はv1.23のまま。SetFocus試行は公式Studio検証で非対応と判明して完全復元。Screen1全文読戻しのバイト一致、公式数式エラー0を確認。新しいアプリ版の公開なし。
- 読取り：[今回の結果](../testing/regression-v123-remaining/results.md)、[95項目監査](../testing/regression-v123-remaining/spec-case-audit.md)、`e2e/regression-v122/`。基準ソースはv1.23 readbackと未変更3画面のv1.22 readback。
- 次回：[Issue #56 フォーカス復帰](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/56)を対応可能な部品階層で修正、[Issue #57 性能・連続再起動](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/57)を切り分ける。実機runはすべて終了済み。期限ガード付きworkflowの自動push起動を外して記録用に整理。
- PDF保存フロー、専用fixture、200%拡大/読上げ、復元/故障注入等は引続き未完。OneDrive/Automateを接続しない。
- **[Issue #51 ABS-RATE-001](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/51)（実テーブルの欠勤時間単価）は未反映。Dataverse変更は今回の回帰試験範囲に含まない。**

---

# 現在の作業と読取り対象：v1.23 回帰修正版公開・全回帰に残件あり

- Issue #54：全回帰・複数幅検証。開始2026-09-18 04:23:59 UTC、停止期限05:23:59 UTC。
- 05:08:43 UTCにv1.23最終候補を公開。検索0件後の旧職員/明細残留、管理者初期化、給与詳細の整数末尾小数点を修正。Studio公式数式エラー0、全7プロパティ読戻し一致。
- 基盤単体50/50 PASS。第2回実機は19/25 PASS、6 FAIL。既存8表示条件・追加5画面×4幅=20表示の幾何学検査はPASS。
- 最終run 35309682325：24/25 PASS、PDF試験1件FAIL（削除済み状態ラベル待ち）。スモーク3/3、163項目、全幅条件PASS。全95仕様ケースの監査は `docs/testing/regression-v122/spec-case-audit.md`。未充足があり、全回帰完了・CORE/REPORT全面合格は宣言しない。
- 正本：`src/screen-ui/v1.23/patches.json`、`manifest.json`、`studio-readback/`。未変更の追加3画面はv1.22読戻し。旧canvas-v3を配布しない。
- 次回読取り：`docs/testing/regression-v122/results.md`、95項目監査、`e2e/regression-v122/`。未接続PDF保存、専用fixture、200%拡大/読み上げ、復元・故障注入等を追跡。
- **Issue #51 ABS-RATE-001（実テーブルの欠勤時間単価）は未反映。Dataverse変更なし。**

---

# 現在の作業と読取り対象：6画面のUI試作 v1.22 公開済み

2026-09-18。ユーザーの画面追加・ダミーFx許可・公開／GitHub記録の依頼を優先し、旧STATUSの「文書のみ」から実装へ移行。Issue #52。

- ホーム、勤務時間報告、期末勤勉支給率、支給明細、メンテナンスを追加。既存職員検索と連携。
- Studio数式エラーなし、変更領域の実機11件と公開Player2件を確認。公開成功確認04:04:36 UTC。詳細は [公開記録](../releases/2026-09-18-screens-v1.22.md) と [試験結果](../testing/screens-v1.22-results.md)。
- 正本：`src/screen-ui/v1.22/`、`scripts/ui/build_v122.py`。既存画面基準はv1.21 studio-readback、変更3式＋追加ナビゲーションはmanifestと読戻し差分を参照。
- 次回：今回の画面を用いてUIを検討。正式データ契約・永続化・実権限連携・正式計算、標準回帰／8条件レイアウトは未完了。旧自動配布パッケージは現行と同一ではない。
- **必須引継ぎ：Issue #51 ABS-RATE-001（欠勤時間単価の実テーブル追加）は未反映。** 今回はDataverseテーブルを編集していない。次回の職員基本テーブル編集で同時に対応する。

---

# 現在の作業と読取り対象：SCR-005 支給明細のUI要件・画像

- 2026/09/18：画面要件定義書 v0.6 の8章に、最新デザインの配置・計算・データ対応・操作・YAML受入条件を追記。
- 画像：`docs/design/images/scr-005-payroll-detail-v1.png`。控除見出し直下の加算式を削除。支給見出し直下の式と上部サマリーは維持。
- 読取り対象：`docs/requirements/screen-requirements.md` 8章、上記画像、`docs/design/design-system.md`、`docs/prototypes/attendance-payroll-prototype.md` 冒頭の優先関係。
- 必要時の対応表：`docs/design/dataverse-commute.md`、`config/dataverse/payrollledger-columns.json`。
- 旧STATUSは2画面試作v0.31を示していたが、最新依頼を優先。旧試作v0.32のYAMLは新しい通勤・控除内訳に未対応で、次回実装の土台として無修正流用しない。
- 今回は文書・画像の保存。YAML作成、Studio検証、Dataverse変更、アプリ公開は未実施。
- 次回：8章からSCR-005の内蔵データ・貼付用YAML／Power Fxを作成し、受入ケースを検証する。

## 次回の職員基本テーブル編集で必須：ABS-RATE-001（未反映）

- [ ] [Issue #51：欠勤時間単価の追加](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/51)。次回M_職員基本／職員基本テーブルを編集する際、同じ作業計画に必ず含める。
- 今回追加したのは試作の `colStaff.AbsenceHourlyRate` だけ。Dataverseの実テーブルには未追加。
- 作業開始時にIssueの最新状態を読み、Openなら項目追加を今回のテーブル編集の対象へ組み込む。型・精度・設定値はその時点で確定する。
- 実テーブルへ反映し、読み戻して項目・型・精度を確認した証跡をIssueへ記録したら完了とし、Issueを閉じる。文書・内蔵データだけの更新では閉じない。
- 次のSTATUS更新でも、実反映が完了するまで本タスクとIssueリンクを先頭の必読部分に引き継ぐ。アプリの実テーブル参照切替が残る場合は別残件として記録する。

---

# 現在の作業と読取り対象：修正1～5・PDF比較ボタンを公開済み

2026-09-17 18:53:57 JSTにテストアプリの公開成功を確認。GitHubへ公開記録・修正要件・取得YAMLを反映済み。現在の正しい状況は [公開記録](../releases/2026-09-17-ui-pdf-comparison.md) を優先する。

- 修正1～5：半透明背景、給与詳細163項目と横スクロール、不要説明文・認定簿ボタンの削除、操作位置変更を公開。
- 比較ボタン：PDF関数（職員情報入りをアプリ内表示）とDownload関数（人事院の空欄PDFを別タブ表示）。通常URLのブラウザ保存を確認。生成PDFの直接保存は未解決。
- ソース：`src/staff-master/patches/v1.21/studio-readback/Screen1.pa.yaml`、`App.pa.yaml`、`src/staff-master/patches/v1.21/ledger-header.paste.yaml`。画面内の版表記はv1.20候補のまま。
- OneDriveの使用・接続は禁止。Automateも使わない。新規接続・データ更新なし。
- 公開Player再試験・狭幅再試験・データ書換え後の再読込鮮度は未実施。
- 今回GitHubへアプリパッケージと接続定義は追加していない。旧自動配布パッケージ・設定は更新していないため、最新公開版と同一と扱わない。
- 以下は過去の記録。給与Refresh未反映・主要15項目維持の記述は最新状態ではない。最新の取得YAMLに給与Refreshも含まれる。

---

# 今回の作業：給与Dataverse参照への移行（v1.19）

- 開始: 2026-09-17 04:11:05 UTC。60分停止期限: 05:11:05 UTC。
- Issue #49、作業ブランチ automation/payroll-v119。実機で7件・0件・金額0・同姓同名・TSVを確認しStudio公開済み。
- 公開版の取得 run 35182918673: 成功。45件の意図したプロパティ変更と9件のStudio列表示名正規化を確認。コントロール361個（Appを含む）の同一性を維持。
- **残件1件**: btnLoad111.OnSelect に Refresh('T_基準給与簿') を追加。現在の公開版は従来どおり職員基本・通勤のみ明示Refresh。
- 補正前の検索欄操作がブラウザー自動承認レビューに拒否された。理由: originへ再接続すると未保存の数式変更を失う可能性。読み取り専用の状態確認も拒否。別経路でアプリ書込みを迂回しない。
- Dataverseの新しい権限追加・ライセンス購入・従量課金設定変更なし。
- 専用テストユーザーの公開版受入: run 35183359299で10件合格（4.2分）。最終公開版SHAとソース・実行ルール・接続定義も一致。ローカル50件合格。PR #50に記録。残るStudio補正の再開には上記リスクの確認が必要。
- 詳細: docs/testing/payroll-v1.19-results.md、src/staff-master/patches/v1.19/manifest.json。pending_changesに承認済みの未反映式を保持。

---

# 現在地

> 対象アプリ：自動テスト専用

更新日：2026-09-17

| 項目 | 状態 |
|---|---|
| 実施環境 | ChatGPT SolのWorkへ一本化 |
| 共有正本 | GitHub main。YAML、Power Fx、要件、設計、テスト仕様、運用方針、進捗、変更履歴 |
| Library | GitHubで版管理しない画像、Excel、Word、PDF、HTML原本、検討用資料を保管 |
| 採用デザイン | B案。要件／基本・詳細設計／デザイン基準v1.04。v1.14の追加条件を含む |
| 標準自動受入の最終完了版 | 隔離テストアプリv1.14、架空25名内蔵。密度・最大6列・氏名横の状態・一覧背景と区切り線・左右余白を反映。追加E2E4件＋P0合格、成功タグv1.14。run 35053952599 |
| B案実装 | モダンボタン・検索入力、固定サマリー、2段一覧、文字サイズ切替、全項目保持 |
| 職員検索サイドバー開閉 | 実装。手動開閉360px／48px。条件・選択・ページ保持 |
| v1.13以降 | 部品差分配布。111のコントロール・変数IDは固定 |
| ローカル検査 | 68チェック、8組の配置式、10枚の配置モデル描画。詳細はRESULTS参照 |
| Studio貼付・動作・見た目 | 旧GitHub v1.11に検索データ未表示の報告（BUG-SEARCH-001）。当該版の再現・原因分析は未完了。今回採用した公開由来基準とv1.12のP0合格とは別に保持 |
| PDF生成・保存フロー | v1.17でA4横2ページ生成・プレビューを実機確認。保存先フロー接続は対象外 |

## 現在の作業と読取り対象

| 項目 | 指定 |
|---|---|
| 対象機能 | PAY-APP-001～004。基準給与簿の内蔵データ削除、Dataverse参照、Fx整理、表示検証、合格後公開 |
| 現在の工程 | ①現行版確認完了、②接続・46プロパティ修正準備、③実機テスト、④公開・読戻し、⑤main記録 |
| 基準公開版 | v1.18。main ce07a1d。候補v1.19 |
| 承認 | Dataverse読込みに必要な権限追加、アプリオーバーライド、合格後公開、GitHub変更送信。追加料金設定は事前確認 |
| 対象ソース | powerapps/canvas-v3/Src、src/staff-master/patches/v1.19、render_staff_history.py、staff-history-synthetic.json |
| 読取・検証資料 | dataverse-payrollledger.md、payrollledger-columns.json、payrollledger-7.json、通勤v1.18検証・公開方式、無人修正運用手順 |
| 画面範囲 | 現行の主要15項目を維持。給与163列への画面拡張は別要件 |
| 未移行 | 勤務・社会保険・税控除は引き続き内蔵fixture。今回の削除対象はPayrollのみ |
| 検証予定 | Studio公式コンパイル、7件・0件・複数月・0円・負数・同姓同名・再読込・TSV、専用利用者E2E、公開msapp読戻し |
| 次の作業 | Studioで既存T_基準給与簿を接続し、差分46プロパティを適用 |

## 前回完了：基準給与簿テーブル作成

| 項目 | 指定 |
|---|---|
| 対象機能 | PAY-DV-001～005。添付からT_基準給与簿を作成し、職員基本の子として整合する合成データを登録 |
| 現在の工程 | 全5工程完了。163列・親Lookup・7件登録、読取り権限、書込みなしの最終検証に合格 |
| 現在公開版 | v1.18。職員基本・通勤はDataverse、給与・勤務・保険・税控除は内蔵。アプリ切替は今回対象外 |
| 承認済み | テーブル作成・読取りに必要な権限追加、必要時のアプリ編集ロック引継ぎ、GitHub変更送信。追加料金設定は未承認で変更しない |
| 対象ソース | config/dataverse/payrollledger-columns.json、scripts/automation/payrollledger_schema.py・payrollledger_dataverse.py・payrollledger_access.py、automation/payrollledger-run.json、.github/workflows/payrollledger-dataverse.yml |
| 関連設計 | docs/design/dataverse-payrollledger.md |
| 関連テスト | tests/automation/test_payrollledger_schema.py、tests/fixtures/payrollledger-7.json |
| 原本 | 05_基準給与簿DB_v0.1 (3)_テーブル定義書.xlsx、添付ID libfile_83586a2630948191b1204fa937bb6cec |
| 証跡 | preflight 35179428426、provision 35179675557、seed 35179933809、verify 35180031165すべて成功。ローカル5件成功。docs/testing/payrollledger-dataverse-results.md・evidence.json |
| 60分制御 | 起算2026-09-17T03:41:43.436Z、期限04:41:43.436Z。工程変更・修復で延長しない |
| 今回の権限・料金 | 承認済みの専用Readerへ基準給与簿Read=Globalのみ追加。各行ReadAccessのみを検証。料金設定変更なし |
| GitHub記録 | PR #48。設計・対応表・fixture・実環境証跡をmainへ統合 |
| 次の作業 | 今回依頼は完了。給与取得元のDataverse切替・内蔵Payroll削除・アプリ検証と公開は後続の別依頼 |
| STATUS不一致の処理 | 通勤v1.18完了の旧STATUSから最新依頼の基準給与簿テーブル追加へ移行。通勤の完了記録は以下に保存 |

## 前回完了：通勤Dataverse切替v1.18

|項目|指定|
|---|---|
|対象機能|通勤の内蔵データ削除・Dataverse参照・認定簿検証・合格後公開 v1.18|
|現在公開版|v1.18。T_通勤をStudioで接続し、35プロパティを公式コンパイルして公開済み|
|工程① 読取り権限|前回完了。承認済みT_通勤 Read=Globalのみ。run 35167594382|
|工程② 接続追加|完了。今回の再開承認により既存Developer環境へ追加。ライセンス購入・課金設定操作なし|
|工程③ Fx整理|完了。稼働用内蔵Commute/LedgerTemplateを削除、69帳票項目を選択通勤から取得。給与等は既存fixtureを維持|
|工程④ 検証|公開前Studio:6件・0件2職員・同姓同名・PDF2ページ合格。専用ユーザー9件はrun 35171721975で合格、再試行0|
|工程⑤ 公開|完了。最終公開ファイルSHA256 74c16fa86102a7dc52682f9342ef8bb8d71520c35b7cb3a18083fc6165cfa49e|
|工程⑥ 記録|完了。PR #47で結果と公開基準をmainへ統合|
|公開読戻し|run 35171416472。35式、全Controls/Connections/References一致。画面360コントロール、ID・親構造・対象外プロパティ不変|
|承認済み|既存Read追加、編集ロック引継ぎ、T_通勤接続追加、GitHub変更送信、問題なければ公開。再承認不要|
|今回の権限・料金|今回の再開では変更なし。新しい権限変更や追加料金は引き続き事前確認|
|対象ソース|powerapps/canvas-v3/Src、powerapps/dataverse-v1.18、src/staff-master/patches/v1.18、scripts/automation/verify_commute_release.py|
|関連設計|docs/design/hybrid-test-data.md、dataverse-commute.md、ledger-v1.17.md|
|関連証跡|docs/testing/commute-v1.18-results.md、commute-v1.18-preview.json、commute-v1.18-readback.json|
|次の作業|今回依頼は完了。未確定の勤務・保険・税控除・給与テーブルは今後の別依頼で追加|
|60分制御|今回の起算2026-09-17T01:07:06Z、期限02:07:06Z。修復しても起算を延長しない。最終受入は01:49:58Zに完了|

給与・勤務・保険・税控除は業務定義確定後に別途Dataverse化する。認定簿PDFの保存先フローは今回も対象外で未接続。旧v1.14タグを現行へそのまま復元しない。現行のStudio公開基準はv1.18、標準ブリッジはその基準からの明示的プロパティ差分に限定する。

## 前回完了：通勤テーブル・6件追加（PR #44）

|項目|指定|
|---|---|
|対象機能|COM-DV-001～003。添付定義からT_通勤を追加し、M_職員基本の子として合成データを登録|
|現在公開版|v1.17を維持。職員基本25名はDataverse、通勤等の画面データは引き続き内蔵|
|現在の工程|全5工程完了。通勤84項目・親Lookup・6件を作成。実環境検証結果をGitHubへ記録|
|対象ソース|scripts/automation/commute_dataverse.py、commute_schema.py、config/dataverse/commute-columns.json、automation/commute-run.json、.github/workflows/commute-dataverse.yml|
|関連設計|docs/design/dataverse-commute.md|
|関連テスト|tests/automation/test_commute_schema.py、tests/fixtures/commute-6.json、docs/testing/commute-dataverse-results.md|
|Library資料|T_通勤_テーブル定義書.xlsx（添付ID libfile_7d3a1d264cc0819195f053d0522a3a83）。84項目と作成条件|
|証跡|事前確認run 35164838218、作成run 35165234474、投入run 35165488926成功。ローカル5件合格|
|権限・料金|既存Automation OIDCと既存テスト環境を利用。権限・ライセンス・課金設定変更なし|
|次の作業|テーブル・親子関連・テストデータは完了。Canvasの通勤取得元切替・利用者ロール変更は別依頼で実施|
|60分制御|起算2026-09-16T23:58:50.271Z。修復時にも起算を保持し、2026-09-17T00:58:50Z前に停止・報告|

前回STATUSは認定簿v1.17完了を示していたため、最新依頼の通勤テーブル追加に切替えた。アプリソース・公開・パッケージには変更しない。

## 前回完了：認定簿v1.17（Issue #35）

|項目|指定|
|---|---|
|対象機能|Issue #35 認定簿表示とA4横2ページPDF。v1.17で完了|
|現在公開版|v1.17。職員基本25名Dataverse、勤務・通勤・保険・税控除・給与は共通内蔵合成データ|
|今回の完了|上部を帳票幅内へ配置、倍率6択、白背景・青字の閉じる、A4横固定、新幹線欄前で改ページし2ページ、PDFプレビュー前面表示|
|証跡|run 35110696763、試験commit 5f51e69c644975309ee312eaf9bc68c440a35e5c、docs/testing/ledger-v1.17-results.md、PR #43|
|対象ソース|powerapps/canvas-v3/Src/Screen1.pa.yaml、automation/change.json、scripts/automation/bridge.py、e2e/hybrid/ledger.test.ts|
|関連設計|docs/design/ledger-v1.17.md、docs/design/hybrid-test-data.md|
|関連テスト|ローカル35件、公開先8件PASS（P0・UI4件・Dataverseアクセス/検索・履歴/給与/認定簿・新認定簿/PDF）。最終run再試行0|
|保存パッケージ|powerapps/dataverse-v1.17/staff-master.msapp。SHA256 90e5d4839b007205286cbb3a311fa77b4a8c94318b535e13a3f098d1352c88de|
|共通数式ビルド|基準msapp v1.15＋累積47プロパティ変更。PDFビューアーの限定した3部品の表示順と実行時ZIndexも厳密照合|
|権限|今回の権限・料金変更なし。Dataverse接続とReferences6ファイルを保持|
|次の作業|依頼5項目は完了。PDF保存先フローは既存どおり未接続。履歴の正式Dataverseテーブルは業務定義確定後|
|今回の読取り対象|docs/design/ledger-v1.17.md、docs/testing/ledger-v1.17-results.md、e2e/hybrid/ledger.test.ts、automation/change.json|
|復元注意|旧標準フロー成功タグv1.14はDataverse接続を含まないため現行へそのまま復元しない。今回保存したv1.17パッケージを保全|
|60分制御|起算13:57:16Zを修復後も維持。最終runは起動50分未満＋10分timeout、14:49:34Zまでに全ゲート成功|

以前のSTATUSはv1.16作業を記載していたが、Issue #35へ切替えた。公開済みv1.16を保持するため、ユーザー了承のv1.17として反映。v1.16の過去結果はdocs/testing/hybrid-v1.16-results.mdに保持する。

## Issue #29：READMEと成功タグの整合（2026-09-16）

- 原因：旧フローがタグ作成後にREADMEを更新していたため、v1.14タグにはv1.13表記が残った。
- README生成・コミット・機械照合をタグ作成前へ移動。schema 2で検証済みソースとREADME訂正commitを区別する。
- 基盤単体28件ローカル合格。元タグ保全・README限定差分・競合拒否・再実行を含む。
- [PR #30](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/30)統合後、[run 35064281800](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35064281800)で基盤単体28件・タグ保全・訂正が成功。mainとv1.14タグ内のREADMEがともにv1.14であることを読戻し確認。
- 訂正前の注釈object `5137c995c2760e9da94f6ec4d82779054eee5e89`を`archive/v1.14-before-readme-fix`へそのまま保全。訂正後タグは`88d4f373fadd25e507c8c9b6b70d6b0c150046e1`を参照し、元の検証済みcommitとの差分はREADME.mdのみ。
- 元の公開・追加E2E・P0証跡はrun 35053952599、公開日時2026-09-16T04:03:25Zを保持。今回は再配布・実機E2E/P0を実行していない。
- PR更新直後の初回mergeはGitHubのmergeable判定待ちで405となった。cleanを読戻し確認後のmergeは成功。タグ訂正Actionsに失敗・再実行はない。

## Issue #27：名称と工程報告の更新（2026-09-16）

- 正式な指定一覧名は「自動開発_職員マスタ検索」。旧名「職員マスタ検索_自動テスト_v1_11」は過去の実行記録として保持する。Power Apps上の改名は今回のStudio・公開Playerで指定名との一致を確認。App ID・URL・画面版v1.14・内部111部品IDを維持。
- configのdisplay_nameをREADME生成に利用し、配布用メタデータも同期。通常配布と旧タグ復元のpack時に指定名を反映し、旧名へ戻るのを防ぐ。元msapp・過去タグ自体は変更しない。
- Work運用方針v1.06、無人開発要件v1.05、テスト仕様v1.03、運用手順を更新。開始前は最大10工程提示後に承認待ちなしで実行し、途中は現在工程、終了・停止時は同じ番号の全工程別結果を同じWorkへ示す。
- 今回の工程は、1 現状確認／2 名称更新／3 報告ルール整備／4 検証／5 GitHub反映／6 Work結果報告。単体テスト8件成功。今回は名称設定・基盤・文書の変更なので、配布・E2E・P0は対象外。公開版v1.14の過去の合格を今回の実行結果として扱わない。
- 進捗はWorkが確認可能なActions・Issue・ログ等から報告する。1step内部が不明なら処理中の工程範囲と確認中を示す。ランナーからWorkへの直接通知や、Work停止中の常時監視は追加していない。
- 作業と反映結果は[Issue #27](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/27)から追跡する。

## 自動化基盤と実行結果

| 項目 | 状態 |
|---|---|
| 無人修正・テスト・公開基盤 | 9ステップすべて完了。ステップ8の自動修復・停止・復元に加え、run 34954109942でv1.12候補の全ゲート合格。PR #6統合後、run 34954509560で成功タグv1.12を確定 |
| Phase 1 P0 | run #8 attempt 3が成功。2026-09-15T01:27:59Z完了。証跡は14日保持 |
| 実環境確認 | Azure Subscriptionあり・所有者。対象はDataverse付き開発者環境、非マネージド。Power Apps Premiumなし |
| GitHub格納状態 | 完全なSolution、active `*.pa.yaml`、`baseline.msapr`、変更専用テスト、厳格な実行時同期ゲートを格納済み。初期ソース確定は `ab1b7456ed8bc7d39cd302c1e23276b789212179`、ステップ7復元確定は `260819a4fa30c4d8c8dcd02acc626c26d7823697` |
| 推奨経路 | 保持した元msappとactive YAMLを使用し、承認済みの既存プロパティをマニフェスト駆動で実行ルールへ同期してSolutionをパックする。新規構造・記載外変更は停止。元のPersistence実証は履歴として保持 |
| Power Platform Git統合 | GitHub接続はプレビュー。GitHub Organization、Managed Environment、Azure Key Vault、Premium相当ライセンス等が必要なため当面見送り |
| GitHub Actions | OIDC、Dataverse URL直接指定、CanView共有、再構成、Solution反映、明示的公開、サーバー側ルール読戻し、変更専用テスト、P0、失敗時復元を連結済み |
| E2Eスクリプト | `e2e/testapp-smoke.test.ts` と `e2e/staff-master-p0.test.ts` を格納済み |
| Power Apps E2E | 基準環境P0はrun #8 attempt 3で成功。隔離環境P0はrun 34925700515、再構成基線はrun 34928950801、ステップ7変更版はrun 34934912204、復元版はrun 34935420385で合格。ステップ8の自動修復・停止・復元はrun 34952452993、v1.12候補はrun 34954109942で合格。全試行はIssue #5と#7へ保持 |
| 合否の境界 | ワークフローやスクリプトの存在だけでは合格としない。対象版の実行結果と証跡で判定する |
| v1.14実行結果 | run 35053952599で7ゲート、追加E2E4件、既存P0 1件、基盤単体15件合格。幅5条件×文字2条件。PR #24統合と成功タグv1.14、README生成・PR #25統合まで確認 |

## テスト設計

[テスト方針v1.00](../testing/test-policy.md)、[テスト仕様書v1.03](../testing/test-specification.md)を作成。95ケース定義＋連続スモーク、独立期待値、8表示条件、PDF実体照合、差分回帰を定義した。v1.02ではIssue #23の追加受入、v1.03ではIssue #27の名称維持・工程報告を定義。既存68件のローカル合格は実機合格ではない。

PDF用紙と改ページはv1.17でA4横2ページとして確定・実機確認。保存先やその他の未決事項は仕様書Q1～Q5を参照。

## 以前の作業計画（履歴）

ステップ1～9は完了。2026-09-15の承認に基づき、既存プロパティ変更を対象とするテスト公開の運用を開始した。

| ステップ | 内容 | 状態 |
|---:|---|---|
| 1 | 要件・構築方針の確定 | 完了 |
| 2 | 合格アプリの保全・Solution化 | 完了 |
| 3 | 隔離テスト環境の作成 | 完了 |
| 4 | 専用ID・GitHub OIDC認証 | 完了 |
| 5 | 自動配布・CanView共有・P0 | 完了 |
| 6 | 編集可能ソースからの再構築 | 完了 |
| 7 | 小変更→公開→変更テスト＋P0 | 完了 |
| 8 | 自動修復・停止・合格版復元 | 完了 |
| 9 | v1.12検証・main統合・成功タグ・運用開始 | 完了 |

Issue #12はv1.13、Issue #23はv1.14として完了。次の修正指示は[運用手順](../operations/staff-master-unattended-runbook.md) に従い、既存の承認範囲内では追加確認なしで修正・テスト・隔離公開・READMEを含む文書更新まで実施する。ActionsがREADMEのPR作成を禁止された場合は、Workが生成ブランチの確認・PR統合を継続する。

[受入・成功版確定記録](../operations/unattended-development-step8-9-acceptance.md)、[成功タグv1.12](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/tree/v1.12)、[Issue #7](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/7) を参照する。

## 未決・ギャップ

- ステップ7では、一時表示変更の無人反映、変更専用テスト＋P0、元表示への復元・再公開・P0を実証した。現行Persistence経路はactive `.pa.yaml` 単独では実行用ルールを再コンパイルしないため、承認対象を厳格照合した実行時ルール同期を使用した。ステップ8で既存プロパティのマニフェスト駆動と修復制御を実証済み。新規コントロール等の一般コンパイルは未対応で、運用ゲートが停止する。
- 最新P0はv1.17の `35110696763`。旧標準フローP0はv1.14の `35053952599`。成功タグv1.14、公開App ID `362ac991-eead-4f07-8373-afdb3ebfdba1`。詳細artifact `10430230837`は2026-09-30まで保持。恒久記録は注釈タグとIssue #23。過去のステップ7証跡は各ステップの記録を参照する。
- 本番列一覧、Dataverseテーブル名・型・ロール、実接続/委任設計は別途。
- TSVから正式XLSX出力への方式は未決。
- 帳票用紙はv1.17でA4横固定、新幹線欄前改ページの2ページを実機確認済み。
- 通勤支給予定と認定簿共通サンプルの金額は未整合。テストデータ改修が必要。
- 認定ID選択UIは未実装。給与簿詳細はサンプル15項目で、本番の未知列は未収録。
- 簡易出力は全件TSVコピーと表示中5行の印刷。正式な全件XLSX出力ではない。
- モダンコントロールの提供状況・アクセシビリティ・PDF実験機能は環境で確認。
- 生成画像は概念図。省略項目と濃い見出しは要件・設計書で補正済み。
- 旧v1.11の配置モデル画像はStudioスクリーンショットではない。v1.14は公開Playerの画面・要素座標・機能を検証済み。Studioの表示モード切替そのものと全スクリーンリーダー・200%拡大監査は今回の自動試験に含めていない。

## Issue #23 完了結果と再発防止（2026-09-16）

- [公開・テストrun 35053952599](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35053952599)：`RELEASE_CANDIDATE_PASSED`。build/auth/import/publish/readback/change_test/p0すべて成功。追加4件、P0 1件で失敗・skip・flakyは0。公開読戻しは`source_and_rules=exact`、初回Player読み込みからv1.14。
- [PR #24](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/24)の試験対象は`aeddf38e0337107f8b8f194bb757addf72753c7e`。同一treeのmain `d0809b9f32325c37a86ab0265c26e04aaa0f1717`へ統合し、[v1.14](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/tree/v1.14)を確定。注釈タグに全7ゲート・対象・run・パッケージSHA-256を保存。
- 公開日時（UTC）：`2026-09-16T04:03:25Z`。この公開時点の一覧名は`職員マスタ検索_自動テスト_v1_11`、画面内表示はv1.14。現在の指定一覧名と手動変更状況はIssue #27の節を参照。
- 氏名と在籍の間隔8px、選択した所属背景の右端、1pxの`#E2E8F0`区切り線、キーボード選択、検索欄開閉2往復と条件・職員・ページ保持が合格。

| Playerの幅 | 標準文字の列数 | 大きな文字の列数 |
|---:|---:|---:|
| 900px | 2 | 1 |
| 1100px | 2 | 2 |
| 1366px | 4 | 3 |
| 1600px | 5 | 4 |
| 1920px | 6 | 5 |

検索欄を閉じた1920pxでは両文字サイズとも6列。1366pxの基本情報幅935pxを維持。1920px標準の基本情報高さは340pxから180pxへ短縮。ヘッダー左右16pxを本文に揃え、本文・詳細の幅を狭めていない。大きな文字と9項目の保持を確認したが、テスト仕様95ケース全体の合格を意味しない。

| 試行・問題 | 判明した原因と対処 |
|---|---|
| run 35050273024 | Player内幅はviewportより1px小さく、選択したgallery行のアクセシブル名には`. Selected.`が付く。実際のmain幅を測定し、氏名・番号・既知の選択suffixを含む一意な行を照合。`.first()`による回避は行わない |
| run 35051495406 | 公開/readback成功直後でも初回Playerが前の版を読み込んだ。UI配置・一覧・開閉とP0は合格。版テストだけを、固定URL再読み込みで版一致を最大90秒確認する手順に変更し、各観測版を保存。古い版を合格とはしない |
| run 35052461896 | 新しいテストを復元版v1.13の旧仕様期待値で実行し、追加4件・P0とも合格。候補/復元の両経路を確認してから再公開 |
| run 35052917449、attempt 1/2 | 認証画面のパスワード欄待機10秒で停止。アプリ変更前。資格情報拒否の証拠はなく、同じ条件の診断run 35053614903と最終runでは成功。根因は未確定。既存認証ライブラリの失敗画面PNGのみ1日保存する処理を追加し、資格情報・認証状態は保存対象に含めない |
| run 35054573508 | 成功タグとREADME生成後、ActionsのPR作成禁止で停止。生成差分とタグを確認してWorkから[PR #25](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/25)を統合しREADMEを更新。今後は既知の拒否だけを`PENDING_WORK_PR`としてブランチ/SHAを保存し、Issueに引き継ぐ。未知の失敗は停止。単体テストで両者を検証 |

失敗段階が後続P0の名前で誤表示される問題も、最初に失敗したゲートを記録するよう修正。復元失敗時の各ゲートも保持する。README引き継ぎ追加後の基盤単体テストは17件成功。最終化run 35054573508自体の失敗履歴は消さず、公開成功・文書更新の完了を分けて記録する。今後もmainのREADMEまで確認してから依頼全体の完了を報告する。

## Issue #12 原因分析・対処（2026-09-15）

- 初回run `34968864160`：v1.13候補のビルド・公開・読戻し・P0成功。追加テストが表示ラベルをクリックし、透明な行選択ボタンに遮られて失敗。実際の行ボタンを名前とroleで指定するよう修正した。
- 復元run `34974840163`：行ボタンクリックと検索欄閉鎖は成功。職員番号の `.first()` が非表示の一覧セルを選び、詳細表示を誤判定。詳細ヘッダーの一意な職員番号・所属で検証するよう修正した。v1.12の再公開・読戻し・P0は成功したが、追加テスト不合格のため復元完了扱いにはしない。
- 復元概要の `not required` 誤表示を修正。復元成功・失敗・未実施を区別する既存テストを補強し、合格した。
- ユーザーの「原因分析して対処」指示に基づき、修正したテストで再度復元確認を実施。復元全ゲート合格後にのみv1.13再展開・追加テスト・P0・成功版確定へ進む。既存P0は変更していない。
- 詳細な試行・判断記録は [Issue #12](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/12)。

復元確認run `34975611706` は `RESTORED`、追加テスト・P0とも合格。候補アプリを変更せずテストの参照先修正だけで解消した。これを根拠にv1.13の再展開へ進む。

### 完了結果

- 再展開run [34976128110](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34976128110)：build/auth/import/publish/readback/change_test/p0すべて成功。追加テスト2件合格。開閉2往復、条件・選択・ページ保持を確認。公開スクリーンショットでも横三本線を確認。
- PR #13をmain `f1f0dd83d7198c09f8a862c6a747b0c48087a522` へ統合。確定run [34976590043](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34976590043) 成功、[v1.13](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/tree/v1.13)を確定。
- 詳細artifact `10399029288` は2026-09-29まで保持。成功タグの注釈とIssueに恒久記録を保持。
- アプリ一覧の表示名は既存の `職員マスタ検索_自動テスト_v1_11`。画面内の版表示はv1.13。今回、アプリ一覧名の変更は行っていない。

## テスト仕様書v1.01更新（2026-09-15）

Issue #12で発生したテストlocatorの誤りを再発防止ルールへ反映した。表示Labelではなく実操作部品を選ぶこと、`.first()`等で一意性問題を回避しないこと、閉じた領域内の非表示セルを状態保持判定に使わないこと、候補版と復元版の双方でlocatorを検証すること、Playwright証跡でテスト不具合とアプリ不具合を区別することを[テスト仕様書v1.01](../testing/test-specification.md#セレクター設計の再発防止ルール)へ追加した。文書だけの変更のためアプリ配布・E2E・P0は対象外。見出しリンク、文書版、変更履歴の整合を確認した。

## Dataverse構築の実行結果（2026-09-16）

- 工程3: [run 35072009746](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35072009746)、読取成功。
- 工程4初回: run 35072236518、作成要求の45秒応答タイムアウト。再送前に存在確認し、作成済みを検出。二重作成なし。
- 工程4完了: [run 35072394136](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35072394136)、24列/Choice/必須/DateOnly/キーActive照合。
- 工程5初回: run 35072617980、1件登録後、DateOnlyのEdm.Date形式不一致で停止。
- 工程5完了: [run 35072724192](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35072724192)、ISO日付のみへ修正。既存fixtureを更新せず5件の値を読戻し照合。
- テーブル: crb3c_staffbasic、集合crb3c_staffbasics。業務保存列24、在籍状態は導出のため保存列なし。稼働アプリには未接続。
- ブラウザでM_職員基本の存在、主列=職員番号を確認。本人アカウントの対象アプリ編集操作は無効。公開アプリはv1.14のまま。
- 既存権限/MFA/課金設定を変更していない。今回のフローは元の作業開始時刻を維持し、期限前停止と中断報告を追加。旧アプリ配布フロー全体の共通期限適用は未完了。
- fixture JSONが実行入力、CSVは同内容のレビュー用出力。実データなし。

## 自動化用IDによる接続前確認（2026-09-16）

- ユーザー指示によりPowerAppsCanvasAppUI-Automationを優先。本人への権限追加を自動実施しない。
- 初回診断run 35073770871は対象メールに一致するsystemusers行がなく停止。認証自体は成功。変更処理なし。
- [再診断run 35073900437](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35073900437)は読取完了。自動化用applicationid一致、アプリOwner=ServicePrincipal、架空5件の読取を確認。
- 共有情報のユーザー2名はCanView。powerapps-testのメールからの一意照合は未完了（systemusers一致0件、aadusersフィルターHTTP400）。表示名だけで同一人物と断定しない。診断の成功はこの照合の成功を意味しない。
- ローカルYAML解析でdemoStaff定義57か所、全demoテーブル定義80か所を確認。詳細は[接続前レビュー](../design/dataverse-connection-review.md)。職員番号11桁等、確定仕様との不一致も記録。
- アプリ新規接続・公開・Power Fx置換・ユーザー権限・課金設定の変更は未実施。工程7も未実施。
- 今回は読取診断と文書のみ。診断は終了済みで、背景で継続する処理はない。

## 承認済み編集権限の付与（2026-09-16）

- ユーザーはAutomationへの追加権限で解消できない場合、hirokazu601218@govaca.onmicrosoft.comへの編集権限付与を明示承認。
- Automationは既に対象アプリのOwnerであり、追加ロールで既存ブリッジの新規接続未対応を解消することはできない。
- 既存共有情報のメールアドレス完全一致・単一ユーザーID・User種別を検証し、対象アプリのみCanViewからCanEditへ変更。
- [run 35075397896](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35075397896)成功。CanEditを読戻し、他のprincipalのロール集合不変を確認。
- 通知送信なし。Dataverseロール、ライセンス、MFAの変更なし。AutomationはOwnerを保持。
- ブラウザで本人の編集ボタンが有効となり、Studioへの遷移を確認。接続追加・公開・Fx置換は別の実施結果として扱う。
- 実行コードはscripts/automation/app_edit_permission.py。automation/app-edit-permission.jsonの元のWork起算時刻を再試行でも保持。ユーザーIDが未一致・複数の場合は書込前に停止する検証が合格。

## 工程6：Dataverse接続追加（2026-09-16）

- hirokazu601218@govaca.onmicrosoft.comのStudio編集画面で、現在の環境のM_職員基本をデータソースへ追加。
- 保存済み表示「2026/9/16 17:57:56」を確認。ページ再読込後もデータ一覧にM_職員基本 / Microsoft Dataverse - 現在の環境が残ることを確認。
- 公開操作なし。公開成功版v1.14を更新したとは扱わない。
- 件数読取を試す一時的なlblMeta111.Text変更ではエディターの置換が正常に反映されず、読取テストは未成立。再読込後の表示は元の「v1.14 ／ B案・架空25名」で、確認式を成果として保存していない。
- 再読込後、Studioが「このアプリは別の場所で既に編集中のコントロールがあるため読み取り専用」と表示。別の作業か自身の古いセッションかは判別不能。オーバーライドは未実施。
- 今回の作業①最新状態確認は完了、②接続追加と保存確認は完了、③Fx置換・実機読取確認は未完了。工程7未着手。
- 新規接続を含むmsappのGitHub取得は未完了。既存の元msappに基づく自動配布で下書きを上書きしないこと。再開時は最新保存版を取得し、接続・ソース・実行ルールの整合を確保する。
- 新たな権限付与、ライセンス購入、従量課金設定変更なし。自動化runは起動していない。


## 2026-09-16 再開結果：工程6・7



- 対象は既存の職員マスタ検索テストアプリ。別Work停止をユーザーが確認した後、Studioの通常のオーバーライド操作で編集を再開。
- 工程6：Dataverse接続、Power Fx置換、5件のStudioプレビュー検証、下書き保存まで完了。公開は未実施。
- 工程7：架空25件を投入し全投入値をDataverseから読戻し。run [35080574989](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35080574989)、job 104743327957、SEED25_VERIFIED。
- Studio操作基盤が応答しなくなり、25件でのページ切替・公開版確認は未実施。旧公開版v1.14を移行成功版とは扱わない。
- 追加権限・ライセンス・従量課金・セキュリティ設定の変更なし。


詳細：[Dataverse v1.15移行の検証と残件](../design/dataverse-v1.15-migration.md)。


## 工程7の再開・公開確認（2026-09-16）

- 既存のテスト環境・同じApp IDへv1.15を公開。Studio保存表示は2026/9/16 19:18:42（日本時間）。新しいPlayerタブで初回から「v1.15 ／ Dataverse・25名」を確認。
- 5件の古い一覧が最新データ読込後も残る不具合を検出。btnLoad111.OnSelect／btnClear111.OnSelectで結果キャッシュを再作成せず、検索済みフラグ・選択・ページをリセットして共通ビューへ戻すよう修正。
- 前回保存パッケージとの差分は上記2プロパティ。書出しYAMLとコンパイル済みInvariantScriptの一致、旧埋め込み職員データが残っていないことを確認。
- 検証アカウントは既存の本人セッション。専用テストユーザーのDataverse権限および既存自動P0は今回未検証。自動受入の成功タグはv1.14のままで、v1.15の成功タグは作成しない。
- 権限・課金・MFA・セキュリティ設定の変更なし。

|項目|Studioプレビュー|公開Player|
|---|---|---|
|Dataverse25件、1ページ目20件／2ページ目5件|合格|合格|
|最終ページ021～025、次へ無効|合格|合格|
|025の番号・所属・採用日を詳細表示|合格|未実施|
|採用前10／在籍10／退職5（基準日2026-09-16）|合格|未実施|
|採用日空欄・未来日、採用当日・退職当日の境界|合格|未実施|
|同姓同名011・012の2件検索|合格|合格|
|2件検索後の再読込で25件・1ページ目へ復帰|合格|合格|
|不一致検索0件、旧職員詳細なし|前回5件時に合格|25件で合格|
|条件クリアで25件・1ページ目へ復帰|合格|合格|

この記録はDataverse移行の範囲をブラウザで実操作した結果。全P0、全画面幅、PDF生成、履歴機能の合格を意味しない。

詳細：[Dataverse v1.15移行の検証と残件](../design/dataverse-v1.15-migration.md)。


## 残件実行：専用ユーザーと履歴の停止条件（2026-09-16）

- 認証は成功したが、専用ユーザーの初期25件表示は失敗。run 35089202365で再試行なしの同じ空表示を確認。既存P0は前提失敗で未実施。
- run 35089495413の読取監査ではAutomationの25件読取成功。専用ユーザーのメール一致systemusersは0件、共有CanView principalのメールは未設定で一意照合できず。権限不足と断定しない。
- 権限追加・ユーザー登録・ライセンス変更・アプリ再公開は実施せず停止。v1.15公開版を保持。全run終了済み。
- 履歴は元データ全列の定義不足。通勤12か月を2か月で代替せず、給与簿概要15項目を全項目扱いにしない。定義書または暫定スキーマの範囲確認が必要。
- [実行結果・再開条件](../testing/dataverse-remaining-results.md)、[履歴項目の不足整理](../design/dataverse-history-readiness.md)を参照。


## 2026-09-16 追加決定：Dataverseと内蔵テストデータの併用

ユーザー指示により、未確定項目の全列定義を待つことは、当面の画面テスト再開の条件から外す。

|データ|当面の取得元|今後|
|---|---|---|
|M_職員基本|既存Dataverseの架空25件|Dataverse接続を継続|
|通勤・給与簿など、テーブル定義未確定のデータ|アプリ内蔵の架空テストデータ|定義確定後にDataverseへテーブルを追加し、取得元を順次変更|

- 内蔵データは暫定の画面・機能テスト用であり、正式テーブル定義や法定計算の検証結果とは扱わない。
- ソースレビューのため、内蔵データは共通の定義箇所へ集約し、画面や各ボタンのPower Fxへ同じデータを重複記載しない。
- Dataverse側の12桁職員番号と対応させ、別職員の履歴や帳票が混在しないことを検証する。
- 将来の移行は、テーブル定義→テーブル追加→架空データ投入→共通の取得処理の切替→回帰確認の順で行う。
- 削除済み住民税欄を復活させず、停止中の別Workの認定簿UI変更も再開しない。
- 現在の公開v1.15の履歴は空一覧のまま。この文書更新は方針の記録であり、内蔵データの追加・アプリ再公開は未実施。次の実装作業として管理する。
- 専用テストユーザーのアクセス問題は独立した残件。今回のユーザー回答は権限変更の承認ではなく、説明の依頼として扱う。



## 2026-09-16 承認済みテストユーザー閲覧権限の追加

ユーザーの「①は了解。それなら権限追加して良いです」を根拠に、StaffMaster-Automation-Test の専用テストユーザーに限定して実施した。

- 管理センターのユーザー追加でメール完全一致 `powerapps-test@govaca.onmicrosoft.com` と表示名「Power Apps 自動テスト」を照合。追加前は環境のユーザー一覧に存在せず、追加後に有効として表示された。
- 新規ロール `StaffMaster Test Reader`（ID `abbe5d58-c4b1-f111-aaac-e4fb1eff79c7`）を作成。M_職員基本（`crb3c_staffbasic`）は読み取り=組織、作成/書き込み/削除/アペンド/アペンド先/割り当て/共有=なし。
- 新規ロール作成時のApp Opener追加をオフ。管理者・カスタマイザー・Environment Makerの追加なし。プラットフォームが新規ロールに設定する標準の基盤特権と、業務テーブル権限は区別する。
- ユーザーへの直接割り当てはこのロールのみ。管理センターで保存成功および直接割り当て一覧を確認。
- ライセンス購入、従量課金、MFA、環境全体のセキュリティ設定、アプリ再公開、Dataverseレコードの変更なし。

### 検証結果

- 権限設定を管理センターで開き直し、M_職員基本の読み取り=組織、他7操作=なしを再確認。
- [run 35092609884](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35092609884)、job 104782247060：認証成功、専用ユーザーの初期25件表示・検索回帰1件合格（21.1秒）。`DATAVERSE_DEDICATED_USER_ACCESS_PASSED` と `DATAVERSE_SEARCH_REGRESSION_PASSED` をログで確認。
- 検証範囲：25件表示、2ページ目と最終025の表示、次へ無効、同姓同名011/012検索、012詳細、再読込で25件/1ページへ復帰、0件検索で旧詳細消去、条件クリア。
- 古い内蔵fixture依存の既存P0は今回の権限確認から明示除外してSKIPPED。コード・期待値は変更せず、全回帰合格やv1.15成功タグ確定とは扱わない。実行時summaryの従来文言は結果と一致しないため、本記録とstepsのSKIPPEDが判定根拠。次回用summaryを修正。
- 現在公開版v1.15と25件データを維持。通勤・給与簿等は内蔵の共通テストデータを追加する方針を継続するが、今回その実装・公開はしていない。
- 今回の処理は終了済み。課金設定や追加ライセンスの変更なし。

次の作業は、通勤・給与簿等の内蔵合成データの共通定義と12桁職員番号への対応、該当画面の回帰確認。テーブル確定後にDataverseへ順次切り替える。専用ユーザーの本人照合・閲覧権限は解決済みで、再度の権限承認依頼は不要。

## 2026-09-16 残件完了：v1.16 共通内蔵履歴

上記のv1.15時点の未実施記録は履歴として保持する。最新結果は先頭の「現在の作業と読取り対象」と[検証記録](../testing/hybrid-v1.16-results.md)を参照。

勤務7件・通勤5件・保険5件・税控除5件・給与7件と認定簿共通値を実装。Studio保存・テスト公開、専用利用者の7件回帰、YAMLと実行ルール読戻し完全一致を確認。接続関連6ファイルはv1.15とバイト単位で一致。今回指定の残件は完了。

将来の正式履歴Dataverse化・未確定全列・PDF保存接続は引き続き別作業。標準Solution配布フローの旧成功タグを偽って更新せず、現行保存パッケージと試験結果をGitHubへ保全する。
