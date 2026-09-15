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
| 基準環境ロール | System Customizer（1件のみ） |
| OIDC疎通 | 成功。run `34921452887` |
| 基準Solution手動export | 成功。Canvasアプリ本体SHA-256 `c127cc4a2e076476572c894b4e081a9280f7213600687b5092ed296f89a9a65c` |

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
- 基準環境の専用アプリユーザーはSystem Customizerのまま保持。
- 失敗PRは閉じ、作業ブランチは原因分析用に保持する。

## 5. 次の候補

最小権限を維持する候補は、基準環境のDataverse URLを直接指定し、環境IDからの管理API解決を避けること。Microsoft公式CLIは `--environment` に環境IDまたは絶対HTTPS URLを受け付ける。

この候補は停止条件到達後の追加試行になるため、自動実行せず、ユーザーの新しい承認を待つ。Power Platform管理者ロールへの権限拡大は推奨しない。
