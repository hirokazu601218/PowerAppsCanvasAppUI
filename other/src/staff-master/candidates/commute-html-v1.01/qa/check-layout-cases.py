"""Independent print typesetting. Does not execute JS or prove Edge behavior."""
import json
from pathlib import Path
from weasyprint import HTML,CSS
from weasyprint.text.fonts import FontConfiguration
import fitz
p=Path(__file__).resolve().parent
(p/'fonts').mkdir(exist_ok=True)
(p/'fonts/QA-Japanese.ttf').write_bytes(fitz.Font('japan').buffer)
fc=FontConfiguration();css=CSS(string='@font-face{font-family:QAJP;src:url('+p.joinpath('fonts/QA-Japanese.ttf').as_uri()+')}html,body{font-family:QAJP,sans-serif!important}',font_config=fc)
results=[]
for name in ['TK-91000'+str(i) for i in range(1,7)]+['four-routes','overflow-expected']:
 d=HTML(filename=str(p/(name+'.html'))).render(stylesheets=[css],font_config=fc)
 overflow=set();bounds=True
 for pg in d.pages:
  for b in pg._page_box.descendants():
   if b.element_tag=='span' and b.element.get('data-field') and type(b).__name__=='BlockBox':
    if any(z.position_y+z.height>b.position_y+b.height+1 for z in b.descendants() if type(z).__name__=='LineBox'):overflow.add(b.element.get('data-field'))
   if b.element_tag=='table' and type(b).__name__=='TableBox' and b.position_y+b.height>pg.height-18.8:bounds=False
 results.append({'case':name,'pages':len(d.pages),'page_mm':[round(d.pages[0].width*25.4/96,2),round(d.pages[0].height*25.4/96,2)],'tables_inside_page':bounds,'overflow_fields':sorted(overflow)})
 if name!='overflow-expected':assert len(d.pages)==2 and bounds and not overflow,name
 else:assert overflow,'maximum length must be detected as too large'
(p/'layout-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
