# ChatGPT Library資料索引

更新日：2026-09-15

## 目的

ChatGPT Libraryに保管する資料の所在、用途、関連機能、読取り条件を管理する。資料の内容はLibraryに置き、この索引には複製しない。

YAML、Power Fx、要件、設計、テスト仕様、運用方針、進捗、変更履歴はGitHubを正本とする。Library内のMarkdownがGitHubの文書と重複する場合、そのLibraryファイルは参考・検討用・非正本として扱う。

## 資料一覧

| Library資料 | 区分 | 用途・関連機能 | 読む条件 | 正本の扱い |
|---|---|---|---|---|
| 職員マスタ_検索ダッシュボード_v0.807.html | HTML原本 | 旧検索ダッシュボードの画面・機能参照 | 旧HTMLとの表示・機能比較、移植仕様の確認時 | Library原本 |
| 職員マスタ_検索ダッシュボード_v0.807_基本設計書.md | 参考Markdown | 旧HTMLの基本設計参照 | GitHubの現行資料だけで旧仕様を確認できない時 | 非正本。GitHub `docs/reference/html-v0.807-basic.md` を優先 |
| 職員マスタ_検索ダッシュボード_v0.807_詳細設計書.md | 参考Markdown | 旧HTMLの詳細設計参照 | GitHubの現行資料だけで旧仕様を確認できない時 | 非正本。GitHub `docs/reference/html-v0.807-detailed.md` を優先 |
| 採用から退職までの共済・保険タイムライン.png | 画像資料 | 共済・保険の時系列確認 | 共済・保険区分、加入・喪失、控除時期を扱う時 | Library原本 |
| PowerApps_UI試作ルール.md | 旧ルール | 過去の運用経緯 | 運用変更の履歴確認時だけ | 非正本。GitHub `docs/operations/work-policy.md` を正本とする |
| 非常勤給与_ファイル格納ルール.md | Library保管ルール | 非常勤給与プロジェクト全体の格納先判断 | Libraryへ成果物を保存・整理する時 | Library側の管理ルール。ただし本リポジトリの正本区分はGitHub運用方針を優先 |

## 更新ルール

- Library資料を追加、移動、改名または役割変更した場合に、この索引を更新する。
- STATUSには、その作業で実際に読むLibrary資料だけを記載する。関係しない資料は読まない。
- Library資料が不要になっても、削除判断はこの索引だけで行わず、利用箇所を確認する。
