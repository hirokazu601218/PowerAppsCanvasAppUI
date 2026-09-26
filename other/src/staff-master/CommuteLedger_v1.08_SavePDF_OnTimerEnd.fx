// tmrLedgerPdf108.OnTimerEnd に設定（PDF保存フロー追加後）
// Power Apps (V2) トリガーの入力は最初の「ファイル」1つだけ。
// フロー名 SaveCommuteLedgerPdf / 応答のテキスト出力 fileurl。
Set(varLedgerPdfRequested108,false);
IfError(
    Set(varLedgerPdf108,PDF(conLedgerPages108,{Size:ddLedgerPaper108.Selected.Value,Orientation:"Landscape",Margin:"0mm",DPI:144,ExpandContainers:true}));
    Set(varLedgerPdfView108,true);
    Set(varLedgerStatus108,"PDFを保存しています…");
    Set(varLedgerSaveResult108,
        SaveCommuteLedgerPdf.Run(
            {file:{name:varLedgerFile108,contentBytes:varLedgerPdf108}}
        )
    );
    If(
        IsBlank(varLedgerSaveResult108.fileurl),
        Set(varLedgerStatus108,"保存先のURLを取得できませんでした。フローの実行結果を確認してください。");
        Notify(varLedgerStatus108,NotificationType.Error),
        Set(varLedgerSavedUrl108,varLedgerSaveResult108.fileurl);
        Set(varLedgerStatus108,"PDFを保存しました。［保存したPDFを開く］からダウンロードできます。")
    ),
    Set(varLedgerStatus108,"PDFの作成または保存に失敗しました。" & FirstError.Message);
    Notify(varLedgerStatus108,NotificationType.Error)
);
Set(varLedgerExport108,false)
