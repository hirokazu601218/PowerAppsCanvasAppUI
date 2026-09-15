# Phase 1.5 実行記録 — CLI暫定経路とGitHub OIDC

更新日: 2026-09-15  
状態: **URL直接指定の無変更展開成功／P0共有待ち**  
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
| 基準環境ロール | System Customizer（専用サービスプリンシパルのみ） |
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

## 4. 初回停止時点の影響と復元

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
| ソース環境権限追加 | 専用サービスプリンシパルへSystem Customizerを付与 |

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

## 7. 再開後の継続規則

ユーザー指示により、同一原因が2回連続しても、承認範囲内に未試行の実質的に異なる対応策がある場合は続行する。同じ対応策の単純反復は禁止し、新対応策がない場合または承認範囲の拡大が必要な場合に停止する。

## 8. Dataverse URL直接指定での再開結果

| 試行 | Run | 対応策 | 結果 |
|---|---|---|---|
| URL直接配布 | [34922824319](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34922824319) | 基準・隔離テストの両方をDataverse URLで直接指定。Canvas再packを無変更配布経路から分離 | 成功 |
| App ID取得 | [34923097678](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34923097678) | 隔離テストDataverse Web APIをOIDCで照会 | 成功 |
| 隔離環境P0 | [34923187435](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34923187435) | 取得したApp IDで既存P0を実行 | アプリ未共有のため失敗 |

URL直接配布runでは、基準環境OIDC認証、Solution `StaffMasterAutomation` 版 `1.11.0.0` の自動export、隔離テスト環境OIDC認証、同一パッケージのimport・publish、SolutionとCanvasアプリの存在確認がすべて成功した。

| 項目 | 確定値 |
|---|---|
| 基準Dataverse URL | `https://org24a2c22d.crm7.dynamics.com/` |
| テストDataverse URL | `https://orge762dd9e.crm7.dynamics.com/` |
| テスト環境ID | `68e00049-b7e5-eda6-9888-9a3cc493c5be` |
| テストApp ID | `362ac991-eead-4f07-8373-afdb3ebfdba1` |
| export SHA-256 | `6091481d9f665cd10fad62c550fc163a81e76f834510201f9ba676b55c93ab39` |
| 証跡保持 | 14日 |

P0の認証処理自体は成功したが、実行画面は「Request access」を表示した。専用テスト利用者へ隔離テストアプリのCanView共有が必要である。これは権限変更のため、実行直前の承認待ちとする。基準アプリの画面、Power Fx、接続、公開状態、共有設定は変更していない。
