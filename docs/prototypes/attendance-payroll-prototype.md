# 勤務時間報告画面・支給明細画面：2画面プロトタイプ v0.32

仕様更新日：2026/09/17。内容の版：v0.32。

> このファイルを勤務報告・給与計算2画面の独立プロトタイプの正本とします。既存公開アプリへの統合・実機検証は未実施です。

## 画面要件との対応・UIイメージのデザイン

[画面要件定義書](../requirements/screen-requirements.md)の名称に統一します。「数値入りの計算過程」は独立した別画面ではなく、**SCR-005 支給明細画面の表示内容**です。ファイル名はリンク継続のため `attendance-payroll-prototype.md` を維持します。

| 画面ID | 正式画面名 | 試作内部名 |
|---|---|---|
| SCR-003 | 勤務時間報告画面 | scrAttendance |
| SCR-005 | 支給明細画面 | scrPayroll |

UIイメージは [B案デザイン基準 v1.04](../design/design-system.md) を適用します。ヘッダー #073B78、主操作 #0F6CBD、本文 #242424、背景 #F7F9FC、面 #FFFFFF、見出し帯 #EDF2F7、枠 #CBD5E1、角丸4px程度、外余白16px・節間20pxを使用。標準文字はタイトル20px、見出し16px、本文14px、補足12px相当、金額右寄せ。旧DADS資料ではなく現行のB案を基準とします。

画像は架空データによるデザイン案です。SCR-005のホームボタン、選択職員・支給対象月の表示を含めます。職員マスタ検索への操作名は要件上未確定のため、画像では仮配置として扱います。ログイン者と対象職員は区別し、同一所属部署の対象職員を表示する想定です。部門制限・アカウント情報引継ぎ・ホーム遷移は実装済みとは扱いません。

今回の変更は名称統一と画像案の作成です。既存YAMLの内部ID・計算ロジックは維持します。既存の2画面間移動ボタンは独立試作専用であり、本番の画面遷移は画面要件定義書へ統合する際に修正します。画像のB案レイアウト・ホーム等を既存YAMLへ全面反映したわけではありません。

## 1. 今回の確定ルール

- 日額単価は1日7時間45分（465分）勤務分。
- 勤務日数は実際に通常勤務した日数。全日欠勤日は数えません。
- 勤務した日のうち7時間45分に満たない部分を欠勤として控除します。
- 全日欠勤は勤務日数から除外済みなので、欠勤控除に重ねて含めません。
- 基本額、欠勤時間単価、欠勤控除、超過勤務手当は途中で丸めません。
- **基本額−欠勤控除＋超過勤務手当の最終合計だけ、円未満を切り捨てます。**
- 給与画面に単価・日数・時間・各算出金額を式として表示します。

コレクションによる独立した2画面の試作です。Dataverse接続やテーブル作成は不要です。アプリ終了・再読み込み・OnStart再実行で、登録内容は初期化されます。

## 2. 計算式と日数の数え方

| 段階 | 計算式 |
|---|---|
| ① 基本額 | 日額単価 × 実際に勤務した日数 |
| 欠勤控除用の時間単価 | 職員基本情報の「欠勤時間単価」を参照 |
| ② 欠勤控除 | 時間単価 × 勤務した日の欠勤時間合計 |
| ③ 超過勤務手当 | 職員基本情報の超過勤務時間単価 × 超過勤務時間合計 |
| ④ 合計（切捨て前） | ① − ② ＋ ③ |
| 支給額（対象項目） | ④の円未満を切り捨て |

7時間45分＝7.75時間＝465分です。7.45時間ではありません。時間は内部で整数の分として保存し、計算時に60で割ります。超過勤務単価は割増込みの時間単価という試作前提を継続します。

| 日の区分 | 通常勤務 | 欠勤記録 | 勤務日数への加算 | 欠勤控除対象 |
|---|---|---|---:|---|
| 勤務日（全時間勤務） | 7時間45分 | 0 | 1日 | 0 |
| 勤務日（一部欠勤） | 例：6時間45分 | 例：1時間 | 1日 | 1時間 |
| 全日欠勤 | 0 | 7時間45分 | **0日** | **対象外** |
| 非勤務日 | 0 | 0 | 0日 | 対象外 |

全日欠勤の記録は残しますが、金額は勤務日数から除外することで反映します。例えば、勤務予定20日のうち1日が全日欠勤なら基本額は日額×19日、全日欠勤に対する追加控除は0円です。実勤務20日とは別に全日欠勤日がある場合は、基本額は日額×20日です。

この初版では勤務日判定を通常勤務分が0より大きいこととし、勤務日は「通常勤務＋欠勤＝465分」を確認します。通常勤務0分の日に超過勤務だけを登録する休日勤務等は未対応です。年休など有給区分も未実装のため、通常勤務の不足をアプリが自動で欠勤扱いにせず、欠勤は明示入力します。月途中の単価変更、通勤手当、税・社会保険料等は対象外です。

## 3. SCR-003 勤務時間報告画面

| 配置 | 表示・操作 |
|---|---|
| 上部 | 職員番号・氏名、勤務月、月分を開く |
| 中段左 | 月の日別一覧：勤務日、区分、通常勤務、欠勤記録、超過勤務、確認状態 |
| 中段右 | 勤務日／全日欠勤／非勤務日の選択と、通常勤務・欠勤・超過勤務の時間／分入力 |
| 右下 | この日を反映 |
| 下部 | 勤務日数（全日欠勤を除く）、通常勤務合計、控除対象の欠勤合計、超過勤務合計、未確認日数 |
| 最下部 | 未確認日を非勤務日にする／編集を破棄／月分を登録 |

全日欠勤の登録は「全日欠勤」を選び、通常0、欠勤7時間45分、超過0を入力します。非勤務日とは区別します。未確認日の一括非勤務化は、未確認行だけが対象です。先に全日欠勤日と勤務日を反映してください。

氏名は職員番号から取得します。未反映入力のまま別の日へ移らないようにし、月編集中は職員・月変更と給与画面への移動を止めます。月分登録または編集破棄で解除します。既登録月の修正は同じ職員・月を置換し、二重登録を防止します。

## 4. SCR-005 支給明細画面：数値入りの計算過程

日額9,750円、欠勤時間単価1,250円/時（架空の設定値）、実勤務20日、勤務した日の欠勤1時間、超過勤務1時間（単価1,950円/時）の表示例です。

