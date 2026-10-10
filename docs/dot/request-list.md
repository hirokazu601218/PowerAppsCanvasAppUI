# dot依頼一覧

| ID | 内容 | 対象 | 状態 | 関連ID |
|---|---|---|---|---|
| DOT-002 | 要件定義HTML改善・DOT-001文書選択統合 | docs/requirements-html-20261010／Draft PR #136 | HTML反映・検証記録は下記、実ブラウザー／iPhone検証待ち | PAY-REQ-HTML-REWORK-001 |
| DOT-001 | 確定仕様・実装・文書の整合 | StaffMaster-Automation-Test／204a48dc-7f23-43dd-b934-4654a3cfa306 | 文書更新・Draft PR #137作成済み、P/H採取と最終照合は未実施 | PAY-IMPLEMENT-001／PAY-AUDIT-001 |

## DOT-001

範囲：GitHubの要件・設計・試験仕様・STATUS・説明HTML・記録とDraft PR。既存フローの無変更readbackを含むが、アプリ編集・データ変更・公開・main統合・権限変更は含まない。

完了条件：依頼ID衝突なし、事実に沿う差分をPRで確認でき、実測と未実施・残件・出典を区別する。アプリ全体の開発完了は別判定。

質問と回答：小さい画面の表示方針は2026-10-10 07:37:54 UTCに「Aで」と承認。通常PCのサマリー固定、狭い・低い領域の全体スクロールを採用。再計算focusの見切れ、履歴AX差は残件。正式P/H・自動E2E・最終照合は未実施。

依存：[PR #135](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/135) → [PR #136](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/136)。既存PRのbase・headは変更せず、実装S‴とPR136最新版を子ブランチに取り込む。

[今回記録](../../records/changes/dot-001/manual-20261010-handoff/QA-REPORT.md)／[作業状態](../handoff/STATUS.md)。

[Draft PR #137](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/137)。文書更新・PR作成済み、正式P/H・最終照合は検証継続。

## DOT-002

対象：[Draft PR #136](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/136)、既存base `docs/pay-html-001-review-20261009`。Libraryの`DOT-002-HTML-rework-handoff-20261010.zip`と`DOT-002-Work-integration-addendum-20261010.txt`を使用。重複時は追補を優先。

DOT-001の必要な文書差分・表示入力・記録を選択統合し、旧140見出し／62資料単一ファイル版を、公式148上位見出し・173下位項目、分割表示・往復導線・短いモバイル要約へ改善。未設定は「要件未設定」と表示する。正本Markdown・制度判断は保持。

[統合検証記録](../../records/changes/dot-002/manual-20261010-integration/QA-REPORT.md)。生成一致、引用53件・参照SHA、リンク、ID、配置、静的検査、模擬JSの結果を記録する。実ブラウザー・375/390幅・iPhone/Safari/Quick Lookは別判定。実動証拠がそろうまでUI完了扱いにしない。

DOT-001の承認A、Live38引継ぎ観測、外部手続の結果手動登録、xlsx出力、84データ列／71表示欄と撤去履歴を保持。正式P/H・選定自動E2E・最終照合は未完了。main統合・アプリ変更・Web公開・権限変更なし。
