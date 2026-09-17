"""Generate reviewable v1.18 property patches; never writes active source or deploys.

Studio connection/compile and live ledger tests are mandatory before promotion.
"""
import hashlib
import sys
import json
import re
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = ROOT / 'src/staff-master/patches/v1.18-candidate'
SOURCE = ROOT / 'powerapps/canvas-v3/Src'

def nodes(value, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, dict) and 'Properties' in child:
                yield key, child, path
            yield from nodes(child, path + (key,))
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child, path)

def mappings():
    result = [
        {'field': 'employee_name', 'source': 'staff', 'column': 'Name', 'format': 'text'},
        {'field': 'employee_number', 'source': 'staff', 'column': 'StaffId', 'format': 'text'},
        {'field': 'organization', 'source': 'staff', 'column': 'Org', 'format': 'text'},
    ]
    for display, column in [('event_date', 'eventdate'), ('submitted_date', 'submitteddate'), ('accepted_date', 'receiveddate')]:
        for part in ['year', 'month', 'day']:
            result.append({'field': display + '_' + part, 'source': 'commute', 'column': 'crb3c_' + column, 'format': part})
    route = {'transport': ('operator', 'text'), 'section_from': ('from', 'text'), 'section_to': ('to', 'text'), 'ticket_type': ('tickettype', 'text'), 'other_basis': ('ticketbasis', 'decimal'), 'season_basis': ('distancekm', 'decimal'), 'other_amount': ('ticketamount', 'amount'), 'season_amount': ('passamount', 'amount'), 'season_months': ('passmonths', 'integer'), 'monthly_amount': ('amount', 'amount'), 'period_start_year': ('recognitionstart', 'era_year'), 'period_start_month': ('recognitionstart', 'start_month'), 'payment_months': ('paymonth', 'paymonth'), 'remarks': ('remarks', 'text')}
    for n in range(1, 5):
        for display, (column, kind) in route.items():
            result.append({'field': f'route_{n}_{display}', 'source': 'commute', 'column': f'crb3c_route{n}_{column}', 'format': kind})
    result.append({'field': 'monthly_amount_total', 'source': 'commute', 'column': 'crb3c_monthlytotal', 'format': 'amount'})
    return result

def expression(item):
    v = ('s.' if item['source'] == 'staff' else 'c.') + item['column']
    kind = item['format']
    if kind == 'text':
        return v
    # Only Reiwa-era test records currently exist. Do not invent an era for earlier dates.
    formatted = {
        'year': f'If(Year({v}) >= 2019, Text(Year({v})-2018,"0"), Text(Year({v}),"0"))',
        'month': f'Text(Month({v}),"0")', 'day': f'Text(Day({v}),"0")',
        'era_year': f'If(Year({v}) >= 2019,"令和" & Text(Year({v})-2018,"0") & "年",Text(Year({v}),"0") & "年")',
        'start_month': f'Text(Month({v}),"0") & "月から"',
        'amount': f'Text({v},"#,##0")', 'integer': f'Text({v},"0")',
        'decimal': f'If(Mod({v},1)=0,Text({v},"0"),Text({v},"0.####"))', 'paymonth': f'Text({v},"0") & "月"',
    }[kind]
    return f'If(IsBlank({v}),Blank(),{formatted})'

def render_ledger():
    rows = ['{Field:"' + m['field'] + '",Value:' + expression(m) + '}' for m in mappings()]
    return 'StaffLedgerFields = With({c:varLedgerCommute111,s:varLedgerStaff111},Table(\n    ' + ',\n    '.join(rows) + '\n));'

