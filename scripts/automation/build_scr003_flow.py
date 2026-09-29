"""Build the SCR-003 serialized mutation flow (connection-neutral source).

Deployment must bind the existing user's Excel, OneDrive and Dataverse connections.
This does not grant privileges or implement bureau/role authorization.
All app mutations must use this ONE flow to share its serialization boundary.
"""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = json.loads((ROOT/'config/dataverse/scr003-attendance-columns.json').read_text())
REPORT='crb3c_attendancereports'
LINES='crb3c_attendancereportlines'
MONTHS='crb3c_attendancetargetmonths'
CONN='shared_commondataserviceforapps'


def expr(s): return '@'+s

def chain(items):
    result={}
    previous=None
    for name, action in items:
        action=copy.deepcopy(action)
        action['runAfter']={previous:['Succeeded']} if previous else {}
        result[name]=action
        previous=name
    return result

def compose(value): return {'type':'Compose','inputs':value}
def setvar(name,value): return {'type':'SetVariable','inputs':{'name':name,'value':value}}
def scope(items): return {'type':'Scope','actions':chain(items)}
def guard(condition):
    # ParseJson enum assertion: fail the enclosing Try scope, before any write.
    return {'type':'ParseJson','inputs':{'content':expr(condition),'schema':{'type':'boolean','enum':[True]}}}
def branch(condition,yes,no=()):
    return {'type':'If','expression':expr(condition),'actions':chain(yes),'else':{'actions':chain(no)}}
def api(operation,params,connector=CONN):
    return {'type':'OpenApiConnection','inputs':{'host':{'apiId':'/providers/Microsoft.PowerApps/apis/'+connector,'connectionName':connector,'operationId':operation},'parameters':params,'authentication':"@parameters('$authentication')"}}
def listrows(entity,filter,top=5000):
    a=api('ListRecords',{'entityName':entity,'$filter':filter,'$top':top})
    a['runtimeConfiguration']={'paginationPolicy':{'minimumItemCount':top}}
    return a

def create(entity,data):return api('CreateRecord',{'entityName':entity,**{'item/'+k:v for k,v in data.items()}})
def update(entity,id,data):return api('UpdateRecord',{'entityName':entity,'recordId':id,**{'item/'+k:v for k,v in data.items()}})
def getreport():return api('GetItem',{'entityName':REPORT,'recordId':expr("variables('reportId')")})
def logical(key): return 'crb3c_'+key.replace('_','')


def numeric(field,raw=False):
    col=field['display_name']
    val="item()?['"+col+"']"
    convert='int' if field['kind']=='integer' else 'float'
    return expr(f"if(empty(string({val})),null,{convert}({val}))")

