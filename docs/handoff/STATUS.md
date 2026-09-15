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
| 関連設計 | `docs/operations/unattended-development-implementation-plan.md`、`docs/operations/unattended-development-phase1-baseline.md` |
| 関連テスト | 既存P0を再実行して合格。文書はリンク・用語・版・記述整合を確認 |
| Library資料 | なし |
| 未解決事項 | 保全・編集経路A/B/Cの選択、サービスプリンシパル作成、公開アプリとGitHub v1.11の差分照合 |

新しい作業へ切り替える時は、この表の対象ソース、要件ID、関連設計、関連テスト、Library資料を更新する。文書だけの変更では関連テストを「対象外。リンク・記述整合のみ確認」とする。

## 自動化基盤と実行結果

| 項目 | 状態 |
|---|---|
| 無人修正・テスト・公開基盤 | Phase 0完了。Phase 1はP0基準確認完了、ソース保全方式の判断待ち |
| Phase 1 P0 | run #8 attempt 3が成功。2026-09-15T01:27:59Z完了。証跡は14日保持 |
| GitHub格納状態 | 画面YAML・個別Power Fxは存在。アプリ全体を再構成できる完全なSolutionソースではない |
| Power Platform Git統合 | GitHub接続はプレビュー。GitHub Organization、Managed Environment、Azure Key Vault等が必要で、現個人リポジトリのままでは開始不可 |
| GitHub Actions | `.github/workflows/powerapps-e2e.yml` と `staff-master-e2e.yml` を構築済み |
| E2Eスクリプト | `e2e/testapp-smoke.test.ts` と `e2e/staff-master-p0.test.ts` を格納済み |
| Power Apps E2E | run #1は失敗。成功実績とは分けて扱い、Actionsで最新結果を確認する |
| 合否の境界 | ワークフローやスクリプトの存在だけでは合格としない。対象版の実行結果と証跡で判定する |

## テスト設計

[テスト方針v1.00](../testing/test-policy.md)、[テスト仕様書v1.00](../testing/test-specification.md)を作成。95ケース定義＋連続スモーク、独立期待値、8表示条件、PDF実体照合、差分回帰を定義した。ケースID・表構造・25名の期待データ整合を文書検査済み。既存68件のローカル合格は実機合格ではない。

正式PDF用紙、保存先、認定IDと金額の整合fixtureは未決／未実装として仕様書Q1～Q5に記録。

## ChatGPT Sol Workの次の作業

1. Phase 1の保全・編集経路A/B/Cを決定する。
2. 選択経路に必要な一回限りの環境・認証準備を人が行う。
3. 公開アプリを変更せず取得するか、複製先で往復再現性を確認する。
4. 差分テンプレートで公開アプリ由来ソースと既存GitHub v1.11を比較する。
5. 基準版をIssue #5で承認後、Phase 2の自動変更パイプラインへ進む。

## 未決・ギャップ

- Power Appsの保全・編集経路。ネイティブGit統合、CLI暫定、Studio自動操作から選択が必要。
- 本番列一覧、Dataverseテーブル名・型・ロール、実接続/委任設計は別途。
- TSVから正式XLSX出力への方式は未決。
- 帳票A3/A4等の正式用紙と実機改ページは未決。
- 通勤支給予定と認定簿共通サンプルの金額は未整合。テストデータ改修が必要。
- 認定ID選択UIは未実装。給与簿詳細はサンプル15項目で、本番の未知列は未収録。
- 簡易出力は全件TSVコピーと表示中5行の印刷。正式な全件XLSX出力ではない。
- モダンコントロールの提供状況・アクセシビリティ・PDF実験機能は環境で確認。
- 生成画像は概念図。省略項目と濃い見出しは要件・設計書で補正済み。
- 今回の配置モデル画像もStudioスクリーンショットではない。実機校正は未実施。
