"""Metadata for approved M_職員基本; does not grant privileges."""
PREFIX = 'crb3c_'
FIELDS = [
    ('staffnumber','職員番号','text',12,True),
    ('fullname','氏名','text',50,False),
    ('lastname','漢字姓','text',30,False),
    ('firstname','漢字名','text',30,False),
    ('email','メールアドレス','email',254,False),
    ('orgshort','組織名略称','text',50,False),
    ('orgfull','本務組織','text',100,False),
    ('birthdate','生年月日','date',None,False),
    ('sex','性別','choice',['男','女'],False),
    ('employmenttype','職員雇用区分','text',30,False),
    ('hiredate','採用日','date',None,False),
    ('leavedate','退職日','date',None,False),
    ('workregistered','給与条件登録','choice',['登録','未登録'],False),
    ('dailyrate','日額単価','integer',None,False),
    ('workminutes','勤務時間（分）','integer',None,False),
    ('commuteregistered','通勤登録','choice',['登録','未登録'],False),
    ('commutemethod','支給方式','text',200,False),
    ('passamount','定期額','integer',None,False),
    ('onewayfare','IC片道運賃','integer',None,False),
    ('pension','厚生年金','choice',['加入','未加入'],False),
    ('employmentinsurance','雇用保険','choice',['加入','未加入'],False),
    ('mutualshort','共済短期','choice',['加入','未加入'],False),
    ('mutuallong','共済長期','choice',['加入','未加入'],False),
    ('taxclass','税表区分','choice',['甲','乙'],True),
]


def label(text, lcid):
    return {'LocalizedLabels':[{'Label':text,'LanguageCode':lcid}]}


def attributes(lcid):
    result=[]
    for name,title,kind,arg,required in FIELDS:
        a={'SchemaName':PREFIX+name, 'DisplayName':label(title,lcid),
           'RequiredLevel':{'Value':'ApplicationRequired' if required else 'None'}}
        if kind in ('text','email'):
            a.update({'@odata.type':'Microsoft.Dynamics.CRM.StringAttributeMetadata',
                      'MaxLength':arg,'FormatName':{'Value':'Email' if kind=='email' else 'Text'}})
            if name=='staffnumber': a['IsPrimaryName']=True
        elif kind=='date':
            a.update({'@odata.type':'Microsoft.Dynamics.CRM.DateTimeAttributeMetadata',
                      'Format':'DateOnly','DateTimeBehavior':{'Value':'DateOnly'}})
        elif kind=='integer':
            a.update({'@odata.type':'Microsoft.Dynamics.CRM.IntegerAttributeMetadata',
                      'MinValue':0,'MaxValue':2147483647,'Format':'None'})
        elif kind=='choice':
            a.update({'@odata.type':'Microsoft.Dynamics.CRM.PicklistAttributeMetadata',
                      'OptionSet':{'@odata.type':'Microsoft.Dynamics.CRM.OptionSetMetadata',
                      'IsGlobal':False,'OptionSetType':'Picklist',
                      'Options':[{'Value':100000000+i,'Label':label(v,lcid)} for i,v in enumerate(arg)]}})
        result.append(a)
    return result


def table(lcid):
    return {'@odata.type':'Microsoft.Dynamics.CRM.EntityMetadata',
            'SchemaName':'crb3c_StaffBasic','DisplayName':label('M_職員基本',lcid),
            'DisplayCollectionName':label('M_職員基本',lcid),
            'Description':label('架空データによる職員マスタ検索検証。1人1行、最新情報。',lcid),
            'OwnershipType':'UserOwned','IsActivity':False,'HasActivities':False,
            'HasNotes':False,'Attributes':attributes(lcid)}


def payload(row):
    result={}
    for name,title,kind,arg,required in FIELDS:
        value=row.get(name)
        if value in ('',None): continue
        if kind=='choice': value=100000000+arg.index(value)
        if kind=='date': value+='T00:00:00Z'
        result[PREFIX+name]=value
    return result
