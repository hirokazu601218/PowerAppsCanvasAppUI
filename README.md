# PowerAppsCanvasAppUI

非常勤職員マスタ検索・通勤手当認定簿のキャンバスアプリ。GitHubをChatGPT SolのWorkで扱う共有正本とする。

**最新試作：v1.11。B案（Fluent 2＋DADS）と職員検索サイドバー開閉を実装。Studio実機確認待ち。**

## 最初に読む

1. [Work運用方針](docs/operations/work-policy.md)と[現在地](docs/handoff/STATUS.md)
2. [要件定義](docs/requirements/requirements.md)
3. [基本設計](docs/design/basic-design.md)、[詳細設計](docs/design/detailed-design.md)、[B案デザイン基準](docs/design/design-system.md)
4. [テスト・レビュー基準](docs/testing/acceptance.md)
5. [v1.12以降のコントロール単位差分配布方針](docs/operations/control-diff-policy.md)

## 最新ソース

- [貼り付け用v1.11](src/staff-master/scrStaffMasterSearch_v1.11.paste.yaml)
- [画面定義v1.11・管理者用](src/staff-master/scrStaffMasterSearch_v1.11.pa.yaml)
- [PDF保存接続用Power Fx](src/staff-master/CommuteLedger_v1.11_SavePDF_OnTimerEnd.fx)
- [導入手順・テストデータ・制約](docs/handoff/install-v1.11.md)
- [検査結果](docs/testing/RESULTS.md)、[機械可読結果](docs/testing/v1.11-validation.json)

架空25名と履歴を内蔵。初期表示にデータ接続・App.Formulas・OnStart・OnVisibleは不要。PDF関数の有効化と保存フロー接続は別途必要。Studio実行・PDF保存は未検証。

v1.11はv1.08正本から作成し、廃止したCodex v1.09/v1.10ブランチのコードは使用していない。v1.08は新版の実機確認が済むまで復元用に保持する。

v1.12以降は変更した部品・プロパティだけを配布する。部品IDの`111`を毎回改名せず、完全版はGitHub上で差分適用して同期する。チャットへ全ソースを毎回再出力しない。

## 構成

| パス | 役割 |
|---|---|
| docs/requirements/ | 要件定義・受入条件 |
| docs/design/ | 基本・詳細設計、デザイン基準、データ契約 |
| docs/operations/ | ChatGPT Sol Workでの運用方針 |
| docs/handoff/ | 現在地、導入手順、変更履歴 |
| docs/testing/ | 試験計画・証跡・レビュー |
| docs/reference/ | 旧HTML設計・旧DADS。現行仕様ではない |
| src/staff-master/ | 現行職員検索YAML・Power Fx |
| src/staff-master/patches/ | v1.12以降の変更部品、manifest、適用・復元手順 |
| src/kojo/ | 別アプリ控除詳細の最新保管版 |
| src/reference/ | 旧DADS部品。現行画面の依存物ではない |
| assets/commute-ledger/ | 認定簿の空様式 |
| tests/ | Workから再実行する静的検査 |
| tools/build_v111.py | v1.08→v1.11専用の再現用移行。v1.12以降には使用しない |

同じ画面の旧版は新版確認後にGit履歴へ集約し、ZIPや一時ファイルは格納しない。資料版は本文で管理、コード版は0.01刻みとする。

検査実行：`python tests/validate_v111.py`。ローカル評価器はMicrosoft公式コンパイラやStudio描画エンジンではない。

要件定義、設計、YAML／Power Fx開発、静的テスト、レビューはすべてChatGPT SolのWorkで行う。ユーザーは業務判断、Power Apps Studioでの実機確認、リリース承認を担当する。
