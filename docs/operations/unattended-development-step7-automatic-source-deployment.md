# ステップ7 実行結果 — GitHubソース自動反映・変更テスト・復元

更新日：2026-09-15  
状態：**完了**  
対象Issue：[Issue #5](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/5)  
対象PR：[PR #6](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/6)

## 1. 承認範囲

隔離テストアプリ `362ac991-eead-4f07-8373-afdb3ebfdba1` のヘッダー表示だけを、一時的に次へ変更した。

- 変更前：`v1.11 ／ B案・架空25名`
- 一時表示：`v1.11 ／ 自動反映テスト中`
- 変更専用テストと既存P0の合格後、元表示へ復元する。
- 基準・本番アプリ、接続、権限、課金は変更しない。
- テスト専用変更のため、v1.12採番・タグ・main統合は行わない。

## 2. 最終結果

| ゲート | 結果 | 証跡 |
|---|---|---|
| GitHub activeソースからmsapp/Solution再構成 | 合格 | [run 34934912204](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34934912204) |
| Dataverse URL直接指定OIDC認証・隔離環境反映・明示的公開 | 合格 | 同run |
| 公開後の固定App IDとサーバー側実行ルール読戻し | 合格 | 同run |
| 一時表示の変更専用Playwrightテスト | 合格 | 同run |
| 変更版の既存P0 | 合格 | 同run |
| 元表示へのソース復元・再公開 | 合格 | [run 34935420385](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34935420385) |
| 復元版の既存P0 | 合格 | 同run |
| 失敗時の隔離アプリ自動復元 | 合格 | run 34931347700、34932982126、34934212145 |
| 基準・本番アプリへの変更 | なし | 対象環境・App ID固定 |

一時表示はrun `34934912204` で確認後、commit `260819a4fa30c4d8c8dcd02acc626c26d7823697` で元へ戻した。現在の隔離アプリは復元版であり、P0合格済みである。

## 3. 試行と新対応策

| run | 判定 | 原因 | 新対応策・安全結果 |
|---:|---|---|---|
| [34931347700](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34931347700) | 不合格 | `.pa.yaml` はサーバーへ保存されたが公開プレイヤーは旧表示 | Power Apps Publish App APIを追加。隔離アプリを自動復元 |
| [34932294037](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34932294037) | 不合格 | Publish App API版 `2016-11-01` が非対応 | `2018-10-01` へ更新。基準・本番は未変更 |
| [34932564310](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34932564310) | 不合格 | 公開後の時刻が必ず進むという判定仮定が誤り | `lastDraftVersion == lastPublishTime` かつ `Ready` へ修正。隔離アプリを復元 |
| [34932982126](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34932982126) | 不合格 | 最新URLでも旧表示。実行用 `Controls/*.json` が旧ルールのまま | 配信キャッシュではなくコンパイル境界と特定。隔離アプリを復元 |
| [34933626895](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34933626895) / [34933780562](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34933780562) | 診断合格 | PAC再パック各方式でも実行用ルールが更新されない | activeソースとコンパイル済みルールを同時検証する限定ブリッジを設計 |
| [34934040875](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34934040875) | デプロイ前停止 | 標準ランナーに `rg` がない | 依存追加をせず標準 `grep` へ変更。Power Appsは未変更 |
| [34934212145](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34934212145) | 不合格 | コンパイル済みルールを同期しても `LoadFromYaml=true` で実行時に採用されない | 隔離アプリを自動復元。次試行で読込みモードとサーバー側ルール検査を追加 |
| [34934912204](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34934912204) | 合格 | なし | 承認対象だけを同期し `LoadFromYaml=false`、サーバー側ルール一致後に変更専用テスト＋P0合格 |
| [34935420385](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34935420385) | 合格 | なし | 一時変更と有効マーカーを同一コミットで除去し、元表示を再公開、P0再合格 |

同じ対応策の単純反復は行わず、各失敗後に未試行で実質的に異なる対応策だけを適用した。

## 4. 実装した安全策

- 対象環境、Solution、App ID、利用者を固定する。
- 一時変更マーカーがある時だけ実行時同期を有効にする。
- activeソースの変更後値が1件、対象コントロール `lblMeta111` が1件、`Text` の変更前値が1件であることをデプロイ前に照合する。
- 公開後にサーバーから同じ固定App IDを再取得し、activeソースと実行用ルールを再照合する。
- 変更専用テストまたはP0不合格時は直前の基準Solutionを隔離アプリへ自動復元する。
- 証跡は14日保持し、概要と試行履歴はIssueへ永久保存する。

## 5. 証跡

| 対象 | artifact | ID | 保持期限（UTC） |
|---|---|---:|---|
| 変更版の再構成 | `step6-source-reconstruction-13` | 10382398248 | 2026-09-29 06:00:46 |
| 変更専用テスト＋P0 | `phase1-5-target-evidence-13` | 10383136592 | 2026-09-29 06:03:06 |
| 復元版の再構成 | `step6-source-reconstruction-14` | 10382428589 | 2026-09-29 06:07:10 |
| 復元後P0 | `phase1-5-target-evidence-14` | 10382753247 | 2026-09-29 06:09:29 |

ダウンロード確認時のP0成果物ZIP SHA-256は、変更版 `52556728615950c29e721d3e25f366313fcfa611d17c8c2975f9b12531d01419`、復元版 `fb3cda8dd57a43033e08b3da08c0599a014a009112c79663d6c1d99d2be44a27` である。

## 6. 技術上の境界と次段階

現在のMicrosoft Persistence経路は、外部編集したactive `.pa.yaml` から実行用ルールを自動再コンパイルしない。ステップ7では承認済みの単一Text変更に限定し、変更前後値を厳格に検証してコンパイル済みルールと読込みモードを同期した。

したがって、ステップ7は「限定された承認変更の無人反映・テスト・復元」の実証完了であり、任意のPower Fx変更を汎用変換できる状態ではない。ステップ8で変更マニフェスト、原因指紋、試行台帳、自動修復ループへ汎用化する。
