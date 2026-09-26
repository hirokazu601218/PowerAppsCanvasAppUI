# 現行単一アプリのE2E運用

> 対象App ID: `204a48dc-7f23-43dd-b934-4654a3cfa306`／環境ID: `68e00049-b7e5-eda6-9888-9a3cc493c5be`

## 範囲と実行

- [.github/workflows/current-app-test-gate.yml](../../.github/workflows/current-app-test-gate.yml)：PRの差分と[試験選定記録](change-records/README.md)を検証。アプリソース変更がある場合は単体ケースと必要な結合ケースを選び、同じPRのE2Eジョブで公開Playerを読み取り専用で操作する。
- [e2e/current-app/navigation.test.ts](../../e2e/current-app/navigation.test.ts)：単体 `UT-HOME-001`（ホームの職員マスタ検索ボタンと部門内一覧）、結合 `IT-HOME-DETAIL-001`（一覧で選択した架空職員の詳細への受渡し）。アプリソース変更のないテスト基盤変更と手動実行では、この2ケースを対象とする。
- [e2e/current-app/search.test.ts](../../e2e/current-app/search.test.ts)：単体 `UT-SRCH-001`（検索入力・実結果）、結合 `IT-SRCH-DETAIL-001`（絞り込んだ結果から詳細への受渡し）。検索部品を改修する場合などに選ぶ。2026-09-26時点で[現行Playerの検索不一致](current-app-search-observation.md)を検出しており、合格済みとは扱わない。未改修の検索ケースを全PRで毎回実行する運用にはしない。
- 新規の改修部品が既存ケースで検証できないときは、新たなケースとコードを追加する。workflow_dispatchは固定の現行アプリでホーム・一覧・詳細の2ケースを実行する。旧版のスタッフP0ワークフローは変更しない。

既存のGitHub Actions用テストアカウントのsecretsと、Power Appsの閲覧権限が前提。対象URLは固定環境IDとApp IDから組み立て、旧App IDやリポジトリ変数による上書きを拒否する。認証状態、動画、traceをartifactへ格納しない。失敗時のスクリーンショットも公開artifactにしない。テストは登録・更新・削除、ソリューション取込み、公開、復元を実施しない。

## 判定の境界

Actionsの「選定記録チェック」成功は記入形式・パス・ケースの参照確認。Codexが影響範囲を確認し、テスト結果と公開版の対応を別途レビューする。E2EのPASSは公開Playerの指定ケースの結果であり、GitHub候補ソースが公開版へ反映された証明ではない。公開版読戻しができない場合は候補ソースの受入を保留する。総合テスト・業務受入は別に判定する。

branch protection/rulesetでチェックを必須に設定しない限り、CIの失敗だけでPRマージは阻止できない。現時点の稼働結果はActionsのrun URLを確認してから記録する。設定・テストコードの追加だけでE2E合格と記載しない。
