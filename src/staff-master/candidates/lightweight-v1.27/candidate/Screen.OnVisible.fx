Set(varCommuteReportBase111,"");Set(varStaffDetailTab111,Coalesce(varStaffDetailTab111,"Basic"));
Set(varPayrollStart111,Coalesce(varPayrollStart111,Date(Year(Today()),1,1)));Set(varPayrollEnd111,Coalesce(varPayrollEnd111,Date(Year(Today()),12,1)));
Set(varFetched111,Blank());Set(varFetchError111,Blank());Set(varStaffChosen111,true);
IfError(Refresh('M_職員基本_STUDIO');Refresh('T_通勤_STUDIO');Refresh('T_基準給与簿_STUDIO');ClearCollect(colStaffSource111,Filter('M_職員基本_STUDIO',crb3c_orgshort=UiDepartment));
Set(varStaff111,Coalesce(LookUp(StaffBasicView,StaffId=varStaff111.StaffId),First(StaffBasicView)));Set(varResultsReady111,false);Select(btnLoadDetails111),
Clear(colStaffSource111);Set(varStaff111,Blank());Select(btnLoadDetails111);Set(varFetchError111,"職員データを取得できませんでした");Set(varFetched111,Blank()));