def candidate():
    # Historical patch preparation always uses the immutable published v1.17 package.
    from scripts.automation.bridge import read_archive
    archive = read_archive(ROOT / 'powerapps/dataverse-v1.17/staff-master.msapp')
    app = yaml.safe_load(archive['Src/App.pa.yaml'])
    screen = yaml.safe_load(archive['Src/Screen1.pa.yaml'])
    controls = {n: (v, path) for n, v, path in nodes(screen)}
    changes = []
    def edit(name, prop, after):
        obj, path = (app['App'], ('App',)) if name == 'App' else controls[name]
        before = obj['Properties'].get(prop)
        if before != after:
            changes.append({'source': 'Src/App.pa.yaml' if name == 'App' else 'Src/Screen1.pa.yaml', 'control': name, 'parent_path': '/'.join(path), 'property': prop, 'operation': 'property_add' if before is None else 'property_update', 'before': before, 'after': after})
    original = app['App']['Properties']['Formulas']
    commute_start = original.index('StaffCommuteHistory = Table(')
    commute_end = original.index('StaffSocialHistory =', commute_start)
    formulas = original[:commute_start] + original[commute_end:]
    formulas = formulas[:formulas.index('StaffLedgerTemplate = Table(')].rstrip()
    marker = '// Synthetic histories: source is tests/fixtures/staff-history-synthetic.json.\n'
    prefix, histories = formulas.split(marker)
    formulas = prefix + '''// Commute records come only from Dataverse; no built-in commute fallback.
StaffSelected = If(Coalesce(varStaffChosen111,false),varStaff111,First(StaffBasicView));
StaffCommuteHistory = SortByColumns(
    Filter('T_通勤', '職員基本'.職員番号 = StaffSelected.StaffId),
    "crb3c_startdate",SortOrder.Ascending,"crb3c_recognitionid",SortOrder.Ascending
);
''' + render_ledger() + '\n' + marker + histories
    edit('App', 'Formulas', formulas)
    edit('lblMeta111', 'Text', '="v1.18 ／ Dataverse・" & Text(StaffTestCount) & "名"')
    edit('lblTestNote111', 'Text', '=If(StaffTestCount>100,"テスト対象の上限（100名）を超えたため一覧を表示できません。","テスト環境：職員基本・通勤・認定簿はDataverseの架空データです。その他の履歴・給与簿は内蔵テストデータです。")')
    edit('lblSectionCommute111', 'Text', '=IfError("通勤支給予定　" & Text(CountRows(StaffCommuteHistory)) & "件（行を選択）","通勤データを取得できません")')
    edit('galCommute111', 'Items', '=StaffCommuteHistory')
    edit('lblEmptyCommute111', 'Visible', '=IfError(IsEmpty(StaffCommuteHistory),false)')
    edit('galCommute111', 'Selectable', '=true')
    edit('galCommute111', 'Default', '=First(StaffCommuteHistory)')
    edit('galCommute111', 'AccessibleLabel', '="通勤認定一覧。表示する行を選択してください"')
    edit('galCommute111', 'ItemAccessibleLabel', '=ThisItem.crb3c_recognitionid & " " & Text(ThisItem.crb3c_startdate,"yyyy/mm/dd") & " " & ThisItem.crb3c_method')
    edit('galCommute111', 'TemplateFill', '=If(ThisItem.IsSelected,ColorValue("#E6F2FF"),Color.White)')
    edit('galCommute111', 'TabIndex', '=0')
    edit('lblHCommute1110', 'Text', '="適用開始日 / 認定ID"')
    exprs = [
        '=Text(ThisItem.crb3c_startdate,"yyyy/mm/dd") & Char(10) & ThisItem.crb3c_recognitionid',
        '=Text(ThisItem.crb3c_enddate,"yyyy/mm/dd")', '=ThisItem.crb3c_method',
        '=If(IsBlank(ThisItem.crb3c_month04),Blank(),Text(ThisItem.crb3c_month04,"#,##0"))',
        '=If(IsBlank(ThisItem.crb3c_month10),Blank(),Text(ThisItem.crb3c_month10,"#,##0"))',
    ]
    for n, expr in enumerate(exprs):
        name = 'lblCCommute111' + str(n)
        edit(name, 'Text', expr)
        edit(name, 'OnSelect', '=Select(Parent)')
        edit(name, 'Fill', '=RGBA(0,0,0,0)')
    edit('btnCertificate111', 'DisplayMode', '=If(Coalesce(varLedgerOpen111,false) || Coalesce(varPayroll111,false) || !IsBlank(varReport111),DisplayMode.Disabled,IfError(If(!IsBlank(galCommute111.Selected.crb3c_commuteid) && galCommute111.Selected.職員基本.職員番号 = StaffSelected.StaffId,DisplayMode.Edit,DisplayMode.Disabled),DisplayMode.Disabled))')
    edit('btnCertificate111', 'OnSelect', '''=IfError(
    With({c:galCommute111.Selected,s:StaffSelected},
        If(IsBlank(c.crb3c_commuteid) || c.職員基本.職員番号 <> s.StaffId,
            Notify("通勤の行を選択してください。",NotificationType.Warning),
            Set(varLedgerStaff111,s);
            Set(varLedgerCommute111,c);
            ClearCollect(colLedgerFields111,StaffLedgerFields);
            Set(varLedgerOpen111,true); Set(varLedgerZoom111,1);
            Set(varLedgerPdfView111,false); Set(varLedgerExport111,false);
            Set(varLedgerPdfRequested111,false); Set(varLedgerPdf111,Blank());
            Set(varLedgerSavedUrl111,""); Set(varLedgerStatus111,"");
            Set(varLedgerFile111,""); Set(varPayroll111,false); Reset(ddLedgerPaper111)
        )
    ),
    Clear(colLedgerFields111); Set(varLedgerOpen111,false);
    Notify("通勤データを取得できませんでした。再読込してください。",NotificationType.Error)
)''')
    edit('lblLedgerStaff111', 'Text', '=varLedgerStaff111.Name & "　職員番号：" & varLedgerStaff111.StaffId & "　認定ID：" & varLedgerCommute111.crb3c_recognitionid')
    # Existing staff-selection/reset handlers also clear any old commute/PDF snapshot.
    for name, (obj, _) in controls.items():
        old = obj['Properties'].get('OnSelect', '')
        if 'Set(varStaff111,' in old:
            new = old
            if name == 'btnLoad111':
                new = new.replace("Refresh('M_職員基本');", "IfError(Refresh('M_職員基本'); Refresh('T_通勤'),Notify(\"Dataverseの再読込に失敗しました。\",NotificationType.Error));", 1)
            new += '; Reset(galCommute111); Clear(colLedgerFields111); Set(varLedgerCommute111,Blank()); Set(varLedgerOpen111,false); Set(varLedgerPdf111,Blank()); Set(varLedgerPdfView111,false)'
            edit(name, 'OnSelect', new)
    return changes

