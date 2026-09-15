# ステップ8～9 受入・成功版確定記録

更新：2026-09-15。指示と承認：[Issue #7](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/7)。構築PR：[PR #6](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/6)。

## ステップ8：合格

[run 34952452993 / attempt 2](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/34952452993) が成功した。実装commitは `190554a284eb7911e1a4200310bb6cd2efc18190`。

| 試行 | 変更確認 | 既存P0 | 結果 |
|---|---|---|---|
| repair-defect | 期待どおり不合格 | 合格 | 意図的誤表示を検出。成功処理へ進まない |
| repair-success | 合格 | 合格 | 期待値を変えずに承認済み表示へ自動修復 |
| stop-defect-1 | 期待どおり不合格 | 合格 | 対応策1を実行・記録 |
| stop-defect-2 | 期待どおり不合格 | 合格 | 対応策2を実行し同一原因を確認 |
| 停止・復元 | 元表示で合格 | 合格 | 既試行の再使用を拒否し、合格版を再公開 |

各試行でビルド、Dataverse URL直接指定OIDC、隔離インポート、明示的公開、サーバー側ソースと実行ルールの読戻しを通過した。復元先は `260819a4fa30c4d8c8dcd02acc626c26d7823697`。09:38:54 UTCに復元後P0合格を記録した。

停止試験の原因指紋は `a0acab7bc29a1edffd336e9cce1d98500fe2b9971836ede7fbb5a0f6bafa1f56`。対応策は名称でなく実際の編集内容のハッシュで識別した。新対応策があれば継続し、既試行しか残っていない場合に `STOPPED` へ遷移する。

[PR #8](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/8) は停止後の記録・終了を検証する記録用PRとして、復元結果を追記後、未統合で閉じた。`automation/acceptance-stop-7` ブランチは保持する。実アプリの不合格と復元は上記runで実行した。

初回attempt 1はGitHub実行マシンの取得に5回失敗し、ステップ0件で未開始のまま終了した。アプリ変更はなく、基盤障害として記録後に一度再投入した。アプリ修復回数に算入していない。

## 受入シナリオの証拠区分

| ID | 検証方法 | 状態 |
|---|---|---|
| BAS-01 正常変更→main・タグ | v1.12候補の実環境テストと成功確定 | ステップ9で実行 |
| BAS-02 自動修復 | 実環境で誤表示→修復→両テスト成功 | 合格 |
| BAS-03 停止・復元・PR終了 | 実環境で同一原因・異なる対応策・重複拒否・復元P0、記録用PR終了 | 合格 |
| BAS-04 認証失敗 | 配布コマンドを代替したオフライン試験でBLOCKED、未配布・未復元 | ローカル合格、候補CIでも実行 |
| BAS-05 承認範囲違反 | 実データ構造の対象・変更前後値・記載外差分の拒否試験 | 合格 |
| BAS-06 P0のみ失敗 | 不完全ゲートを拒否し、オフラインのランナー試験で復元を確認 | ローカル合格、候補CIでも実行 |
| BAS-07 追加テストのみ失敗 | 上記repair-defect/stop-defectの実環境結果 | 合格 |
| BAS-08 復元失敗 | オフラインの実制御フローでRESTORE_FAILEDとなり再配布しないことを確認 | ローカル合格、候補CIでも実行 |

認証を実際に壊したり、実環境で復元不能な障害を作る試験は行わない。オフライン試験を実環境合格と表記しない。

## ステップ9：候補検証へ進行

候補表示は `v1.12 ／ B案・架空25名`。成功採番とタグ付与は、候補の全ゲート合格とmainの内容一致を確認してから行う。候補の成功前にv1.12タグを作らない。

`staff-master-finalize.yml` が候補SHA、mainとのツリー一致、最新run、artifact、固定App ID、公開状態、Solutionハッシュを照合し、タグ注釈へ永久保存用の受領記録を作成する。成功結果はIssue #7とタグに追記される。

## 証跡と運用範囲

- 受入artifact：`staff-master-transaction-34952452993-2` / ID `10390581175`。
- 保持期限：2026-09-29 09:38:55 UTC。GitHub報告のZIP SHA-256：`b77970ad2684f5c242e680f72b2e14d1f30229126c0009438a8f19a8d9f80b39`。
- 期限なしの試行記録：[step8-acceptance.json](../../automation/evidence/step8-acceptance.json)、Issue #7。
- [運用手順](staff-master-unattended-runbook.md)：指示・承認、修復、停止、タグ採番、復元、認証エラー、証跡保持。
- 対応範囲は既存コントロールの既存プロパティに対する承認済み変更。新規構造や接続、任意のPower Fxの一般コンパイルは対象外として検査で停止する。
