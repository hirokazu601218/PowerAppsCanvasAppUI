# 通勤認定簿 公式様式の並行配置

状態：公開済み、変更範囲の実画面試験PASS、業務受入待ち。CHANGE-20261003-COMMUTE-OFFICIAL。

現行App ID 204a48dc-7f23-43dd-b934-4654a3cfa306、公開版 2026-10-03T18:31:30.4607518Z。
旧 crb3c_reports/commute-ledger-studio.html と通常ボタンは維持。新 new_reports/commute-ledger-official-v102.html を独立配置し、btnCertificateOfficial102「新様式（受入テスト）」を追加。

基本・詳細設計は docs/design/basic/basic-design.md と docs/design/detailed/detailed-design.md へ確定反映済み。受入手順は docs/acceptance/user-acceptance.md。SVG罫線と見出しは原PDFから抽出し、71表示値を重ねる。既存scriptは維持し、toolbarは版名だけ更新。

公式2ページ原寸、幅に応じた自動折返し、固定行高、枠超過時の表示・印刷停止。経路5〜8等の従来未取得欄は空欄。任意の行高拡張や業務計算追加はしない。

| 検証 | 結果 |
|---|---|
| 実体HTMLベース照合・既存script保持 | PASS |
| 全画面YAMLの新ボタン以外構造差分 | 0 |
| 公開版パッケージと新旧Webリソース読戻し | Actions37159201219 PASS |
| 新旧71欄一致・別タブ・2ページPDF・枠超過停止 | Actions37158642318 4件PASS |
| 静的様式比較 | 空欄＋架空6例の7ケース確認 |
| ユーザー業務受入・実機印刷設定 | 未実施 |
| 総合試験D-07・全データ組合せ | 後続、未実施 |

受入合格まで旧版を残し、切替・削除はユーザー指示後。基盤ゲート成功を業務受入合格へ転記しない。
