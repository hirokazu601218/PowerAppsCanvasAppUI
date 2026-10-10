# DOT-001 検証・引継ぎ記録

開始2026-10-10 10:22:53 UTC。ZIPの事実確認時点09:44:53 UTCとWorkの着手時点を区別。

- main：252abe4aa5d3b1d99a584a30c97d9b48153c91f5。実装：fba65fdaefcf3b70821d7831ce86a4262ea4a214。
- PR135 head：c1008452348fd27448742796069647584278dca6。PR136 head：38362c8cf7ded201b1d185eeaccf2892f40c5f51（引継ぎ後更新あり）。
- 子ブランチに両依存を取り込み、STATUSの唯一の競合は両追記を保持して解消。既存head・main・PR baseを変更しない。文書編集前B：d74a4986a46f94fa93f474f7c35efd638e420098。
- 候補パッチ2件・対象3文書：before SHA-256一致とgit apply --check PASS。FR-G-01/03とIF-01を確認し外部手続／xlsx表現を訂正。SD-06は再適用しない。

## 証拠区分

| 区分 | 確認範囲／状態 |
|---|---|
| 確定仕様 | A承認、給与10月7日・人給10月8日決定を維持 |
| ソース保存 | S‴一致、ソース・要求・選定・試験コードは今回変更しない |
| アプリ公開 | 引継ぎLive38観測、Workでの再確認なし |
| 公式Export | 同梱published38-source-summary.jsonの比較。PAC Hの代用不可 |
| Player実測 | 同梱player38-sanitized.json。Tab5/5・24/24×2・表示復帰。focus／AX制限あり |
| 自動試験 | 選定15とPR選定19は別。今回実機E2E未実施 |
| P/H | 未取得。readback安全性確認済みだが実行画面未サインイン |
| 最終照合 | 前提P/H不足により未実施。postpublish JSON未作成 |
| 次候補002～004 | 未適用・未公開。今回適用なし |

## フロー・CI事前確認

current-app-postpublish-docs.ymlのreadback_only=trueはmetadata前後読取り、PAC download、固定App/Ready/前後一致と旧v25 SHA guard。rawパッケージをartifactへ保存せずアプリ・Dataverse・flow・権限の変更なし。guard不一致を弱めない。今回runは未実施なので新しいFAIL/PASSは記録しない。

文書C後のfull reconciliationはP/H不足で起動しない。PRの配置・レビュー静的検査とselectionは読取り検査。子PRのbaseは実装ブランチのためアプリsource差分なし、E2E選定は空。workflow変更なし。

## 残課題

正式P/H、公開後最終照合、選定E2E、focus完全表示・履歴AX、Issue #51、D-07、制度式・実効認可・外部保存契約を維持。文書更新の完了を開発全体の完了としない。表示の実描画・iPhone実機は今回未実施。

## ローカル検査結果

- レビューHTML：46ページ・2,316相対リンクPASS。生成一致PASS。
- 要件HTML：16ファイル生成一致PASS。iPhone版62資料・2,098,237 bytes再生成一致・内部参照確認PASS。
- 既存review単体15件、governance3件PASS。
- 試験選定：source_paths/test_files/case_idsすべて空（文書差分）。実機E2Eは未実施。
- 配置検査初回FAIL：record.jsonのchange_idがディレクトリ名dot-001と大文字小文字不一致。メタデータをdot-001に修正し、利用者依頼ID DOT-001をrequest_idとして保持。検査条件は変更しない。
- 新規実描画、クリック実測、iPhone実機は未実施。

## GitHub保存・CI読戻し

Draft PR #137。文書編集前B=d74a4986a46f94fa93f474f7c35efd638e420098、文書出典D=6064ca820553511e1d52b19f896a063213eb88c8、生成物C=72f7fb56dab560c0fadc89a03be5f9d0bbcb3242。Cのtree 74818c8630363cb66f9059f02dba8e91115e169dはローカルと一致。アプリsource・要求・選定・実機試験コードの差分0。

- [配置CI](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/38045453079)：SUCCESS。
- [HTML CI](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/38045453047)：SUCCESS。
- [選定CI](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/38045453051)：SUCCESS。実機E2E対象なし。
- 要件HTMLの追加検査：467相対リンク・出典SHA一致PASS。
- 作業開始は利用者時刻2026-10-10 19:22:53 JSTからUTC換算して記録。初稿の15:22 UTCは誤記であり訂正した。
