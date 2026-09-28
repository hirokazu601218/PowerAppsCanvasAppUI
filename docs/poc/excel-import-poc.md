# Excel一括取込 PoC 構築候補（未公開・未検証）

対象：StaffMaster-Automation-Test / App ID `204a48dc-7f23-43dd-b934-4654a3cfa306`。要求 `CHANGE-20260928-EXCEL-IMPORT-POC`、画面配置 `FUT-IMPORT-001`。2026-09-28時点で**アプリ・保存先・フローの実体は未作成**。この文書は実機作業の入力であり、実装済みや技術的な成功の証拠ではない。

## 検証ファイル
Library `/非常勤給与/PoC_Excel一括取込_架空データ.xlsx`。シート `取込データ`、テーブル `ImportPoCTest`、列順 `採用識別子・職員番号・氏名・部署略称・採用日`、データ3行。採用識別子 TEST-HIRE-001/002/003、3行目の職員番号は空欄。Excelの採用日は文字列 ISO 日付、職員番号は12桁の文字列として扱い、先頭ゼロを保持する。ローカルのopenpyxlで現物を読取り確認済み。

## 検証構成

1. テスト専用SharePointリスト `PoC_Excel取込依頼` を用意。Title（任意の取込要求ID）、添付ファイルあり、状態（受付／実行中／完了／失敗）、結果メッセージ。正式職員マスタのデータソースに接続しない。
2. テスト専用SharePointリスト `PoC_Excel取込行` を用意。Title（採用識別子）、要求ID、行番号、職員番号（1行テキスト、空欄可）、氏名、部署略称、採用日（PoCでは1行テキスト）、結果（成功／失敗）、メッセージ。検証用サイト内に限定する。権限は既存のテスト利用者のみに絞る。
3. Canvas専用画面 `scrExcelImportPoc` に `frmExcelImportPoc`（取込依頼リストの新規フォーム、添付カードを有効化、1ファイル）、`btnImportRunPoc`、`lblImportStatusPoc`、`galImportRowsPoc`、`btnImportHomePoc` を配置。ホーム `scrHome` に「データ一括取込み」ボタンと `Navigate(scrExcelImportPoc,ScreenTransition.None)` を追加。フォームの添付コントロールはフォーム内でのみ保存できる。
4. 「取込を実行」は添付数1・拡張子xlsxを確認して `SubmitForm(frmExcelImportPoc)`。フォーム `OnSuccess` から保存済み依頼IDを引数に `flowExcelImportPoc.Run(...)` を呼ぶ。二重押下を防止。フロー失敗時は処理完了表示にしない。
5. Power AutomateフローはPower Apps (V2)から依頼IDを受取り、SharePointの依頼項目／添付一覧を再取得する。添付は必ず1件かつ.xlsx、サイズ制限内とサーバー側でも確認する。添付コンテンツを検証用ドキュメントライブラリの一時フォルダに作成し、その作成結果のIdentifierをExcel Online (Business)「表内に存在する行を一覧表示」に渡す。テーブル名は固定 `ImportPoCTest`。日本語列名にOData Select Queryは使わない。
6. 取得した各行を要求ID・行番号とともに `PoC_Excel取込行` に新規作成。職員番号空欄はPoCでは受け入れ、空欄のまま保存する。行単位失敗は行別結果へ記録し、総件数・成功・失敗を依頼リストへ保存する。一時ファイルの後片付けは取得結果の確認後に実施する。
7. 画面の結果ギャラリーは `Filter(PoC_Excel取込行, 要求ID = varImportRequestId)`。再表示時には依頼リストの最近の履歴から要求IDを選び直し、`Refresh` でサーバー側行を再取得する。Power Appsのコレクションだけを永続化根拠にしない。

この方式ではファイル選択の直後に添付を確定し、フォーム保存後にフローを実行する。フローの同期応答より前に終了し得るため、画面では依頼リストの状態を手動更新できるようにする。SharePointサイト・リストの具体的な接続、フローの実行権限、Excelコネクタで動的Identifierを使えるかは環境で試験するまで未判定。

