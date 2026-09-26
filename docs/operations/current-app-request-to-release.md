# 現行単一アプリ：変更要求から公開・文書反映まで

> 現行App ID：`204a48dc-7f23-43dd-b934-4654a3cfa306`。ユーザーの改修・機能追加指示を変更要求、フロー実行指示を着手契機として扱う。ソース変更・公開がない文書整理には適用しない。

## 実行順と証跡

| 工程 | Codexの実施内容 | 必ず残すもの |
|---|---|---|
| 1. 要求を登録 | [変更要求](../changes/requests/README.md)に指示、対象要件ID、受入条件、対象App IDを記録。未決の業務判断を区別 | `docs/changes/requests/<変更ID>.json`、必要なら[未決一覧](../requirements/open-decisions.md) |
| 2. 構築と選定 | 対象部品の変更、影響確認、既存ケースの再利用またはコード追加。改修部品の単体を必須とし、影響する場合だけ結合を選ぶ | 変更ソース、同IDの[選定記録](../testing/change-records/README.md)、テストコード、静的検査結果 |
| 3. 試験・公開 | 隔離データで操作、Studio検査。現行の**同じ1アプリ**へ保存・公開し、版と接続を確認。失敗時は版・復旧状況を区別 | ソースコミット、対象環境・App ID、保存版と公開版、単体／結合結果、失敗・復旧記録 |
| 4. 公開版照合 | 公開Playerの変更箇所を操作し、PAC読戻しと公開メタデータを確認。旧値残留、他画面、帳票など影響範囲を再検査 | [公開後記録](../verification/templates/current-app-postpublish.example.json)の版、観察時刻、パッケージSHA-256、結果と残件 |
| 5. 文書反映 | **公開版と変更要求の差分を照合して**要件定義、基本設計、詳細設計を更新。結合対象なら[テスト実施要領](../testing/test-specification.md)のケース操作・独立期待値も更新。試験結果・不足・未確定を区別 | 変更IDと公開版識別時刻を含む3文書、必要時は結合ケース仕様・要件[対応表](../requirements/traceability-matrix.md)、実施記録 |
| 6. 再照合・報告 | [公開後文書照合Actions](../../.github/workflows/current-app-postpublish-docs.yml)を文書ブランチで実行。読戻しのSHA・版・ID、文書差分、選定済みの単体／結合E2Eを確認してから文書PRを統合し、同じWorkへ報告 | Actions run URL、文書PR、未実施・FAIL・BLOCKEDの区別と残件 |

現行の[テスト選定Actions](../../.github/workflows/current-app-test-gate.yml)は変更要求・選定記録・テストケースをPR上で照合する。PR作成時にE2Eが動いても、まだ反映していないソースを公開Playerで試した結果とはみなさない。公開後文書照合Actionsは、文書PRで変更した公開後記録の静的チェックに加え、公開後に**文書ブランチを指定して手動起動**する。記録した公開版のパッケージSHA-256と版を実環境で再確認し、[選定記録](../testing/change-records/README.md)のケースを再実行する。パッケージ読戻しとPlayerの観察は別の証拠である。失敗時は文書PRを完了扱いせず、結果を同じWorkへ報告する。branch protectionの必須チェック設定はこの手順の追加だけでは有効にならないため、Workが実行結果を確認してから統合する。

文書ブランチは公開に使用した`source_commit`と、文書編集前の`documentation_base_commit`を公開後記録に固定する。前者からアプリソース・試験選定・テストコードが変わっていないことと、後者から3文書と必要な結合ケース仕様が変更されたことを別々に検査する。読戻しで接続・権限・公開版との差異が出た場合は元の要求をPASSにせず原因を調べる。Actionsは差分、版、選定ケースの実行を機械的に確認できるが、文章の業務的な正しさやPlayerの人手観察の真偽は判定できない。Codexがソース、公開版、文書を内容まで照合し、ユーザーが業務受入を判断する。

## 現行の配布経路に関する制限

[旧配布ワークフロー](../../records/workflows/staff-master-transaction.yml)と`records/config/apps/staff-master.json`は別App ID `362ac991-eead-4f07-8373-afdb3ebfdba1`を向く。これらを現行アプリの公開・復元に起動しない。**本手順はCodexが対象アプリで構築・保存・公開した後の照合をActionsで自動化したもの**。現行App ID向けのpack/import/publish/restoreをActionsで自動実行可能とは宣言しない。単一アプリへ安全な自動配布を追加する場合は、接続、バックアップ、復旧、実機再照合を別途実証する。

総合テストの業務シナリオ・実施時期・仕様の範囲は[未決事項 D-07](../requirements/open-decisions.md)。決定まで[総合テスト計画](../testing/system-test-plan.md)は策定待ちとし、今回のケース再実行を総合テストPASSとしない。
