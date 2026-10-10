# PAY-HTML-002 CI配置修正

- 初回コミット: `23a8752dae9438424da7c12ad9cafc2a6e80c494`
- [初回アプリ選定CI](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/37978759967): FAIL。`selection record changed without an app source change`。
- HTML検査・文書配置検査はPASS。アプリE2EはSKIPPED、実アプリ操作なし。
- 原因: レビューHTML専用の実施済み検証記録を実アプリ専用の `docs/testing/change-records/` に配置した。
- 修正: 内容を変更せず `review-test-selection.json` として当実行記録へ移動。移行対照表へ記録した。参照元は存在しない。
- 既存アプリのCI、権限、テスト判定は変更しない。HTML46ページ・モデル・図・CSS・JSは初回コミットと同一。
- 再検証: 配置検査、アプリ選定の対象なし判定、レビュー単体・静的検査を確認。実機業務受入・アプリE2Eの合格を意味しない。
