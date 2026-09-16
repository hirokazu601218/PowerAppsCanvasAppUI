# PowerAppsCanvasAppUI

> 対象アプリ：共通（自動テスト／ハンドメイド）

非常勤職員マスタ検索・通勤手当認定簿のキャンバスアプリ。GitHubのmainをChatGPT SolのWorkで扱う共有正本とする。

現在のテスト公開版は **v1.16（職員基本：Dataverse、未確定履歴：共通内蔵テストデータ）** です。専用利用者による7件の回帰テストと保存アプリのソース・実行用数式の読戻し照合が合格しました。[検証結果](docs/testing/hybrid-v1.16-results.md)と[データの所在・将来の切替手順](docs/design/hybrid-test-data.md)を参照してください。

<!-- staff-master-release:start -->
標準自動受入の最終完了版：**[v1.14](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/tree/v1.14)**（隔離テストアプリ）。追加テスト・既存P0・公開後の読戻し照合が合格しています。

- [検証結果](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35053952599)
- [変更要求](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/23)
- 公開日時（UTC）：2026-09-16T04:03:25Z
- アプリ一覧名（指定）：`自動開発_職員マスタ検索`。現在の画面内版はv1.16です。上記タグは旧Solution配布フローのv1.14記録であり、今回のStudio公開＋読取受入v1.16とは分けています。
<!-- staff-master-release:end -->

