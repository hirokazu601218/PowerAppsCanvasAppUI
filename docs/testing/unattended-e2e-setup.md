# Power Apps 完全無人テスト運用手順

## 1. 完了状態

職員マスタ検索アプリの無人E2Eテスト環境は構築済み。

- 対象アプリ: `職員マスタ検索_自動テスト_v1_11`
- App ID: `0e5f5c05-b67d-4a27-af71-ebe5e5381221`
- 環境ID: `2fa12587-ea8f-ee93-ac2f-054f6b7fe2bb`
- 実行基盤: GitHub Actions + Microsoft Power Platform Playwright samples
- テストユーザー: `powerapps-test@govaca.onmicrosoft.com`
- 権限: アプリ利用者（管理者・共同所有者ではない）
- 実行時刻: 毎日03:00（日本時間）
- 証跡保存: 14日
- 料金: 公開リポジトリのGitHub標準ランナーを使用

2026-09-15に、専用ユーザーの無人認証からUI操作、結果判定、証跡保存まで全工程の成功を確認した。

- 成功した再実行: https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34906474076
- 定期実行設定後の成功確認: https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34907785873

## 2. 自動テスト内容

`e2e/staff-master-p0.test.ts`は、dynabookでの利用を想定した1366×768で次を確認する。

1. 公開アプリを開く
2. 「非常勤職員マスタ検索」が表示される
3. 初期状態が「職員一覧 25件」である
4. 「山田 太郎」が表示される
5. 検索欄へ「山田」を入力して検索する
6. 「職員一覧 2件」になる
7. 「山田 太郎」と「山田 花子」が表示される
8. 検索条件をクリアする
9. 「職員一覧 25件」へ戻る
10. スクリーンショット、動画、トレース、テスト結果を保存する

## 3. 自動実行条件

`.github/workflows/staff-master-e2e.yml`は次の場合に起動する。

| 条件 | 動作 |
|---|---|
| 毎日03:00（日本時間） | 定期実行 |
| GitHub ActionsのRun workflow | 手動実行 |
| `e2e/staff-master-p0.test.ts`の変更 | 自動実行 |
| `.github/workflows/staff-master-e2e.yml`の変更 | 自動実行 |

実行結果はGitHubの `Actions` → `Staff Master E2E` で確認する。証跡は各実行結果の `Artifacts` に `staff-master-evidence-*` として保存される。

## 4. 結果通知

定時実行、Run workflow、テスト設定変更による実行が完了すると、次の固定Issueへ結果を自動追記する。

- 通知先: https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/4
- 通知項目: 実行種別、完了日時、総合結果、認証結果、P0テスト結果、実行詳細
- 成功時: スクリーンショット成果物への直接リンクを表示
- 認証失敗などで成果物がない場合: 「成果物なし」と表示

Issueはリポジトリ所有者へ割り当て済み。GitHub側の通知設定に従い、Web・メール・モバイル通知で確認する。

## 5. 認証情報

GitHubの `Settings` → `Secrets and variables` → `Actions` → `Secrets` に次を登録する。

| Secret | 値 |
|---|---|
| `POWERAPPS_TEST_EMAIL` | `powerapps-test@govaca.onmicrosoft.com` |
| `POWERAPPS_TEST_PASSWORD` | 専用ユーザーの現在のパスワード |

パスワードは認証ステップだけに渡される。npmの依存関係導入、ビルド、UIテストには渡されない。ワークフローは専用ユーザー以外のメールアドレスが設定された場合に停止する。

パスワード変更、MFA、Security Defaults、条件付きアクセスの変更により無人認証が失敗した場合は、セキュリティ設定を緩和せず認証方式を再評価する。

## 6. アプリ更新時

1. Power Apps Studioで保存する
2. 「公開」→「このバージョンの公開」を実行する
3. GitHubの `Actions` → `Staff Master E2E` → `Run workflow` で確認する

アプリを公開しただけではGitHub Actionsは即時起動しない。翌日03:00の定期実行を待つか、手動実行する。

## 7. 関連ファイル

- `.github/workflows/staff-master-e2e.yml`: 実行条件、認証、証跡保存
- `e2e/staff-master-p0.test.ts`: P0テスト
- `docs/testing/test-policy.md`: テスト方針
- `docs/testing/test-specification.md`: テスト仕様
- `docs/testing/unattended-e2e-setup.md`: 本書
