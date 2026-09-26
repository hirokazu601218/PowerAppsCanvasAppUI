"""Diagnostic PNG from YAML geometry. NOT a Canvas screenshot or an alternative UI.

Run with --font /path/to/Japanese-Regular.ttf --bold /path/to/Japanese-Semibold.ttf.
Uses Pillow plus the limited local evaluator. Font metrics/platform rendering differ.
"""
from pathlib import Path
import argparse, json, math, functools
from PIL import Image, ImageDraw, ImageFont
from preflight import read,index
from model_engine import ModelEngine

R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--font',required=True);ap.add_argument('--bold',required=True)
ap.add_argument('--out',default='qa-local');args=ap.parse_args()
app=read(R/'src/staff-master/scrStaffMasterSearch_v1.11.paste.yaml');nodes,parents=index(app)
out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
@functools.lru_cache(maxsize=80)
def font(size,bold):return ImageFont.truetype(args.bold if bold else args.font,max(8,round(size)))
def color(v,default=(0,0,0,0)):
    if isinstance(v,tuple):return tuple(round(c) for c in v[:3])+(round(v[3]*255),)
    if not v:return default
    if v.startswith('#'):return tuple(int(v[i:i+2],16) for i in (1,3,5))+(255,)
    return {'Color.White':(255,255,255,255),'Color.Black':(0,0,0,255),'Color.Transparent':(0,0,0,0)}.get(v,default)
def intersect(a,b):
    r=(max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3]))
    return r if r[2]>r[0] and r[3]>r[1] else None
