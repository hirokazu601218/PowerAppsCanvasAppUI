# ドキュメント分類一覧

> 対象アプリ：共通（自動テスト／ハンドメイド）

この一覧は、ファイルの配置を変えずに各Markdown文書の対象アプリを確認できるようにするための索引です。

## 対象アプリ

| 区分 | 環境 | 環境ID | アプリ | アプリID |
|---|---|---|---|---|
| 自動テスト専用 | StaffMaster-Automation-Test | `68e00049-b7e5-eda6-9888-9a3cc493c5be` | 職員マスタ検索_自動テスト_v1_11 | `362ac991-eead-4f07-8373-afdb3ebfdba1` |
| ハンドメイド専用 | 山下 浩和 の環境 | `2fa12587-ea8f-ee93-ac2f-054f6b7fe2bb` | ハンドメイド職員マスタ検索 | `0e5f5c05-b67d-4a27-af71-ebe5e5381221` |

「共通」は、両アプリに適用する仕様・参考資料、またはハンドメイド版を基準に自動テスト版を構築・比較する文書を表します。

## 共通（自動テスト／ハンドメイド）

| ドキュメント | タイトル | 概要 |
|---|---|---|
| [AGENTS.md](../AGENTS.md) | 作業入口 | 作業開始時に読む資料と参照順を定めた、AI・作業者向けの入口。 |
| [README.md](../README.md) | リポジトリ案内 | リポジトリ全体の目的、正本、最新ソース、主要フォルダを案内するトップページ。 |
| [docs/README.md](README.md) | ドキュメント分類一覧 | 対象アプリの識別情報と、全Markdownの対象区分・概要をまとめた本索引。 |
| [docs/design/basic-design.md](design/basic-design.md) | 基本設計書 | 画面構成、配置、検索サイドバー、状態保持などの基本設計。 |
| [docs/design/design-system.md](design/design-system.md) | B案デザイン基準 | B案の文字、色、余白、操作性、アクセシビリティに関するデザイン基準。 |
| [docs/design/detailed-design.md](design/detailed-design.md) | 詳細設計書 | コントロール、データ契約、状態遷移、配置式、帳票・出力を定めた詳細設計。 |
| [docs/handoff/CHANGELOG.md](handoff/CHANGELOG.md) | 変更履歴 | アプリ、文書構成、運用ルールの版ごとの変更履歴。 |
| [docs/handoff/install-v1.08.md](handoff/install-v1.08.md) | v1.08導入・検査手順 | v1.08のStudio導入方法、内蔵テストデータ、操作確認、検査結果。 |
| [docs/handoff/install-v1.11.md](handoff/install-v1.11.md) | v1.11導入・操作手順 | v1.11のStudio導入・操作手順と、デザイン・PDF・検査上の注意事項。 |
| [docs/operations/control-diff-policy.md](operations/control-diff-policy.md) | YAML差分配布方針 | v1.12以降にコントロール単位のYAML差分を安全に配布・適用する方針。 |
| [docs/operations/library-materials-index.md](operations/library-materials-index.md) | Library資料索引 | ChatGPT Libraryに保管する関連資料の所在、用途、読取り条件の索引。 |
| [docs/operations/templates/powerapps-baseline-diff-template.md](operations/templates/powerapps-baseline-diff-template.md) | 基準版差分記録テンプレート | 公開アプリ由来の基準版とGitHub版の構造・数式・動作差分を記録する様式。 |
| [docs/operations/unattended-development-implementation-plan.md](operations/unattended-development-implementation-plan.md) | 無人開発基盤構築計画 | 無人修正・テスト・公開基盤を段階的に構築する全体計画と役割分担。 |
| [docs/operations/unattended-development-phase1-5-execution-plan.md](operations/unattended-development-phase1-5-execution-plan.md) | Phase 1.5実行計画 | CLIとGitHub OIDCによる暫定展開経路の構成、実行順、停止条件を定めた計画。 |
| [docs/operations/unattended-development-phase1-5-execution-record.md](operations/unattended-development-phase1-5-execution-record.md) | Phase 1.5実行記録 | Phase 1.5で行った認証、export、round-trip、隔離環境テストの実行記録。 |
| [docs/operations/work-policy.md](operations/work-policy.md) | Work運用方針 | ChatGPT Sol Workでの役割、実装手順、確認条件、検証方法を定めた運用正本。 |
| [docs/reference/DADS_PowerApps_デザイン基準_v1.01.md](reference/DADS_PowerApps_デザイン基準_v1.01.md) | DADSベースデザイン基準 | DADSをPower Apps向けに変換した、色・文字・部品・アクセシビリティ等の旧基準。 |
| [docs/reference/HTML_v0.808_UI評価と改良提案_v1.01.md](reference/HTML_v0.808_UI評価と改良提案_v1.01.md) | HTML版UI評価・改良提案 | HTML版v0.808のUIを評価し、Power Apps化に向けた改善案を整理した参考資料。 |
| [docs/reference/README.md](reference/README.md) | 参考資料案内 | 現行仕様ではない旧HTML設計・旧デザイン資料の位置付けと参照上の注意。 |
| [docs/reference/html-v0.807-basic.md](reference/html-v0.807-basic.md) | 旧HTML版基本設計書 | 旧HTML版v0.807の利用者、外部データ、画面、機能、業務フローの基本設計。 |
| [docs/reference/html-v0.807-detailed.md](reference/html-v0.807-detailed.md) | 旧HTML版詳細設計書 | 旧HTML版v0.807のデータ解析、関数、表示、Excel出力、帳票連携の詳細設計。 |
| [docs/requirements/requirements.md](requirements/requirements.md) | 要件定義書 | 職員検索、履歴、帳票、出力、サイドバー、表示品質に関するアプリ要件。 |
| [docs/requirements/unattended-development-requirements.md](requirements/unattended-development-requirements.md) | 無人開発基盤要件定義書 | 自然言語の指示から修正・展開・E2E・復元まで行う無人開発基盤の要件。 |
| [docs/testing/RESULTS.md](testing/RESULTS.md) | 格納前検査結果 | v1.08・v1.11のYAML、数式、配置、項目保持などの格納前検査結果。 |
| [docs/testing/acceptance.md](testing/acceptance.md) | テスト・レビュー基準 | 要件R01～R14に対応する受入観点と旧テスト手順の索引。 |
| [docs/testing/test-policy.md](testing/test-policy.md) | テスト方針 | テストの対象、実施時期、テスト層、合否基準、証跡を定めた方針。 |
| [docs/testing/test-specification.md](testing/test-specification.md) | テスト仕様書 | テストデータ、環境、操作、期待値、判定方法をケース単位で定めた詳細仕様。 |
| [src/reference/README.md](../src/reference/README.md) | 旧DADS部品案内 | 旧DADSスタイル確認画面・トークン・共通部品の位置付けを説明する案内。 |
| [src/staff-master/patches/README.md](../src/staff-master/patches/README.md) | 差分YAML案内 | v1.11を基準とする差分YAMLの格納方法、適用単位、安全上の注意。 |

