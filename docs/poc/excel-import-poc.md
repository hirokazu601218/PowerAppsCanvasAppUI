# Excel一括取込 PoC — 実機取込成功・公開後照合は未完了

対象：StaffMaster-Automation-Test / App ID `204a48dc-7f23-43dd-b934-4654a3cfa306`。要求 `CHANGE-20260928-EXCEL-IMPORT-POC`、画面配置 `FUT-IMPORT-001`。正式職員マスタと実在データは変更していない。

## 構築した操作
ホーム「データ一括取込み」→ `scrExcelImportPoc` → Excel選択 →「取込を実行」→ 読取件数・登録成功／失敗件数と保存済み行を表示。ホームへ戻って再度開くとDataverseをRefreshする。

## 検証ファイル
Library `非常勤給与/PoC_Excel一括取込_架空データ.xlsx`。シート `取込データ`、テーブル `ImportPoCTest`。採用識別子・職員番号・氏名・部署略称・採用日の5列、3行。TEST-HIRE-001/002の職員番号は000000000101/000000000102、003は空欄。採用日は文字列ISO日付。元ファイルは変更していない。

## 実装構成
- Dataverse `PoC_Excel取込行_STUDIO`（ID `71dee774-8b1d-48c3-ad2b-32cc55cd2de2`）。採用識別子、職員番号、氏名、部署略称、採用日、取込要求ID、行番号、取込結果のテキスト列。
- `PoC_Excel取込依頼_STUDIO`（ID `881b7b78-fc3f-4292-b3f4-3099757ec22c`）の添付有効フォームをファイル選択に利用。事前検証依頼 `POC-REQ-20260928-01` の保存済み添付ファイル名は再表示PASS。ただしバイナリのダウンロード・ハッシュ照合は未完了。
- 今回の取込ではSubmitFormを使わず、選択ファイルのname/contentBytesを `PoC_ExcelImport_STUDIO` に直接渡す。
- フロー：Power Apps (V2) → OneDrive for Businessの一時xlsx作成 → Excel Online (Business)で `ImportPoCTest` の行を読取 → テキスト出力 `rowsjson`。
- CanvasはParseJSONで5列を取り出し、Patchで隔離行表へ登録する。GUIDの取込要求ID・行番号・結果「成功」を保存。採用識別子と氏名が空の行を含む場合は登録前に止める。行単位のPatch失敗は `colImportErrors` に記録する。
- ギャラリーはサーバーの隔離行表を直接参照。全バッチを表示する。
- [実装式と接続構成](../../src/excel-import-poc/README.md)。フローの環境内GUID、run ID、公開パッケージ全文は未取得。
- 当初のSharePoint候補は採用していない。

## 実測結果（所有者のStudioプレビュー）
| ケース | 独立期待値 | 実測と判定 |
|---|---|---|
| ファイル選択 | 指定xlsx名を表示 | PASS |
| Excel読取 | 3行・5列・先頭ゼロ・空欄1件 | PASS。実JSONを観察 |
| 正常登録 | 3行追加、成功3・失敗0 | PASS。初回と修正後再実行でそれぞれ「読取3件／登録成功3件／失敗0件」。合計6行 |
| ホーム往復 | 再表示後も保存済み3行と5項目 | PASS。001/002の先頭ゼロ、003の空欄も確認 |
| UT-IMP-01 未選択 | エラー、保存行増加なし | PASS。「Excelファイルを1件選択してください。」。表示改善後も再試験PASS |
| UT-IMP-05 非xlsx | 拡張子エラー、保存行増加なし | PASS。`PoC_invalid.txt` を拒否 |
| 破損xlsx | 成功扱いしない | 添付コントロールで「問題が発生しました」。Excelコネクタまで到達した証拠なし。サーバー読取失敗試験の代替にしない |
| 指定テーブルなしxlsx | 読取失敗を表示 | NOT_RUN |
| 行書込拒否・一部失敗 | 行別失敗を表示 | NOT_RUN |
| 実行中再押下 | 二重起動を抑止 | DisplayMode実装済み、実測NOT_RUN |
| Studio数式検査 | 数式エラー0 | PASS。「エラーは検出されませんでした」 |
| 公開Player・PAC読戻し | 同じ公開版の操作・版/SHA一致 | BLOCKED。再認証が必要で安全な認証手順が単独パスワード選択を受け付けず未完了 |

最初のフロー応答は式を文字列として返して失敗。動的valueトークンへ修正し、実3行JSONで再試験PASS。数式再入力で混入した重複式も修正後、Studioエラー0と正常登録を再確認した。失敗履歴を隠していない。

## 保存・公開
2026-09-28 23:04:54 JSTに保存済み表示。23:06:20 JSTに対象環境・同一アプリの `Publish successful` 通知を確認。公開操作成功は確認済みだが、公開版番号・公開Player・PACパッケージSHAの照合は未完了。Studio結果を公開Player PASSへ転記しない。

## 残件とPoC境界
- 公開Playerで正常／異常系と新規セッション再表示、版番号・PAC読戻し・Actions照合。
- 指定テーブルなし、空テーブル、列不足、行保存拒否、一部失敗、実行中連打の実測。
- 行別エラー詳細の可視表示と再ログイン後の失敗履歴保持は未検証。
- 一時OneDriveファイルは `PoC_ExcelImport_STUDIO_` 接頭辞で残る。後片付け未実装。
- 再実行は新規行を追加する。重複抑止・本番項目条件・サーバー入力検証・大量行ページング・所有者以外の権限は後続。
- 現在の保存行は架空データだけの6件。共有権限を広げる変更は実施していない。
- 本番のFR-E-01全体完了、業務受入、総合試験PASSとはしない。

詳細は[実施記録](../../records/changes/change-20260928-excel-import-poc/manual-20260928-excel-import/record.json)を参照。
