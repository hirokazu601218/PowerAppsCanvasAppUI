// v1.22 UI prototype. All new monetary and access-profile values are synthetic.
UiTheme = {Header:ColorValue("#073B78"),Primary:ColorValue("#0F6CBD"),Text:ColorValue("#242424"),Background:ColorValue("#F7F9FC"),Band:ColorValue("#EDF2F7"),Border:ColorValue("#CBD5E1"),Selected:ColorValue("#DCEAFF")};
UiDepartment = Coalesce(varUiDepartment,"03会計課");
UiIsAdmin = Coalesce(varUiAdmin,false);
UiAccount = {Name:User().FullName,Email:User().Email,Department:UiDepartment,IsAdmin:UiIsAdmin};
UiMonth = Coalesce(varUiMonth,Date(2026,9,1));
UiStaff = ForAll(StaffBasicView As s,{StaffNo:s.StaffId,Name:s.Name,Org:s.Org,DailyRate:9750,AbsenceHourlyRate:1250,ScheduledMinutes:465});
UiSelected = LookUp(UiStaff,StaffNo=varUiStaffNo && Org=UiDepartment);
UiVersion = Coalesce(varUiRegistrationVersion,1);
UiTargetKey = Coalesce(varUiStaffNo,"") & "|" & Text(UiMonth,"yyyy-mm") & "|" & Text(UiVersion);
UiDays = If(Month(UiMonth)=11,0,20);
UiAbsence = If(Month(UiMonth)=11,0,Coalesce(varUiAbsenceMinutes,60));
UiCommute = If(Month(UiMonth)=11,0,6250);
UiRegistered = Month(UiMonth)<>10;
UiFixed = UiSelected.DailyRate * UiDays;
UiReduction = UiSelected.AbsenceHourlyRate * UiAbsence / 60;
UiSalary = UiFixed-UiReduction;
UiGross = UiSalary+UiCommute;
UiDeductionRows = Table(
 {Code:"mutual_short_current",Name:"共済短期掛金",Group:"社会保険関係",Basis:"短期・月額 200,000円 × 仮率4.50%",Amount:9000},
 {Code:"mutual_childcare_current",Name:"子ども・子育て支援掛金",Group:"社会保険関係",Basis:"算定基礎額 200,000円 × 仮率0.10%",Amount:200},
 {Code:"retirement_contribution_current",Name:"退職等年金掛金",Group:"社会保険関係",Basis:"適用区分：対象外（仮例）",Amount:0},
 {Code:"pension_insurance_current",Name:"厚生年金保険料",Group:"社会保険関係",Basis:"厚生年金・月額 200,000円 × 仮率9.00%",Amount:18000},
 {Code:"employment_insurance_current",Name:"雇用保険料",Group:"社会保険関係",Basis:"対象賃金 200,000円 × 仮率0.50%",Amount:1000},
 {Code:"income_tax_current",Name:"所得税",Group:"税・その他",Basis:"税額表参照（仮）：被課税金額165,550円・甲欄・扶養0人。表示用の仮値",Amount:3000},
 {Code:"resident_tax_current",Name:"住民税",Group:"税・その他",Basis:"税額通知書の当月額（仮）を適用",Amount:7000},
 {Code:"savings_current",Name:"貯金預入",Group:"税・その他",Basis:"本人申込額（仮）：毎月10,000円",Amount:10000}
);
UiSocial = If(Month(UiMonth)=11,0,Sum(Filter(UiDeductionRows,Group="社会保険関係"),Amount));
UiDeductions = If(Month(UiMonth)=11,0,Sum(UiDeductionRows,Amount));
UiNet = RoundDown(UiGross-UiDeductions,0);
UiStatus = If(IsBlank(UiSelected.StaffNo),"職員マスタ検索で対象職員を選択してください",!UiRegistered,"勤務時間報告が未登録です",UiGross-UiDeductions<0,"要確認：負の最終額は本試作の対象外です",varUiResultKey<>UiTargetKey,"対象または勤務登録版が変わりました。再計算してください","");
UiReady = IsBlank(UiStatus);
UiDailyRows = ForAll(Sequence(30) As d,{WorkDate:Date(2026,Month(UiMonth),d.Value),DayType:If(d.Value<=20,"勤務日",d.Value=21,"全日欠勤","非勤務日"),RegularMinutes:If(d.Value=1,465-UiAbsence,d.Value<=20,465,0),AbsenceMinutes:If(d.Value=1,UiAbsence,d.Value=21,465,0)});
