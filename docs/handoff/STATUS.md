# 現在地

更新日：2026-09-15

| 項目 | 状態 |
|---|---|
| 実施環境 | ChatGPT SolのWorkへ一本化 |
| 共有正本 | GitHub main。YAML、Power Fx、要件、設計、テスト仕様、運用方針、進捗、変更履歴 |
| Library | GitHubで版管理しない画像、Excel、Word、PDF、HTML原本、検討用資料を保管 |
| 採用デザイン | B案。要件／基本・詳細設計／デザイン基準v1.03 |
| 最新成功版 | 隔離テストアプリv1.13、架空25名内蔵。検索開閉を横三本線へ変更。追加テスト2件＋P0合格、成功タグv1.13 |
| B案実装 | モダンボタン・検索入力、固定サマリー、2段一覧、文字サイズ切替、全項目保持 |
| 職員検索サイドバー開閉 | 実装。手動開閉360px／48px。条件・選択・ページ保持 |
| v1.13以降 | 部品差分配布。111のコントロール・変数IDは固定 |
| ローカル検査 | 68チェック、8組の配置式、10枚の配置モデル描画。詳細はRESULTS参照 |
| Studio貼付・動作・見た目 | 旧GitHub v1.11に検索データ未表示の報告（BUG-SEARCH-001）。当該版の再現・原因分析は未完了。今回採用した公開由来基準とv1.12のP0合格とは別に保持 |
| PDF生成・保存フロー | 実機未検証、接続設定が必要 |
| 別アプリ控除詳細 | v1.01を保管。B案移行は今回対象外 |

## 現在の作業と読取り対象

| 項目 | 指定 |
|---|---|
| 対象機能 | Issue #12完了：検索領域開閉アイコンを横三本線へ変更（成功版v1.13） |
| 基準版 | P0再合格済み公開アプリ `職員マスタ検索_自動テスト_v1_11`。GitHub v1.11と差分照合済み。P0合格済み公開版を採用し、旧版は参照として保持 |
| 要件ID | AUT-001～AUT-025、NFR-001～NFR-013（`docs/requirements/unattended-development-requirements.md` v1.03） |
| 対象ソース | `scripts/automation/`、`tests/automation/`、`automation/`、`config/apps/`、`.github/workflows/staff-master-transaction.yml`、`staff-master-finalize.yml`、`e2e/changes/approved-property.test.ts`、 `.github/workflows/phase2-source-reconstruction.yml`、`phase1-5-target-p0.yml`、`tools/powerapps-source-reconstruct/`、`powerapps/canvas-v3/`、`powerapps/solution-src/`、`e2e/staff-master-p0.test.ts` |
| 関連設計 | `docs/operations/staff-master-unattended-runbook.md`、`docs/operations/unattended-development-step8-9-acceptance.md`、 `docs/operations/unattended-development-implementation-plan.md`、`docs/operations/unattended-development-phase1-5-execution-plan.md`、`docs/operations/unattended-development-step6-source-reconstruction.md`、`docs/operations/unattended-development-step7-automatic-source-deployment.md` |
| 関連テスト | ステップ8受入run 34952452993、v1.12変更テスト＋P0・安全制御10件run 34954109942、mainとタグの確定run 34954509560が合格 |
| Library資料 | なし |
| 未解決事項 | Issue #12の失敗原因は解消。v1.13公開・追加テスト・P0・main統合・成功タグ確定済み。次の修正指示待ち |

新しい作業へ切り替える時は、この表の対象ソース、要件ID、関連設計、関連テスト、Library資料を更新する。文書だけの変更では関連テストを「対象外。リンク・記述整合のみ確認」とする。

## 自動化基盤と実行結果

