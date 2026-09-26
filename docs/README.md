# ドキュメント分類一覧

> 対象アプリ：共通（自動テスト／ハンドメイド）

この一覧は、ファイルの配置を変えずに各Markdown文書の対象アプリを確認できるようにするための索引です。

## 対象アプリ

| 区分 | 環境 | アプリ | App ID・扱い |
|---|---|---|---|
| 職員マスタ検索（継続対象1件） | StaffMaster-Automation-Test | 自動開発_職員マスタ検索（旧_STUDIO_EDIT） | `204a48dc-7f23-43dd-b934-4654a3cfa306`。隔離STUDIOテーブルを参照 |
| 旧安定版（削除候補） | 同上 | 削除候補_自動開発_職員マスタ検索 | `362ac991-eead-4f07-8373-afdb3ebfdba1`。削除は未実施 |
| ハンドメイド専用（別環境） | 山下 浩和 の環境 | ハンドメイド職員マスタ検索 | `0e5f5c05-b67d-4a27-af71-ebe5e5381221`。今回の変更対象外 |

同じ検証環境の旧配布試験用を含むその他3アプリも「削除候補_」と表示する。[単一アプリ運用](operations/single-app-workflow.md)で各IDと停止条件を確認する。表示名の変更だけではGitHub上の旧App ID参照は変わらない。過去の実行記録は当時のIDと名称を保持する。

「共通」は、両アプリに適用する仕様・参考資料、またはハンドメイド版を基準に自動テスト版を構築・比較する文書を表します。以下は文書の目的別に分類し、各表の「対象アプリ」で適用範囲を示します。

## 1. 入口・索引

| サブ分類 | ドキュメント | タイトル | 対象アプリ | 概要 |
|---|---|---|---|---|
| 作業入口 | [AGENTS.md](../AGENTS.md) | 作業入口 | 共通 | 作業開始時に読む資料と参照順を定めた、AI・作業者向けの入口。 |
| リポジトリ案内 | [README.md](../README.md) | リポジトリ案内 | 共通 | リポジトリ全体の目的、正本、最新ソース、主要フォルダを案内するトップページ。 |
| 文書索引 | [docs/README.md](README.md) | ドキュメント分類一覧 | 共通 | 全Markdownの分類、対象アプリ、タイトル、概要をまとめた本索引。 |

## 2. アプリ要件・設計

| サブ分類 | ドキュメント | タイトル | 対象アプリ | 概要 |
|---|---|---|---|---|
| 要件定義 | [docs/requirements/requirements.md](requirements/requirements.md) | 要件定義書 | 共通 | 職員検索、履歴、帳票、出力、サイドバー、表示品質に関するアプリ要件。 |
| 基本設計 | [docs/design/basic-design.md](design/basic-design.md) | 基本設計書 | 共通 | 画面構成、配置、検索サイドバー、状態保持などの基本設計。 |
| 詳細設計 | [docs/design/detailed-design.md](design/detailed-design.md) | 詳細設計書 | 共通 | コントロール、データ契約、状態遷移、配置式、帳票・出力の詳細設計。 |
| UI・デザイン | [docs/design/design-system.md](design/design-system.md) | デザイン基準 | 共通 | 文字、色、余白、操作性、アクセシビリティに関するデザイン基準。 |

## 3. 導入・引継ぎ・変更管理

| サブ分類 | ドキュメント | タイトル | 対象アプリ | 概要 |
|---|---|---|---|---|
| 現在地 | [docs/handoff/STATUS.md](handoff/STATUS.md) | 現在地・作業状況 | 自動テスト専用 | 最新成功版、現在の作業、読取り対象、未決事項を示す現在地。 |
| 変更履歴 | [docs/handoff/CHANGELOG.md](handoff/CHANGELOG.md) | 変更履歴 | 共通 | アプリ、文書構成、運用ルールの版ごとの変更履歴。 |
| 導入手順 | [docs/handoff/install-v1.08.md](handoff/install-v1.08.md) | v1.08導入・検査手順 | 共通 | v1.08のStudio導入、内蔵テストデータ、操作確認、検査結果。 |
| 導入手順 | [docs/handoff/install-v1.11.md](handoff/install-v1.11.md) | v1.11導入・操作手順 | 共通 | v1.11のStudio導入・操作方法と、PDF・検査上の注意事項。 |

