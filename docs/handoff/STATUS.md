# 現在地

更新日：2026-09-15

| 項目 | 状態 |
|---|---|
| 実施環境 | ChatGPT SolのWorkへ一本化 |
| 共有正本 | GitHub main。YAML、Power Fx、要件、設計、テスト仕様、運用方針、進捗、変更履歴 |
| Library | GitHubで版管理しない画像、Excel、Word、PDF、HTML原本、検討用資料を保管 |
| 採用デザイン | B案。要件／基本・詳細設計／デザイン基準v1.03 |
| 最新試作 | 職員検索v1.11、架空25名内蔵。v1.08正本から作成 |
| B案実装 | モダンボタン・検索入力、固定サマリー、2段一覧、文字サイズ切替、全項目保持 |
| 職員検索サイドバー開閉 | 実装。手動開閉360px／48px。条件・選択・ページ保持 |
| v1.12以降 | 部品差分配布。111のコントロール・変数IDは固定 |
| ローカル検査 | 68チェック、8組の配置式、10枚の配置モデル描画。詳細はRESULTS参照 |
| Studio貼付・動作・見た目 | v1.11検索データ未表示のユーザー報告あり（BUG-SEARCH-001）。厳密な実行版照合・再現・原因分析は未実施。未解決 |
| PDF生成・保存フロー | 実機未検証、接続設定が必要 |
| 別アプリ控除詳細 | v1.01を保管。B案移行は今回対象外 |

## 現在の作業と読取り対象

| 項目 | 指定 |
|---|---|
| 対象機能 | Power Apps無人修正・テスト・公開基盤の設計 |
| 基準版 | P0再合格済み公開アプリ `職員マスタ検索_自動テスト_v1_11`。GitHub v1.11との差分は未照合 |
| 要件ID | AUT-001～AUT-024（`docs/requirements/unattended-development-requirements.md`） |
| 対象ソース | `.github/workflows/staff-master-e2e.yml`、`e2e/staff-master-p0.test.ts`、`src/staff-master/`。Phase 1は調査・文書のみ |
| 関連設計 | `docs/operations/unattended-development-implementation-plan.md`、`docs/operations/unattended-development-phase1-baseline.md`、`docs/operations/unattended-development-phase1-5-execution-plan.md` |
| 関連テスト | 既存P0を再実行して合格。文書はリンク・用語・版・記述整合を確認 |
| Library資料 | なし |
| 未解決事項 | `pac canvas pack` の `System.FormatException`、Studio検証済みSourceCodeの再取得、無変更round-trip、P0 |

新しい作業へ切り替える時は、この表の対象ソース、要件ID、関連設計、関連テスト、Library資料を更新する。文書だけの変更では関連テストを「対象外。リンク・記述整合のみ確認」とする。

## 自動化基盤と実行結果

| 項目 | 状態 |
|---|---|
| 無人修正・テスト・公開基盤 | Phase 0・Phase 1完了。Phase 1.5はSolution、隔離テスト環境、OIDC、GitHub正本化まで完了。`pac canvas pack` の同一例外2回で自動停止 |
| Phase 1 P0 | run #8 attempt 3が成功。2026-09-15T01:27:59Z完了。証跡は14日保持 |
| 実環境確認 | Azure Subscriptionあり・所有者。対象はDataverse付き開発者環境、非マネージド。Power Apps Premiumなし |
| GitHub格納状態 | 公開P0版から取得した完全なSolutionソースとCanvasソースを `powerapps/` 配下へ格納済み |
| 推奨経路 | StudioでSourceCodeを検証済みにして再取得する案、またはPAC CLI 2.12.2を避ける案を次回承認前に比較 |
| Power Platform Git統合 | GitHub接続はプレビュー。GitHub Organization、Managed Environment、Azure Key Vault、Premium相当ライセンス等が必要なため当面見送り |
| GitHub Actions | `.github/workflows/powerapps-e2e.yml` と `staff-master-e2e.yml` を構築済み |
| E2Eスクリプト | `e2e/testapp-smoke.test.ts` と `e2e/staff-master-p0.test.ts` を格納済み |
| Power Apps E2E | run #1は失敗。成功実績とは分けて扱い、Actionsで最新結果を確認する |
| 合否の境界 | ワークフローやスクリプトの存在だけでは合格としない。対象版の実行結果と証跡で判定する |

## テスト設計

[テスト方針v1.00](../testing/test-policy.md)、[テスト仕様書v1.00](../testing/test-specification.md)を作成。95ケース定義＋連続スモーク、独立期待値、8表示条件、PDF実体照合、差分回帰を定義した。ケースID・表構造・25名の期待データ整合を文書検査済み。既存68件のローカル合格は実機合格ではない。

正式PDF用紙、保存先、認定IDと金額の整合fixtureは未決／未実装として仕様書Q1～Q5に記録。

## ChatGPT Sol Workの次の作業

1. Issue #5と実行記録を基に、`System.FormatException`の回避候補を比較する。
2. 次の修正方針を提示し、ユーザー承認を得る。
3. 承認後、Studio検証済みSourceCodeの再取得または別CLI版で無変更round-tripを1回実行する。
4. import成功後、隔離テスト環境のテスト利用者権限を確認してP0を実行する。
5. round-tripとP0の両方が成功した場合だけPhase 2へ進む。

## 未決・ギャップ

- CLI暫定経路は `pac canvas pack/unpack` の非推奨機能を含むため、無変更round-tripの成功を採用条件とする。
- 本番列一覧、Dataverseテーブル名・型・ロール、実接続/委任設計は別途。
- TSVから正式XLSX出力への方式は未決。
- 帳票A3/A4等の正式用紙と実機改ページは未決。
- 通勤支給予定と認定簿共通サンプルの金額は未整合。テストデータ改修が必要。
- 認定ID選択UIは未実装。給与簿詳細はサンプル15項目で、本番の未知列は未収録。
- 簡易出力は全件TSVコピーと表示中5行の印刷。正式な全件XLSX出力ではない。
- モダンコントロールの提供状況・アクセシビリティ・PDF実験機能は環境で確認。
- 生成画像は概念図。省略項目と濃い見出しは要件・設計書で補正済み。
- 今回の配置モデル画像もStudioスクリーンショットではない。実機校正は未実施。
