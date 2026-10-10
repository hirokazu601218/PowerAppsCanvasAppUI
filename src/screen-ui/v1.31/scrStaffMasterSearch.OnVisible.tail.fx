=Set(varStaffDetailTab111,Coalesce(varStaffDetailTab111,"Basic"));
Set(varPayrollStart111,Coalesce(varPayrollStart111,Date(Year(Today()),1,1)));Set(varPayrollEnd111,Coalesce(varPayrollEnd111,Date(Year(Today()),12,1)));
Set(varFetched111,Blank());Set(varFetchError111,Blank());Set(varStaffChosen111,true);
IfError(Refresh('M_職員基本_STUDIO');Refresh('T_通勤_STUDIO');Refresh('T_基準給与簿_STUDIO');ClearCollect(colStaffSource111,Filter('M_職員基本_STUDIO',組織名略称=UiDepartment));
If(CountRows(colStaffSource111)>=500,Error({Kind:ErrorKind.Validation,Message:"職員の取得上限に達しました"}));
If(Coalesce(varResultsReady111,false) && varSearchDepartment111=UiDepartment,
ClearCollect(colResult111,Filter(StaffBasicView As s,(IsBlank(varSearchKeyword111) || Lower(varSearchKeyword111) in Lower(Text(s.StaffId) & "|" & Text(s.Name) & "|" & Text(s.OrgFull) & "|" & Text(s.Org) & "|" & Text(s.Birth) & "|" & Text(s.Sex) & "|" & Text(s.Hire) & "|" & Text(s.Leave) & "|" & Text(s.Status) & "|" & Text(s.WorkReg) & "|" & Text(s.Daily) & "|" & Text(s.Hours) & "|" & Text(s.CommuteReg) & "|" & Text(s.Method) & "|" & Text(s.Pass) & "|" & Text(s.Fare) & "|" & Text(s.SocialReg) & "|" & Text(s.Health) & "|" & Text(s.Pension) & "|" & Text(s.ResidentReg) & "|" & Text(s.TaxMay) & "|" & Text(s.TaxJune) & "|" & Text(s.TaxJuly) & "|" & Text(s.FixedReg) & "|" & Text(s.TaxClass) & "|" & Text(s.Employment))) && (varSearchOrg111="すべて" || s.Org=varSearchOrg111) && (varSearchStatus111="すべて" || s.Status=varSearchStatus111)));
Set(varStaff111,Coalesce(LookUp(colResult111,StaffId=varStaff111.StaffId),First(colResult111)));
Set(varPage111,Min(Max(1,Coalesce(varPage111,1)),Max(1,RoundUp(CountRows(colResult111)/20,0)))),
Set(varResultsReady111,false);Clear(colResult111);Set(varSearchDepartment111,UiDepartment);
Set(varStaff111,Coalesce(LookUp(StaffBasicView,StaffId=varStaff111.StaffId),First(StaffBasicView)));
Set(varPage111,Min(Max(1,Coalesce(varPage111,1)),Max(1,RoundUp(CountRows(StaffBasicView)/20,0)))));
Reset(galStaff111);true,
Clear(colStaffSource111);Clear(colResult111);Set(varResultsReady111,true);Set(varPage111,1);Set(varStaff111,Blank());
Clear(colCommute111);Clear(colWork111);Clear(colSocial111);Clear(colTax111);Clear(colResident111);Clear(colHistory111);Clear(colHistorySelection111);Clear(colPayrollSource111);Clear(colPayrollColumns111);Clear(colPayrollExceptions111);
Set(varStaffSource111,Blank());Set(varHistoryId111,Blank());Set(varHistoryStaff111,Blank());Set(varPayrollCellTitle111,Blank());Set(varPayrollCellText111,Blank());
Set(varFetchError111,"職員データを取得できませんでした：" & FirstError.Message);Set(varFetched111,Blank());Notify(varFetchError111,NotificationType.Error);false);
If(IsBlank(varFetchError111),Select(btnLoadDetails111));
