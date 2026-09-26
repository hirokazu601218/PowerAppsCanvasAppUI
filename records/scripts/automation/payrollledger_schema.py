"""Exact 163-column workbook mapping plus Dataverse primary name and parent lookup."""
import json,re,uuid
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[2]
SPEC=json.loads((ROOT/'config/dataverse/payrollledger-columns.json').read_text())
FIELDS=SPEC['fields']
def label(text,lcid):return {'LocalizedLabels':[{'Label':text,'LanguageCode':lcid}]}
def attributes(lcid):
 attrs=[]
 for f in FIELDS:
  a={'SchemaName':f['logical_name'],'DisplayName':label(f['display_name'],lcid),'Description':label(f['source_constraint'],lcid),'RequiredLevel':{'Value':'None'}}
  kind=f['kind']
  if kind=='text':a.update({'@odata.type':'Microsoft.Dynamics.CRM.StringAttributeMetadata','MaxLength':f['max_length'],'FormatName':{'Value':'Text'}})
  elif kind=='date':a.update({'@odata.type':'Microsoft.Dynamics.CRM.DateTimeAttributeMetadata','Format':'DateOnly','DateTimeBehavior':{'Value':'DateOnly'}})
  elif kind=='integer':a.update({'@odata.type':'Microsoft.Dynamics.CRM.IntegerAttributeMetadata','MinValue':f['min'],'MaxValue':f['max'],'Format':'None'})
  elif kind=='decimal':a.update({'@odata.type':'Microsoft.Dynamics.CRM.DecimalAttributeMetadata','MinValue':f['min'],'MaxValue':f['max'],'Precision':f['precision']})
  attrs.append(a)
 attrs.append({'@odata.type':'Microsoft.Dynamics.CRM.StringAttributeMetadata','SchemaName':'crb3c_name','DisplayName':label('基準給与簿レコード名',lcid),'RequiredLevel':{'Value':'ApplicationRequired'},'MaxLength':100,'IsPrimaryName':True,'FormatName':{'Value':'Text'}})
 return attrs

def table(lcid):
 return {'@odata.type':'Microsoft.Dynamics.CRM.EntityMetadata','SchemaName':'crb3c_PayrollLedger','DisplayName':label('T_基準給与簿',lcid),'DisplayCollectionName':label('T_基準給与簿',lcid),'Description':label('添付T_基準給与簿_テーブル定義書163項目。職員基本1件に基準給与簿0件以上。テスト専用。',lcid),'OwnershipType':'UserOwned','IsActivity':False,'HasActivities':False,'HasNotes':False,'Attributes':attributes(lcid)}

def relationship(lcid,parent_id):
 return {'@odata.type':'Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata','SchemaName':'crb3c_staffbasic_payrollledger','ReferencedEntity':'crb3c_staffbasic','ReferencedAttribute':parent_id,'ReferencingEntity':'crb3c_payrollledger','ReferencingEntityNavigationPropertyName':'crb3c_StaffBasic','ReferencedEntityNavigationPropertyName':'crb3c_StaffBasic_PayrollLedgers','AssociatedMenuConfiguration':{'Behavior':'UseCollectionName','Group':'Details','Label':label('基準給与簿',lcid),'Order':10000},'CascadeConfiguration':{'Assign':'NoCascade','Delete':'Restrict','Merge':'NoCascade','Reparent':'NoCascade','Share':'NoCascade','Unshare':'NoCascade','RollupView':'NoCascade'},'Lookup':{'@odata.type':'Microsoft.Dynamics.CRM.LookupAttributeMetadata','SchemaName':'crb3c_StaffBasicId','DisplayName':label('職員基本',lcid),'Description':label('職員番号の代替キーで照合した親レコードへの参照。職員に基準給与簿0件を許容。',lcid),'RequiredLevel':{'Value':'ApplicationRequired'}}}


