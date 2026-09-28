# Excel import PoC — Studio implementation

App ID: `204a48dc-7f23-43dd-b934-4654a3cfa306`. Environment: StaffMaster-Automation-Test. This folder records manually applied Power Fx, not an importable full canvas package. PAC package readback remains required.

## Canvas wiring

- `scrHome.Button3`: Text=`"データ一括取込み"`; OnSelect=`Navigate(scrExcelImportPoc, ScreenTransition.None)`.
- `scrExcelImportPoc.OnVisible`: `Refresh('PoC_Excel取込行_STUDIO'); ResetForm(Form1); NewForm(Form1)`.
- `Form1`: DataSource=`'PoC_Excel取込依頼_STUDIO'`, Item=`Defaults('PoC_Excel取込依頼_STUDIO')`, DefaultMode=`FormMode.New`. Only attachment card retained. Attachment control is `DataCardValue7`. The form supplies file selection; current import passes file content directly to the flow, without SubmitForm.
- `Button1`: Text=`"取込を実行"`; OnSelect=[source](Button1.OnSelect.powerfx); DisplayMode=`If(varImportRunning, DisplayMode.Disabled, DisplayMode.Edit)`.
- `Gallery1.Items`: `'PoC_Excel取込行_STUDIO'` (persistent server source, all PoC batches).
- `Title1.Text`: `ThisItem.採用識別子 & "  |  " & ThisItem.氏名`.
- `Subtitle1.Text`: `"職員番号: " & Coalesce(ThisItem.職員番号, "（空欄）") & "　部署: " & ThisItem.部署略称 & "　採用日: " & ThisItem.採用日 & "　結果: " & ThisItem.取込結果`.
- `Text1`: PoC title and `varImportMessage`. Row Patch failures are collected into `colImportErrors`; failure-detail display needs readback validation.
- `Button2`: Text=`"ホームへ戻る"`; OnSelect=`Navigate(scrHome, ScreenTransition.None)`.

## Power Automate `PoC_ExcelImport_STUDIO`

1. Power Apps (V2), file input `file`.
2. OneDrive for Business Create file. Folder `/`, name `PoC_ExcelImport_STUDIO_` + `guid()` + `.xlsx`, content `base64ToBinary(triggerBody()['file']['contentBytes'])`.
3. Excel Online (Business) List rows present in a table. OneDrive for Business / ドキュメント. File token `outputs('ファイルの作成')?['body/Id']`. Custom table `ImportPoCTest`.
4. Respond to a Power App or flow. Text output `rowsjson`, dynamic value token `outputs('表内に存在する行を一覧表示')?['body/value']`.

Flow reads Excel; canvas validates and writes only `PoC_Excel取込行_STUDIO`. Temporary OneDrive files remain under the isolated name prefix. Cleanup, server validation, pagination, idempotency and non-owner permissions are not established by this PoC.
