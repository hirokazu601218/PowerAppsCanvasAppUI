=Set(varHistoryId111,ThisItem.RecordId);
RemoveIf(colHistorySelection111,Section=varStaffDetailTab111);
Collect(colHistorySelection111,{Section:varStaffDetailTab111,RecordId:ThisItem.RecordId})
