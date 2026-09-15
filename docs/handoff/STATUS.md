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
| 関連設計 | `docs/operations/unattended-development-implementation-plan.md`、`docs/operations/unattended-development-phase1-5-execution-plan.md`、`docs/operations/unattended-development-step6-source-reconstruction.md` |
| 関連テスト | 基準環境P0再合格。URL直接指定の無変更Solution展開成功。activeソース再構成・隔離公開・固定App ID再取得・ソース完全一致・隔離環境P0成功（run 34928950801） |
| Library資料 | なし |
| 未解決事項 | 小変更での修正→公開→変更専用テスト＋P0の一周検証、公開アプリ由来activeソースと旧GitHub v1.11ソースの差分照合 |

新しい作業へ切り替える時は、この表の対象ソース、要件ID、関連設計、関連テスト、Library資料を更新する。文書だけの変更では関連テストを「対象外。リンク・記述整合のみ確認」とする。

## 自動化基盤と実行結果

| 項目 | 状態 |
|---|---|
| 無人修正・テスト・公開基盤 | 9ステップ中ステップ1～6完了。Dataverse URL直接指定の配布、CanView共有、activeソース再構成、隔離公開、再取得完全一致、隔離P0まで成功 |
| Phase 1 P0 | run #8 attempt 3が成功。2026-09-15T01:27:59Z完了。証跡は14日保持 |
| 実環境確認 | Azure Subscriptionあり・所有者。対象はDataverse付き開発者環境、非マネージド。Power Apps Premiumなし |
| GitHub格納状態 | 完全なSolutionに加え、再構成可能なactive `*.pa.yaml` と `baseline.msapr` を `powerapps/canvas-v3/` へ格納済み。成功確定commitは `ab1b7456ed8bc7d39cd302c1e23276b789212179` |
| 推奨経路 | Microsoft公式 `PowerApps-Tooling` のPersistenceライブラリを固定commitで使用し、`baseline.msapr`＋active `pa.yaml`から再構成する。非推奨 `pac canvas pack/unpack` は使用しない |
| Power Platform Git統合 | GitHub接続はプレビュー。GitHub Organization、Managed Environment、Azure Key Vault、Premium相当ライセンス等が必要なため当面見送り |
| GitHub Actions | OIDC、URL直接指定round-trip、CanView共有、隔離P0に加え、再構成→Solutionパック→隔離公開→再取得比較→P0→成功時ソース確定のゲートを構築済み |
| E2Eスクリプト | `e2e/testapp-smoke.test.ts` と `e2e/staff-master-p0.test.ts` を格納済み |
| Power Apps E2E | 基準環境P0はrun #8 attempt 3で成功。隔離環境P0はrun 34925700515、再構成版P0はrun 34928950801で成功（1 passed）。全試行はIssue #5と実行記録へ保持 |
| 合否の境界 | ワークフローやスクリプトの存在だけでは合格としない。対象版の実行結果と証跡で判定する |

## テスト設計

[テスト方針v1.00](../testing/test-policy.md)、[テスト仕様書v1.00](../testing/test-specification.md)を作成。95ケース定義＋連続スモーク、独立期待値、8表示条件、PDF実体照合、差分回帰を定義した。ケースID・表構造・25名の期待データ整合を文書検査済み。既存68件のローカル合格は実機合格ではない。

正式PDF用紙、保存先、認定IDと金額の整合fixtureは未決／未実装として仕様書Q1～Q5に記録。

## ChatGPT Sol Workの次の作業

1. ステップ7の小さな表示変更候補、変更範囲、変更専用テスト、復元条件を提示し、ユーザー承認を得る。
2. 承認後、`powerapps/canvas-v3/Src/Screen1.pa.yaml` を作業ブランチで変更する。
3. activeソースからmsappとSolutionを再構成し、隔離Dataverse URLへ反映・公開する。
4. 変更専用テストと既存P0を実行し、両方の合格を確認する。
5. 成功時は変更版を作業ブランチへ確定し、失敗時は直前の合格Solutionへ復元する。
6. 公開アプリ由来activeソースと旧GitHub v1.11ソースの差分照合を継続する。
7. 承認範囲内に未試行の新対応策がある限り続行し、同じ対応策は単純反復しない。新対応策が尽きた場合または権限・費用・本番変更など範囲を超える場合に停止する。

## 未決・ギャップ

- Dataverse URL直接指定のSolution配布、固定隔離アプリへのCanView共有・P0、Microsoft公式Persistenceライブラリによるactiveソース再構成は成功した。次の未完了ゲートは、意図的な小変更を含む変更専用テスト＋P0の一周検証。
- 最終P0 runは `34928950801`。再構成証跡 `step6-source-reconstruction-6`（ID `10381275802`）は2026-09-29 04:29:53 UTC、P0証跡 `phase1-5-target-evidence-6`（ID `10380538667`）は2026-09-29 04:31:55 UTCまで保持する。
- 本番列一覧、Dataverseテーブル名・型・ロール、実接続/委任設計は別途。
- TSVから正式XLSX出力への方式は未決。
- 帳票A3/A4等の正式用紙と実機改ページは未決。
- 通勤支給予定と認定簿共通サンプルの金額は未整合。テストデータ改修が必要。
- 認定ID選択UIは未実装。給与簿詳細はサンプル15項目で、本番の未知列は未収録。
- 簡易出力は全件TSVコピーと表示中5行の印刷。正式な全件XLSX出力ではない。
- モダンコントロールの提供状況・アクセシビリティ・PDF実験機能は環境で確認。
- 生成画像は概念図。省略項目と濃い見出しは要件・設計書で補正済み。
- 今回の配置モデル画像もStudioスクリーンショットではない。実機校正は未実施。
