# Phase 1 公開アプリ基準版の保全・Git統合事前確認

> 対象アプリ：ハンドメイド専用

更新日: 2026-09-15  
状態: **判断待ち（P0基準確認は完了、ソース保全方式は未決）**  
追跡Issue: [#5](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/5)

## 1. 結論

公開済みテストアプリは既存P0回帰テストに再合格し、Phase 1開始時点の動作基準として確定できた。

ただし、現在のGitHubには画面YAMLと個別Power Fxはあるものの、公開アプリ全体を再構成できる完全なSolutionソースはない。公開アプリとGitHub v1.11が同一であることも、現時点では証明できない。

MicrosoftのPower Platform Git IntegrationをGitHubで使うには、GitHub Organization、Managed Environment、Azure Key Vault、Dataverse System Administrator、カスタムのアンマネージドSolution等が必要で、機能はプレビューである。現在の個人リポジトリをそのまま接続する構成ではないため、Phase 2着手前に保全・編集経路を選ぶ必要がある。

## 2. P0基準記録

| 項目 | 確定値 |
|---|---|
| アプリ名 | `ハンドメイド職員マスタ検索` |
| App ID | `0e5f5c05-b67d-4a27-af71-ebe5e5381221` |
| Environment ID | `2fa12587-ea8f-ee93-ac2f-054f6b7fe2bb` |
| 実行URL | `https://apps.powerapps.com/play/e/2fa12587-ea8f-ee93-ac2f-054f6b7fe2bb/a/0e5f5c05-b67d-4a27-af71-ebe5e5381221?tenantId=a00c92fa-e1db-4aa6-ab28-356c3203353d` |
| GitHub Actions run | [run #8 / attempt 3](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34910200078) |
| 開始 | 2026-09-15T01:26:17Z |
| 完了 | 2026-09-15T01:27:59Z |
| 結果 | success |
| Job ID | `104217469138` |
| 証跡 | [staff-master-evidence-8](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34910200078/artifacts/10376996512) |
| 証跡SHA-256 | `272346c033be48f252731bd9ea57fb261ebc4a923e8151d1d7266248884ed3a2` |
| 証跡失効予定 | 2026-09-29T01:27:52Z（14日保持） |
| 対象コミット | `db9c9c4b2110febd53f222187e077bf3fe16bdf0` |

### 合格したP0項目

1. アプリ起動
2. 初期表示25件
3. 「山田」検索2件
4. 山田花子の選択と詳細表示
5. 900×600表示時の主要領域、重なり、横スクロール
6. 条件クリア後25件へ復帰

## 3. 今回変更していないもの

この確認では、Power Appsの画面、Power Fx、公開状態、接続、環境設定、権限、認証ポリシーを変更していない。既存の成功ジョブを再実行し、GitHub上へ記録を追加しただけである。

## 4. 現在のGitHub格納状態

既存リポジトリには、少なくとも以下が格納されている。

- `src/staff-master/scrStaffMasterSearch_v1.11.pa.yaml`
- `src/staff-master/scrStaffMasterSearch_v1.11.paste.yaml`
- 個別の `.fx` ファイル
- E2EテストとGitHub Actionsワークフロー
- 要件、設計、運用文書

これらは画面・式の編集素材ではあるが、アプリ全体の構成、依存関係、コンポーネント、接続参照を含む完全なSolutionソースではない。したがって、現状をGitHub正本と確定することはできない。

## 5. Microsoft公式仕様から確認した制約

### Power Platform CLI

Microsoft公式の `pac canvas` リファレンスでは、`pac canvas pack` と `pac canvas unpack` は非推奨であり、ソース管理にはPower Platform Git Integrationの利用が案内されている。`pac canvas download` は `.msapp` の取得とディレクトリ展開を提供する。

- [pac canvas reference](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/canvas)

### Power Platform Git Integration

Git統合では、開発環境のアンマネージドSolutionをソース管理し、下流環境へManaged Solutionを配置する構成が案内されている。テスト・本番環境へGitを直接接続する運用は推奨されていない。

- [Git integration overview](https://learn.microsoft.com/en-us/power-platform/alm/git-integration/overview)

GitHub接続はプレビューで、少なくとも次の前提がある。

- GitHub Organizationの管理権限
- 開発・対象側のManaged Environment
- 同一テナントのAzure SubscriptionとAzure Key Vault
- Dataverse System Administrator
- カスタムのアンマネージドSolution
- GitHub App、秘密鍵、Key Vault、Power Platform接続の初期設定

- [Connect to GitHub (preview)](https://learn.microsoft.com/en-us/power-platform/alm/git-integration/connecting-to-github)

現在のリポジトリは個人アカウント `hirokazu601218` 配下であるため、この前提を満たすには組織・Azure・環境側の一回限りの構築が必要になる。

## 6. 保全経路の評価

| 選択肢 | 概要 | 利点 | 主な制約・リスク |
|---|---|---|---|
| A. ネイティブGit統合 | GitHub Organization等を準備し、開発環境のSolutionを接続 | Microsoft推奨の将来構成。Solution全体を正本化しやすい | プレビュー。組織、Managed Environment、Azure Key Vault等が必要 |
| B. CLI暫定経路 | `pac canvas download` で公開アプリを保全し、検証環境でpack/import往復を評価 | 現行アプリを取得して差分調査を始めやすい | pack/unpack非推奨。長期の正本方式には不適。往復再現性の実証が必要 |
| C. Studio操作経路 | GitHubで変更案を管理し、Power Apps Studioへの適用をブラウザ自動化 | GitHub Organization等を先に用意せず検証可能 | UI変化に弱い。CLI中心という当初方針から外れる |

## 7. 未実施と理由

次は未実施である。

- 公開アプリの `.msapp` ダウンロード
- Solutionへのアプリ追加
- Solution export/unpack
- Power Platform Git Integrationの接続
- サービスプリンシパル作成

公開アプリの変更を避けること、および専用サービスプリンシパル／Power Platform CLI認証プロファイルが未構成であることが理由である。環境・権限・接続の変更は承認範囲外なので自動作成していない。

## 8. Phase 2開始条件

次のすべてを満たすまでPhase 2の実装は開始しない。

1. A/B/Cの保全・編集経路を選択する。
2. 必要な一回限りの環境・認証準備を人が完了する。
3. 公開アプリを変更しない取得、または複製先での往復検証に成功する。
4. [基準版差分テンプレート](templates/powerapps-baseline-diff-template.md)で公開版とGitHub版を比較する。
5. 基準採用結果をIssue #5に記録する。
6. 次の成功版だけを `v1.12` として採番し、同名のGitタグを付ける。

