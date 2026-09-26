# 現行フローに必要な文書

対象は継続利用する App ID `204a48dc-7f23-43dd-b934-4654a3cfa306` です。ここには「今後の変更要求・設計・試験・受入で読む文書」だけを置きます。過去の結果は [`records/`](../records/README.md)、別件は [`other/`](../other/README.md) に分けます。

| 文書群 | 役割・入口 |
|---|---|
| [変更要求](changes/requests/README.md) | ユーザーの改修依頼・受入条件・固定App ID。改修単位でJSONを追加 |
| [要件・未決](requirements/requirements.md) | 要件定義、[画面要件](requirements/screen-requirements.md)、[非機能](requirements/non-functional-requirements.md)、[未決一覧](requirements/open-decisions.md)、[追跡表](requirements/traceability-matrix.md) |
| [基本設計](design/basic-design.md)・[詳細設計](design/detailed-design.md) | 画面・データ・Power Fxの設計。デザイン基準とDataverse設計もここ |
| [試験計画](testing/test-policy.md)・[試験仕様](testing/test-specification.md) | 単体、結合、総合と現行E2E。改修ごとの[試験選定](testing/change-records/README.md)とテンプレート |
| [受入](acceptance/user-acceptance.md) | 業務受入条件とユーザー確認 |
| [運用](operations/work-policy.md) | 作業規則、[単一アプリ手順](operations/single-app-workflow.md)、[変更から公開後まで](operations/current-app-request-to-release.md)、[配置規則](operations/document-organization.md) |
| [STATUS](handoff/STATUS.md) | 現在の作業・参照対象・未完了。過去の時系列は記録へ移管 |

現行のソース、E2E、Actions、配置ポリシーは `docs/` の外にもあります。新規の `docs/` は[許可リスト](../config/document-routing.json)または改修単位の許可パターンで検査します。必要な新種類の文書は同じPRで許可リスト・配置規則を更新してください。実行結果を `docs/` に置かないでください。ただし公開後チェックの入力となる小さな確認用JSONは運用上の①に残し、詳細な出力は②に保存します。
