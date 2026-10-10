=Set(varStaffDetailTab111,ThisItem.Key);
Set(varHistoryId111,With({rememberedId:LookUp(colHistorySelection111,Section=varStaffDetailTab111).RecordId},
Coalesce(LookUp(colHistory111,Section=varStaffDetailTab111 && RecordId=rememberedId).RecordId,
First(Filter(colHistory111,Section=varStaffDetailTab111)).RecordId))); Reset(galHistory111)
