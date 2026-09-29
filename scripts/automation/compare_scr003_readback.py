"""Read-only structural comparison of the downloaded Canvas source and candidate."""
import hashlib, json, re, sys, zipfile
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[2]
def controls(nodes):
    out={}
    if isinstance(nodes,dict):
        for key,value in nodes.items():
            if isinstance(value,dict) and ('Control' in value or 'Properties' in value):
                out[key]=value
            out.update(controls(value))
    elif isinstance(nodes,list):
        for value in nodes: out.update(controls(value))
    return out

def normalized(value):
    # Formatting whitespace outside strings is not a Power Fx behavior change.
    if not isinstance(value,str):return value
    tokens=re.findall(r'"(?:""|[^"\\]|\\.)*"|\S',value.strip().lstrip('='))
    return ''.join(tokens)

def main():
    with zipfile.ZipFile(sys.argv[1]) as z:
        names=z.namelist()
        def read_screen(screen):
            name=next(n for n in names if n.replace('\\','/').endswith('/'+screen+'.pa.yaml'))
            raw=z.read(name)
            print(screen+' SHA256 '+hashlib.sha256(raw).hexdigest())
            return yaml.safe_load(raw)
        reports=read_screen('scrAttendanceFormal')
        maintenance=read_screen('scrMaintenance')
        home=read_screen('scrHome')
        checked=0; differences=[]
        for file,actual in [('scrAttendanceFormal.paste.yaml',reports),('attendance-month-settings.paste.yaml',maintenance)]:
            expected=controls(yaml.safe_load((ROOT/'src/screen-ui/v1.29'/file).read_text()))
            found=controls(actual)
            for name,control in expected.items():
                if name not in found: differences.append(name+': missing');continue
                for prop,value in control.get('Properties',{}).items():
                    got=found[name].get('Properties',{}).get(prop)
                    # Canvas export omits Gallery.Visible at its true default.
                    if name=='galAttendanceFormalLines' and prop=='Visible' and got is None and value=='=true': got='=true'
                    if normalized(value)!=normalized(got):differences.append(name+'.'+prop)
                    checked+=1
        report_controls=controls(reports)
        # Screens are represented as a mapping beneath Screens in current source.
        for name,actual,prop,file in [
            ('scrAttendanceFormal',report_controls,'OnVisible','scrAttendanceFormal.OnVisible.fx'),
            ('btnHomeAttendance',controls(home),'OnSelect','btnHomeAttendance.OnSelect.fx')]:
            value=actual.get(name,{}).get('Properties',{}).get(prop)
            if normalized(value)!=normalized((ROOT/'src/screen-ui/v1.29'/file).read_text()):differences.append(name+'.'+prop)
            checked+=1
        properties=[n for n in names if n.endswith('Properties.json')]
        limit=any(json.loads(z.read(n)).get('DefaultConnectedDataSourceMaxGetRowsCount')==2000 for n in properties)
        if not limit: differences.append('DataRowLimit expected 2000')
        print(json.dumps({'checked_properties':checked,'differences':differences},ensure_ascii=False))
        if differences:raise SystemExit('Candidate/readback difference requires review')
        print('PASS: authored attendance properties and data row limit match readback')

if __name__=='__main__':main()
