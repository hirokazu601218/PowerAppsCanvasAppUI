# Phase 1.5 実行記録 — CLI暫定経路とGitHub OIDC

更新日: 2026-09-15  
状態: **自動停止（同一原因2回）**  
対象Issue: [#5](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/5)  
対象PR: [#6](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/6)

## 1. 完了した構築

| 項目 | 結果 |
|---|---|
| 基準Solution | `StaffMasterAutomation`、表示名「職員マスタ自動化」、版 `1.11.0.0` |
| 基準アプリ | `職員マスタ検索_自動テスト_v1_11` をSolutionへ追加 |
| 専用テスト環境 | `StaffMaster-Automation-Test` |
| テスト環境ID | `68e00049-b7e5-eda6-9888-9a3cc493c5be` |
| テストDataverse URL | `https://orge762dd9e.crm7.dynamics.com/` |
| Entraアプリ | `PowerAppsCanvasAppUI-Automation` |
| Application ID | `1c94f011-c447-4af1-968f-ec564f489395` |
| GitHub OIDC | `powerapps-test` Environmentに限定して作成 |
| Client Secret | 0件 |
| テスト環境ロール | System Administrator（隔離テスト環境のみ） |
| 基準環境ロール | 未付与。基準環境の権限は変更していない |
| OIDC疎通 | 成功。run `34921452887` |
| 基準Solution手動export | 成功。`StaffMasterAutomation_1_11_0_0.zip`、SHA-256 `08ba313f78030c96541c7aa359ac402de34fab044fbb27d29ce97009f4d155ed` |

## 2. 自動export試行

| 試行 | Run | 変更 | 結果 |
|---|---|---|---|
| 1 | [34921838271](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34921838271) | 基準環境IDでOIDC認証し、`pac org who` 後にexport | 失敗 |
| 2 | [34921903514](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34921903514) | 管理API確認を減らし、`pac solution list --environment <ID>` へ変更 | 同一原因で失敗 |

## 3. 同一原因の判定

- テストケースID: `P15-BASELINE-EXPORT`
- 失敗工程: 基準環境へのPAC CLI接続確認
- 正規化エラー: サービスプリンシパルが `Microsoft.BusinessAppPlatform/scopes/admin/environments?$expand=permissions` へアクセスできない
- 判定: **同一原因2回連続**

OIDCトークン発行とアプリ認証は両試行とも成功した。失敗は、環境IDを対象Dataverseへ解決する過程でPAC CLIがPower Platform管理APIの環境一覧を参照したことによる。

## 4. 影響と復元

- 基準アプリの画面、Power Fx、接続、公開状態は未変更。
- 基準Solutionの自動exportは未完了。
- テスト環境へのSolution import・publishは未実行。
- テストアプリは作成されていない。
- 変更対象がないため、合格版への復元操作は不要。
- 基準環境には専用アプリユーザー／追加ロールを作成していない。
- 失敗PRは閉じ、作業ブランチは原因分析用に保持する。

## 5. 承認後の再開結果

ユーザーの新しい承認後、基準SolutionパッケージをGitHubへ保全し、PAC CLIでSolution全体とCanvasソースを展開した。

| 項目 | 結果 |
|---|---|
| GitHub正本 | `powerapps/solution-src` と `powerapps/canvas-src` |
| Canvas編集対象 | `powerapps/canvas-src/Src/App.fx.yaml`、`Screen1.fx.yaml` |
| 完全再構成データ | `powerapps/canvas-src` 全体 |
| Canvas埋込み先 | `powerapps/solution-src/CanvasApps/crb3c_v111_99a38_DocumentUri.msapp` |
| 生成エラー数 | `CanvasManifest.json` 上で parser 0、binding 0 |
| ソース環境権限追加 | なし |

## 6. 無変更round-trip試行

| 試行 | Run | 変更 | 結果 |
|---|---|---|---|
| 準備 | [34922299417](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34922299417) | round-tripワークフロー初版 | `pac --version` が非対応。Canvas処理前に停止 |
| 1 | [34922400570](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34922400570) | SourceCode形式で無変更pack | `System.FormatException` |
| 2 | [34922496534](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34922496534) | 元control JSONを使う `--disable-load-from-yaml` を追加 | 同じ `System.FormatException` |

- テストケースID: `P15-ROUNDTRIP-PACK`
- 失敗工程: `pac canvas pack`
- CLI版: `Microsoft.PowerApps.CLI.Tool 2.12.2`
- 正規化エラー: `System.FormatException`
- 判定: **同一原因2回連続**
- Solution import、テスト環境公開、P0は未実行
- テスト環境は変更されていないため、直前合格版への復元は不要

OIDC単体確認も、PACの環境一覧API参照が同一原因で2回続いたため自動停止した。OIDCトークン交換自体は成功しており、Client Secretは作成していない。

## 7. 停止後の扱い

- PR #6を閉じる。
- `automation/phase1-baseline` ブランチは原因分析用に保持する。
- 証跡artifactは14日保持し、本記録とIssue #5の概要・結果は恒久保存する。
- 次の候補は、テスト環境のPower Apps Studioで基準アプリを一度開いて保存しSourceCodeを検証済みにする方法、またはPAC CLI 2.12.2のFormatExceptionを回避できる別CLI版／Studio UI経路。
- 停止後の追加試行になるため、次工程は新しい修正方針を提示し、ユーザー承認後に開始する。