[隔離テストアプリを開く](https://apps.powerapps.com/play/e/68e00049-b7e5-eda6-9888-9a3cc493c5be/a/362ac991-eead-4f07-8373-afdb3ebfdba1?tenantId=a00c92fa-e1db-4aa6-ab28-356c3203353d)。共有済みアカウントでサインインしてください。架空25名の検証用アプリです。

検索・一覧・固定サマリー・履歴・文字サイズ切替・検索領域の開閉に対応。v1.14では、基本情報の密度と最大6列の可変配置、氏名横の在籍表示、一覧の選択色・区切り線、業務領域を維持した左右余白を反映しました。幅5条件×文字サイズ2条件、追加E2E4件と既存P0の結果は[STATUS](docs/handoff/STATUS.md)で確認できます。

一覧表示名「自動開発_職員マスタ検索」はStudio・公開Playerで確認済みです。同じApp ID・URLを継続利用し、内部の`111`を含む部品IDも維持しています。

自動化を開始する前に、このWorkへ最大10工程を示し、追加承認を待たずに進めます。実行中は現在工程、終了・停止時は全工程の成功／失敗／対象外／未実施を同じWorkへ報告します。詳細は[運用手順](docs/operations/staff-master-unattended-runbook.md)を参照してください。

## 最初に読む

作業の入口は[AGENTS.md](AGENTS.md)とする。新しい作業への着手時に必ず読む範囲は、次の短い2か所に限定する。

文書ごとの対象アプリは、[ドキュメント分類一覧](docs/README.md)で確認する。

1. [Work運用方針](docs/operations/work-policy.md)の「1. 方針」
2. [STATUS](docs/handoff/STATUS.md)の「現在の作業と読取り対象」

その後はSTATUSに記載された対象ソース、要件ID、関連設計、関連テスト、Library資料だけを基本の読取り対象とする。優先順位、STATUS不一致時の扱い、追加読取りと確認条件はWork運用方針を正本とし、READMEには重複記載しない。

## 正本と保管場所

- GitHubを正本とするもの：YAML、Power Fx、要件、設計、テスト仕様、運用方針、進捗、変更履歴
- ChatGPT Libraryで保管するもの：画像、Excel、Word、PDF、HTML原本、検討用資料などGitHubで版管理しない成果物
- 同じMarkdownをGitHubとLibraryの両方で正本として管理しない
- Library資料の所在と読取り条件は[Library資料索引](docs/operations/library-materials-index.md)で確認する

## 自動テストアプリの現行ソース

- [公開由来のCanvasソース](powerapps/canvas-v3/Src/Screen1.pa.yaml)
- [累積変更マニフェスト](automation/change.json)、[対象環境・App ID](config/apps/staff-master.json)
- [無人修正・テスト公開の運用手順](docs/operations/staff-master-unattended-runbook.md)
- [デザイン基準](docs/design/design-system.md)、[テスト仕様書](docs/testing/test-specification.md)
- [現行Dataverse・履歴・配置・P0回帰](e2e/hybrid/)、[旧版回復用P0](e2e/staff-master-p0.test.ts)

公開後にサーバー側の実行ルールを読戻し、追加テストとP0の両方に合格した候補だけをmainへ統合します。成功タグを作る前に、検証済み記録からREADMEの成功版欄と文書専用コミットを生成します。READMEの版・リンク・検証runと候補版を照合し、テスト済みソースとの差分がREADMEだけであることを確認してから、そのコミットへ成功タグを付けます。不一致ならタグ作成を停止します。現在のリポジトリ設定ではActionsによるPR作成が禁止されているため、生成した変更をこのWorkがPR経由で統合します。ユーザーへの追加確認は不要です。Actionsだけで文書更新完了とはせず、mainへの反映まで確認します。詳細は運用手順を参照してください。

## ハンドメイド用・旧v1.11の参照ソース

- [貼り付け用v1.11](src/staff-master/scrStaffMasterSearch_v1.11.paste.yaml)
- [画面定義v1.11・管理者用](src/staff-master/scrStaffMasterSearch_v1.11.pa.yaml)
- [PDF保存接続用Power Fx](src/staff-master/CommuteLedger_v1.11_SavePDF_OnTimerEnd.fx)
- [導入手順・テストデータ・制約](docs/handoff/install-v1.11.md)
- [検査結果](docs/testing/RESULTS.md)、[機械可読結果](docs/testing/v1.11-validation.json)

これらは旧貼付用ソースで、自動テストアプリの現行ソースとは分けて管理します。旧v1.11の検索データ未表示報告は旧版の課題として保持します。PDF関数の有効化と保存フロー接続は別途必要で、PDF生成・保存の実機検証は未完了です。

v1.11はv1.08正本から作成し、廃止したCodex v1.09/v1.10ブランチのコードは使用していない。v1.08は新版の実機確認が済むまで復元用に保持する。

v1.12以降は変更した部品・プロパティだけを配布する。部品IDの`111`を毎回改名せず、完全版はGitHub上で差分適用して同期する。チャットへ全ソースを毎回再出力しない。

## 構成

| パス | 役割 |
|---|---|
| AGENTS.md | エージェント向けの短い作業入口。詳細ルールはWork運用方針を参照 |
| docs/requirements/ | 要件定義・受入条件 |
| docs/design/ | 基本・詳細設計、デザイン基準、データ契約 |
| docs/operations/ | Work運用方針、差分配布方針、Library資料索引 |
| docs/handoff/ | 現在地、導入手順、変更履歴 |
| docs/testing/ | 試験計画・証跡・レビュー |
| docs/reference/ | 旧HTML設計・旧DADS。現行仕様ではない |
| powerapps/canvas-v3/ | 自動テストアプリの現行Canvasソース |
| powerapps/solution-src/ | 自動テストアプリのSolutionソース |
| automation/、scripts/automation/ | 承認済み差分、配布・復元・成功版確定・README更新 |
| e2e/ | 変更専用テストと既存P0回帰 |
| src/staff-master/ | ハンドメイド用・旧v1.11のYAML・Power Fx |
| src/staff-master/patches/ | v1.12以降の変更部品、manifest、適用・復元手順 |
| src/reference/ | 旧DADS部品。現行画面の依存物ではない |
| assets/commute-ledger/ | 認定簿の空様式 |
| tests/ | Workから再実行する静的検査 |
| tools/build_v111.py | v1.08→v1.11専用の再現用移行。v1.12以降には使用しない |

同じ画面の旧版は新版確認後にGit履歴へ集約し、ZIPや一時ファイルは格納しない。資料版は本文で管理、コード版は0.01刻みとする。

自動化基盤の単体検査：`python -m unittest discover -s tests/automation -v`。旧v1.11の静的検査：`python tests/validate_v111.py`。公開アプリの合否はActionsの読戻し・追加E2E・P0で判断し、ローカル検査だけで実機合格とはしません。