| 項目 | 状態 |
|---|---|
| 無人修正・テスト・公開基盤 | 9ステップすべて完了。ステップ8の自動修復・停止・復元に加え、run 34954109942でv1.12候補の全ゲート合格。PR #6統合後、run 34954509560で成功タグv1.12を確定 |
| Phase 1 P0 | run #8 attempt 3が成功。2026-09-15T01:27:59Z完了。証跡は14日保持 |
| 実環境確認 | Azure Subscriptionあり・所有者。対象はDataverse付き開発者環境、非マネージド。Power Apps Premiumなし |
| GitHub格納状態 | 完全なSolution、active `*.pa.yaml`、`baseline.msapr`、変更専用テスト、厳格な実行時同期ゲートを格納済み。初期ソース確定は `ab1b7456ed8bc7d39cd302c1e23276b789212179`、ステップ7復元確定は `260819a4fa30c4d8c8dcd02acc626c26d7823697` |
| 推奨経路 | 保持した元msappとactive YAMLを使用し、承認済みの既存プロパティをマニフェスト駆動で実行ルールへ同期してSolutionをパックする。新規構造・記載外変更は停止。元のPersistence実証は履歴として保持 |
| Power Platform Git統合 | GitHub接続はプレビュー。GitHub Organization、Managed Environment、Azure Key Vault、Premium相当ライセンス等が必要なため当面見送り |
| GitHub Actions | OIDC、Dataverse URL直接指定、CanView共有、再構成、Solution反映、明示的公開、サーバー側ルール読戻し、変更専用テスト、P0、失敗時復元を連結済み |
| E2Eスクリプト | `e2e/testapp-smoke.test.ts` と `e2e/staff-master-p0.test.ts` を格納済み |
| Power Apps E2E | 基準環境P0はrun #8 attempt 3で成功。隔離環境P0はrun 34925700515、再構成基線はrun 34928950801、ステップ7変更版はrun 34934912204、復元版はrun 34935420385で合格。ステップ8の自動修復・停止・復元はrun 34952452993、v1.12候補はrun 34954109942で合格。全試行はIssue #5と#7へ保持 |
| 合否の境界 | ワークフローやスクリプトの存在だけでは合格としない。対象版の実行結果と証跡で判定する |

## テスト設計

[テスト方針v1.00](../testing/test-policy.md)、[テスト仕様書v1.01](../testing/test-specification.md)を作成。95ケース定義＋連続スモーク、独立期待値、8表示条件、PDF実体照合、差分回帰を定義した。ケースID・表構造・25名の期待データ整合を文書検査済み。既存68件のローカル合格は実機合格ではない。

正式PDF用紙、保存先、認定IDと金額の整合fixtureは未決／未実装として仕様書Q1～Q5に記録。

## ChatGPT Sol Workの次の作業

ステップ1～9は完了。2026-09-15の承認に基づき、既存プロパティ変更を対象とするテスト公開の運用を開始した。

| ステップ | 内容 | 状態 |
|---:|---|---|
| 1 | 要件・構築方針の確定 | 完了 |
| 2 | 合格アプリの保全・Solution化 | 完了 |
| 3 | 隔離テスト環境の作成 | 完了 |
| 4 | 専用ID・GitHub OIDC認証 | 完了 |
| 5 | 自動配布・CanView共有・P0 | 完了 |
| 6 | 編集可能ソースからの再構築 | 完了 |
| 7 | 小変更→公開→変更テスト＋P0 | 完了 |
| 8 | 自動修復・停止・合格版復元 | 完了 |
| 9 | v1.12検証・main統合・成功タグ・運用開始 | 完了 |

次はこのWorkで修正指示を受け、[運用手順](../operations/staff-master-unattended-runbook.md) に従って方針提示・承認後に実行する。Issue #12はv1.13として完了。次の成功版候補はv1.14。追加の修正指示をこのWorkで受け付ける。

