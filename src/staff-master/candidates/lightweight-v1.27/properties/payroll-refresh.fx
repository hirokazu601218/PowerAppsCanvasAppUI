Set(varPayrollStart111,Coalesce(varPayrollStart111,Date(Year(Today()),1,1)));
Set(varPayrollEnd111,Coalesce(varPayrollEnd111,Date(Year(Today()),12,1)));
Clear(colPayrollSource111); Clear(colPayrollColumns111); Clear(colPayrollExceptions111); Set(varPayrollFetched111,Blank());
If(!IsBlank(StaffSelected.StaffId),IfError(
 ClearCollect(colPayrollSource111,Filter('T_基準給与簿_STUDIO',crb3c_staffnumber=StaffSelected.StaffId));
 Clear(colPayrollColumns111); Clear(colPayrollExceptions111);
ForAll(colPayrollSource111 As p,With({dt:IfError(With({m:Match(Trim(Coalesce(p.crb3c_payment_date,"")),"(?<Era>令和|平成|昭和|R|H|S)(?<EraYear>元|[0-9]{1,2})[年./-](?<M>[0-9]{1,2})[月./-](?<D>[0-9]{1,2})日?",MatchOptions.Complete)},
 If(IsBlank(m.FullMatch),Blank(),With({y:Switch(m.Era,"令和",2018,"R",2018,"平成",1988,"H",1988,"昭和",1925,"S",1925)+If(m.EraYear="元",1,Value(m.EraYear)),mo:Value(m.M),dy:Value(m.D)},
 With({dt:Date(y,mo,dy)},If(Year(dt)=y && Month(dt)=mo && Day(dt)=dy && Value(Substitute(m.EraYear,"元","1"))>0 && Switch(m.Era,"令和",dt>=Date(2019,5,1),"R",dt>=Date(2019,5,1),"平成",dt>=Date(1989,1,8)&&dt<Date(2019,5,1),"H",dt>=Date(1989,1,8)&&dt<Date(2019,5,1),"昭和",dt>=Date(1926,12,25)&&dt<Date(1989,1,8),"S",dt>=Date(1926,12,25)&&dt<Date(1989,1,8),false),dt,Blank()))))),Blank())},
 If(IsBlank(dt),Collect(colPayrollExceptions111,{RecordId:Text(p.crb3c_studiopayrollledgerid),PaymentText:p.crb3c_payment_date}),
 dt>=varPayrollStart111 && dt<DateAdd(varPayrollEnd111,1,TimeUnit.Months),
 Collect(colPayrollColumns111,{RecordId:Text(p.crb3c_studiopayrollledgerid),PaymentDate:dt,Sequence:p.crb3c_sequence,Record:p}))));
 Set(varPayrollFetched111,Now()),
 Clear(colPayrollSource111); Clear(colPayrollColumns111); Clear(colPayrollExceptions111); Notify("給与データを取得できませんでした。",NotificationType.Error)));