def build():
    schema={'type':'object','required':['operation','expectedVersion'], 'properties':{
        'operation':{'type':'string','enum':['import','edit','report','reopen','month']},
        'expectedVersion':{'type':'integer','minimum':-1},
        'reportId':{'type':'string'},'month':{'type':'string'},'bureau':{'type':'string'},
        'enabled':{'type':'boolean'},'rows':{'type':'array'}}}
    request="body('Request')"
    op=request+"?['operation']"
    fields=next(e for e in SPEC['entities'] if e['key']=='detail')['fields']
    fields=[f for f in fields if f['key']!='batch_id']
    props={};mapping={}
    for f in fields:
        col=f['display_name']; val="item()?['"+col+"']"
        if f['key']=='staff_number':
            mapping[col]=expr(f"formatNumber(int({val}),'000000000000','en-US')")
            props[col]={'type':'string','minLength':12,'maxLength':12}
        elif f['kind']=='text':
            mapping[col]=expr(f"string(coalesce({val},''))")
            props[col]={'type':'string','maxLength':f['max_length']}
            if f['required']: props[col]['minLength']=1
        else:
            mapping[col]=numeric(f)
            props[col]={'type': ['integer' if f['kind']=='integer' else 'number','null'],
                        'minimum':f['min'],'maximum':f['max']}
            if f['required']: props[col]['type']=props[col]['type'][0]
    props.update({'勤務月':{'type':'string','minLength':7,'maxLength':7},'所属部局名':{'type':'string','minLength':1,'maxLength':100}})
    mapping['勤務月']=expr("string(item()?['勤務月'])")
    mapping['所属部局名']=expr("string(item()?['所属部局名'])")
    # Raw lexical checks prevent int() accepting/truncating malformed identifiers.
    rawstaff="string(item()?['職員番号'])"
    stripped=rawstaff
    for digit in '0123456789':stripped=f"replace({stripped},'{digit}','')"
    rawtests=[f"greater(length({rawstaff}),0)",f"lessOrEquals(length({rawstaff}),12)",f"equals({stripped},'')"]
    rawtests += [f"contains(item(),'{c}')" for c in SPEC['import_contract']['columns']]
    for f in fields:
        val="item()?['"+f['display_name']+"']"
        if f['kind']=='integer': rawtests.append(f"or(empty(string({val})),isInt(string({val})))")
    rawinvalid={'type':'Query','inputs':{'from':expr("variables('rows')"),'where':expr('not(and('+','.join(rawtests)+'))')}}
    valuechecks=["equals(item()?['勤務月'],body('Request')?['month'])","equals(item()?['所属部局名'],body('Request')?['bureau'])"]
    for f in fields:
        val="item()?['"+f['display_name']+"']"
        if f['kind']=='decimal': valuechecks.append(f"equals(coalesce({val},0),float(formatNumber(coalesce({val},0),'0.000','en-US')))")
    normalized={'type':'Select','inputs':{'from':expr("variables('rows')"),'select':mapping}}
    row_schema={'type':'array','minItems':1,'maxItems':999,'items':{'type':'object','required':list(props),'properties':props}}
    quoted_bureau="replace(body('Request')?['bureau'],decodeUriComponent('%27'),decodeUriComponent('%27%27'))"
    month_filter=expr("concat('crb3c_workmonth eq ',body('Request')?['month'],'-01 and crb3c_enabled eq true')")
    report_filter=expr("concat('crb3c_workmonth eq ',body('Request')?['month'],'-01 and crb3c_bureaukey eq ',decodeUriComponent('%27'),"+quoted_bureau+",decodeUriComponent('%27'))")
    reportid=expr("variables('reportId')")
    version="int(coalesce(variables('report')?['crb3c_importversion'],0))"
    match_version="equals("+version+",body('Request')?['expectedVersion'])"
    data={logical(f['key']):expr("items('Stage_rows')?['"+f['display_name']+"']") for f in fields}
    data.update({'crb3c_name':expr("concat(variables('batch'),'-',string(items('Stage_rows')?['No']))"),
                 'crb3c_batchid':expr("variables('batch')"),
                 'crb3c_AttendanceReportId@odata.bind':expr("concat('/crb3c_attendancereports(',variables('reportId'),')')")})
    import_or_edit=[
        ('Import_message',setvar('message','Excelの列・値・局・勤務月を確認してください。既存明細は変更されていません。')),
        ('Read_source',branch("equals("+op+",'import')",[
            ('Xlsx_only',guard("and(endsWith(toLower(coalesce(triggerBody()?['file']?['name'],'')),'.xlsx'),not(empty(triggerBody()?['file']?['contentBytes'])))")),
            ('Create_temp',api('CreateFile',{'folderPath':'/','name':expr("concat('SCR003_',variables('batch'),'.xlsx')"),'body':expr("base64ToBinary(triggerBody()?['file']?['contentBytes'])")},'shared_onedriveforbusiness')),
            ('Remember_temp',setvar('fileId',expr("body('Create_temp')?['Id']"))),
            ('Excel_rows',api('GetItems',{'source':'me','drive':'__BIND_EXISTING_DRIVE__','file':expr("variables('fileId')"),'table':'TestData'},'shared_excelonlinebusiness')),
            ('Use_excel_rows',setvar('rows',expr("body('Excel_rows')?['value']")))],
            [('Use_edit_rows',setvar('rows',expr(request+"?['rows']")))])),
        ('Count_rows',guard("and(greater(length(variables('rows')),0),lessOrEquals(length(variables('rows')),999))")),
        ('Raw_invalid',rawinvalid),('Check_raw',guard("equals(length(body('Raw_invalid')),0)")),
        ('Normalize',normalized),('Check_shape',{'type':'ParseJson','inputs':{'content':expr("body('Normalize')"),'schema':row_schema}}),
        ('Invalid_values',{'type':'Query','inputs':{'from':expr("body('Normalize')"),'where':expr('not(and('+','.join(valuechecks)+'))')}}),
        ('Check_values',guard("equals(length(body('Invalid_values')),0)")),
        ('Staff_keys',{'type':'Select','inputs':{'from':expr("body('Normalize')"),'select':{'key':expr("item()?['職員番号']")}}}),
        ('Line_keys',{'type':'Select','inputs':{'from':expr("body('Normalize')"),'select':{'key':expr("item()?['No']")}}}),
        ('No_duplicates',guard("and(equals(length(union(body('Staff_keys'),body('Staff_keys'))),length(variables('rows'))),equals(length(union(body('Line_keys'),body('Line_keys'))),length(variables('rows'))))")),
        ('Target_message',setvar('message','勤務月が報告対象外です。メンテナンスの設定を確認してください。')),
        ('Target_month',listrows(MONTHS,month_filter,2)),('Enabled_month',guard("equals(length(body('Target_month')?['value']),1)")),
        ('Find_report',listrows(REPORT,report_filter,2)),('Unique_report',guard("lessOrEquals(length(body('Find_report')?['value']),1)")),
        ('Version_message',setvar('message','報告済または別の操作で更新されています。一覧を再読込してください。')),
        ('Get_or_create_report',branch("equals(length(body('Find_report')?['value']),0)",[
            ('New_report_only',guard("and(equals(body('Request')?['operation'],'import'),equals(body('Request')?['expectedVersion'],-1))")),
            ('Create_report',create(REPORT,{'crb3c_name':expr("concat(body('Request')?['month'],' ',body('Request')?['bureau'])"),'crb3c_workmonth':expr("concat(body('Request')?['month'],'-01')"),'crb3c_bureaukey':expr(request+"?['bureau']"),'crb3c_bureauname':expr(request+"?['bureau']"),'crb3c_status':100000000,'crb3c_importversion':0})),
            ('New_report',setvar('report',expr("body('Create_report')")))],
            [('Existing_report',setvar('report',expr("first(body('Find_report')?['value'])"))),
             ('Existing_version',guard(match_version)),
             ('Editable_status',guard("equals(variables('report')?['crb3c_status'],100000000)")),
             ('Edit_report_match',guard("or(equals(body('Request')?['operation'],'import'),equals(body('Request')?['reportId'],variables('report')?['crb3c_attendancereportid']))"))])),
        ('Remember_report',setvar('reportId',expr("variables('report')?['crb3c_attendancereportid']"))),
        ('Stage_message',setvar('message','明細保存に失敗しました。再読込し、反映状態を確認してください。旧版は保持されています。')),
        ('Stage_rows',{'type':'Foreach','foreach':expr("body('Normalize')"),'actions':chain([('Stage_line',create(LINES,data))])}),
        ('Read_staged',listrows(LINES,expr("concat('crb3c_batchid eq ',decodeUriComponent('%27'),variables('batch'),decodeUriComponent('%27'))"),1000)),
        ('Verify_staged',guard("equals(length(body('Read_staged')?['value']),length(body('Normalize')))")),
        ('Before_commit',getreport()),
        ('Commit_guard',guard("and(equals(body('Before_commit')?['crb3c_status'],100000000),equals(body('Before_commit')?['crb3c_importversion'],variables('report')?['crb3c_importversion']))")),
        ('Activate_batch',update(REPORT,reportid,{'crb3c_activebatchid':expr("variables('batch')"),'crb3c_importversion':expr('add('+version+',1)')})),
        ('Committed',setvar('result',{'success':True,'reportId':reportid,'count':expr("length(body('Normalize'))"),'version':expr('add('+version+',1)'),'message':'明細を保存しました。'}))]
    # Excel's default is only 256 rows. Request one extra beyond the accepted
    # 999-row bound, so oversized files are rejected rather than truncated.
    import_or_edit[1][1]['actions']['Excel_rows']['runtimeConfiguration']={'paginationPolicy':{'minimumItemCount':1000}}
    transitions=[
        ('Transition_message',setvar('message','報告状態または版が変わっています。一覧を再読込してください。')),
        ('Transition_id',setvar('reportId',expr(request+"?['reportId']"))),
        ('Transition_report',getreport()),('Transition_remember',setvar('report',expr("body('Transition_report')"))),
        ('Transition_version',guard(match_version)),
        ('Transition_state',guard("if(equals(body('Request')?['operation'],'report'),and(equals(variables('report')?['crb3c_status'],100000000),not(empty(variables('report')?['crb3c_activebatchid']))),equals(variables('report')?['crb3c_status'],100000001))")),
        ('Change_state',branch("equals("+op+",'report')",[
            ('Report',update(REPORT,reportid,{'crb3c_status':100000001,'crb3c_reportedat':expr('utcNow()'),'crb3c_importversion':expr('add('+version+',1)')}))],
            [('Reopen',update(REPORT,reportid,{'crb3c_status':100000000,'crb3c_reopenedat':expr('utcNow()'),'crb3c_importversion':expr('add('+version+',1)')}))])),
        ('Transition_done',setvar('result',{'success':True,'reportId':reportid,'count':0,'version':expr('add('+version+',1)'),'message':'報告状態を更新しました。'}))]
    month=[
        ('Month_message',setvar('message','勤務月はyyyy-mm形式で指定してください。')),
        ('Check_month',guard("and(equals(length(string(body('Request')?['month'])),7),equals(formatDateTime(concat(body('Request')?['month'],'-01'),'yyyy-MM'),body('Request')?['month']))")),
        ('Find_month',listrows(MONTHS,expr("concat('crb3c_workmonth eq ',body('Request')?['month'],'-01')"),2)),
        ('Unique_month',guard("lessOrEquals(length(body('Find_month')?['value']),1)")),
        ('Set_month',branch("equals(length(body('Find_month')?['value']),0)",[
            ('Create_month',create(MONTHS,{'crb3c_name':expr(request+"?['month']"),'crb3c_workmonth':expr("concat(body('Request')?['month'],'-01')"),'crb3c_enabled':expr(request+"?['enabled']")}))],
            [('Update_month',update(MONTHS,expr("first(body('Find_month')?['value'])?['crb3c_attendancetargetmonthid']"),{'crb3c_enabled':expr(request+"?['enabled']")}))])),
        ('Month_done',setvar('result',{'success':True,'reportId':'','count':0,'version':0,'message':'報告対象月を設定しました。'}))]
    # Month parsing runs before any writes.
    execute=[('Request',{'type':'ParseJson','inputs':{'content':expr("json(triggerBody()['text'])"),'schema':schema}}),
             ('Valid_request_month',branch("or(equals(body('Request')?['operation'],'import'),equals(body('Request')?['operation'],'edit'),equals(body('Request')?['operation'],'month'))",[('Validate_month_format',guard("and(equals(length(string(body('Request')?['month'])),7),equals(formatDateTime(concat(body('Request')?['month'],'-01'),'yyyy-MM'),body('Request')?['month']))"))])),
             ('Operation',branch("or(equals("+op+",'import'),equals("+op+",'edit'))",import_or_edit,
                          [('Other_operation',branch("equals("+op+",'month')",month,transitions))]))]
    definition={'$schema':'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#','contentVersion':'1.0.0.0',
                'parameters':{'$authentication':{'type':'SecureObject','defaultValue':{}},'$connections':{'type':'Object','defaultValue':{}}},
                'triggers':{'manual':{'type':'Request','kind':'PowerAppV2','inputs':{'schema':{'type':'object','required':['text'],'properties':{
                    'text':{'title':'requestjson','type':'string','x-ms-dynamically-added':True,'x-ms-content-hint':'TEXT'},
                    'file':{'title':'file','type':'object','x-ms-dynamically-added':True,'x-ms-content-hint':'FILE','properties':{'name':{'type':'string'},'contentBytes':{'type':'string','format':'byte'}}}}}},'runtimeConfiguration':{'concurrency':{'runs':1,'maximumWaitingRuns':10}}}},
                'actions':chain([('Initialize',{'type':'InitializeVariable','inputs':{'variables':[
                    {'name':'rows','type':'array','value':[]},{'name':'report','type':'object','value':{}},
                    {'name':'reportId','type':'string','value':''},{'name':'fileId','type':'string','value':''},
                    {'name':'batch','type':'string','value':expr('guid()')},{'name':'message','type':'string','value':'入力または接続を確認してください。'},
                    {'name':'result','type':'object','value':{'success':False,'reportId':'','count':0,'version':-1,'message':'処理未完了'}}]}}),('Execute',scope(execute))])}
    actions=definition['actions']
    actions['Failure']={**setvar('result',{'success':False,'reportId':reportid,'count':0,'version':-1,'message':expr("variables('message')")}), 'runAfter':{'Execute':['Failed','TimedOut']}}
    actions['Cleanup']={**branch("not(empty(variables('fileId')))",[('Delete_temp',api('DeleteFile',{'id':expr("variables('fileId')")},'shared_onedriveforbusiness'))]),'runAfter':{'Failure':['Succeeded','Skipped']}}
    actions['Respond']={'type':'Response','kind':'PowerApp','runAfter':{'Cleanup':['Succeeded','Failed','Skipped','TimedOut']},'inputs':{'statusCode':200,'body':{'resultjson':expr("string(variables('result'))")},'schema':{'type':'object','properties':{'resultjson':{'title':'resultjson','type':'string','x-ms-dynamically-added':True}}}}}
    actions['Respond']['operationOptions']='Asynchronous'
    return definition

if __name__=='__main__':
    dest=ROOT/'powerapps/flows/scr003/definition.json'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(build(),ensure_ascii=False,indent=2)+'\n')
    print(dest)