| 表示段 | UIに見える式 |
|---|---|
| ① 基本額 | **9,750円/日 × 20日 ＝ 195,000円** |
| ② 欠勤控除 | **1,250円/時 × 1時間 ＝ 1,250円** |
| ③ 超過勤務手当 | **1,950円/時 × 1時間 ＝ 1,950円** |
| ④ 合計から切捨て | **① − ② ＋ ③ ≈ 195,700円 → 195,700円** |

中間額は画面上のみ小数6桁の概数（≈／約）で表示します。内部の計算ではその表示値を使わず、丸めていない数値を使います。最後に `RoundDown(合計, 0)` を一度だけ適用します。この試作の入力制約では合計は非負です。

欠勤がない場合も欠勤0時間・控除0円を表示します。UIでは分から時間への換算式を表示せず、1時間、0.5時間のように表示します。1分など循環小数となる時間は「約0.016667時間」と小数6桁の概数で表示します。計算内部では元の分数÷60を使い、表示値を再利用しません。未登録月を0円として扱いません。対象や報告書登録版が変わったら旧結果を隠して再計算を促します。

## 5. 内蔵データ

Dataverse定義ではなく試作用のコレクションです。

| コレクション | 用途 |
|---|---|
| colStaff | 職員番号、氏名、日額、欠勤時間単価、超過勤務時間単価、所定465分 |
| colDraft | 編集中の1名・1か月の明細 |
| colAttendance | 登録済みの日別明細。勤務日区分、全日欠勤区分、通常勤務分、欠勤分、超過勤務分等 |
| colMonths | 職員番号＋勤務月の登録状態と登録版 |

`PlannedDay` は旧版からの内部名を引き継いでいますが、現版では「勤務日」選択の印です。勤務予定日数を給与計算に使うものではありません。日数は `CountIf(rows, RegularMinutes>0)`、控除対象時間は `Sum(Filter(rows, RegularMinutes>0), AbsenceMinutes)` で計算します。`FullDayAbsence` は全日欠勤記録です。

00001：試験 太郎、日額9,750円、欠勤時間単価1,250円/時、超過勤務単価1,950円/時。00002：試験 花子、日額9,000円、欠勤時間単価1,200円/時、超過勤務単価1,875円/時。両名とも所定7時間45分。

00001の2026/09は計算確認用に1～20日を勤務日とし、9/1を通常6時間45分＋欠勤1時間＋超過1時間としています。他の勤務日は通常7時間45分、21～30日は非勤務です。土日祝日判定を示すものではない架空データです。00002は未登録です。

### 未反映タスク：ABS-RATE-001

