"""Static visual QA only; does not exercise browser JS or deployed resources."""
from pathlib import Path
import re,json,html,importlib.util,argparse,subprocess
from weasyprint import HTML
import fitz,numpy as np
parser=argparse.ArgumentParser()
parser.add_argument('--pdf',type=Path,required=True)
parser.add_argument('--font',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[2];w=args.output.resolve();w.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('builder',root/'src/commute-ledger/v1.02/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
s=b.build(root/'other/src/staff-master/candidates/commute-html-v1.01/src/commute-ledger.html',args.pdf)
s=re.sub(r'<script\b[^>]*>.*?</script>','',s,flags=re.S).replace('<body>','<body class="ready">').replace('id="report" hidden','id="report"')
s=s.replace('</head>','<style>@font-face{font-family:"Noto Sans CJK JP";src:url('+args.font.resolve().as_uri()+')}</style></head>')
ref=fitz.open(args.pdf);results=[]
fixture_script="""
const api=require('./other/src/staff-master/candidates/commute-html-v1.01/src/report.js');
const rows=require('./other/src/staff-master/candidates/commute-html-v1.01/tests/commute-6.json');
process.stdout.write(JSON.stringify(rows.map(r=>api.model({...r.data,crb3c_commuteid:r.id,_crb3c_staffbasicid_value:r.parent_id},{crb3c_staffbasicid:r.parent_id,crb3c_staffnumber:r.data.crb3c_staffnumber,crb3c_fullname:r.data.crb3c_fullname,crb3c_orgshort:'試験所属'},r.id))));
"""
values=json.loads(subprocess.check_output(['node','-e',fixture_script],cwd=root,text=True))
for i,v in enumerate([{}]+values):
 content=re.sub(r'(<span[^>]*data-field="([^"]+)"[^>]*>)(</span>)',lambda m:m[1]+html.escape(v.get(m[2],''))+m[3],s)
 path=w/f'case-{i}.pdf';HTML(string=content,base_url=str(w)).write_pdf(path)
 d=fitz.open(path);r={'case':i,'page_count':len(d),'sizes':[[p.rect.width,p.rect.height] for p in d]}
 if i==0:
  r['pixels']=[]
  for j,p in enumerate(d):
   a=np.frombuffer(ref[j].get_pixmap(matrix=fitz.Matrix(2,2),colorspace=fitz.csGRAY).samples,dtype=np.uint8);z=np.frombuffer(p.get_pixmap(matrix=fitz.Matrix(2,2),colorspace=fitz.csGRAY).samples,dtype=np.uint8)
   r['pixels'].append({'mean_absolute_difference':float(np.abs(a.astype(float)-z).mean()),'fraction_diff_over_32':float((np.abs(a.astype(float)-z)>32).mean())})
 if i in (0,3):
  for j,p in enumerate(d):p.get_pixmap(matrix=fitz.Matrix(1.4,1.4)).save(w/f'case-{i}-page-{j+1}.png')
 results.append(r)
(w/'render-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