## 4. テスト・品質管理

| サブ分類 | ドキュメント | タイトル | 対象アプリ | 概要 |
|---|---|---|---|---|
| 全体計画 | [docs/testing/test-policy.md](testing/test-policy.md) | 全体テスト計画 | 現行単一アプリ | 単体・結合・総合・受入の区分、改修時の選定、リスク、合否。旧版は[履歴](testing/archive/test-policy-v1.00.md)。 |
| 実施要領 | [docs/testing/test-specification.md](testing/test-specification.md) | テスト実施要領・ケース仕様 | 現行プロファイル＋旧版履歴 | 現行ケースを先頭に、旧版ケースID・見出しも履歴として保持。 |
| 選定記録 | [docs/testing/change-records/README.md](testing/change-records/README.md) | 改修ごとの試験選定記録 | 現行単一アプリ | 変更部品、単体ケース、結合の影響判断とActionsのチェック対象。 |
| 業務受入 | [docs/testing/user-acceptance.md](testing/user-acceptance.md) | 受入テスト計画と結果 | 現行単一アプリ | ユーザーが確認する業務シナリオ、期待結果、受入結果を記録。 |
| 旧受入基準 | [docs/testing/acceptance.md](testing/acceptance.md) | テスト・レビュー基準 | 旧版履歴 | 旧T01～T14の索引。現行受入の結果ではない。 |
| 検査結果 | [docs/testing/RESULTS.md](testing/RESULTS.md) | 格納前検査結果 | 共通 | v1.08・v1.11のYAML、数式、配置、項目保持などの検査結果。 |
| 現行E2E運用 | [docs/testing/current-app-e2e.md](testing/current-app-e2e.md) | 現行アプリE2E運用 | 現行単一アプリ | 選定記録のActionsチェック、固定App IDでの読み取り専用E2Eと検証限界。 |
| E2E運用 | [docs/testing/unattended-e2e-setup.md](testing/unattended-e2e-setup.md) | 完全無人テスト運用手順 | ハンドメイド専用 | GitHub ActionsとPlaywrightによるハンドメイド版の無人E2E運用手順。 |

## 5. プロジェクト運用・差分管理

| サブ分類 | ドキュメント | タイトル | 対象アプリ | 概要 |
|---|---|---|---|---|
| Work運用 | [docs/operations/work-policy.md](operations/work-policy.md) | Work運用方針 | 共通 | ChatGPT Sol Workでの役割、実装手順、確認条件、検証方法を定めた運用正本。 |
| 画面変更の運用 | [docs/operations/single-app-workflow.md](operations/single-app-workflow.md) | 単一アプリ運用 | 職員マスタ検索 | 旧編集用アプリ1件で実装・試験・公開・ユーザー確認する順序と旧ID自動化の停止条件。 |
| 旧運用案 | [docs/operations/three-app-release-flow.md](operations/three-app-release-flow.md) | 3アプリ運用案（廃止） | 履歴 | 2026-09-25時点の案。現行手順には使わない。 |
| 差分管理 | [docs/operations/control-diff-policy.md](operations/control-diff-policy.md) | YAML差分配布方針 | 共通 | コントロール単位のYAML差分を安全に配布・適用する方針。 |
| 差分管理 | [src/staff-master/patches/README.md](../src/staff-master/patches/README.md) | 差分YAML案内 | 共通 | 差分YAMLの格納方法、適用単位、安全上の注意。 |
| 基準版比較 | [docs/operations/templates/powerapps-baseline-diff-template.md](operations/templates/powerapps-baseline-diff-template.md) | 基準版差分記録テンプレート | 共通 | 公開アプリ由来の基準版とGitHub版の差分を記録する様式。 |
| 資料管理 | [docs/operations/library-materials-index.md](operations/library-materials-index.md) | Library資料索引 | 共通 | ChatGPT Library内の関連資料の所在、用途、読取り条件の索引。 |

## 6. 無人開発・自動化基盤