def build_fixtures(parents,parent_id):
    """Seven synthetic records, five existing parents; no real payroll calculation."""
    from calendar import monthrange
    by={p['crb3c_staffnumber']:p for p in parents}
    # Staff 03 has three periods; staff 04's period is before retirement.
    cases=[(3,4,250000,0),(3,5,255000,5000),(3,6,255000,-2000),
           (4,3,230000,0),(11,4,240000,0),(12,4,260000,0),(5,4,0,0)]
    rows=[]
    for sequence,(n,month,base,adjustment) in enumerate(cases,1):
        sid=f'0099000000{n:02}';p=by[sid]
        rid=f'PAY-2026{month:02}-{sid}'
        d={f['logical_name']:None if f['kind']=='text' else 0 for f in FIELDS}
        def put(**kw):d.update({'crb3c_'+k:v for k,v in kw.items()})
        gross=base+adjustment;tax=10000 if base else 0;net=gross-tax
        put(name=rid,period_year='令和08年',period_start=f'{month:02}月01日',
            period_end=f'{month:02}月{monthrange(2026,month)[1]:02}日',
            payment_date=f'令和08年{month:02}月23日',target_date=f'令和08年{month:02}月01日',
            organization=p.get('crb3c_orgfull') or p.get('crb3c_orgshort'),sequence=sequence,
            staffnumber=sid,fullname=p['crb3c_fullname'],basepay_current=base,
            basepay_adjustment=adjustment,gross=gross,taxable_total=gross,taxable_income=gross,
            income_tax_current=tax,deduction_total_current=tax,net=net,
            transfer1=net-50000 if n==12 else net,transfer2=50000 if n==12 else 0,
            business_type='月次給与',assignment_type='本務',classification='一般',
            remarks='合成テスト専用。金額は動作検証用の任意値。法定給与・税・保険計算を表さない。')
        rows.append({'id':str(uuid.uuid5(uuid.NAMESPACE_URL,'staff-payrollledger-fixture/'+rid)),
                     'parent_id':p[parent_id],'data':d})
    return rows


def validate_rows(rows,parents):
    import calendar
    from decimal import Decimal
    by={p['crb3c_staffnumber']:p for p in parents}
    assert len({r['id'] for r in rows})==len(rows)
    for row in rows:
        d=row['data'];sid=d['crb3c_staffnumber']
        assert re.fullmatch(r'[0-9]{12}',sid) and sid in by
        p=by[sid]
        assert row['parent_id']==p['crb3c_staffbasicid']
        assert d['crb3c_fullname']==p['crb3c_fullname']
        assert d['crb3c_organization']==(p.get('crb3c_orgfull') or p.get('crb3c_orgshort'))
        year=2018+int(re.fullmatch(r'令和([0-9]{2})年',d['crb3c_period_year'])[1])
        def md(v):
            match=re.fullmatch(r'([0-9]{2})月([0-9]{2})日',v)
            return date(year,int(match[1]),int(match[2]))
        start,end=md(d['crb3c_period_start']),md(d['crb3c_period_end'])
        assert start<=end and p.get('crb3c_hiredate'), 'No payroll before an established hire date'
        assert start>=date.fromisoformat(p['crb3c_hiredate'][:10])
        if p.get('crb3c_leavedate'):assert end<=date.fromisoformat(p['crb3c_leavedate'][:10])
        for key in ('payment_date','target_date'):
            m=re.fullmatch(r'令和([0-9]{2})年([0-9]{2})月([0-9]{2})日',d['crb3c_'+key])
            assert m
            date(2018+int(m[1]),int(m[2]),int(m[3]))
        for f in FIELDS:
            v=d[f['logical_name']]
            if v is None:continue
            if f['kind']=='text':assert isinstance(v,str) and len(v)<=f['max_length']
            elif f['kind']=='integer':assert type(v) is int and f['min']<=v<=f['max']
            else:
                assert isinstance(v,(int,float)) and f['min']<=v<=f['max']
                assert Decimal(str(v)).as_tuple().exponent>=-f['precision']
        value=lambda i:d[FIELDS[i-1]['logical_name']] or 0
        assert value(54)==sum(value(i) for i in range(12,54))
        assert value(54)==value(55)+value(56)
        for offset in (0,1):
            assert value(75+offset)==sum(value(i+offset) for i in range(57,74,2))
            assert value(107+offset)==value(75+offset)+sum(value(i+offset) for i in range(77,106,2))
        assert value(109)==value(54)-value(107)-value(108)
        assert value(109)==value(110)+value(111)+value(112)