[Issue #51：次回の職員基本テーブル編集時に欠勤時間単価を追加](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/51) は未完了です。今回は内蔵 `colStaff.AbsenceHourlyRate` のみ追加し、Dataverse実テーブルは変更していません。単価1,250円／1,200円は独立して設定した架空の試験値で、日額から算出した本番単価ではありません。実テーブルの項目・精度・設定方法は次回編集時に確定します。実テーブルへの追加を読戻し確認し、証跡を残してからIssueを閉じます。

## 6. 導入・更新手順

1. タブレットキャンバスアプリ（1366×768、縦横比固定・画面に合わせた拡大縮小）に `scrAttendance` と `scrPayroll` を用意します。スマートフォン専用配置は未実装です。
2. 旧版導入済みの場合は `conAttendancePrototype`、`conPayrollPrototype` を削除し、下の対応YAMLで置換します。App.OnStartも全置換します。
3. `App.StartScreen` を `scrAttendance` に設定し、OnStartを実行します。追加項目があるため再初期化が必要で、試作入力は消去されます。
4. 00001・2026/09で勤務報告と計算過程を確認します。

YAMLはコントロール貼り付け形式です。コードフェンス行はコピーしません。クラシックコントロール主体、白・青配色、メイリオ16pt以上の構成を継続しています。Power Apps Studioでの貼り付け・コンパイル・実画面操作は未検証です。

### App.OnStart

```powerfx
// 試作専用：再実行すると登録内容を初期化します。
ClearCollect(colStaff,
    {StaffNo:"00001", StaffName:"試験 太郎", StaffLabel:"00001  試験 太郎", DailyRate:9750, AbsenceHourlyRate:1250, OvertimeHourlyRate:1950, ScheduledMinutes:465},
    {StaffNo:"00002", StaffName:"試験 花子", StaffLabel:"00002  試験 花子", DailyRate:9000, AbsenceHourlyRate:1200, OvertimeHourlyRate:1875, ScheduledMinutes:465}
);
// 計算確認用：1～20日を勤務日に設定。土日祝日判定を行うサンプルではありません。
// 9/1は通常6時間45分＋欠勤1時間＋超過1時間。他の勤務日は通常7時間45分。
ClearCollect(colAttendance,
    ForAll(Sequence(30) As n,
        {StaffNo:"00001", StaffName:"試験 太郎", WorkMonth:Date(2026,9,1),
         WorkDate:Date(2026,9,n.Value), PlannedDay:n.Value<=20, FullDayAbsence:false,
         RegularMinutes:If(n.Value=1,405,If(n.Value<=20,465,0)),
         AbsenceMinutes:If(n.Value=1,60,0), OvertimeMinutes:If(n.Value=1,60,0), Confirmed:true}
    )
);
ClearCollect(colMonths,{StaffNo:"00001",WorkMonth:Date(2026,9,1),Revision:Text(GUID())});
ClearCollect(colDraft,First(colAttendance)); Clear(colDraft);
Set(varLoaded,false); Set(varDayDirty,false);
Set(varStaff,First(colStaff)); Set(varMonth,Date(2026,9,1)); Set(varDayDate,Date(2026,9,1));
Set(varCalcReady,false); Set(varPayStaff,First(colStaff)); Set(varPayMonth,Date(2026,9,1));
Set(varPayRevision,""); Set(varWorkDays,0); Set(varRegularMinutes,0);
Set(varAbsenceMinutes,0); Set(varOvertimeMinutes,0); Set(varAbsenceHourlyRate,0);
Set(varBasePay,0); Set(varAbsenceDeduction,0); Set(varOvertimePay,0);
Set(varTotalBeforeTruncation,0); Set(varFinalPay,0)
```

### SCR-003 勤務時間報告画面のYAML：scrAttendance

```yaml
- conAttendancePrototype:
    Control: GroupContainer@1.3.0
    Variant: ManualLayout
    Properties:
      X: =0
      Y: =0
      Width: =Parent.Width
      Height: =Parent.Height
      Fill: =Color.White
    Children:
    - lblATitle:
        Control: Label@2.5.1
        Properties:
          Text: ="勤務時間報告書"
          X: =24
          Y: =16
          Width: =700
          Height: =48
          Size: =26
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
          FontWeight: =FontWeight.Semibold
    - lblASub:
        Control: Label@2.5.1
        Properties:
          Text: ="職員・勤務月を選択 → 日ごとに入力 → 月分を登録"
          X: =24
          Y: =66
          Width: =1000
          Height: =36
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - btnToPay:
        Control: Classic/Button@2.2.0
        Properties:
          Text: ="支給明細へ"
          X: =1120
          Y: =24
          Width: =210
          Height: =44
          Size: =16
          Font: ="Meiryo"
          Fill: =RGBA(241, 246, 251, 1)
          Color: =RGBA(0, 74, 153, 1)
          BorderThickness: =0
          RadiusTopLeft: =8
          RadiusTopRight: =8
          RadiusBottomLeft: =8
          RadiusBottomRight: =8
          OnSelect: =Navigate(scrPayroll,ScreenTransition.None)
          DisplayMode: =If(!varLoaded, DisplayMode.Edit, DisplayMode.Disabled)
    - lblAStaff:
        Control: Label@2.5.1
        Properties:
          Text: ="職員番号・氏名"
          X: =24
          Y: =108
          Width: =400
          Height: =36
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - ddStaff:
        Control: Classic/DropDown@2.3.1
        Properties:
          X: =24
          Y: =148
          Width: =440
          Height: =44
          Items: =colStaff
          Value: ="StaffLabel"
          Default: =First(colStaff).StaffLabel
          Size: =16
          Font: ="Meiryo"
          AccessibleLabel: ="職員番号・氏名"
          DisplayMode: =If(!varLoaded, DisplayMode.Edit, DisplayMode.Disabled)
    - lblAMonth:
        Control: Label@2.5.1
        Properties:
          Text: ="勤務月（その月の日付）"
          X: =488
          Y: =108
          Width: =300
          Height: =36
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - dpMonth:
        Control: Classic/DatePicker@2.6.0
        Properties:
          X: =488
          Y: =148
          Width: =210
          Height: =44
          DefaultDate: =Date(2026, 9, 1)
          Format: ="yyyy/mm/dd"
          Language: ="ja-JP"
          Size: =16
          Font: ="Meiryo"
          AccessibleLabel: ="勤務月。その月の任意の日付を選択"
          DisplayMode: =If(!varLoaded, DisplayMode.Edit, DisplayMode.Disabled)
    - btnOpen:
        Control: Classic/Button@2.2.0
        Properties:
          Text: ="月分を開く"
          X: =722
          Y: =148
          Width: =180
          Height: =44
          Size: =16
          Font: ="Meiryo"
          Fill: =RGBA(0, 74, 153, 1)
          Color: =Color.White
          BorderThickness: =0
          RadiusTopLeft: =8
          RadiusTopRight: =8
          RadiusBottomLeft: =8
          RadiusBottomRight: =8
          OnSelect: |-
            =Set(varStaff,ddStaff.Selected);
            Set(varMonth,Date(Year(dpMonth.SelectedDate),Month(dpMonth.SelectedDate),1));
            If(IsBlank(LookUp(colMonths,StaffNo=varStaff.StaffNo && WorkMonth=varMonth)),
                ClearCollect(colDraft,
                    ForAll(Sequence(Day(DateAdd(DateAdd(varMonth,1,TimeUnit.Months),-1,TimeUnit.Days))) As n,
                        {StaffNo:varStaff.StaffNo, StaffName:varStaff.StaffName, WorkMonth:varMonth,
                         WorkDate:DateAdd(varMonth,n.Value-1,TimeUnit.Days), PlannedDay:false, FullDayAbsence:false,
                         RegularMinutes:0, AbsenceMinutes:0, OvertimeMinutes:0, Confirmed:false}
                    )
                ),
                ClearCollect(colDraft,Filter(colAttendance,StaffNo=varStaff.StaffNo && WorkMonth=varMonth))
            );
            Set(varDayDate,varMonth); Set(varLoaded,true);
            Reset(ddDayType); Reset(txtRegHour); Reset(txtRegMinute); Reset(txtAbsHour); Reset(txtAbsMinute); Reset(txtOtHour); Reset(txtOtMinute); Set(varDayDirty,false)
          DisplayMode: =If(!varLoaded && !IsBlank(dpMonth.SelectedDate), DisplayMode.Edit, DisplayMode.Disabled)
    - lblAContext:
        Control: Label@2.5.1
        Properties:
          Text: =If(varLoaded,varStaff.StaffLabel & " ／ " & Text(varMonth,"yyyy/mm") & " ／ 所定 " & Text(Int(varStaff.ScheduledMinutes/60)) & "時間" & Text(Mod(varStaff.ScheduledMinutes,60),"00") & "分","月分を開いて入力してください。00001の2026/09に見本があります。")
          X: =24
          Y: =208
          Width: =1250
          Height: =44
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - lblAColumns:
        Control: Label@2.5.1
        Properties:
          Text: ="勤務日           区分       通常       欠勤       超過     確認"
          X: =24
          Y: =262
          Width: =770
          Height: =40
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
          Fill: =RGBA(241, 246, 251, 1)
    - galDays:
        Control: Gallery@2.15.0
        Variant: BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0
        Properties:
          X: =24
          Y: =306
          Width: =770
          Height: =316
          Items: =SortByColumns(colDraft,"WorkDate",SortOrder.Ascending)
          TemplateSize: =48
          TemplatePadding: =0
          TemplateFill: =If(ThisItem.WorkDate=varDayDate,RGBA(241, 246, 251, 1),Color.White)
          OnSelect: =If(varDayDirty,Notify("入力中の日を反映してから選択してください。",NotificationType.Warning),Set(varDayDate,ThisItem.WorkDate);Reset(ddDayType); Reset(txtRegHour); Reset(txtRegMinute); Reset(txtAbsHour); Reset(txtAbsMinute); Reset(txtOtHour); Reset(txtOtMinute); Set(varDayDirty,false))
        Children:
        - lblDayRow:
            Control: Label@2.5.1
            Properties:
              Text: =Text(ThisItem.WorkDate,"mm/dd") & "（" & Text(ThisItem.WorkDate,"ddd","ja-JP") & "）"
              X: =8
              Y: =0
              Width: =160
              Height: =44
              Size: =16
              Font: ="Meiryo"
              Color: =RGBA(28, 45, 65, 1)
              OnSelect: =Select(Parent)
        - lblDayKind:
            Control: Label@2.5.1
            Properties:
              Text: =If(!ThisItem.Confirmed,"未確認",If(ThisItem.FullDayAbsence,"全欠",If(ThisItem.PlannedDay,"勤務日","非勤務")))
              X: =175
              Y: =0
              Width: =105
              Height: =44
              Size: =16
              Font: ="Meiryo"
              Color: =RGBA(28, 45, 65, 1)
              OnSelect: =Select(Parent)
        - lblDayReg:
            Control: Label@2.5.1
            Properties:
              Text: =Text(Int(ThisItem.RegularMinutes/60),"00") & ":" & Text(Mod(ThisItem.RegularMinutes,60),"00")
              X: =290
              Y: =0
              Width: =100
              Height: =44
              Size: =16
              Font: ="Meiryo"
              Color: =RGBA(28, 45, 65, 1)
              OnSelect: =Select(Parent)
        - lblDayAbs:
            Control: Label@2.5.1
            Properties:
              Text: =Text(Int(ThisItem.AbsenceMinutes/60),"00") & ":" & Text(Mod(ThisItem.AbsenceMinutes,60),"00")
              X: =405
              Y: =0
              Width: =100
              Height: =44
              Size: =16
              Font: ="Meiryo"
              Color: =RGBA(28, 45, 65, 1)
              OnSelect: =Select(Parent)
        - lblDayOt:
            Control: Label@2.5.1
            Properties:
              Text: =Text(Int(ThisItem.OvertimeMinutes/60),"00") & ":" & Text(Mod(ThisItem.OvertimeMinutes,60),"00")
              X: =520
              Y: =0
              Width: =100
              Height: =44
              Size: =16
              Font: ="Meiryo"
              Color: =RGBA(28, 45, 65, 1)
              OnSelect: =Select(Parent)
        - lblDayConfirmed:
            Control: Label@2.5.1
            Properties:
              Text: =If(ThisItem.Confirmed,"済","未")
              X: =660
              Y: =0
              Width: =80
              Height: =44
              Size: =16
              Font: ="Meiryo"
              Color: =RGBA(28, 45, 65, 1)
              OnSelect: =Select(Parent)
    - lblEditorTitle:
        Control: Label@2.5.1
        Properties:
          Text: =If(varLoaded,Text(varDayDate,"yyyy/mm/dd") & " の勤務","日を選択して入力")
          X: =834
          Y: =262
          Width: =490
          Height: =36
          Size: =20
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
          FontWeight: =FontWeight.Semibold
    - lblRegular:
        Control: Label@2.5.1
        Properties:
          Text: ="通常勤務（超過勤務を除く）"
          X: =834
          Y: =350
          Width: =470
          Height: =36
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - txtRegHour:
        Control: Classic/TextInput@2.3.2
        Properties:
          X: =834
          Y: =388
          Width: =90
          Height: =44
          Default: =Text(Int(Coalesce(LookUp(colDraft,WorkDate=varDayDate,RegularMinutes),0)/60))
          Format: =TextFormat.Number
          Size: =18
          Font: ="Meiryo"
          AccessibleLabel: ="通常勤務の時間"
          OnChange: =Set(varDayDirty, true)
          DisplayMode: =If(varLoaded, DisplayMode.Edit, DisplayMode.Disabled)
    - lblRH:
        Control: Label@2.5.1
        Properties:
          Text: ="時間"
          X: =930
          Y: =392
          Width: =56
          Height: =36
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - txtRegMinute:
        Control: Classic/TextInput@2.3.2
        Properties:
          X: =996
          Y: =388
          Width: =90
          Height: =44
          Default: =Text(Mod(Coalesce(LookUp(colDraft,WorkDate=varDayDate,RegularMinutes),0),60))
          Format: =TextFormat.Number
          Size: =18
          Font: ="Meiryo"
          AccessibleLabel: ="通常勤務の分"
          OnChange: =Set(varDayDirty, true)
          DisplayMode: =If(varLoaded, DisplayMode.Edit, DisplayMode.Disabled)
    - lblRM:
        Control: Label@2.5.1
        Properties:
          Text: ="分"
          X: =1092
          Y: =392
          Width: =56
          Height: =36
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - lblOvertime:
        Control: Label@2.5.1
        Properties:
          Text: ="超過勤務"
          X: =834
          Y: =510
          Width: =470
          Height: =36
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - txtOtHour:
        Control: Classic/TextInput@2.3.2
        Properties:
          X: =834
          Y: =548
          Width: =90
          Height: =44
          Default: =Text(Int(Coalesce(LookUp(colDraft,WorkDate=varDayDate,OvertimeMinutes),0)/60))
          Format: =TextFormat.Number
          Size: =18
          Font: ="Meiryo"
          AccessibleLabel: ="超過勤務の時間"
          OnChange: =Set(varDayDirty, true)
          DisplayMode: =If(varLoaded, DisplayMode.Edit, DisplayMode.Disabled)
    - lblOH:
        Control: Label@2.5.1
        Properties:
          Text: ="時間"
          X: =930
          Y: =552
          Width: =56
          Height: =36
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - txtOtMinute:
        Control: Classic/TextInput@2.3.2
        Properties:
          X: =996
          Y: =548
          Width: =90
          Height: =44
          Default: =Text(Mod(Coalesce(LookUp(colDraft,WorkDate=varDayDate,OvertimeMinutes),0),60))
          Format: =TextFormat.Number
          Size: =18
          Font: ="Meiryo"
          AccessibleLabel: ="超過勤務の分"
          OnChange: =Set(varDayDirty, true)
          DisplayMode: =If(varLoaded, DisplayMode.Edit, DisplayMode.Disabled)
    - lblOM:
        Control: Label@2.5.1
        Properties:
          Text: ="分"
          X: =1092
          Y: =552
          Width: =56
          Height: =36
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - btnApplyDay:
        Control: Classic/Button@2.2.0
        Properties:
          Text: ="この日を反映"
          X: =834
          Y: =604
          Width: =220
          Height: =40
          Size: =16
          Font: ="Meiryo"
          Fill: =RGBA(0, 74, 153, 1)
          Color: =Color.White
          BorderThickness: =0
          RadiusTopLeft: =8
          RadiusTopRight: =8
          RadiusBottomLeft: =8
          RadiusBottomRight: =8
          OnSelect: |-
            =If(
                !IsMatch(txtRegHour.Text,"[0-9]{1,2}") || !IsMatch(txtRegMinute.Text,"[0-9]{1,2}") ||
                !IsMatch(txtAbsHour.Text,"[0-9]{1,2}") || !IsMatch(txtAbsMinute.Text,"[0-9]{1,2}") ||
                !IsMatch(txtOtHour.Text,"[0-9]{1,2}") || !IsMatch(txtOtMinute.Text,"[0-9]{1,2}"),
                Notify("時間・分を0以上の整数で入力してください。",NotificationType.Error),
                With({rh:Value(txtRegHour.Text),rm:Value(txtRegMinute.Text),ah:Value(txtAbsHour.Text),am:Value(txtAbsMinute.Text),oh:Value(txtOtHour.Text),om:Value(txtOtMinute.Text),planned:ddDayType.Selected.Value="勤務日",fullAbsent:ddDayType.Selected.Value="全日欠勤"},
                    If(rm>=60 || am>=60 || om>=60 || rh*60+rm+oh*60+om>1440 ||
                        (planned && (rh*60+rm<=0 || rh*60+rm+ah*60+am<>465)) ||
                        (fullAbsent && (rh*60+rm<>0 || ah*60+am<>465 || oh*60+om<>0)) ||
                        (!planned && !fullAbsent && rh*60+rm+ah*60+am+oh*60+om<>0),
                        Notify("分は0～59。勤務日は通常勤務が正で通常＋欠勤＝7時間45分。全日欠勤は欠勤7時間45分のみ。非勤務日はすべて0。実勤務は24時間以内です。",NotificationType.Error),
                        Patch(colDraft,LookUp(colDraft,WorkDate=varDayDate),
                            {PlannedDay:planned,FullDayAbsence:fullAbsent,RegularMinutes:rh*60+rm,AbsenceMinutes:ah*60+am,OvertimeMinutes:oh*60+om,Confirmed:true});
                        Set(varDayDirty,false);
                        Notify("選択日を反映しました。最後に月分を登録してください。",NotificationType.Success)
                    )
                )
            )
          DisplayMode: =If(varLoaded, DisplayMode.Edit, DisplayMode.Disabled)
    - lblPending:
        Control: Label@2.5.1
        Properties:
          Text: =If(varDayDirty,"入力中：この日を反映してください", "時間は「時間」と「分」に分けて入力")
          X: =834
          Y: =574
          Width: =490
          Height: =48
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
          Visible: =false
    - lblASummary:
        Control: Label@2.5.1
        Properties:
          Text: ="勤務日数（全日欠勤を除く） " & CountIf(colDraft,RegularMinutes>0) & "日 ／ 通常 " & Text(Sum(colDraft,RegularMinutes)/60,"0.##") & "時間 ／ 控除対象の欠勤 " & Text(Int(Sum(Filter(colDraft,RegularMinutes>0),AbsenceMinutes)/60)) & "時間" & Text(Mod(Sum(Filter(colDraft,RegularMinutes>0),AbsenceMinutes),60),"00") & "分 ／ 超過 " & Text(Int(Sum(colDraft,OvertimeMinutes)/60)) & "時間" & Text(Mod(Sum(colDraft,OvertimeMinutes),60),"00") & "分 ／ 未確認 " & CountIf(colDraft,!Confirmed) & "日"
          X: =24
          Y: =650
          Width: =1290
          Height: =36
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
          Fill: =RGBA(241, 246, 251, 1)
    - btnRest:
        Control: Classic/Button@2.2.0
        Properties:
          Text: ="未確認日を非勤務日にする"
          X: =24
          Y: =696
          Width: =310
          Height: =44
          Size: =16
          Font: ="Meiryo"
          Fill: =RGBA(241, 246, 251, 1)
          Color: =RGBA(0, 74, 153, 1)
          BorderThickness: =0
          RadiusTopLeft: =8
          RadiusTopRight: =8
          RadiusBottomLeft: =8
          RadiusBottomRight: =8
          OnSelect: =UpdateIf(colDraft,!Confirmed,{PlannedDay:false,FullDayAbsence:false,RegularMinutes:0,AbsenceMinutes:0,OvertimeMinutes:0,Confirmed:true});Reset(ddDayType); Reset(txtRegHour); Reset(txtRegMinute); Reset(txtAbsHour); Reset(txtAbsMinute); Reset(txtOtHour); Reset(txtOtMinute); Set(varDayDirty,false)
          DisplayMode: =If(varLoaded && !varDayDirty, DisplayMode.Edit, DisplayMode.Disabled)
    - btnDiscard:
        Control: Classic/Button@2.2.0
        Properties:
          Text: ="編集を破棄"
          X: =350
          Y: =696
          Width: =180
          Height: =44
          Size: =16
          Font: ="Meiryo"
          Fill: =RGBA(241, 246, 251, 1)
          Color: =RGBA(0, 74, 153, 1)
          BorderThickness: =0
          RadiusTopLeft: =8
          RadiusTopRight: =8
          RadiusBottomLeft: =8
          RadiusBottomRight: =8
          OnSelect: =Set(varLoaded,false); Clear(colDraft);Reset(ddDayType); Reset(txtRegHour); Reset(txtRegMinute); Reset(txtAbsHour); Reset(txtAbsMinute); Reset(txtOtHour); Reset(txtOtMinute); Set(varDayDirty,false)
          DisplayMode: =If(varLoaded, DisplayMode.Edit, DisplayMode.Disabled)
    - btnRegister:
        Control: Classic/Button@2.2.0
        Properties:
          Text: ="月分を登録"
          X: =1080
          Y: =696
          Width: =250
          Height: =44
          Size: =16
          Font: ="Meiryo"
          Fill: =RGBA(0, 74, 153, 1)
          Color: =Color.White
          BorderThickness: =0
          RadiusTopLeft: =8
          RadiusTopRight: =8
          RadiusBottomLeft: =8
          RadiusBottomRight: =8
          OnSelect: |-
            =If(varDayDirty,
                Notify("入力中の日を先に反映してください。",NotificationType.Warning),
                CountIf(colDraft,!Confirmed)>0,
                Notify("未確認日があります。入力するか、未確認日を休務にしてください。",NotificationType.Warning),
                // コレクション専用の置換。Dataverseにはこの削除・再追加方式を流用しません。
                RemoveIf(colAttendance,StaffNo=varStaff.StaffNo && WorkMonth=varMonth);
                Collect(colAttendance,colDraft);
                With({existing:LookUp(colMonths,StaffNo=varStaff.StaffNo && WorkMonth=varMonth)},
                    If(IsBlank(existing),
                        Collect(colMonths,{StaffNo:varStaff.StaffNo,WorkMonth:varMonth,Revision:Text(GUID())}),
                        Patch(colMonths,existing,{Revision:Text(GUID())})
                    )
                );
                Set(varLoaded,false); Clear(colDraft);
                Notify("月分をアプリ内に登録しました。",NotificationType.Success)
            )
          DisplayMode: =If(varLoaded && !varDayDirty, DisplayMode.Edit, DisplayMode.Disabled)
    - ddDayType:
        Control: Classic/DropDown@2.3.1
        Properties:
          X: =834
          Y: =306
          Width: =460
          Height: =44
          Items: =["勤務日", "全日欠勤", "非勤務日"]
          Value: ="Value"
          Default: =If(Coalesce(LookUp(colDraft,WorkDate=varDayDate,FullDayAbsence),false),"全日欠勤",If(Coalesce(LookUp(colDraft,WorkDate=varDayDate,PlannedDay),false),"勤務日","非勤務日"))
          Size: =16
          Font: ="Meiryo"
          AccessibleLabel: ="勤務日・全日欠勤・非勤務日の区分"
          DisplayMode: =If(varLoaded, DisplayMode.Edit, DisplayMode.Disabled)
          OnChange: =Set(varDayDirty,true)
    - lblAbsence:
        Control: Label@2.5.1
        Properties:
          Text: ="欠勤時間（通常＋欠勤＝7時間45分）"
          X: =834
          Y: =430
          Width: =490
          Height: =36
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - txtAbsHour:
        Control: Classic/TextInput@2.3.2
        Properties:
          X: =834
          Y: =468
          Width: =90
          Height: =44
          Default: =Text(Int(Coalesce(LookUp(colDraft,WorkDate=varDayDate,AbsenceMinutes),0)/60))
          Format: =TextFormat.Number
          Size: =18
          Font: ="Meiryo"
          AccessibleLabel: ="欠勤時間の時間"
          OnChange: =Set(varDayDirty, true)
          DisplayMode: =If(varLoaded, DisplayMode.Edit, DisplayMode.Disabled)
    - lblAH:
        Control: Label@2.5.1
        Properties:
          Text: ="時間"
          X: =930
          Y: =472
          Width: =56
          Height: =36
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - txtAbsMinute:
        Control: Classic/TextInput@2.3.2
        Properties:
          X: =996
          Y: =468
          Width: =90
          Height: =44
          Default: =Text(Mod(Coalesce(LookUp(colDraft,WorkDate=varDayDate,AbsenceMinutes),0),60))
          Format: =TextFormat.Number
          Size: =18
          Font: ="Meiryo"
          AccessibleLabel: ="欠勤時間の分"
          OnChange: =Set(varDayDirty, true)
          DisplayMode: =If(varLoaded, DisplayMode.Edit, DisplayMode.Disabled)
    - lblAM:
        Control: Label@2.5.1
        Properties:
          Text: ="分"
          X: =1092
          Y: =472
          Width: =56
          Height: =36
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
```

### SCR-005 支給明細画面のYAML：scrPayroll

```yaml
- conPayrollPrototype:
    Control: GroupContainer@1.3.0
    Variant: ManualLayout
    Properties:
      X: =0
      Y: =0
      Width: =Parent.Width
      Height: =Parent.Height
      Fill: =Color.White
    Children:
    - lblPTitle:
        Control: Label@2.5.1
        Properties:
          Text: ="支給明細画面"
          X: =24
          Y: =16
          Width: =1000
          Height: =48
          Size: =26
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
          FontWeight: =FontWeight.Semibold
    - btnToAttendance:
        Control: Classic/Button@2.2.0
        Properties:
          Text: ="勤務報告へ"
          X: =1120
          Y: =24
          Width: =210
          Height: =44
          Size: =16
          Font: ="Meiryo"
          Fill: =RGBA(241, 246, 251, 1)
          Color: =RGBA(0, 74, 153, 1)
          BorderThickness: =0
          RadiusTopLeft: =8
          RadiusTopRight: =8
          RadiusBottomLeft: =8
          RadiusBottomRight: =8
          OnSelect: =Navigate(scrAttendance,ScreenTransition.None)
          DisplayMode: =If(true, DisplayMode.Edit, DisplayMode.Disabled)
    - lblPStaff:
        Control: Label@2.5.1
        Properties:
          Text: ="職員番号・氏名"
          X: =24
          Y: =78
          Width: =400
          Height: =36
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - ddPayStaff:
        Control: Classic/DropDown@2.3.1
        Properties:
          X: =24
          Y: =118
          Width: =440
          Height: =44
          Items: =colStaff
          Value: ="StaffLabel"
          Default: =First(colStaff).StaffLabel
          Size: =16
          Font: ="Meiryo"
          AccessibleLabel: ="職員番号・氏名"
          DisplayMode: =If(true, DisplayMode.Edit, DisplayMode.Disabled)
    - lblPMonth:
        Control: Label@2.5.1
        Properties:
          Text: ="勤務月（その月の日付）"
          X: =488
          Y: =78
          Width: =310
          Height: =36
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - dpPayMonth:
        Control: Classic/DatePicker@2.6.0
        Properties:
          X: =488
          Y: =118
          Width: =210
          Height: =44
          DefaultDate: =Date(2026, 9, 1)
          Format: ="yyyy/mm/dd"
          Language: ="ja-JP"
          Size: =16
          Font: ="Meiryo"
          AccessibleLabel: ="勤務月。その月の任意の日付を選択"
          DisplayMode: =If(true, DisplayMode.Edit, DisplayMode.Disabled)
    - btnCalculate:
        Control: Classic/Button@2.2.0
        Properties:
          Text: ="給与を計算"
          X: =722
          Y: =118
          Width: =210
          Height: =44
          Size: =16
          Font: ="Meiryo"
          Fill: =RGBA(0, 74, 153, 1)
          Color: =Color.White
          BorderThickness: =0
          RadiusTopLeft: =8
          RadiusTopRight: =8
          RadiusBottomLeft: =8
          RadiusBottomRight: =8
          OnSelect: |-
            =Set(varCalcReady,false);
            Set(varPayStaff,ddPayStaff.Selected);
            Set(varPayMonth,Date(Year(dpPayMonth.SelectedDate),Month(dpPayMonth.SelectedDate),1));
            With({m:LookUp(colMonths,StaffNo=varPayStaff.StaffNo && WorkMonth=varPayMonth)},
                If(IsBlank(m),
                    Notify("対象月の報告書は未登録です。",NotificationType.Warning),
                    varPayStaff.ScheduledMinutes<>465 || IsBlank(varPayStaff.AbsenceHourlyRate) || varPayStaff.AbsenceHourlyRate<0 || IsBlank(varPayStaff.DailyRate) || varPayStaff.DailyRate<0 ||
                    IsBlank(varPayStaff.OvertimeHourlyRate) || varPayStaff.OvertimeHourlyRate<0,
                    Notify("日額・欠勤時間単価・超過勤務単価・所定時間465分を確認してください。",NotificationType.Error),
                    With({rows:Filter(colAttendance,StaffNo=varPayStaff.StaffNo && WorkMonth=varPayMonth)},
                        Set(varWorkDays,CountIf(rows,RegularMinutes>0));
                        Set(varRegularMinutes,Sum(rows,RegularMinutes));
                        Set(varAbsenceMinutes,Sum(Filter(rows,RegularMinutes>0),AbsenceMinutes));
                        Set(varOvertimeMinutes,Sum(rows,OvertimeMinutes))
                    );
                    Set(varBasePay,varPayStaff.DailyRate*varWorkDays);
                    // 職員基本情報の欠勤時間単価を使用。日額から再計算しない。
                    Set(varAbsenceHourlyRate,varPayStaff.AbsenceHourlyRate);
                    // 各項目は丸めず保持。最終合計のみ円未満を切り捨て。
                    Set(varAbsenceDeduction,varAbsenceHourlyRate*(varAbsenceMinutes/60));
                    Set(varOvertimePay,varPayStaff.OvertimeHourlyRate*(varOvertimeMinutes/60));
                    Set(varTotalBeforeTruncation,varBasePay-varAbsenceDeduction+varOvertimePay);
                  Set(varFinalPay,RoundDown(varTotalBeforeTruncation,0));
                  Set(varPayRevision,m.Revision); Set(varCalcReady,true)
                )
            )
          DisplayMode: =If(!IsBlank(dpPayMonth.SelectedDate), DisplayMode.Edit, DisplayMode.Disabled)
    - lblPStatus:
        Control: Label@2.5.1
        Properties:
          Text: =If(varCalcReady && ddPayStaff.Selected.StaffNo=varPayStaff.StaffNo && Date(Year(dpPayMonth.SelectedDate),Month(dpPayMonth.SelectedDate),1)=varPayMonth && LookUp(colMonths,StaffNo=varPayStaff.StaffNo && WorkMonth=varPayMonth,Revision)=varPayRevision,varPayStaff.StaffLabel & " ／ " & Text(varPayMonth,"yyyy/mm") & " ／ 登録済み報告書", "対象を選んで計算してください。報告書更新後は再計算が必要です。")
          X: =24
          Y: =170
          Width: =1290
          Height: =42
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - lblBaseTitle:
        Control: Label@2.5.1
        Properties:
          Text: ="① 基本額（日額 × 勤務日数）"
          X: =24
          Y: =224
          Width: =1290
          Height: =36
          Size: =18
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
          FontWeight: =FontWeight.Semibold
          Fill: =RGBA(241, 246, 251, 1)
    - lblBaseFormula:
        Control: Label@2.5.1
        Properties:
          Text: =If(varCalcReady && ddPayStaff.Selected.StaffNo=varPayStaff.StaffNo && Date(Year(dpPayMonth.SelectedDate),Month(dpPayMonth.SelectedDate),1)=varPayMonth && LookUp(colMonths,StaffNo=varPayStaff.StaffNo && WorkMonth=varPayMonth,Revision)=varPayRevision,Text(varPayStaff.DailyRate,"#,##0") & "円/日 × " & Text(varWorkDays) & "日 ＝ " & Text(varBasePay,"#,##0") & "円","—")
          X: =40
          Y: =266
          Width: =1270
          Height: =44
          Size: =24
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - lblAbsTitle:
        Control: Label@2.5.1
        Properties:
          Text: ="② 欠勤控除（時間単価 × 欠勤時間）"
          X: =24
          Y: =324
          Width: =1290
          Height: =36
          Size: =18
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
          FontWeight: =FontWeight.Semibold
          Fill: =RGBA(241, 246, 251, 1)
    - lblAbsRate:
        Control: Label@2.5.1
        Properties:
          Text: =""
          X: =40
          Y: =366
          Width: =1270
          Height: =38
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
          Visible: =false
    - lblAbsFormula:
        Control: Label@2.5.1
        Properties:
          Text: =If(varCalcReady && ddPayStaff.Selected.StaffNo=varPayStaff.StaffNo && Date(Year(dpPayMonth.SelectedDate),Month(dpPayMonth.SelectedDate),1)=varPayMonth && LookUp(colMonths,StaffNo=varPayStaff.StaffNo && WorkMonth=varPayMonth,Revision)=varPayRevision,Text(varAbsenceHourlyRate,"#,##0.######") & "円/時 × " & If(Mod(varAbsenceMinutes,3)<>0,"約","") & Text(varAbsenceMinutes/60,"0.######") & "時間" & " ＝ " & Text(varAbsenceDeduction,"#,##0.######") & "円","—")
          X: =40
          Y: =376
          Width: =1270
          Height: =60
          Size: =22
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - lblOTTitle:
        Control: Label@2.5.1
        Properties:
          Text: ="③ 超過勤務手当（時間単価 × 超過勤務時間）"
          X: =24
          Y: =464
          Width: =1290
          Height: =36
          Size: =18
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
          FontWeight: =FontWeight.Semibold
          Fill: =RGBA(241, 246, 251, 1)
    - lblOTFormula:
        Control: Label@2.5.1
        Properties:
          Text: =If(varCalcReady && ddPayStaff.Selected.StaffNo=varPayStaff.StaffNo && Date(Year(dpPayMonth.SelectedDate),Month(dpPayMonth.SelectedDate),1)=varPayMonth && LookUp(colMonths,StaffNo=varPayStaff.StaffNo && WorkMonth=varPayMonth,Revision)=varPayRevision,Text(varPayStaff.OvertimeHourlyRate,"#,##0.######") & "円/時 × " & If(Mod(varOvertimeMinutes,3)<>0,"約","") & Text(varOvertimeMinutes/60,"0.######") & "時間" & " ＝ " & Text(varOvertimePay,"#,##0.######") & "円","—")
          X: =40
          Y: =506
          Width: =1270
          Height: =44
          Size: =24
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - lblTotalTitle:
        Control: Label@2.5.1
        Properties:
          Text: ="対象項目の支給額 ＝ ① 基本額 − ② 欠勤控除 ＋ ③ 超過勤務手当"
          X: =24
          Y: =572
          Width: =1290
          Height: =38
          Size: =18
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
          FontWeight: =FontWeight.Semibold
          Fill: =RGBA(241, 246, 251, 1)
    - lblTotalFormula:
        Control: Label@2.5.1
        Properties:
          Text: =If(varCalcReady && ddPayStaff.Selected.StaffNo=varPayStaff.StaffNo && Date(Year(dpPayMonth.SelectedDate),Month(dpPayMonth.SelectedDate),1)=varPayMonth && LookUp(colMonths,StaffNo=varPayStaff.StaffNo && WorkMonth=varPayMonth,Revision)=varPayRevision,"① − ② ＋ ③ ≈ " & Text(varTotalBeforeTruncation,"#,##0.######") & "円 → 切捨て後 " & Text(varFinalPay,"#,##0") & "円","—")
          X: =40
          Y: =616
          Width: =1270
          Height: =52
          Size: =26
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
          FontWeight: =FontWeight.Semibold
    - lblPRounding:
        Control: Label@2.5.1
        Properties:
          Text: ="端数処理：途中では丸めず、最終合計の円未満を切り捨て。中間額の表示は小数6桁の概数。"
          X: =24
          Y: =684
          Width: =1290
          Height: =32
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
    - lblPScope:
        Control: Label@2.5.1
        Properties:
          Text: ="全日欠勤は勤務日数にも欠勤控除にも含めません。通勤手当・税・社会保険料等は対象外です。"
          X: =24
          Y: =722
          Width: =1290
          Height: =32
          Size: =16
          Font: ="Meiryo"
          Color: =RGBA(28, 45, 65, 1)
```

## 7. 計算の中心部分

給与ボタン内の抜粋です。`rows` は職員番号・勤務月で抽出した登録済み明細です。導入には上のYAMLに含まれるボタン式全体を使ってください。

```powerfx
Set(varWorkDays,CountIf(rows,RegularMinutes>0));
Set(varAbsenceMinutes,Sum(Filter(rows,RegularMinutes>0),AbsenceMinutes));
Set(varOvertimeMinutes,Sum(rows,OvertimeMinutes));
Set(varBasePay,varPayStaff.DailyRate*varWorkDays);
Set(varAbsenceHourlyRate,varPayStaff.AbsenceHourlyRate);
Set(varAbsenceDeduction,varAbsenceHourlyRate*(varAbsenceMinutes/60));
Set(varOvertimePay,varPayStaff.OvertimeHourlyRate*(varOvertimeMinutes/60));
Set(varTotalBeforeTruncation,varBasePay-varAbsenceDeduction+varOvertimePay);
Set(varFinalPay,RoundDown(varTotalBeforeTruncation,0));
```

## 8. 確認シナリオ

日額9,750円、欠勤時間単価1,250円/時、超過勤務単価1,950円/時の期待値。小数部分は説明用の概数で、計算途中は丸めません。

| 条件 | 計算する勤務日数 | 欠勤控除（概数） | 最終支給額 |
|---|---:|---:|---:|
| 実勤務20日、欠勤・超過なし | 20日 | 0円 | 195,000円 |
| 実勤務20日、そのうち欠勤1時間、超過なし | 20日 | 1,250円 | 193,750円 |
| 実勤務20日、そのうち欠勤1時間、超過1時間（内蔵例） | 20日 | 1,250円 | 195,700円 |
| 勤務予定20日のうち全日欠勤1日、他は全時間勤務 | 19日 | 0円 | 185,250円 |
| 実勤務20日、そのうち欠勤30分、超過なし | 20日 | 625円 | 194,375円 |
| 勤務予定20日すべて全日欠勤 | 0日 | 0円 | 0円 |
| 登録済み全日非勤務 | 0日 | 0円 | 0円 |
| 実勤務20日、そのうち欠勤1分、超過1分 | 20日 | 20.833333円 | 195,011円 |

最後の例は超過勤務手当32.5円を丸めず足し、合計195,011.666666…円から円未満を切り捨てます。欠勤控除や超過勤務手当を先に整数化しないことを確認するケースです。

実機で確認する項目：全日欠勤を勤務日数・控除対象から除外／未登録月の通知／分60・負数・小数・空欄の拒否／勤務日の通常＋欠勤が465分／全日欠勤は欠勤465分のみ／未確認日があれば登録不可／再登録時の重複防止／報告書更新後の再計算／計算式の表示と結果の一致。

実施済み：YAML構文・式参照の静的確認、上記金額の独立計算。未実施：Power Appsランタイムでのコンパイル、操作・描画確認。

## 9. 次の段階

画面確認後にDataverseテーブルを定義します。勤務日・全日欠勤・非勤務日を区別し、単価履歴、有給区分、計算時単価の保存、重複防止・同時更新などを設計します。試作の `RemoveIf + Collect` はメモリ内専用で、Dataverseにはそのまま流用しません。

## 10. 技術資料

- [Microsoft公式：Collect・Clear・ClearCollect](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-clear-collect-clearcollect)
- [Microsoft公式：Patch](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-patch)

給与計算・端数処理はユーザー指定によります。