| サブ分類 | ドキュメント | タイトル | 対象アプリ | 概要 |
|---|---|---|---|---|
| 要件・計画 | [docs/requirements/unattended-development-requirements.md](requirements/unattended-development-requirements.md) | 無人開発基盤要件定義書 | 共通 | 自然言語の指示から修正・展開・E2E・復元まで行う基盤の要件。 |
| 要件・計画 | [docs/operations/unattended-development-implementation-plan.md](operations/unattended-development-implementation-plan.md) | 無人開発基盤構築計画 | 共通 | 無人修正・テスト・公開基盤を段階的に構築する全体計画。 |
| 環境構築・実行記録 | [docs/operations/unattended-development-phase1-baseline.md](operations/unattended-development-phase1-baseline.md) | 公開アプリ基準版保全記録 | ハンドメイド専用 | ハンドメイド版のP0合格状態、保全方法、Git統合前の制約を記録。 |
| 環境構築・実行記録 | [docs/operations/unattended-development-phase1-5-execution-plan.md](operations/unattended-development-phase1-5-execution-plan.md) | Phase 1.5実行計画 | 共通 | CLIとGitHub OIDCによる暫定展開経路の構成、実行順、停止条件。 |
| 環境構築・実行記録 | [docs/operations/unattended-development-phase1-5-execution-record.md](operations/unattended-development-phase1-5-execution-record.md) | Phase 1.5実行記録 | 共通 | 認証、export、round-trip、隔離環境テストの実行記録。 |
| ソース再構成・自動展開 | [docs/operations/unattended-development-step6-source-reconstruction.md](operations/unattended-development-step6-source-reconstruction.md) | 編集可能ソース再構成結果 | 自動テスト専用 | 公開アプリから編集可能なCanvasソースを再構成した方法・結果・証跡。 |
| ソース再構成・自動展開 | [docs/operations/unattended-development-step7-automatic-source-deployment.md](operations/unattended-development-step7-automatic-source-deployment.md) | 自動反映・変更テスト結果 | 自動テスト専用 | GitHubソースの自動反映、変更テスト、失敗時復元を実証した結果。 |
| 運用・受入 | [docs/operations/unattended-development-step8-9-acceptance.md](operations/unattended-development-step8-9-acceptance.md) | 受入・成功版確定記録 | 自動テスト専用 | 自動化基盤の受入結果、成功版確定、運用開始範囲の記録。 |
| 運用・受入 | [docs/operations/staff-master-unattended-runbook.md](operations/staff-master-unattended-runbook.md) | 無人修正・テスト公開手順 | 自動テスト専用 | 修正指示から自動展開、E2E、成功版確定、失敗時復元までの実運用手順。 |

## 7. 参考・旧資料

| サブ分類 | ドキュメント | タイトル | 対象アプリ | 概要 |
|---|---|---|---|---|
| 参考資料案内 | [docs/reference/README.md](reference/README.md) | 参考資料案内 | 共通 | 現行仕様ではない旧HTML設計・旧デザイン資料の位置付けと注意事項。 |
| 旧デザイン基準 | [docs/reference/DADS_PowerApps_デザイン基準_v1.01.md](reference/DADS_PowerApps_デザイン基準_v1.01.md) | DADSベースデザイン基準 | 共通 | DADSをPower Apps向けに変換した旧デザイン基準。 |
| UI評価 | [docs/reference/HTML_v0.808_UI評価と改良提案_v1.01.md](reference/HTML_v0.808_UI評価と改良提案_v1.01.md) | HTML版UI評価・改良提案 | 共通 | HTML版v0.808のUI評価とPower Apps化に向けた改善案。 |
| 旧HTML設計 | [docs/reference/html-v0.807-basic.md](reference/html-v0.807-basic.md) | 旧HTML版基本設計書 | 共通 | 旧HTML版v0.807の外部データ、画面、機能、業務フローの基本設計。 |
| 旧HTML設計 | [docs/reference/html-v0.807-detailed.md](reference/html-v0.807-detailed.md) | 旧HTML版詳細設計書 | 共通 | 旧HTML版v0.807のデータ解析、関数、Excel出力、帳票連携の詳細設計。 |
| 旧部品 | [src/reference/README.md](../src/reference/README.md) | 旧DADS部品案内 | 共通 | 旧DADSスタイル確認画面、トークン、共通部品の位置付け。 |
