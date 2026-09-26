// tmrLedgerPdf111.OnTimerEnd に設定（PDF保存フロー追加後）
// Power Apps (V2) トリガーの入力は最初の「ファイル」1つだけ。
// フロー名 SaveCommuteLedgerPdf / 応答のテキスト出力 fileurl。
Set(varLedgerPdfRequested111,false);
IfError(
    Set(varLedgerPdf111,PDF(conLedgerPages111,{Size:ddLedgerPaper111.Selected.Value,Orientation:"Landscape",Margin:"0mm",DPI:144,ExpandContainers:true}));
    Set(varLedgerPdfView111,true);
    Set(varLedgerStatus111,"PDFを保存しています…");
    Set(varLedgerSaveResult111,
        SaveCommuteLedgerPdf.Run(
            {file:{name:varLedgerFile111,contentBytes:varLedgerPdf111}}
        )
    );
    If(
        IsBlank(varLedgerSaveResult111.fileurl),
        Set(varLedgerStatus111,"保存先のURLを取得できませんでした。フローの実行結果を確認してください。");
        Notify(varLedgerStatus111,NotificationType.Error),
        Set(varLedgerSavedUrl111,varLedgerSaveResult111.fileurl);
        Set(varLedgerStatus111,"PDFを保存しました。［保存したPDFを開く］からダウンロードできます。")
    ),
    Set(varLedgerStatus111,"PDFの作成または保存に失敗しました。" & FirstError.Message);
    Notify(varLedgerStatus111,NotificationType.Error)
);
Set(varLedgerExport111,false)
