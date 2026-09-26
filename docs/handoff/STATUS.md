# 現在の作業と読取り対象

更新：2026-09-26。過去の時系列全文は[移行前STATUS](../../records/docs/handoff/STATUS-history.md)へ保管。

## 現行の対象

- 継続対象：App ID `204a48dc-7f23-43dd-b934-4654a3cfa306` の単一アプリ。旧配布対象 `362ac991-eead-4f07-8373-afdb3ebfdba1` は現行ではない。
- 現行の[要件](../requirements/requirements.md)、[基本設計](../design/basic-design.md)、[詳細設計](../design/detailed-design.md)、[試験方針](../testing/test-policy.md)、[未決一覧](../requirements/open-decisions.md)を基準にする。
- 専用利用者の検索FAIL／結合BLOCKED、公開版と保存ソースの照合、画面・データ権限、SCR-005計算元などは未解消。移行だけで試験完了とはしない。
- 旧配布・復元・認証診断のActions定義30本は `records/workflows/` に保管し停止する。現行の読み取り専用テスト2本と別アプリ用定期E2E1本は継続する。現行アプリの公開・データ・権限はこの移行では変更しない。

## 今回の文書移行の読取り対象

[三分法](../operations/document-organization.md)、[対照表](../../records/operations/migration/source-map.csv)、[現行の手順](../operations/current-app-request-to-release.md)、[配置検査](../../scripts/governance/validate_document_placement.py)。移行PRの静的チェック結果とGitHub側必須チェック設定はPRで確認し、未設定を合格扱いしない。
