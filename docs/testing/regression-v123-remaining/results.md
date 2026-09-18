# v1.23 回帰残件の実施結果

2026-09-18。開始05:26:19 UTC、停止期限06:26:19 UTC。ユーザーの「残件を実施して」により再開。公開アプリはv1.23のまま、基準mainは`fbe62315b51830dbffca4f21671fc9ebdef596ba`。今回の変更は試験・証跡・引継ぎであり、新しいアプリ版の公開はしていない。

**TEST-PDF-001を解消。33自動ケースの最新観測は31 PASS / 2 FAIL。全残件完了ではない。** 全29件実行後、追加4件と影響ケースを対象再実行した集計であり、「同じrunで33件すべて合格」ではない。[ケース別JSON](final-results.json)に各runと試験SHAを対応付けた。95仕様ケースは38 PASS / 4 FAIL / 21 BLOCKED / 32 NOT_RUN（部分実施を含む）。[全件監査](spec-case-audit.md)を参照。

## 工程結果

|工程|結果|根拠・例外|
|---|---|---|
|1 PDF試験修正・実PDF検査|成功|旧状態ラベルと旧戻るボタンへの依存を除き、現行Viewerと閉じる/再表示を検証。実PDF2枚を取得・解析・描画。|
|2 実行可能な未実施項目|一部失敗|基本9項目×5名、勤務/保険/税、帳票69×6、複合検索、キーボード巡回、コピー拒否などを追加。フォーカス・性能試験で不合格。|
|3 公開版全回帰・複数幅|一部失敗|全29件＋対象14件＋コピー拒否1件の結果を統合。既存8表示条件×5往復、追加5画面×4幅は合格。|
|4 GitHub記録|成功|試験コード、95項目監査、PDF/画像/ハッシュ/試験ログを保存。Issue #54継続、#56/#57へ不合格を分離。|

## 実行履歴

|Actions run|範囲|結果|診断|
|---|---|---|---|
|[35311175084](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35311175084)|PDF 1件|0 PASS / 1 FAIL|削除済みの戻るボタン待機を検出し修正。|
|[35311508834](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35311508834)|PDFと追加4件|3 PASS / 2 FAIL|実PDF成功。通勤方式の陽性fixture不一致とフォーカス問題を検出。|
|[35312153742](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35312153742)|当時の全29件|19 PASS / 10 FAIL|実PDF/69項目×6/基本・履歴/追加画面等PASS。検索クリア同期1、レイアウト描画同期8、フォーカス1で失敗。|
|[35312778650](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35312778650)|追加試験予定|認証前提BLOCKED|公式認証処理がログイン画面で終了。E2E未実行。認証設定を変更せず、後続runは認証成功。|
|[35312872559](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35312872559)|追加4件＋フォーカス|2 PASS / 3 FAIL|3リロードとTab巡回PASS。閉p95超過、フォーカス、コピー通知の検索スコープ不一致。|
|[35312985549](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35312985549)|影響14件|11 PASS / 3 FAIL|描画・クリア完了待ちで8幅条件と検索がPASS。フォーカス/コピー通知/連続再起動後一覧タイムアウト。|
|[35313676573](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35313676573)|コピー拒否1件|1 PASS|拒否注入を先に検証し、通知をPlayer/App両フレームから検出。拒否1回、手動TSV8行。|

全run終了済み。最終workflowは自動push起動を外して記録用とし、手動実行は全33ケースを対象とする。今回起算の期限ガードを保持しており、次のWorkで再実行する際はそのWorkの開始時刻を設定する。失敗ケースを除外して成功扱いにする設定ではない。元runの部分選択と現在の全件コマンドは区別する。

## 実PDFと見た目

- [実生成PDF](evidence/ledger-A4-landscape.pdf)：421,567 bytes、2ページ、各841.89×595.28 pt（A4横）。SHA256 `13a789bcfd8591852326325f87229fc4d74b0f317232bbdbb12e40a0f7a0ccec`。
- Power AppsのネイティブPDF()出力を取得。HTML印刷による代替ではない。生成時の画面倍率は200%、印刷用紙寸法は倍率に影響されない。
- 文字抽出で`009900000011`、`試験同姓同名`、`03会計課`を照合。操作ボタン/ホーム/検索文字は混入しない。
- [1枚目](evidence/ledger-rendered-1.png)と[2枚目](evidence/ledger-rendered-2.png)を96dpiで描画し実画像を確認。両ページ非白紙、順序維持、黒いViewerや操作バーの混入なし。
- 埋込み空様式との枠比較は最大約0.97px、外枠差最大1px（1mm=約3.78px）。[検査JSON](evidence/pdf-visual-check.json)、再現スクリプト`tests/check_pdf_frames.py`。初回の二値化行閾値は2枚目のアンチエイリアスで罫線1本を誤検出したため、灰色濃度の積分重心で確認。**全69差込位置の許容差や正式用紙承認まで認定するものではない。PDF-02はNOT_RUNを維持。**
- Popplerは`Restoring state when no valid states to pop`を2回警告した。終了コード0で描画・文字抽出は成功したが、全PDF処理系での互換性保証とはしない。
- PDF/PNGのみを認証済みActionsログに複写し、公式ログ取得で復元。バイト数・SHA256一致を[manifest](evidence/manifest.json)へ記録。認証データや任意の通信データは収集・保存していない。