## Power Fx 候補（Studioに貼る前に接続名・内部列名を確認）

```powerfx
// scrExcelImportPoc.OnVisible
Refresh(PoC_Excel取込依頼);
Refresh(PoC_Excel取込行);
Set(varImportRunning, false);
Set(varImportMessage, "Excelファイルを1件選択してください。");

// btnImportRunPoc.OnSelect（attImportPocはフォームの添付カード内）
If(
    varImportRunning,
    Notify("取込処理中です。", NotificationType.Information),
    If(
        CountRows(attImportPoc.Attachments) <> 1,
        Notify("Excelファイルを1件選択してください。", NotificationType.Error),
        If(
            !EndsWith(Lower(First(attImportPoc.Attachments).Name), ".xlsx"),
            Notify(".xlsxファイルを選択してください。", NotificationType.Error),
            Set(varImportRunning, true);
            Set(varImportMessage, "ファイルを保存しています。");
            SubmitForm(frmExcelImportPoc)
        )
    )
)

// frmExcelImportPoc.OnSuccess
Set(varImportRequestId, frmExcelImportPoc.LastSubmit.ID);
Set(varImportMessage, "Excelを読み取っています。");
IfError(
    Set(varImportFlowResult, flowExcelImportPoc.Run(varImportRequestId)),
    Set(varImportMessage, "フローを開始できませんでした。");
    Notify(varImportMessage, NotificationType.Error),
    Refresh(PoC_Excel取込依頼);
    Refresh(PoC_Excel取込行);
    Set(varImportMessage, "実行結果を更新してください。")
);
Set(varImportRunning, false)

// frmExcelImportPoc.OnFailure
Set(varImportRunning, false);
Set(varImportMessage, "ファイルの保存に失敗しました。");
Notify(frmExcelImportPoc.Error, NotificationType.Error)

// btnImportRefreshPoc.OnSelect
Refresh(PoC_Excel取込依頼);
Refresh(PoC_Excel取込行)

// galImportRowsPoc.Items（実際の内部列名に置換）
SortByColumns(Filter(PoC_Excel取込行, 要求ID = varImportRequestId), "行番号", SortOrder.Ascending)
```

### 検証境界
添付コントロールはSharePoint/Dataverseフォーム内に置く必要がある。Power Appsモバイル版では1回に1ファイルを選択する。Excel Online (Business)の「行一覧」は既定で最大256行なので、本番要件にはページネーション設計が必要。現PoCは3行。採用識別子の重複判定、再実行時の冪等性、ロールと部局の認可、本番の必須列と欠損時の処理はPoC成功後に決める。再実行前には検証用リストの前回分と新規分を区別する。正式マスタへPatchしない。

## 単体テスト（実機未実施）
| ID | 入力・操作 | 独立した期待値 |
| --- | --- | --- |
| UT-IMP-01 | ファイル未選択で実行 | 添付エラー、依頼／行レコードは増えない |
| UT-IMP-02 | 指定Excelを選択し実行 | 依頼1件、テーブル3行読取、隔離行3件。001/002の12桁先頭ゼロ保持、003の職員番号空欄保持 |
| UT-IMP-03 | 実行後に画面を開き直して要求履歴を選択 | サーバーから3行と結果を再表示 |
| UT-IMP-04 | テーブル名が違う.xlsx | 行3件を成功扱いにせず依頼が失敗、読取エラーを表示 |
| UT-IMP-05 | .xlsx以外のファイル | 画面とフロー双方で拒否、隔離行0件 |
| UT-IMP-06 | 同一依頼IDで実行中に再押下 | 多重起動しない。フロー側の冪等性はPoCで要測定 |

実測記録には環境、App ID、公開版、フロー実行ID、依頼ID、操作時刻、期待／実際の行数と値、エラー本文、画面再表示後の値を残す。失敗や未実施をPASSへ読み替えない。
