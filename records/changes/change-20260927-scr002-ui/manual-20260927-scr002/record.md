# SCR-002変更要求・2026-09-27 実施記録

- 変更ID：`CHANGE-20260927-SCR002-UI`、対象環境：`68e00049-b7e5-eda6-9888-9a3cc493c5be`、同一App ID：`204a48dc-7f23-43dd-b934-4654a3cfa306`。
- 編集前：Studioの未公開保存版v21をダウンロードして画面定義を確認。旧公開版はv20。保存版と旧公開版の全ソース一致は確認できていない。
- 編集後：Studioで保存。ダウンロードした保存パッケージのSHA-256は`43423bbb872e05f61b1727a4d2f9e4418c2e8d1d7700ad6f0e0b5cfd810dca6d`。画面定義の差分は[変更箇所](../../../../src/screen-ui/v1.24/studio-readback/scr002-ui-20260927.delta.json)を参照。この値は**公開版のパッケージ読戻しSHAではない**。
- 公開：2026-09-27 12:01:08 JST、Studioの「Publish successful / is now available to everyone」を確認。Power Apps Playerで「古いバージョン」の表示から「最新の情報に更新」を実行し、同じApp IDを再読込み。Makerの版履歴でv22（2026-09-27 12:00:28）が「ライブ」と確認。公開版のパッケージSHAは未取得。
- 数式：StudioのApp checkerで数式エラー0件。アクセシビリティ251件・パフォーマンス11件を表示したが、この改修での増減は未比較。

| ケース | 確認方法 | 結果 | 範囲と残件 |
|---|---|---|---|
| `UT-SCR002-HEADER-001` | 編集プレビュー・公開Playerの視認と専用利用者のE2E | 手動／自動PASS | ホーム左・SCR-002右、旧年月選択なし。狭幅での重なりは別途確認 |
| `UT-SCR002-HISTORY-001` | 所有者・011と専用利用者で勤務条件／通勤／社会保険／税固定控除を切替 | 手動／自動PASS（単一履歴） | 長文カードなし、職員011の詳細表示。複数履歴の選択はNOT_RUN |
| `UT-SCR002-PAYROLL-001` | 所有者・011の視認と専用利用者の件数・先頭行E2E | 手動／自動PASS（先頭表示） | 開始・終了月維持。青／白配色は手動視認。163項目末尾、複数行、全データ値はNOT_RUN |
| `IT-SCR002-NAV-001` | 所有者の公開Playerと専用利用者のE2Eで011のSCR-002→SCR-005→SCR-002 | 手動／自動PASS | 同一職員番号で復帰。対象月保持、他所属制限は別ケースで未確認 |
| `IT-SCR002-HOME-001` | 編集プレビューと専用利用者のE2EでSCR-002ヘッダーのホーム→SCR-001 | 手動／自動PASS | 公開PlayerのSCR-001を確認。未保存破棄確認はNOT_RUN |

試験コードは[選定記録](../../../../docs/testing/change-records/change-20260927-scr002-ui.json)に5件を登録。専用利用者の[Actions run 36293464353](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36293464353)は選定・認証・単体3件・結合2件がすべてPASS（2026-09-27 13:11 JST、コミット`9ec937c842c82260a154f8794bfebad5bddb8060`）。[文書配置](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36293464363)と[公開後照合の静的チェック](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36293464474)もPASS。後者はPRの文書検査であり、PAC読戻しではない。

最初の[run 36291762746](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36291762746)では結合ケースだけFAIL（4/5）。原因はテストの正規表現が半角スペースを固定し、SCR-005の全角スペース入り職員表示に一致しなかったこと。所有者の公開Playerで旧式0件／空白可変式1件を確認し、職員番号011と氏名の一致条件を保って試験コードを修正した。再実行は5/5 PASS。失敗を公開アプリの不具合や権限のPASSへ読み替えない。

公開Player画像は作業環境の`scr002-published-20260927.png`、`scr002-published-payroll-20260927.png`。公開後のパッケージSHA・公開メタデータ時刻の読戻しと文書照合Actionの手動起動はNOT_RUN。全163項目末尾、複数履歴、他所属権限、保存エラーを合格としない。総合テストは未決のまま。

最初のGitHub送信は自動承認審査が送信先の確認を要求して停止した。2026-09-27 12:28 JSTに利用者が`hirokazu601218/PowerAppsCanvasAppUI`への送信とActions実行を承認。[PR #87](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/87)は公開版パッケージ・文書の照合が未了のためdraftのままであり、mainへの統合は未実施。手動起動に必要なGitHubブラウザ認証がこのWorkで完了しておらず、本人による認証操作が中断されたので再試行していない。
