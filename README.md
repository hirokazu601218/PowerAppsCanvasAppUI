# PowerAppsCanvasAppUI

非常勤職員マスタ検索・通勤手当認定簿のキャンバスアプリ。GitHubをChatGPT SolのWorkで扱う共有正本とする。

**採用設計：B案（Fluent 2＋DADS）。現行コード：v1.08、B案未反映。次の開発版：v1.09。**

## 最初に読む

1. [Work運用方針](docs/operations/work-policy.md)と[現在地](docs/handoff/STATUS.md)
2. [要件定義](docs/requirements/requirements.md)
3. [基本設計](docs/design/basic-design.md)、[詳細設計](docs/design/detailed-design.md)、[B案デザイン基準](docs/design/design-system.md)
4. [テスト・レビュー基準](docs/testing/acceptance.md)

## 最新ソース

- [貼り付け用v1.08](src/staff-master/scrStaffMasterSearch_v1.08.paste.yaml)
- [画面定義v1.08・管理者用](src/staff-master/scrStaffMasterSearch_v1.08.pa.yaml)
- [PDF保存接続用Power Fx](src/staff-master/CommuteLedger_v1.08_SavePDF_OnTimerEnd.fx)
- [導入手順・テストデータ・制約](docs/handoff/install-v1.08.md)

25名のテストデータ内蔵。Studio実行とPDF保存は未検証。現行実装をB案対応済みと取り違えない。

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
| src/kojo/ | 別アプリ控除詳細の最新保管版 |
| src/reference/ | 旧DADS部品。現行画面の依存物ではない |
| assets/commute-ledger/ | 認定簿の空様式 |
| tests/ | Workから再実行する静的検査 |

同じ画面の旧版はGit履歴で管理し、ZIPや一時ファイルは格納しない。資料版は本文で管理、コード版は0.01刻みとする。

要件定義、設計、YAML／Power Fx開発、静的テスト、レビューはすべてChatGPT SolのWorkで行う。ユーザーは業務判断、Power Apps Studioでの実機確認、リリース承認を担当する。