[受入・成功版確定記録](../operations/unattended-development-step8-9-acceptance.md)、[成功タグv1.12](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/tree/v1.12)、[Issue #7](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/7) を参照する。

## 未決・ギャップ

- ステップ7では、一時表示変更の無人反映、変更専用テスト＋P0、元表示への復元・再公開・P0を実証した。現行Persistence経路はactive `.pa.yaml` 単独では実行用ルールを再コンパイルしないため、承認対象を厳格照合した実行時ルール同期を使用した。ステップ8で既存プロパティのマニフェスト駆動と修復制御を実証済み。新規コントロール等の一般コンパイルは未対応で、運用ゲートが停止する。
- 最新P0はv1.13の `34976128110`。成功タグv1.13、公開App ID `362ac991-eead-4f07-8373-afdb3ebfdba1`。以下は過去のステップ7証跡：変更版証跡は `step6-source-reconstruction-13`（ID `10382398248`）と `phase1-5-target-evidence-13`（ID `10383136592`）、復元版証跡は `step6-source-reconstruction-14`（ID `10382428589`）と `phase1-5-target-evidence-14`（ID `10382753247`）。いずれも2026-09-29まで保持する。
- 本番列一覧、Dataverseテーブル名・型・ロール、実接続/委任設計は別途。
- TSVから正式XLSX出力への方式は未決。
- 帳票A3/A4等の正式用紙と実機改ページは未決。
- 通勤支給予定と認定簿共通サンプルの金額は未整合。テストデータ改修が必要。
- 認定ID選択UIは未実装。給与簿詳細はサンプル15項目で、本番の未知列は未収録。
- 簡易出力は全件TSVコピーと表示中5行の印刷。正式な全件XLSX出力ではない。
- モダンコントロールの提供状況・アクセシビリティ・PDF実験機能は環境で確認。
- 生成画像は概念図。省略項目と濃い見出しは要件・設計書で補正済み。
- 今回の配置モデル画像もStudioスクリーンショットではない。実機校正は未実施。

## Issue #12 原因分析・対処（2026-09-15）

- 初回run `34968864160`：v1.13候補のビルド・公開・読戻し・P0成功。追加テストが表示ラベルをクリックし、透明な行選択ボタンに遮られて失敗。実際の行ボタンを名前とroleで指定するよう修正した。
- 復元run `34974840163`：行ボタンクリックと検索欄閉鎖は成功。職員番号の `.first()` が非表示の一覧セルを選び、詳細表示を誤判定。詳細ヘッダーの一意な職員番号・所属で検証するよう修正した。v1.12の再公開・読戻し・P0は成功したが、追加テスト不合格のため復元完了扱いにはしない。
- 復元概要の `not required` 誤表示を修正。復元成功・失敗・未実施を区別する既存テストを補強し、合格した。
- ユーザーの「原因分析して対処」指示に基づき、修正したテストで再度復元確認を実施。復元全ゲート合格後にのみv1.13再展開・追加テスト・P0・成功版確定へ進む。既存P0は変更していない。
- 詳細な試行・判断記録は [Issue #12](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/12)。

復元確認run `34975611706` は `RESTORED`、追加テスト・P0とも合格。候補アプリを変更せずテストの参照先修正だけで解消した。これを根拠にv1.13の再展開へ進む。

### 完了結果

- 再展開run [34976128110](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34976128110)：build/auth/import/publish/readback/change_test/p0すべて成功。追加テスト2件合格。開閉2往復、条件・選択・ページ保持を確認。公開スクリーンショットでも横三本線を確認。
- PR #13をmain `f1f0dd83d7198c09f8a862c6a747b0c48087a522` へ統合。確定run [34976590043](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34976590043) 成功、[v1.13](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/tree/v1.13)を確定。
- 詳細artifact `10399029288` は2026-09-29まで保持。成功タグの注釈とIssueに恒久記録を保持。
- アプリ一覧の表示名は既存の `職員マスタ検索_自動テスト_v1_11`。画面内の版表示はv1.13。今回、アプリ一覧名の変更は行っていない。

## テスト仕様書v1.01更新（2026-09-15）

Issue #12で発生したテストlocatorの誤りを再発防止ルールへ反映した。表示Labelではなく実操作部品を選ぶこと、`.first()`等で一意性問題を回避しないこと、閉じた領域内の非表示セルを状態保持判定に使わないこと、候補版と復元版の双方でlocatorを検証すること、Playwright証跡でテスト不具合とアプリ不具合を区別することを[テスト仕様書v1.01](../testing/test-specification.md#セレクター設計の再発防止ルール)へ追加した。文書だけの変更のためアプリ配布・E2E・P0は対象外。見出しリンク、文書版、変更履歴の整合を確認した。
