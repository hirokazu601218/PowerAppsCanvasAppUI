Set(varFetched111,Blank()); Set(varFetchError111,Blank()); Set(varHistoryId111,Blank()); Set(varPayrollCellTitle111,Blank());Set(varPayrollCellText111,Blank()); Set(varHistoryStaff111,StaffSelected.StaffId);
Clear(colCommute111);Clear(colWork111);Clear(colSocial111);Clear(colTax111);Clear(colHistory111);Clear(colPayrollSource111);Clear(colPayrollColumns111);Clear(colPayrollExceptions111);
Set(varStaffSource111,LookUp(colStaffSource111,職員番号=StaffSelected.StaffId));
If(!IsBlank(StaffSelected.StaffId),IfError(
 ClearCollect(colCommute111,Filter('T_通勤_STUDIO',職員基本.職員番号=StaffSelected.StaffId));
 ClearCollect(colWork111,Filter(StaffWorkHistory,StaffId=StaffSelected.StaffId));
 ClearCollect(colSocial111,Filter(StaffSocialHistory,StaffId=StaffSelected.StaffId));
 ClearCollect(colTax111,Filter(StaffTaxHistory,StaffId=StaffSelected.StaffId));
 ClearCollect(colPayrollSource111,Filter('T_基準給与簿_STUDIO',crb3c_staffnumber=StaffSelected.StaffId));
 If(CountRows(colCommute111)>=500 || CountRows(colPayrollSource111)>=500,Error({Kind:ErrorKind.Validation,Message:"詳細の取得上限に達しました"}));
 ClearCollect(colHistory111,
 ForAll(colWork111 As p,{Section:"Work",RecordId:p.RecordId,Title:p.RecordId,Period:Text(p.Start,"yyyy/mm/dd") & " ～ " & If(p.End=Date(2099,3,31),"",Text(p.End,"yyyy/mm/dd")),State:If(p.Start>Today(),"予定",p.End<Today(),"過去","現行")}),
 ForAll(colSocial111 As p,{Section:"Social",RecordId:p.RecordId,Title:p.RecordId,Period:p.Category,State:"登録済"}),
 ForAll(colTax111 As p,{Section:"Tax",RecordId:p.RecordId,Title:p.RecordId,Period:Text(p.Start,"yyyy/mm/dd") & " ～ " & If(p.End=Date(2099,3,31),"",Text(p.End,"yyyy/mm/dd")),State:If(p.Start>Today(),"予定",p.End<Today(),"過去","現行")}),
 ForAll(colCommute111 As p,{Section:"Commute",RecordId:Text(p.T_通勤_STUDIO),Title:p.通勤認定ID & " / " & p.支給方式,Period:Text(p.適用開始日,"yyyy/mm/dd") & " ～ " & Text(p.適用終了日,"yyyy/mm/dd"),State:If(p.適用開始日>Today(),"予定",!IsBlank(p.適用終了日)&&p.適用終了日<Today(),"過去","現行")}));
Set(varHistoryId111,First(Filter(colHistory111,Section=varStaffDetailTab111)).RecordId);Clear(colPayrollColumns111); Clear(colPayrollExceptions111);
ForAll(colPayrollSource111 As p,With({dt:IfError(With({m:Match(Trim(Coalesce(p.crb3c_payment_date,"")),"(?<Era>令和|平成|昭和|R|H|S)(?<EraYear>元|[0-9]{1,2})[年./-](?<M>[0-9]{1,2})[月./-](?<D>[0-9]{1,2})日?",MatchOptions.Complete)},
 If(IsBlank(m.FullMatch),Blank(),With({y:Switch(m.Era,"令和",2018,"R",2018,"平成",1988,"H",1988,"昭和",1925,"S",1925)+If(m.EraYear="元",1,Value(m.EraYear)),mo:Value(m.M),dy:Value(m.D)},
 With({dt:Date(y,mo,dy)},If(Year(dt)=y && Month(dt)=mo && Day(dt)=dy && Value(Substitute(m.EraYear,"元","1"))>0 && Switch(m.Era,"令和",dt>=Date(2019,5,1),"R",dt>=Date(2019,5,1),"平成",dt>=Date(1989,1,8)&&dt<Date(2019,5,1),"H",dt>=Date(1989,1,8)&&dt<Date(2019,5,1),"昭和",dt>=Date(1926,12,25)&&dt<Date(1989,1,8),"S",dt>=Date(1926,12,25)&&dt<Date(1989,1,8),false),dt,Blank()))))),Blank())},
 If(IsBlank(dt),Collect(colPayrollExceptions111,{RecordId:Text(p.crb3c_studiopayrollledgerid),PaymentText:p.crb3c_payment_date}),
 dt>=varPayrollStart111 && dt<DateAdd(varPayrollEnd111,1,TimeUnit.Months),
 Collect(colPayrollColumns111,{RecordId:Text(p.crb3c_studiopayrollledgerid),PaymentDate:dt,Sequence:p.crb3c_sequence,Record:p}))));
 Set(varFetched111,Now()),
 Clear(colCommute111);Clear(colWork111);Clear(colSocial111);Clear(colTax111);Clear(colHistory111);Clear(colPayrollSource111);Clear(colPayrollColumns111);Clear(colPayrollExceptions111);Set(varHistoryId111,Blank());Set(varFetchError111,"詳細データを取得できませんでした：" & FirstError.Message);Notify(varFetchError111,NotificationType.Error)),Set(varFetched111,Now()));