def write():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'properties').mkdir(exist_ok=True)
    changes = candidate()
    for change in changes:
        name = change['control'] + '.' + change['property'] + '.fx'
        (OUT / 'properties' / name).write_text(change['after'][1:] + '\n')
        change['property_file'] = 'properties/' + name
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE / 'App.pa.yaml', SOURCE / 'Screen1.pa.yaml']}
    manifest = {'state': 'UNCOMPILED_CANDIDATE_NOT_DEPLOYED', 'baseVersion': '1.17', 'targetVersion': '1.18', 'base_commit': 'c98777dda8c663c41710683d0bdb03bb55047f3b', 'baseline_source_sha256': hashes, 'dependencies': ['Studio data source T_通勤 connected in existing environment', 'Approved dedicated-user Read permission', 'Existing controls and 111 identifiers preserved'], 'changes': changes}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    (OUT / 'ledger-field-map.json').write_text(json.dumps(mappings(), ensure_ascii=False, indent=2) + '\n')
    fixtures = json.loads((ROOT / 'tests/fixtures/staff-history-synthetic.json').read_text())
    fixtures.pop('Commute'); fixtures.pop('LedgerTemplate')
    (OUT / 'staff-history-synthetic.json').write_text(json.dumps(fixtures, ensure_ascii=False, indent=2) + '\n')
    renderer = (ROOT / 'scripts/automation/render_staff_history.py').read_text()
    renderer = renderer.replace("KINDS = ('Work', 'Commute', 'Social', 'Tax', 'Payroll')", "KINDS = ('Work', 'Social', 'Tax', 'Payroll')")
    renderer = renderer.replace("return result + 'StaffLedgerTemplate = ' + table(fixtures['LedgerTemplate']) + ';'", 'return result.rstrip()')
    start = renderer.index("    for row in fixtures['Commute']:")
    end = renderer.index("\nif __name__ == '__main__':", start)
    renderer = renderer[:start] + renderer[end:]
    (OUT / 'render_staff_history.py').write_text(renderer)
    print(f'Prepared {len(changes)} property edits and {len(mappings())} ledger mappings; active source unchanged')

if __name__ == '__main__':
    raise SystemExit('v1.18 is Studio-compiled and published. Use the applied v1.18 manifest; do not regenerate a candidate over the active source.')
