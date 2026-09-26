StaffReferenceDate = DateValue(Text(DateAdd(Now(), TimeZoneOffset(Now()) + 540, TimeUnit.Minutes), "yyyy-mm-dd"), "en-US");
StaffTestCount = CountIf('M_職員基本', true);
StaffBasicView = If(StaffTestCount <= 100, ForAll(
    SortByColumns('M_職員基本', "crb3c_staffnumber", SortOrder.Ascending) As s,
    {
        StaffId: s.crb3c_staffnumber,
        Name: s.crb3c_fullname,
        Org: s.crb3c_orgshort,
        OrgFull: s.crb3c_orgfull,
        Birth: Text(s.crb3c_birthdate, "yyyy/mm/dd"),
        Sex: Text(s.crb3c_sex),
        Hire: Text(s.crb3c_hiredate, "yyyy/mm/dd"),
        Leave: Text(s.crb3c_leavedate, "yyyy/mm/dd"),
        Status: If(IsBlank(s.crb3c_hiredate) || s.crb3c_hiredate > StaffReferenceDate, "採用前", !IsBlank(s.crb3c_leavedate) && s.crb3c_leavedate < StaffReferenceDate, "退職", "在籍"),
        WorkReg: If(Text(s.crb3c_workregistered)="登録","登録済",Text(s.crb3c_workregistered)),
        Daily: s.crb3c_dailyrate,
        Hours: If(IsBlank(s.crb3c_workminutes), Blank(), Text(RoundDown(s.crb3c_workminutes/60,0),"0") & ":" & Text(Mod(s.crb3c_workminutes,60),"00")),
        CommuteReg: If(Text(s.crb3c_commuteregistered)="登録","登録済",Text(s.crb3c_commuteregistered)),
        Method: s.crb3c_commutemethod,
        Pass: s.crb3c_passamount,
        Fare: s.crb3c_onewayfare,
        SocialReg: "",
        Health: Text(s.crb3c_mutualshort),
        Pension: Text(s.crb3c_pension),
        ResidentReg: "",
        TaxMay: Blank(),
        TaxJune: Blank(),
        TaxJuly: Blank(),
        FixedReg: If(IsBlank(s.crb3c_taxclass),"","登録済"),
        TaxClass: Text(s.crb3c_taxclass),
        Employment: Text(s.crb3c_employmentinsurance)
    }
));
// Commute records come only from Dataverse; no built-in commute fallback.
StaffSelected = If(Coalesce(varStaffChosen111,false),varStaff111,First(StaffBasicView));
StaffCommuteHistory = SortByColumns(
    Filter('T_通勤', '職員基本'.職員番号 = StaffSelected.StaffId),
    "crb3c_startdate",SortOrder.Ascending,"crb3c_recognitionid",SortOrder.Ascending
);
StaffLedgerFields = With({c:varLedgerCommute111,s:varLedgerStaff111},Table(
    {Field:"employee_name",Value:s.Name},
    {Field:"employee_number",Value:s.StaffId},
    {Field:"organization",Value:s.Org},
    {Field:"event_date_year",Value:If(IsBlank(c.crb3c_eventdate),Blank(),If(Year(c.crb3c_eventdate) >= 2019, Text(Year(c.crb3c_eventdate)-2018,"0"), Text(Year(c.crb3c_eventdate),"0")))},
    {Field:"event_date_month",Value:If(IsBlank(c.crb3c_eventdate),Blank(),Text(Month(c.crb3c_eventdate),"0"))},
    {Field:"event_date_day",Value:If(IsBlank(c.crb3c_eventdate),Blank(),Text(Day(c.crb3c_eventdate),"0"))},
    {Field:"submitted_date_year",Value:If(IsBlank(c.crb3c_submitteddate),Blank(),If(Year(c.crb3c_submitteddate) >= 2019, Text(Year(c.crb3c_submitteddate)-2018,"0"), Text(Year(c.crb3c_submitteddate),"0")))},
    {Field:"submitted_date_month",Value:If(IsBlank(c.crb3c_submitteddate),Blank(),Text(Month(c.crb3c_submitteddate),"0"))},
    {Field:"submitted_date_day",Value:If(IsBlank(c.crb3c_submitteddate),Blank(),Text(Day(c.crb3c_submitteddate),"0"))},
    {Field:"accepted_date_year",Value:If(IsBlank(c.crb3c_receiveddate),Blank(),If(Year(c.crb3c_receiveddate) >= 2019, Text(Year(c.crb3c_receiveddate)-2018,"0"), Text(Year(c.crb3c_receiveddate),"0")))},
    {Field:"accepted_date_month",Value:If(IsBlank(c.crb3c_receiveddate),Blank(),Text(Month(c.crb3c_receiveddate),"0"))},
    {Field:"accepted_date_day",Value:If(IsBlank(c.crb3c_receiveddate),Blank(),Text(Day(c.crb3c_receiveddate),"0"))},
    {Field:"route_1_transport",Value:c.crb3c_route1_operator},
    {Field:"route_1_section_from",Value:c.crb3c_route1_from},
    {Field:"route_1_section_to",Value:c.crb3c_route1_to},
    {Field:"route_1_ticket_type",Value:c.crb3c_route1_tickettype},
    {Field:"route_1_other_basis",Value:If(IsBlank(c.crb3c_route1_ticketbasis),Blank(),If(Mod(c.crb3c_route1_ticketbasis,1)=0,Text(c.crb3c_route1_ticketbasis,"0"),Text(c.crb3c_route1_ticketbasis,"0.####")))},
    {Field:"route_1_season_basis",Value:If(IsBlank(c.crb3c_route1_distancekm),Blank(),If(Mod(c.crb3c_route1_distancekm,1)=0,Text(c.crb3c_route1_distancekm,"0"),Text(c.crb3c_route1_distancekm,"0.####")))},
    {Field:"route_1_other_amount",Value:If(IsBlank(c.crb3c_route1_ticketamount),Blank(),Text(c.crb3c_route1_ticketamount,"#,##0"))},
    {Field:"route_1_season_amount",Value:If(IsBlank(c.crb3c_route1_passamount),Blank(),Text(c.crb3c_route1_passamount,"#,##0"))},
    {Field:"route_1_season_months",Value:If(IsBlank(c.crb3c_route1_passmonths),Blank(),Text(c.crb3c_route1_passmonths,"0"))},
    {Field:"route_1_monthly_amount",Value:If(IsBlank(c.crb3c_route1_amount),Blank(),Text(c.crb3c_route1_amount,"#,##0"))},
    {Field:"route_1_period_start_year",Value:If(IsBlank(c.crb3c_route1_recognitionstart),Blank(),If(Year(c.crb3c_route1_recognitionstart) >= 2019,"令和" & Text(Year(c.crb3c_route1_recognitionstart)-2018,"0") & "年",Text(Year(c.crb3c_route1_recognitionstart),"0") & "年"))},
    {Field:"route_1_period_start_month",Value:If(IsBlank(c.crb3c_route1_recognitionstart),Blank(),Text(Month(c.crb3c_route1_recognitionstart),"0") & "月から")},
    {Field:"route_1_payment_months",Value:If(IsBlank(c.crb3c_route1_paymonth),Blank(),Text(c.crb3c_route1_paymonth,"0") & "月")},
    {Field:"route_1_remarks",Value:c.crb3c_route1_remarks},
    {Field:"route_2_transport",Value:c.crb3c_route2_operator},
    {Field:"route_2_section_from",Value:c.crb3c_route2_from},
    {Field:"route_2_section_to",Value:c.crb3c_route2_to},
    {Field:"route_2_ticket_type",Value:c.crb3c_route2_tickettype},
    {Field:"route_2_other_basis",Value:If(IsBlank(c.crb3c_route2_ticketbasis),Blank(),If(Mod(c.crb3c_route2_ticketbasis,1)=0,Text(c.crb3c_route2_ticketbasis,"0"),Text(c.crb3c_route2_ticketbasis,"0.####")))},
    {Field:"route_2_season_basis",Value:If(IsBlank(c.crb3c_route2_distancekm),Blank(),If(Mod(c.crb3c_route2_distancekm,1)=0,Text(c.crb3c_route2_distancekm,"0"),Text(c.crb3c_route2_distancekm,"0.####")))},
    {Field:"route_2_other_amount",Value:If(IsBlank(c.crb3c_route2_ticketamount),Blank(),Text(c.crb3c_route2_ticketamount,"#,##0"))},
    {Field:"route_2_season_amount",Value:If(IsBlank(c.crb3c_route2_passamount),Blank(),Text(c.crb3c_route2_passamount,"#,##0"))},
    {Field:"route_2_season_months",Value:If(IsBlank(c.crb3c_route2_passmonths),Blank(),Text(c.crb3c_route2_passmonths,"0"))},
    {Field:"route_2_monthly_amount",Value:If(IsBlank(c.crb3c_route2_amount),Blank(),Text(c.crb3c_route2_amount,"#,##0"))},
    {Field:"route_2_period_start_year",Value:If(IsBlank(c.crb3c_route2_recognitionstart),Blank(),If(Year(c.crb3c_route2_recognitionstart) >= 2019,"令和" & Text(Year(c.crb3c_route2_recognitionstart)-2018,"0") & "年",Text(Year(c.crb3c_route2_recognitionstart),"0") & "年"))},
    {Field:"route_2_period_start_month",Value:If(IsBlank(c.crb3c_route2_recognitionstart),Blank(),Text(Month(c.crb3c_route2_recognitionstart),"0") & "月から")},
    {Field:"route_2_payment_months",Value:If(IsBlank(c.crb3c_route2_paymonth),Blank(),Text(c.crb3c_route2_paymonth,"0") & "月")},
    {Field:"route_2_remarks",Value:c.crb3c_route2_remarks},
    {Field:"route_3_transport",Value:c.crb3c_route3_operator},
    {Field:"route_3_section_from",Value:c.crb3c_route3_from},
    {Field:"route_3_section_to",Value:c.crb3c_route3_to},
    {Field:"route_3_ticket_type",Value:c.crb3c_route3_tickettype},
    {Field:"route_3_other_basis",Value:If(IsBlank(c.crb3c_route3_ticketbasis),Blank(),If(Mod(c.crb3c_route3_ticketbasis,1)=0,Text(c.crb3c_route3_ticketbasis,"0"),Text(c.crb3c_route3_ticketbasis,"0.####")))},
    {Field:"route_3_season_basis",Value:If(IsBlank(c.crb3c_route3_distancekm),Blank(),If(Mod(c.crb3c_route3_distancekm,1)=0,Text(c.crb3c_route3_distancekm,"0"),Text(c.crb3c_route3_distancekm,"0.####")))},
    {Field:"route_3_other_amount",Value:If(IsBlank(c.crb3c_route3_ticketamount),Blank(),Text(c.crb3c_route3_ticketamount,"#,##0"))},
    {Field:"route_3_season_amount",Value:If(IsBlank(c.crb3c_route3_passamount),Blank(),Text(c.crb3c_route3_passamount,"#,##0"))},
    {Field:"route_3_season_months",Value:If(IsBlank(c.crb3c_route3_passmonths),Blank(),Text(c.crb3c_route3_passmonths,"0"))},
    {Field:"route_3_monthly_amount",Value:If(IsBlank(c.crb3c_route3_amount),Blank(),Text(c.crb3c_route3_amount,"#,##0"))},
    {Field:"route_3_period_start_year",Value:If(IsBlank(c.crb3c_route3_recognitionstart),Blank(),If(Year(c.crb3c_route3_recognitionstart) >= 2019,"令和" & Text(Year(c.crb3c_route3_recognitionstart)-2018,"0") & "年",Text(Year(c.crb3c_route3_recognitionstart),"0") & "年"))},
    {Field:"route_3_period_start_month",Value:If(IsBlank(c.crb3c_route3_recognitionstart),Blank(),Text(Month(c.crb3c_route3_recognitionstart),"0") & "月から")},
    {Field:"route_3_payment_months",Value:If(IsBlank(c.crb3c_route3_paymonth),Blank(),Text(c.crb3c_route3_paymonth,"0") & "月")},
    {Field:"route_3_remarks",Value:c.crb3c_route3_remarks},
    {Field:"route_4_transport",Value:c.crb3c_route4_operator},
    {Field:"route_4_section_from",Value:c.crb3c_route4_from},
    {Field:"route_4_section_to",Value:c.crb3c_route4_to},
    {Field:"route_4_ticket_type",Value:c.crb3c_route4_tickettype},
    {Field:"route_4_other_basis",Value:If(IsBlank(c.crb3c_route4_ticketbasis),Blank(),If(Mod(c.crb3c_route4_ticketbasis,1)=0,Text(c.crb3c_route4_ticketbasis,"0"),Text(c.crb3c_route4_ticketbasis,"0.####")))},
    {Field:"route_4_season_basis",Value:If(IsBlank(c.crb3c_route4_distancekm),Blank(),If(Mod(c.crb3c_route4_distancekm,1)=0,Text(c.crb3c_route4_distancekm,"0"),Text(c.crb3c_route4_distancekm,"0.####")))},
    {Field:"route_4_other_amount",Value:If(IsBlank(c.crb3c_route4_ticketamount),Blank(),Text(c.crb3c_route4_ticketamount,"#,##0"))},
    {Field:"route_4_season_amount",Value:If(IsBlank(c.crb3c_route4_passamount),Blank(),Text(c.crb3c_route4_passamount,"#,##0"))},
    {Field:"route_4_season_months",Value:If(IsBlank(c.crb3c_route4_passmonths),Blank(),Text(c.crb3c_route4_passmonths,"0"))},
    {Field:"route_4_monthly_amount",Value:If(IsBlank(c.crb3c_route4_amount),Blank(),Text(c.crb3c_route4_amount,"#,##0"))},
    {Field:"route_4_period_start_year",Value:If(IsBlank(c.crb3c_route4_recognitionstart),Blank(),If(Year(c.crb3c_route4_recognitionstart) >= 2019,"令和" & Text(Year(c.crb3c_route4_recognitionstart)-2018,"0") & "年",Text(Year(c.crb3c_route4_recognitionstart),"0") & "年"))},
    {Field:"route_4_period_start_month",Value:If(IsBlank(c.crb3c_route4_recognitionstart),Blank(),Text(Month(c.crb3c_route4_recognitionstart),"0") & "月から")},
    {Field:"route_4_payment_months",Value:If(IsBlank(c.crb3c_route4_paymonth),Blank(),Text(c.crb3c_route4_paymonth,"0") & "月")},
    {Field:"route_4_remarks",Value:c.crb3c_route4_remarks},
    {Field:"monthly_amount_total",Value:If(IsBlank(c.crb3c_monthlytotal),Blank(),Text(c.crb3c_monthlytotal,"#,##0"))}
));
// Payroll history is filtered on its parent employee in Dataverse.
StaffPayrollHistory = SortByColumns(
    Filter('T_基準給与簿', '職員基本'.職員番号 = StaffSelected.StaffId),
    "crb3c_payment_date",SortOrder.Descending,"crb3c_sequence",SortOrder.Descending
);
// Synthetic histories: source is tests/fixtures/staff-history-synthetic.json.
StaffWorkHistory = Table(
    {StaffId:"009900000003", RecordId:"W-3-CURRENT", Start:Date(2026,4,1), End:Date(2027,3,31), Daily:15000, Scheduled:"7:45", Hours:"7:45", Overtime:0, Change:"合成テスト", Reason:"職員03の勤務条件", Finish:"17:00", DailyHours:7.75},
    {StaffId:"009900000003", RecordId:"W-3-PAST", Start:Date(2025,4,1), End:Date(2026,3,31), Daily:14000, Scheduled:"7:45", Hours:"7:45", Overtime:0, Change:"合成テスト", Reason:"過去の合成テスト", Finish:"17:00", DailyHours:7.75},
    {StaffId:"009900000003", RecordId:"W-3-FUTURE", Start:Date(2027,4,1), End:Date(2099,3,31), Daily:16000, Scheduled:"7:45", Hours:"7:45", Overtime:0, Change:"合成テスト", Reason:"将来の合成テスト", Finish:"17:00", DailyHours:7.75},
    {StaffId:"009900000005", RecordId:"W-5-CURRENT", Start:Date(2026,4,1), End:Date(2099,3,31), Daily:0, Scheduled:"0:00", Hours:"0:00", Overtime:0, Change:"合成テスト", Reason:"職員05の勤務条件", Finish:"17:00", DailyHours:0.0},
    {StaffId:"009900000011", RecordId:"W-11-CURRENT", Start:Date(2026,4,1), End:Date(2099,3,31), Daily:11100, Scheduled:"8:00", Hours:"8:00", Overtime:0, Change:"合成テスト", Reason:"職員11の勤務条件", Finish:"17:00", DailyHours:8.0},
    {StaffId:"009900000012", RecordId:"W-12-CURRENT", Start:Date(2026,4,1), End:Date(2099,3,31), Daily:11200, Scheduled:"0:00", Hours:"0:00", Overtime:0, Change:"合成テスト", Reason:"職員12の勤務条件", Finish:"17:00", DailyHours:0.0},
    {StaffId:"009900000025", RecordId:"W-25-CURRENT", Start:Date(2026,4,1), End:Date(2099,3,31), Daily:12500, Scheduled:"6:00", Hours:"6:00", Overtime:0, Change:"合成テスト", Reason:"職員25の勤務条件", Finish:"17:00", DailyHours:6.0}
);
StaffSocialHistory = Table(
    {StaffId:"009900000003", RecordId:"S-3-2026", Category:"合成テスト", Birth:"2000/04/01", AgeApril:26, AgeMarch:27, Care:"テスト・判定対象外", PensionExempt:"テスト・判定対象外", Elderly:"テスト・判定対象外", Grade:0, Monthly:203000},
    {StaffId:"009900000005", RecordId:"S-5-2026", Category:"合成テスト", Birth:"2000/04/01", AgeApril:26, AgeMarch:27, Care:"テスト・判定対象外", PensionExempt:"テスト・判定対象外", Elderly:"テスト・判定対象外", Grade:0, Monthly:0},
    {StaffId:"009900000011", RecordId:"S-11-2026", Category:"合成テスト", Birth:"1981/04/01", AgeApril:45, AgeMarch:46, Care:"テスト・判定対象外", PensionExempt:"テスト・判定対象外", Elderly:"テスト・判定対象外", Grade:0, Monthly:211000},
    {StaffId:"009900000012", RecordId:"S-12-2026", Category:"合成テスト", Birth:"1982/04/01", AgeApril:44, AgeMarch:45, Care:"テスト・判定対象外", PensionExempt:"テスト・判定対象外", Elderly:"テスト・判定対象外", Grade:0, Monthly:212000},
    {StaffId:"009900000025", RecordId:"S-25-2026", Category:"合成テスト", Birth:"1995/04/01", AgeApril:31, AgeMarch:32, Care:"テスト・判定対象外", PensionExempt:"テスト・判定対象外", Elderly:"テスト・判定対象外", Grade:0, Monthly:225000}
);
StaffTaxHistory = Table(
    {StaffId:"009900000003", RecordId:"T-3-2026", Start:Date(2026,4,1), End:Date(2099,3,31), TaxClass:"甲", Employment:"加入", Saving:0, Loan:0, Dependents:0, Note:"職員03専用の合成データ・計算検証対象外"},
    {StaffId:"009900000005", RecordId:"T-5-2026", Start:Date(2026,4,1), End:Date(2099,3,31), TaxClass:"甲", Employment:"未設定", Saving:0, Loan:0, Dependents:0, Note:"職員05専用の合成データ・計算検証対象外"},
    {StaffId:"009900000011", RecordId:"T-11-2026", Start:Date(2026,4,1), End:Date(2099,3,31), TaxClass:"甲", Employment:"加入", Saving:0, Loan:0, Dependents:0, Note:"職員11専用の合成データ・計算検証対象外"},
    {StaffId:"009900000012", RecordId:"T-12-2026", Start:Date(2026,4,1), End:Date(2099,3,31), TaxClass:"乙", Employment:"未加入", Saving:0, Loan:0, Dependents:0, Note:"職員12専用の合成データ・計算検証対象外"},
    {StaffId:"009900000025", RecordId:"T-25-2026", Start:Date(2026,4,1), End:Date(2099,3,31), TaxClass:"甲", Employment:"加入", Saving:0, Loan:0, Dependents:0, Note:"職員25専用の合成データ・計算検証対象外"}
);
StaffResidentHistory = FirstN(Table({StaffId:"",Amount:0,Period:"",Start:Date(2000,1,1),End:Date(2000,1,1)}),0);
