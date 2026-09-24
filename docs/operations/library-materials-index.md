# ChatGPT Library資料索引

> 対象アプリ：共通（自動テスト／ハンドメイド）

更新日：2026-09-24

## 目的

ChatGPT Libraryに保管する資料の所在、用途、関連機能、読取り条件を管理する。資料の内容はLibraryに置き、この索引には複製しない。

YAML、Power Fx、要件、設計、テスト仕様、運用方針、進捗、変更履歴はGitHubを正本とする。Library内のMarkdownがGitHubの文書と重複する場合、そのLibraryファイルは参考・検討用・非正本として扱う。Libraryの「skills」フォルダ内のMarkdownは保管ルール文書であり、自動実行される正式なSkillまたはSKILL.mdではない。

## 資料一覧

| Library資料 | Library内パス | 区分 | 用途・関連機能 | 読む条件 | 正本の扱い |
|---|---|---|---|---|---|
| 職員マスタ_検索ダッシュボード_v0.807.html | `/非常勤給与/検索ダッシュボード/` | HTML原本 | 旧検索ダッシュボードの画面・機能参照 | 旧HTMLとの表示・機能比較、移植仕様の確認時 | Library原本 |
| 職員マスタ_検索ダッシュボード_v0.807_基本設計書.md | `/非常勤給与/検索ダッシュボード/` | 参考Markdown | 旧HTMLの基本設計参照 | GitHubの現行資料だけで旧仕様を確認できない時 | 非正本。GitHub `docs/reference/html-v0.807-basic.md` を優先 |
| 職員マスタ_検索ダッシュボード_v0.807_詳細設計書.md | `/非常勤給与/検索ダッシュボード/` | 参考Markdown | 旧HTMLの詳細設計参照 | GitHubの現行資料だけで旧仕様を確認できない時 | 非正本。GitHub `docs/reference/html-v0.807-detailed.md` を優先 |
| 採用から退職までの共済・保険タイムライン.png | `/非常勤給与/法定控除・社会保険/` | 画像資料 | 共済・保険の時系列確認 | 共済・保険区分、加入・喪失、控除時期を扱う時 | Library原本 |
| PowerApps_UI試作ルール.md | `/非常勤給与/PowerApps_UI試作/` | 旧ルール | 過去の運用経緯 | 運用変更の履歴確認時だけ | 非正本。GitHub `docs/operations/work-policy.md` を正本とする |
| 非常勤給与_ファイル格納ルール.md | `/非常勤給与/skills/` | Library保管ルール | 非常勤給与プロジェクト全体の格納先判断 | Libraryへ成果物を保存・整理する時 | Library側の管理ルール。ただし本リポジトリの正本区分はGitHub運用方針を優先 |
| T_通勤_テーブル定義書.xlsx | 添付ID `libfile_7d3a1d264cc0819195f053d0522a3a83`（フォルダ未確認） | Excel原本 | 通勤84項目・作成条件、COM-DV-001～003 | 通勤テーブルの作成・項目変更時 | 原本は添付。実装対応表はGitHub `config/dataverse/commute-columns.json` |
| 05_基準給与簿DB_v0.1 (3)_テーブル定義書.xlsx | 添付ID `libfile_83586a2630948191b1204fa937bb6cec`（フォルダ未確認） | Excel原本 | 基準給与簿163項目、PAY-DV-001～005 | 基準給与簿テーブルの作成・項目変更時 | 原本は添付。実装対応表はGitHub `config/dataverse/payrollledger-columns.json` |

| 勤務報告_給与試算_2画面_v0.1.md | `/非常勤給与/` | 参考Markdown（内容v0.3） | 勤務報告入力・給与計算過程表示の独立プロトタイプ | 過去の検討経緯確認時。開発時はGitHub正本を読む | 非正本。GitHub `docs/prototypes/attendance-payroll-prototype.md` を優先 |

| PowerApps-lightweight-v1.27-recovery-20260924.zip | `/非常勤給与/`、`libfile_01c27280e03481918efa159544b696c5` | アプリ復旧用パッケージ | 軽量版移行前の公開msapp・保存下書き・軽量版検証済み下書きとSHA256台帳 | 軽量版の復旧、保存内容の再照合時 | 非公開のバイナリ保全。仕様・ソース・判定記録の正本はGitHub。収録時点で軽量版安定アプリは未公開 |

## 更新ルール

- PowerAppsCanvasAppUIに関係するLibrary資料を追加、移動、改名、削除または役割変更した場合は、この索引を更新する。
- 現在の作業で読むLibrary資料が変わる場合は、STATUSも更新する。STATUSには実際に読むLibrary資料だけを記載し、関係しない資料は読まない。
- Library資料が不要になっても、削除判断はこの索引だけで行わず、利用箇所を確認する。