## 自動テスト専用

| ドキュメント | タイトル | 概要 |
|---|---|---|
| [docs/handoff/STATUS.md](handoff/STATUS.md) | 現在地・作業状況 | 最新成功版、現在の作業、読取り対象、未決事項を示す自動テスト版の現在地。 |
| [docs/operations/staff-master-unattended-runbook.md](operations/staff-master-unattended-runbook.md) | 無人修正・テスト公開手順 | 修正指示から自動展開、E2E、成功版確定、失敗時復元までの実運用手順。 |
| [docs/operations/unattended-development-step6-source-reconstruction.md](operations/unattended-development-step6-source-reconstruction.md) | 編集可能ソース再構成結果 | 公開アプリから編集可能なCanvasソースを再構成した方法・結果・証跡。 |
| [docs/operations/unattended-development-step7-automatic-source-deployment.md](operations/unattended-development-step7-automatic-source-deployment.md) | 自動反映・変更テスト結果 | GitHubソースの自動反映、変更テスト、失敗時復元を実証した結果。 |
| [docs/operations/unattended-development-step8-9-acceptance.md](operations/unattended-development-step8-9-acceptance.md) | 受入・成功版確定記録 | 自動化基盤の受入結果、成功版確定、運用開始範囲をまとめた記録。 |

## ハンドメイド専用

| ドキュメント | タイトル | 概要 |
|---|---|---|
| [docs/operations/unattended-development-phase1-baseline.md](operations/unattended-development-phase1-baseline.md) | 公開アプリ基準版保全記録 | 公開済みハンドメイド版のP0合格状態、保全方法、Git統合前の制約を記録。 |
| [docs/testing/unattended-e2e-setup.md](testing/unattended-e2e-setup.md) | 完全無人テスト運用手順 | ハンドメイド版を毎日検査するGitHub Actions＋Playwrightの無人E2E運用手順。 |
