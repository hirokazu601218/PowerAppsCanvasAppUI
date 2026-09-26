# PDF以外の残件対応 — v1.24

開始2026-09-18 06:35:22 UTC、停止期限07:35:22 UTC（再起算なし）。

公開済み：3モーダルのフォーカス復帰、件数ベースの一覧高さ、通常データ準備待ち、内蔵0/1/20/21/40件・長文負数。追加で基本情報の氏名・所属を1行＋全文Tooltipへ修正。

- Studio公式数式エラー0、当初9プロパティ＋追加Wrap2プロパティを読戻し照合。Screen1の657部品IDを維持。App.Formulas全文一致。
- 基盤単体50/50 PASS（20.060秒）。これは実アプリへの故障注入・復元演習の代用ではない。
- 公開Player手動：40件=20件×2ページ、TSV全40番号・26列、TSV閉鎖後フォーカス復帰を確認。
- 一括39ケース：[Actions run 35318861503](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35318861503)。結果：`{"status": "completed", "run": 35318861503, "conclusion": "failure", "passed": 36, "failed": 3, "total": 39, "failedCases": ["BOUNDARY-0: initial zero count leaves TSV enabled", "REMAIN-MODAL: visible-to-hidden race before disabled assertion; focus assertions not completed", "SUPPLEMENT-PERF: close p95 2111ms exceeds 1000ms"], "widths": "8 staff conditions and 5 screens x 4 widths passed", "artifact": 10536238440}`。
- 一括run開始後にWrap2項目を追加修正したため、一括結果は修正前v1.24候補の証跡。最終版の影響2欄は別途確認し、全ケースを最終版で再実行済みとはしない。
- PDF生成・保存・OS印刷は実施していない。Dataverse書込みなし。Issue #51未反映を継続。

95項目：{'PASS': 42, 'NOT_RUN': 35, 'FAIL': 2, 'EXCLUDED': 9, 'BLOCKED': 7}。詳細は[全件監査](spec-case-audit.md)。前回PASSの継承を含み、このWorkで95件すべてを実施した数ではない。

未完：全モーダルのTab/Shift+Tab閉じ込め、長文全8条件、全履歴統合照合、200%ブラウザー拡大、コントラストの全状態、実支援技術、承認済み画像差分、実複製での導入／再適用／復元／故障注入、スマホの報告閲覧。専用環境・人手評価・60分上限のため未完を維持。

## 工程別結果

| 工程 | 結果 | 証跡・理由 |
|---|---|---|
| 1 対象確定 | 成功 | PDF除外と95項目監査 |
| 2 不合格修正 | 一部成功 | フォーカス・起動待ち・一覧高さ反映。性能の判定はrun結果 |
| 3 条件整備・検証 | 一部成功 | 内蔵7条件。全前提・全95項目完了ではない |
| 4 公開・回帰・複数幅 | 公開成功／試験結果は上記 | 6画面、既存8条件と追加5画面×4幅を回帰対象に含む |
| 5 GitHub記録 | 成功 | PR #59、ソース読戻し・manifest・本記録 |
