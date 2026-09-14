# Power Apps 完全無人テスト導入手順

## 1. 現在できていること

- 公開済み`TestApp`を対象にしたPlaywrightスモークテスト
- Microsoft公式`power-platform-playwright-samples`の固定版を利用
- GitHub Actionsの手動実行
- 成否、トレース、動画、失敗時スクリーンショットの30日保存
- 成功時スクリーンショットの保存
- GitHub Actions Run #7で、認証から結果判定まで全工程の合格を確認済み

テスト内容は次のとおり。

1. `TextInput1`へ`ChatGPT自動テスト成功`を入力
2. `Button1`を押す
3. `Text1`に`入力結果：ChatGPT自動テスト成功`が表示されることを確認

## 2. 初回疎通用の設定

GitHubの`Settings` → `Secrets and variables` → `Actions` → `Secrets`で次を登録する。

| Secret | 値 |
|---|---|
| `POWERAPPS_TEST_EMAIL` | テスト用Microsoft組織アカウント |
| `POWERAPPS_TEST_PASSWORD` | 同アカウントのパスワード |

パスワードはファイルやIssueへ記載しない。Actionsの暗号化Secretだけに登録する。

初期値はパスワード認証である。現在のテナントではこの方式による無人実行に成功している。パスワード変更、条件付きアクセス、MFAやSecurity Defaultsの変更後は認証が失敗する可能性があるため、その時点でテナントの方針に合う認証方式を再評価する。

## 3. 証明書認証へ切り替える場合

現在は設定不要。テナント側のポリシー変更などによりパスワード認証を継続できない場合だけ、Microsoft Entra ID側の対応方式と公式サンプルの対応状況を確認して切り替える。

### GitHub Variables

`Settings` → `Secrets and variables` → `Actions` → `Variables`で登録する。

| Variable | 値 |
|---|---|
| `POWERAPPS_AUTH_MODE` | `certificate` |
| `POWERAPPS_AUTH_PROVIDER` | `local-file` |

### GitHub Secrets

| Secret | 値 |
|---|---|
| `POWERAPPS_TEST_EMAIL` | 証明書を割り当てたテストユーザー |
| `POWERAPPS_TEST_CERT_BASE64` | PFXファイルをBase64化した文字列 |
| `POWERAPPS_TEST_CERT_PASSWORD` | PFXにパスワードを付けた場合のみ |

PFXはActions実行中だけ一時ファイルに復元され、成果物には含めない。

## 4. 実行方法

1. GitHubで`Actions`を開く
2. `Power Apps E2E`を選ぶ
3. `Run workflow`を押す
4. `TestApp smoke test`の結果を確認する
5. 実行画面の`Artifacts`から`powerapps-testapp-evidence-*`を取得する

## 5. 次段階

実アプリ用に次を追加済み。

- `.github/workflows/staff-master-e2e.yml`: 実アプリ専用の手動実行ワークフロー
- `e2e/staff-master-p0.test.ts`: `INIT-01`、`SRCH-02`、`ZERO-03`の最小P0テスト

実行前に、`src/staff-master/scrStaffMasterSearch_v1.11.paste.yaml`を別のCanvasアプリへ導入して公開する。公開後、GitHubのRepository Variable `POWERAPPS_STAFF_APP_URL`へWebリンクを登録し、`Staff Master E2E`を手動実行する。

このP0テストが安定して合格した後に、`docs/testing/test-specification.md`の残りを優先度順にPlaywrightへ移植する。検索、0件時の古い詳細消去、ページング、サイドバー開閉、職員詳細表示の順で広げる。定期実行は実アプリのP0合格後に追加する。

## 6. 参照

- Microsoft Learn: Power Platform Playwright samples overview
  - https://learn.microsoft.com/en-us/power-platform/developer/playwright-samples/overview
- Microsoft Learn: Authentication guide
  - https://learn.microsoft.com/en-us/power-platform/developer/playwright-samples/authentication-guide
- Microsoft Learn: CI/CD integration
  - https://learn.microsoft.com/en-us/power-platform/developer/playwright-samples/cicd
- 固定した公式サンプルのコミット
  - https://github.com/microsoft/power-platform-playwright-samples/commit/43e3db8d131aeb09415b1faef030e783fd2e320f
