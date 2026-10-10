# dot依頼一覧

| ID | 内容 | 対象 | 状態 | 関連ID |
|---|---|---|---|---|
| DOT-001 | 確定仕様・実装・文書の整合 | StaffMaster-Automation-Test／204a48dc-7f23-43dd-b934-4654a3cfa306 | 文書更新・Draft PR準備、P/H採取と最終照合は未実施 | PAY-IMPLEMENT-001／PAY-AUDIT-001 |

## DOT-001

範囲：GitHubの要件・設計・試験仕様・STATUS・説明HTML・記録とDraft PR。既存フローの無変更readbackを含むが、アプリ編集・データ変更・公開・main統合・権限変更は含まない。

完了条件：依頼ID衝突なし、事実に沿う差分をPRで確認でき、実測と未実施・残件・出典を区別する。アプリ全体の開発完了は別判定。

質問と回答：小さい画面の表示方針は2026-10-10 07:37:54 UTCに「Aで」と承認。通常PCのサマリー固定、狭い・低い領域の全体スクロールを採用。再計算focusの見切れ、履歴AX差は残件。正式P/H・自動E2E・最終照合は未実施。

依存：[PR #135](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/135) → [PR #136](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/136)。既存PRのbase・headは変更せず、実装S‴とPR136最新版を子ブランチに取り込む。

[今回記録](../../records/changes/dot-001/manual-20261010-handoff/QA-REPORT.md)／[作業状態](../handoff/STATUS.md)。
