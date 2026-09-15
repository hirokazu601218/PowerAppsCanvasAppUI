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
| 要件ID | AUT-001～AUT-025、NFR-001～NFR-013（`docs/requirements/unattended-development-requirements.md` v1.02） |
| 対象ソース | `.github/workflows/phase2-source-reconstruction.yml`、`phase1-5-target-p0.yml`、`tools/powerapps-source-reconstruct/`、`powerapps/canvas-v3/`、`powerapps/solution-src/`、`e2e/staff-master-p0.test.ts` |
| 関連設計 | `docs/operations/unattended-development-implementation-plan.md`、`docs/operations/unattended-development-phase1-5-execution-plan.md`、`docs/operations/unattended-development-step6-source-reconstruction.md`、`docs/operations/unattended-development-step7-automatic-source-deployment.md` |
| 関連テスト | 基準環境P0再合格。変更版の再構成・隔離公開・変更専用テスト＋P0成功（run 34934912204）。一時変更の復元・再公開・P0成功（run 34935420385） |
| Library資料 | なし |
| 未解決事項 | ステップ8の原因指紋・自動修復・反復制御の汎用化、公開アプリ由来activeソースと旧GitHub v1.11ソースの差分照合 |

新しい作業へ切り替える時は、この表の対象ソース、要件ID、関連設計、関連テスト、Library資料を更新する。文書だけの変更では関連テストを「対象外。リンク・記述整合のみ確認」とする。

## 自動化基盤と実行結果

| 項目 | 状態 |
|---|---|
| 無人修正・テスト・公開基盤 | 9ステップ中ステップ1～7完了。GitHub上の一時表示変更を隔離アプリへ無人反映し、変更専用テスト＋P0合格後に元表示へ復元・再公開・P0再合格 |
| Phase 1 P0 | run #8 attempt 3が成功。2026-09-15T01:27:59Z完了。証跡は14日保持 |
| 実環境確認 | Azure Subscriptionあり・所有者。対象はDataverse付き開発者環境、非マネージド。Power Apps Premiumなし |
| GitHub格納状態 | 完全なSolution、active `*.pa.yaml`、`baseline.msapr`、変更専用テスト、厳格な実行時同期ゲートを格納済み。初期ソース確定は `ab1b7456ed8bc7d39cd302c1e23276b789212179`、ステップ7復元確定は `260819a4fa30c4d8c8dcd02acc626c26d7823697` |
| 推奨経路 | Microsoft公式 `PowerApps-Tooling` のPersistenceライブラリを固定commitで使用し、`baseline.msapr`＋active `pa.yaml`から再構成する。非推奨 `pac canvas pack/unpack` は使用しない |
| Power Platform Git統合 | GitHub接続はプレビュー。GitHub Organization、Managed Environment、Azure Key Vault、Premium相当ライセンス等が必要なため当面見送り |
| GitHub Actions | OIDC、Dataverse URL直接指定、CanView共有、再構成、Solution反映、明示的公開、サーバー側ルール読戻し、変更専用テスト、P0、失敗時復元を連結済み |
| E2Eスクリプト | `e2e/testapp-smoke.test.ts` と `e2e/staff-master-p0.test.ts` を格納済み |
| Power Apps E2E | 基準環境P0はrun #8 attempt 3で成功。隔離環境P0はrun 34925700515、再構成基線はrun 34928950801、ステップ7変更版はrun 34934912204、復元版はrun 34935420385で合格。全試行はIssue #5へ保持 |
| 合否の境界 | ワークフローやスクリプトの存在だけでは合格としない。対象版の実行結果と証跡で判定する |

## テスト設計

[テスト方針v1.00](../testing/test-policy.md)、[テスト仕様書v1.00](../testing/test-specification.md)を作成。95ケース定義＋連続スモーク、独立期待値、8表示条件、PDF実体照合、差分回帰を定義した。ケースID・表構造・25名の期待データ整合を文書検査済み。既存68件のローカル合格は実機合格ではない。

正式PDF用紙、保存先、認定IDと金額の整合fixtureは未決／未実装として仕様書Q1～Q5に記録。

## ChatGPT Sol Workの次の作業

次はステップ8「原因分析・自動修復・反復制御の汎用化」とする。

1. ステップ7専用の表示ルール同期を、承認済み変更マニフェストから対象コントロール・プロパティ・変更前後値を検証する汎用ゲートへ置き換える。
2. テストケースID＋失敗工程＋正規化エラーの原因指紋と、試行済み対応策の台帳を実装する。
3. 隔離アプリだけで意図的な不合格を発生させ、未試行の新対応策を自動適用して合格へ到達することを検証する。
4. 同じ対応策の単純反復を拒否し、新対応策が尽きた場合の停止と合格版復元を検証する。
5. 変更専用テストとP0、Issue・PR・Actions・14日証跡の相互追跡を維持する。

基準・本番アプリ、課金、接続、権限、v1.12採番は変更しない。

## 未決・ギャップ

- ステップ7では、一時表示変更の無人反映、変更専用テスト＋P0、元表示への復元・再公開・P0を実証した。現行Persistence経路はactive `.pa.yaml` 単独では実行用ルールを再コンパイルしないため、承認対象を厳格照合した実行時ルール同期を使用した。ステップ8でこの同期と修復判断を汎用化する。
- 最終P0 runは復元後の `34935420385`。変更版証跡は `step6-source-reconstruction-13`（ID `10382398248`）と `phase1-5-target-evidence-13`（ID `10383136592`）、復元版証跡は `step6-source-reconstruction-14`（ID `10382428589`）と `phase1-5-target-evidence-14`（ID `10382753247`）。いずれも2026-09-29まで保持する。
- 本番列一覧、Dataverseテーブル名・型・ロール、実接続/委任設計は別途。
- TSVから正式XLSX出力への方式は未決。
- 帳票A3/A4等の正式用紙と実機改ページは未決。
- 通勤支給予定と認定簿共通サンプルの金額は未整合。テストデータ改修が必要。
- 認定ID選択UIは未実装。給与簿詳細はサンプル15項目で、本番の未知列は未収録。
- 簡易出力は全件TSVコピーと表示中5行の印刷。正式な全件XLSX出力ではない。
- モダンコントロールの提供状況・アクセシビリティ・PDF実験機能は環境で確認。
- 生成画像は概念図。省略項目と濃い見出しは要件・設計書で補正済み。
- 今回の配置モデル画像もStudioスクリーンショットではない。実機校正は未実施。