## 追加照合と画面幅

- 基本9項目×003/004/011/012/025、勤務・保険・税の全セル/見出し/順序/ヘッダー位置を独立fixtureと照合。
- 通勤6レコードの帳票69項目、給与163項目の既存全照合を再実施。日付・和暦・金額・空経路・同姓同名の番号分離を含む。
- 3条件AND、数値・通勤方式・正式所属名検索、0件時の詳細消去、文字14→16→14pxと選択保持、サイドバー360→48pxと詳細328px拡張を確認。
- 職員画面：1366×768/1920×1080 × 標準/大 × 開/閉の8条件で各5往復。初期状態と各操作の描画幅が期待値に到達してから採寸し、累積ずれを確認。
- 追加5画面：900×600、1100×800、1366×768、1920×1080の20表示でボタン到達・重なり・配置を検査。全画像の人手受入やブラウザ200%拡大の代替ではない。
- サイドバー閉鎖中のTab全巡回、再展開後入力到達、3回リロード時の検索/選択/帳票解除を検証。実PDF生成後の新規セッション再起動は未網羅。
- コピー拒否はブラウザのClipboard.writeTextにNotAllowedErrorを注入。1回の拒否・エラー通知・手動TSV保持を確認。通知はPlayer側にも出るためiframe限定の検索を修正。許可復旧後のクリップボード実値検査は別残件。

## 不合格と再開位置

1. [Issue #56 BUG-FOCUS-001](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/56)：認定簿・給与詳細・出力の閉じる後、5秒待機しても起点ボタンへフォーカスが戻らない。背景遮蔽と対象職員保持は合格。`SetFocus(btnCertificate111)`の試行はStudioで拒否され、[公式Container制限](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-setfocus)と一致。サポートされる部品階層とモーダル設計の修正が必要。試行を元に戻して公式数式エラー0で保存し、Screen1全文が基準とバイト一致した。[復元記録](focus-restoration.json)。
2. [Issue #57 PERF-RELOAD-001](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/57)：p95(ms)は起動4400、検索462、選択442、閉1026、開305。閉の目標1000msを超過。測定はPlaywright操作・待機を含む。次runは10回起動後の一覧7件待ちで30秒タイムアウトし再測定未完。アプリ初期化/試験同期/連続ナビゲーションの切り分けが必要。生CSV/JSONはrun35312872559の14日保持artifact、p95と失敗ログは本記録に保全。
3. PDF保存/保存失敗注入は未接続、OneDrive/Automateは従前指示どおり接続していない。大件数・長文fixture、200%拡大、支援技術での読上げ、復元/故障注入などは95項目表で継続。部分実施を一括PASSにしない。
4. [Issue #51 ABS-RATE-001](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/51)は実テーブル未反映。今回Dataverseテーブルを編集していない。次回M_職員基本の編集時に対応する。

## 静的検査・現行データ

既存automation単体は50/50 PASS。`python tests/audit_current_ui.py`もPASS。[監査JSON](source-audit.json)：814コントロール、重複ID0、旧651部品の型/親/Variant保持、5配布形式対と7パッチ一致。不正Classic/Button AccessibleLabelなし、PDFViewerはScreen直下。これはMicrosoftのコンパイラや全プロパティスキーマの代替ではない。

データは従来の[現行プロファイル](../regression-v122/plan.md)を継承。Staff25、Commute6、Payroll7、Work7、Social5、Tax5。3所属へ割当済み23名（8/8/7）がUI対象で、未割当001/005はUIから到達しない。全25名を1所属で表示することを正解にせず、大件数ページ境界を合格にしていない。勤務/保険/税の共通定義と独立fixtureも照合した。

通常のUI試作として確認を進められる公開v1.23を維持する。全回帰合格・本番利用承認・正式計算や永続化の完了を意味しない。
