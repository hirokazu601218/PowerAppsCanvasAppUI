# Power Apps 完全無人テスト導入手順

## 1. 現在できていること

- 公開済み`TestApp`を対象にしたPlaywrightスモークテスト
- Microsoft公式`power-platform-playwright-samples`の固定版を利用
- GitHub Actionsの手動実行
- 成否、トレース、動画、失敗時スクリーンショットの30日保存
- 成功時スクリーンショットの保存

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

初期値はパスワード認証である。テナントのMFAやSecurity Defaultsにより、無人ログインが拒否される場合がある。この場合もMFAを無効化せず、次節の証明書方式へ切り替える。

## 3. 完全無人化用の証明書設定

Microsoft公式がCI/CD向けに推奨する証明書認証を使用する。Microsoft Entra ID側でテストユーザーの証明書ベース認証を構成した後、PFXをGitHub ActionsのSecretへ登録する。

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

最小スモークテストが安定して合格した後に、`docs/testing/test-specification.md`の95ケースを優先度順にPlaywrightへ移植する。最初は検索、サイドバー開閉、検索後の自動閉鎖、職員詳細表示を対象とする。

## 6. 参照

- Microsoft Learn: Power Platform Playwright samples overview
  - https://learn.microsoft.com/en-us/power-platform/developer/playwright-samples/overview
- Microsoft Learn: Authentication guide
  - https://learn.microsoft.com/en-us/power-platform/developer/playwright-samples/authentication-guide
- Microsoft Learn: CI/CD integration
  - https://learn.microsoft.com/en-us/power-platform/developer/playwright-samples/cicd
- 固定した公式サンプルのコミット
  - https://github.com/microsoft/power-platform-playwright-samples/commit/43e3db8d131aeb09415b1faef030e783fd2e320f
