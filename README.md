# PowerAppsCanvasAppUI

非常勤職員マスタ検索・通勤手当認定簿のキャンバスアプリ。GitHubのmainをChatGPT SolのWorkで扱う共有正本とする。

**最新試作：v1.11。B案（Fluent 2＋DADS）と職員検索サイドバー開閉を実装。検索データ未表示のユーザー報告あり・原因調査待ち。**

## 最初に読む

作業の入口は[AGENTS.md](AGENTS.md)とする。新しい作業への着手時に必ず読む範囲は、次の短い2か所に限定する。

1. [Work運用方針](docs/operations/work-policy.md)の「1. 方針」
2. [STATUS](docs/handoff/STATUS.md)の「現在の作業と読取り対象」

その後はSTATUSに記載された対象ソース、要件ID、関連設計、関連テスト、Library資料だけを基本の読取り対象とする。優先順位、STATUS不一致時の扱い、追加読取りと確認条件はWork運用方針を正本とし、READMEには重複記載しない。

## 正本と保管場所

- GitHubを正本とするもの：YAML、Power Fx、要件、設計、テスト仕様、運用方針、進捗、変更履歴
- ChatGPT Libraryで保管するもの：画像、Excel、Word、PDF、HTML原本、検討用資料などGitHubで版管理しない成果物
- 同じMarkdownをGitHubとLibraryの両方で正本として管理しない
- Library資料の所在と読取り条件は[Library資料索引](docs/operations/library-materials-index.md)で確認する

## 最新ソース

- [貼り付け用v1.11](src/staff-master/scrStaffMasterSearch_v1.11.paste.yaml)
- [画面定義v1.11・管理者用](src/staff-master/scrStaffMasterSearch_v1.11.pa.yaml)
- [PDF保存接続用Power Fx](src/staff-master/CommuteLedger_v1.11_SavePDF_OnTimerEnd.fx)
- [導入手順・テストデータ・制約](docs/handoff/install-v1.11.md)
- [検査結果](docs/testing/RESULTS.md)、[機械可読結果](docs/testing/v1.11-validation.json)

架空25名と履歴を内蔵し、データ接続・App.Formulas・OnStart・OnVisibleへの依存なしで初期表示する設計。ただし実機で検索データ未表示の報告があり、動作保証ではありません。PDF関数の有効化と保存フロー接続は別途必要。Studio実行・PDF保存は未検証。

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
| src/staff-master/ | 現行職員検索YAML・Power Fx |
| src/staff-master/patches/ | v1.12以降の変更部品、manifest、適用・復元手順 |
| src/reference/ | 旧DADS部品。現行画面の依存物ではない |
| assets/commute-ledger/ | 認定簿の空様式 |
| tests/ | Workから再実行する静的検査 |
| tools/build_v111.py | v1.08→v1.11専用の再現用移行。v1.12以降には使用しない |

同じ画面の旧版は新版確認後にGit履歴へ集約し、ZIPや一時ファイルは格納しない。資料版は本文で管理、コード版は0.01刻みとする。

検査実行：`python tests/validate_v111.py`。ローカル評価器はMicrosoft公式コンパイラやStudio描画エンジンではない。