findings=[];shots=[]
def render(w,h,expanded,large,scroll=0):
    e=ModelEngine(nodes,parents.copy(),w,h)
    e.state.update(varSearchSidebarExpanded111=expanded,varLargeText111=large)
    canvas=Image.new('RGBA',(w,h),'#F7F9FC');draw=ImageDraw.Draw(canvas)
    def prop(n,k,default=None):
        v=e.prop(n,k);return default if v is None else v
    def visit(n,ox,oy,clip,row=None):
        if not prop(n,'Visible',True):return
        c=nodes[n];kind=c['Control'];x,y,cw,ch=e.rect(n)
        parent=parents[n]
        if parent and nodes[parent].get('Variant')=='AutoLayout':
            x=prop(parent,'PaddingLeft',0);y=prop(parent,'PaddingTop',0)
            if parent=='conRightScroll111':y-=scroll
        x+=ox;y+=oy;rect=(round(x),round(y),round(x+cw),round(y+ch))
        visible=intersect(rect,clip) if clip else None
        bg=color(prop(n,'Fill'))
        isbutton=kind.endswith('Button@1.0.0') or kind.startswith('Classic/Button')
        if isbutton and kind.startswith('Modern'):
            bg=color('#0F6CBD') if prop(n,'Appearance')=='ButtonAppearance.Primary' else (0,0,0,0)
        if visible and bg[3]:draw.rectangle(visible,fill=bg)
        if kind.startswith('GroupContainer') or kind.startswith('Gallery'):
            if kind.startswith('Gallery'):
                data=prop(n,'Items',[]);rowh=prop(n,'TemplateSize',48)
                for i,r in enumerate(data):
                    e.rows[n]=r
                    for child in c.get('Children',[]):visit(next(iter(child)),x,y+i*rowh,visible,r)
                e.rows.pop(n,None)
            else:
                for child in c.get('Children',[]):visit(next(iter(child)),x,y,visible)
            if visible and c.get('Variant')=='AutoLayout':
                if prop(n,'LayoutOverflowY')=='LayoutOverflow.Scroll':
                    draw.rounded_rectangle((rect[2]-9,max(rect[1]+4,visible[1]),rect[2]-5,min(rect[1]+150,visible[3])),radius=2,fill='#ADB5BD')
                if prop(n,'LayoutOverflowX')=='LayoutOverflow.Scroll':
                    draw.rounded_rectangle((max(rect[0]+4,visible[0]),rect[3]-12,min(rect[0]+320,visible[2]),rect[3]-8),radius=2,fill='#ADB5BD')
        elif kind.startswith('Label') or isbutton or 'Input' in kind or 'DropDown' in kind:
            if n=='btnRow111':return # Transparent accessible row hit target, not visible text.
            t=prop(n,'Text','')
            if 'DropDown' in kind:t=prop(n,'Default','')+'  ▾'
            if not t and 'Input' in kind:t=prop(n,'Placeholder',prop(n,'HintText',''))
            t=str(t)
            size=prop(n,'Size',10.5)*4/3
            f=font(size,prop(n,'FontWeight') in ['FontWeight.Semibold','FontWeight.Bold'])
            padl=prop(n,'PaddingLeft',8 if isbutton else 0);padr=prop(n,'PaddingRight',8 if isbutton else 0)
            pt=prop(n,'PaddingTop',4);pb=prop(n,'PaddingBottom',4)
            width=max(1,cw-padl-padr);lineheight=size*(prop(n,'LineHeight',1.35))
            lines=[]
            for para in t.split('\n'):
                line=''
                for char in para:
                    if f.getlength(line+char)>width and line:lines.append(line);line=''
                    line+=char
                lines.append(line)
            needed=len(lines)*lineheight+pt+pb
            if needed>ch+1 and t:
                findings.append({'screen':[w,h,expanded,large],'control':n,'text':t,'required_h':round(needed,1),'height':ch,'lines':len(lines)})
            if visible:
                layer=Image.new('RGBA',(max(1,math.ceil(cw)),max(1,math.ceil(ch))),(0,0,0,0));ld=ImageDraw.Draw(layer)
                dy=pt+max(0,(ch-pt-pb-len(lines)*lineheight)/2)
                align=prop(n,'Align','Align.Center' if isbutton else 'Align.Left')
                fg=color(prop(n,'Color'),(36,36,36,255))
                for line in lines:
                    tw=f.getlength(line)
                    dx=padl+(max(0,width-tw)/2 if align=='Align.Center' else max(0,width-tw) if align=='Align.Right' else 0)
                    ld.text((dx,dy),line,font=f,fill=fg,anchor='lt');dy+=lineheight
                crop=(visible[0]-rect[0],visible[1]-rect[1],visible[2]-rect[0],visible[3]-rect[1])
                canvas.alpha_composite(layer.crop(crop),(visible[0],visible[1]))
        if visible and prop(n,'BorderThickness',0):
            # Draw only border segments inside the parent's clip.
            line=Image.new('RGBA',(max(1,math.ceil(cw)),max(1,math.ceil(ch))),(0,0,0,0));d=ImageDraw.Draw(line)
            d.rectangle((0,0,max(0,cw-1),max(0,ch-1)),outline=color(prop(n,'BorderColor'),(203,213,225,255)),width=1)
            canvas.alpha_composite(line.crop((visible[0]-rect[0],visible[1]-rect[1],visible[2]-rect[0],visible[3]-rect[1])),(visible[0],visible[1]))
    visit('conMain111',0,0,(0,0,w,h))
    filename=f'{w}x{h}-{"open" if expanded else "closed"}-{"large" if large else "standard"}-scroll{scroll}.png'
    canvas.convert('RGB').save(out/filename);shots.append(filename)
for w,h in [(1366,768),(1920,1080)]:
    for expanded in [True,False]:
        for large in [False,True]:render(w,h,expanded,large)
render(1366,768,True,False,480)
render(1366,768,False,True,1040)
(out/'layout-model-findings.json').write_text(json.dumps({'scope':'Approximation from actual YAML coordinates; Noto Sans JP substitutes Segoe UI/Japanese fallback. Not Studio.','shots':shots,'text_overflow':findings},ensure_ascii=False,indent=2))
print(json.dumps({'images':len(shots),'text_overflow_instances':len(findings)},ensure_ascii=False))
