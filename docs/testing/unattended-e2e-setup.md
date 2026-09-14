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

> 公開保留：以下の互換スクリプトは暫定版。確認済みなのは文字列変換の実行だけで、Studioでのコンパイル・動作確認は未完了。生成物を検証なしで公開しない。

実アプリ用に次を追加済み。

- `.github/workflows/staff-master-e2e.yml`: 実アプリ専用の手動実行ワークフロー
- `e2e/staff-master-p0.test.ts`: `INIT-01`、`SRCH-02`、`ZERO-03`の最小P0テスト
- `tools/patch-v111-studio-compat.mjs`: v1.11を現行Studioへ貼り付ける前の互換修正

現行Studioではv1.11原本に、Galleryの`.Items`参照8か所と`SetFocus` 8個の式エラーが出ることを実機で確認した。次のコマンドで互換修正版を生成する。スクリプトは想定した出現件数と一致しない原本には適用せず停止する。

```bash
node tools/patch-v111-studio-compat.mjs \
  src/staff-master/scrStaffMasterSearch_v1.11.paste.yaml \
  src/staff-master/scrStaffMasterSearch_v1.11.studio-compat.paste.yaml
```

Power Appsには下書き`職員マスタ検索_自動テスト_v1_11`（App ID: `0e5f5c05-b67d-4a27-af71-ebe5e5381221`）を作成済み。この下書きには途中の手修正が含まれ、最新の式エラー一覧は再取得が必要。暫定生成物の一括再取込みはまだ行わない。

### 暫定スクリプトの既知の問題と公開条件

- `SetFocus(...)`を`Set(varFocusCompat111,true)`へ置換しても、元のフォーカス移動は再現されない。モーダル表示時と終了時のキーボードフォーカスを維持する修正が必要。
- `galStaff111.Height`の置換式は全検索結果件数を使用しており、2ページ目の残件数を反映しない。25件なら2ページ目は5行分になることを確認する。
- 他Galleryの`AllItems`への置換は、読み込まれた行数と高さの依存関係を実機で検証する。
- App checkerの式エラー0件だけでなく、初期25件、山田検索2件、検索後のサイドバー閉鎖、条件クリア、20件＋5件のページング、モーダルのフォーカス移動を確認してから公開する。
- クラウドブラウザのタブ取得がタイムアウトしており、取込み・公開・実アプリE2E実行は未完了。認証エラーとは確認されていないため、Secret再登録やMFA無効化は行わない。

公開後、GitHubのRepository Variable `POWERAPPS_STAFF_APP_URL`へWebリンクを登録し、`Staff Master E2E`を手動実行する。

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
