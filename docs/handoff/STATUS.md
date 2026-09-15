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
| 対象機能 | Power Apps無人修正・テスト・公開基盤：ステップ9候補検証・成功版確定 |
| 基準版 | P0再合格済み公開アプリ `職員マスタ検索_自動テスト_v1_11`。GitHub v1.11と差分照合済み。P0合格済み公開版を採用し、旧版は参照として保持 |
| 要件ID | AUT-001～AUT-025、NFR-001～NFR-013（`docs/requirements/unattended-development-requirements.md` v1.03） |
| 対象ソース | `scripts/automation/`、`tests/automation/`、`automation/`、`config/apps/`、`.github/workflows/staff-master-transaction.yml`、`staff-master-finalize.yml`、`e2e/changes/approved-property.test.ts`、 `.github/workflows/phase2-source-reconstruction.yml`、`phase1-5-target-p0.yml`、`tools/powerapps-source-reconstruct/`、`powerapps/canvas-v3/`、`powerapps/solution-src/`、`e2e/staff-master-p0.test.ts` |
| 関連設計 | `docs/operations/staff-master-unattended-runbook.md`、`docs/operations/unattended-development-step8-9-acceptance.md`、 `docs/operations/unattended-development-implementation-plan.md`、`docs/operations/unattended-development-phase1-5-execution-plan.md`、`docs/operations/unattended-development-step6-source-reconstruction.md`、`docs/operations/unattended-development-step7-automatic-source-deployment.md` |
| 関連テスト | 基準環境P0再合格。変更版の再構成・隔離公開・変更専用テスト＋P0成功（run 34934912204）。一時変更の復元・再公開・P0成功（run 34935420385） |
| Library資料 | なし |
| 未解決事項 | v1.12候補の最終テスト、main統合、成功タグの確定 |

新しい作業へ切り替える時は、この表の対象ソース、要件ID、関連設計、関連テスト、Library資料を更新する。文書だけの変更では関連テストを「対象外。リンク・記述整合のみ確認」とする。

## 自動化基盤と実行結果

| 項目 | 状態 |
|---|---|
| 無人修正・テスト・公開基盤 | 9ステップ中ステップ1～8完了。run 34952452993 attempt 2で自動修復、同一原因と対応策識別、停止、v1.11復元、復元後の表示確認＋P0に合格。ステップ9実行中 |
| Phase 1 P0 | run #8 attempt 3が成功。2026-09-15T01:27:59Z完了。証跡は14日保持 |
| 実環境確認 | Azure Subscriptionあり・所有者。対象はDataverse付き開発者環境、非マネージド。Power Apps Premiumなし |
| GitHub格納状態 | 完全なSolution、active `*.pa.yaml`、`baseline.msapr`、変更専用テスト、厳格な実行時同期ゲートを格納済み。初期ソース確定は `ab1b7456ed8bc7d39cd302c1e23276b789212179`、ステップ7復元確定は `260819a4fa30c4d8c8dcd02acc626c26d7823697` |
| 推奨経路 | 保持した元msappとactive YAMLを使用し、承認済みの既存プロパティをマニフェスト駆動で実行ルールへ同期してSolutionをパックする。新規構造・記載外変更は停止。元のPersistence実証は履歴として保持 |
| Power Platform Git統合 | GitHub接続はプレビュー。GitHub Organization、Managed Environment、Azure Key Vault、Premium相当ライセンス等が必要なため当面見送り |
| GitHub Actions | OIDC、Dataverse URL直接指定、CanView共有、再構成、Solution反映、明示的公開、サーバー側ルール読戻し、変更専用テスト、P0、失敗時復元を連結済み |
| E2Eスクリプト | `e2e/testapp-smoke.test.ts` と `e2e/staff-master-p0.test.ts` を格納済み |
| Power Apps E2E | 基準環境P0はrun #8 attempt 3で成功。隔離環境P0はrun 34925700515、再構成基線はrun 34928950801、ステップ7変更版はrun 34934912204、復元版はrun 34935420385で合格。全試行はIssue #5へ保持 |
| 合否の境界 | ワークフローやスクリプトの存在だけでは合格としない。対象版の実行結果と証跡で判定する |

## テスト設計

[テスト方針v1.00](../testing/test-policy.md)、[テスト仕様書v1.00](../testing/test-specification.md)を作成。95ケース定義＋連続スモーク、独立期待値、8表示条件、PDF実体照合、差分回帰を定義した。ケースID・表構造・25名の期待データ整合を文書検査済み。既存68件のローカル合格は実機合格ではない。

正式PDF用紙、保存先、認定IDと金額の整合fixtureは未決／未実装として仕様書Q1～Q5に記録。

## ChatGPT Sol Workの次の作業

ステップ8は実環境受入に合格。2026-09-15のユーザー指示でステップ9まで連続実行を承認済み。

1. v1.12候補を隔離公開し、変更表示テストと既存P0を実行する。
2. 全ゲート合格後、PR #6の候補SHAを固定してmainへ統合する。
3. テスト対象とmainの内容一致を再検査し、成功タグv1.12を作る。
4. Issue #7、受入記録、STATUSを最終結果へ更新する。

## 未決・ギャップ

- ステップ7では、一時表示変更の無人反映、変更専用テスト＋P0、元表示への復元・再公開・P0を実証した。現行Persistence経路はactive `.pa.yaml` 単独では実行用ルールを再コンパイルしないため、承認対象を厳格照合した実行時ルール同期を使用した。ステップ8で既存プロパティのマニフェスト駆動と修復制御を実証済み。新規コントロール等の一般コンパイルは未対応で、運用ゲートが停止する。
- 最新P0はステップ8の復元後 `34952452993` attempt 2。以下は過去のステップ7証跡：変更版証跡は `step6-source-reconstruction-13`（ID `10382398248`）と `phase1-5-target-evidence-13`（ID `10383136592`）、復元版証跡は `step6-source-reconstruction-14`（ID `10382428589`）と `phase1-5-target-evidence-14`（ID `10382753247`）。いずれも2026-09-29まで保持する。
- 本番列一覧、Dataverseテーブル名・型・ロール、実接続/委任設計は別途。
- TSVから正式XLSX出力への方式は未決。
- 帳票A3/A4等の正式用紙と実機改ページは未決。
- 通勤支給予定と認定簿共通サンプルの金額は未整合。テストデータ改修が必要。
- 認定ID選択UIは未実装。給与簿詳細はサンプル15項目で、本番の未知列は未収録。
- 簡易出力は全件TSVコピーと表示中5行の印刷。正式な全件XLSX出力ではない。
- モダンコントロールの提供状況・アクセシビリティ・PDF実験機能は環境で確認。
- 生成画像は概念図。省略項目と濃い見出しは要件・設計書で補正済み。
- 今回の配置モデル画像もStudioスクリーンショットではない。実機校正は未実施。
