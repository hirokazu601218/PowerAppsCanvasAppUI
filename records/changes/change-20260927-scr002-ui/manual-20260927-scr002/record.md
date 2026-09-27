# SCR-002変更要求・2026-09-27 実施記録

- 変更ID：`CHANGE-20260927-SCR002-UI`、対象環境：`68e00049-b7e5-eda6-9888-9a3cc493c5be`、同一App ID：`204a48dc-7f23-43dd-b934-4654a3cfa306`。
- 編集前：Studioの未公開保存版v21をダウンロードして画面定義を確認。旧公開版はv20。保存版と旧公開版の全ソース一致は確認できていない。
- 編集後：Studioで保存。ダウンロードした保存パッケージのSHA-256は`43423bbb872e05f61b1727a4d2f9e4418c2e8d1d7700ad6f0e0b5cfd810dca6d`。画面定義の差分は[変更箇所](../../../../src/screen-ui/v1.24/studio-readback/scr002-ui-20260927.delta.json)を参照。この値は**公開版のパッケージ読戻しSHAではない**。
- 公開：2026-09-27 12:01:08 JST、Studioの「Publish successful / is now available to everyone」を確認。Power Apps Playerで「古いバージョン」の表示から「最新の情報に更新」を実行し、同じApp IDを再読込み。Makerの版履歴でv22（2026-09-27 12:00:28）が「ライブ」と確認。公開版のパッケージSHAは未取得。
- 数式：StudioのApp checkerで数式エラー0件。アクセシビリティ251件・パフォーマンス11件を表示したが、この改修での増減は未比較。

| ケース | 確認方法 | 結果 | 範囲と残件 |
|---|---|---|---|
| `UT-SCR002-HEADER-001` | 編集プレビューと公開Playerでヘッダーを視認、変更定義を照合 | 手動PASS | ホーム左・SCR-002右、旧年月選択なし。自動ケースはGitHub未送信で未実行 |
| `UT-SCR002-HISTORY-001` | 所有者・011で勤務条件／通勤／社会保険／税固定控除を切替 | 手動PASS（単一履歴） | 長文カードなし、職員011の詳細表示。複数履歴の選択はNOT_RUN |
| `UT-SCR002-PAYROLL-001` | 所有者・011の給与簿を視認、1レコードと先頭行・青／白配色を確認 | 手動PASS（先頭表示） | 表示開始・終了月維持。163項目末尾、複数行、全データ値はNOT_RUN |
| `IT-SCR002-NAV-001` | 編集プレビューで011のSCR-002→SCR-005→SCR-002 | 手動PASS（編集プレビュー） | 公開Playerでの同じ往復と他所属制限はNOT_RUN |
| `IT-SCR002-HOME-001` | 編集プレビューでSCR-002ヘッダーのホーム→SCR-001 | 手動PASS（編集プレビュー） | 公開Playerでの同じ復路、未保存破棄確認はNOT_RUN |

試験コードは[選定記録](../../../../docs/testing/change-records/change-20260927-scr002-ui.json)に5件を登録。GitHub Actionsの単体・結合E2E、公開後パッケージSHA読戻し、版番号照合、文書照合ActionsはNOT_RUN。公開Player画像は作業環境の`scr002-published-20260927.png`、`scr002-published-payroll-20260927.png`。所有者以外・権限、複数履歴、163行末尾、保存エラーを合格としない。総合テストは未決のまま。

最初のGitHub送信は自動承認審査が送信先の確認を要求して停止した。2026-09-27 12:28 JSTに利用者が`hirokazu601218/PowerAppsCanvasAppUI`への送信とActions実行を承認し、同リポジトリの変更ブランチで続行する。Actionsの結果は各runで別途記録する。
