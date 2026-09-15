# ステップ6：Canvas編集可能ソース再構成 実行結果

更新日：2026-09-15  
対象Issue：[Issue #5](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/5)  
対象PR：[PR #6](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/6)

## 1. 結論

ステップ6は合格した。GitHub上のactive Canvasソースからアプリを再構成し、隔離テスト環境へSolutionとして反映・公開した後、固定App IDを直接指定して再取得できた。再取得したactiveソースは投入元と完全一致し、専用テスト利用者によるP0回帰も合格した。

基準・本番アプリ、基準環境の公開状態、課金、接続、既存権限は変更していない。

## 2. 採用した再構成経路

1. Microsoft公式リポジトリ [PowerApps-Tooling](https://github.com/microsoft/PowerApps-Tooling) をコミット `aed72a37c3b10b08f81c9d2257d5c38da33dccbe` に固定する。
2. `Microsoft.PowerPlatform.PowerApps.Persistence` で基準 `.msapp` を展開する。
3. active `Src/*.pa.yaml` と非ソース部分を保持する `baseline.msapr` を分離する。
4. `baseline.msapr` とactiveソースから `LoadFromYaml=true` の `.msapp` を再構成する。
5. 再構成した `.msapp` をSolutionへ組み込み、`pac solution pack` でパックする。
6. GitHub OIDCで隔離Dataverse URLへ認証し、インポート・公開する。
7. 固定App IDを直接指定してアプリを再取得し、activeソースを照合する。
8. P0合格後にだけ、編集可能ソースをGitHubへ確定する。

非推奨の `pac canvas pack/unpack` は使用しない。

## 3. 最終結果

| 項目 | 結果 |
|---|---|
| 最終Actions | [run 34928950801](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34928950801) |
| 再構成ツールのビルド | 成功。警告0、エラー0 |
| activeソース抽出 | 成功 |
| ローカル再構成後ソース比較 | 完全一致 |
| `LoadFromYaml` | `true` を検証 |
| Solutionパック | 基準版・再構成版とも成功 |
| OIDC認証 | 隔離Dataverse URLへ成功 |
| インポート・公開 | 成功 |
| 固定App IDでの再取得 | 成功（`362ac991-eead-4f07-8373-afdb3ebfdba1`） |
| サーバー再取得後ソース比較 | 完全一致 |
| 共有権限 | 専用利用者の `CanView` を維持・読戻し確認 |
| P0 | 成功、`1 passed (20.0s)` |
| GitHub正本確定 | 成功、commit `ab1b7456ed8bc7d39cd302c1e23276b789212179` |
| 復元処理 | 最終成功runでは未発動 |

## 4. GitHubへ確定した編集可能ソース

- `powerapps/canvas-v3/Src/App.pa.yaml`
- `powerapps/canvas-v3/Src/Screen1.pa.yaml`
- `powerapps/canvas-v3/Src/_EditorState.pa.yaml`
- `powerapps/canvas-v3/baseline.msapr`

再構成ヘルパーは `tools/powerapps-source-reconstruct/`、自動ゲートは `.github/workflows/phase2-source-reconstruction.yml` に置く。

## 5. 試行履歴

| run | 結果 | 原因 | 新対応策・復元 |
|---:|---|---|---|
| 34928407934 | 失敗 | 初期workflow YAMLの改行エスケープ不備 | YAMLを修正。ジョブ未開始、環境変更なし |
| 34928530595 | 失敗 | 別の改行エスケープ不備 | 残る書式を修正。ジョブ未開始、環境変更なし |
| 34928581847 | 失敗 | PAC 2.12.2が `pac --version` を受け付けない | `dotnet tool list` へ変更。環境変更なし |
| 34928655007 | 失敗 | 元msapp内のバックスラッシュ区切りを汎用unzipで比較できない | 同じPersistenceパーサーで比較する方式へ変更。環境変更なし |
| 34928755228 | 失敗 | インポート・公開成功後、ID列を持たない `pac canvas list` 表をID検索して偽陰性 | 固定ID直接ダウンロードをID検証とした。隔離アプリは基準Solutionへ自動復元済み |
| 34928950801 | 合格 | なし | 全ゲート合格後のみ正本を確定 |

同じ対応策の単純反復は行わず、各原因に対して実質的に異なる対応策を使用した。

## 6. 証跡

| 種別 | artifact | ID | SHA-256 | 期限 |
|---|---|---:|---|---|
| 再構成・比較 | `step6-source-reconstruction-6` | 10381275802 | `ef3445d087d09669f24f698bd42d009128c3b51263e174c23701265e5aaa658a` | 2026-09-29 04:29:53 UTC |
| P0 | `phase1-5-target-evidence-6` | 10380538667 | `0ca6732ebac2693044bcc90aad6feea141050466e2c6a8f670f0de958c3c960a` | 2026-09-29 04:31:55 UTC |

Issue上の概要・結果とGitHubコミットは永久保存し、実行証跡は14日保持する。

## 7. 次のゲート

次はステップ7として、業務ロジックへ影響しない小さな表示変更をactive `pa.yaml` に加え、「修正→再構成→隔離公開→変更専用テスト→P0」を一周させる。変更内容と追加テストは実行前にユーザー承認を得る。
