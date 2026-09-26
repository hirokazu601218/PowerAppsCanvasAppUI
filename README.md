# PowerAppsCanvasAppUI

職員マスタ検索の継続対象は App ID `204a48dc-7f23-43dd-b934-4654a3cfa306` の1件です。旧配布・復旧の自動化は現行アプリには適用しません。別環境のハンドメイドアプリも別件として管理します。

## 三つの配置区分

| 区分 | 場所 | 用途 |
|---|---|---|
| ① 実行に必要 | [`docs/`](docs/README.md) と現行ソース・設定・Actions | 変更要求、要件・基本／詳細設計、試験・受入、未決、現行運用・現行アプリのプログラム |
| ② 実行結果・履歴 | [`records/`](records/README.md) | 旧版資料、旧Actionsと設定、検証結果、公開後の実測・実行記録 |
| ③ 別件 | [`other/`](other/README.md) | ハンドメイド版、HTML試作、DADS参考資料など現行フローの対象外 |

画像の空様式は `assets/` に保持します。`records/` と `other/` は `assets/`、`docs/` と同階層です。①に属する実装は `.github/workflows/`、`config/`、`e2e/current-app/`、`powerapps/`、`scripts/`、`src/screen-ui/v1.24/`、`tests/` 等に置きます。`docs/` だけが①の全体ではありません。

作業入口は [AGENTS.md](AGENTS.md) → [運用方針§1](docs/operations/work-policy.md) → [現在のSTATUS](docs/handoff/STATUS.md) です。[配置・投稿規則](docs/operations/document-organization.md)に沿って作成・アップロードし、PRで `Document placement validation` を確認してください。[移動対照表](records/operations/migration/source-map.csv)で旧パスを検索できます。

現行アプリの公開・試験は[単一アプリ運用](docs/operations/single-app-workflow.md)に従います。過去の公開版説明・旧URL・旧手順は[移行前README](records/README-before-migration.md)と[実行記録](records/README.md)に残し、現行アプリの合格根拠に流用しません。
