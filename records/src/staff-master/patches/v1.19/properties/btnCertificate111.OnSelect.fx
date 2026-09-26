IfError(
    With({c:galCommute111.Selected,s:StaffSelected},
        If(IsBlank(c.T_通勤) || c.職員基本.職員番号 <> s.StaffId,
            Notify("通勤の行を選択してください。",NotificationType.Warning),
            Set(varLedgerStaff111,s);
            Set(varLedgerCommute111,c);
            ClearCollect(colLedgerFields111,StaffLedgerFields);
            Set(varLedgerOpen111,true); Set(varLedgerZoom111,1);
            Set(varLedgerPdfView111,false); Set(varLedgerExport111,false);
            Set(varLedgerPdfRequested111,false); Set(varLedgerPdf111,Blank());
            Set(varLedgerSavedUrl111,""); Set(varLedgerStatus111,"");
            Set(varLedgerFile111,""); Set(varPayroll111,false); Reset(ddLedgerPaper111)
        )
    ),
    Clear(colLedgerFields111); Set(varLedgerOpen111,false);
    Notify("通勤データを取得できませんでした。再読込してください。",NotificationType.Error)
)
