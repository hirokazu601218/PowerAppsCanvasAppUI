"""Limited local Power Fx parser/evaluator for data-flow regression checks.
Not Microsoft's compiler. Unsupported execution functions fail explicitly.
"""
import re, math, datetime
TOKEN=re.compile(r'\s+|//[^\n]*|/\*[\s\S]*?\*/|"(?:""|[^"])*"|\d+(?:\.\d+)?|[A-Za-z_][A-Za-z_0-9]*|<>|<=|>=|&&|\|\||[=<>+*/&!.,:;(){}\[\]%-]')
class Parser:
 def __init__(self,s):
  s=s.removeprefix('=');self.t=[];pos=0
  for m in TOKEN.finditer(s):
   if m.start()!=pos:raise ValueError('Unknown token '+repr(s[pos:m.start()]))
   pos=m.end();v=m[0]
   if not v.isspace() and not v.startswith(('//','/*')):self.t.append(v)
  if pos!=len(s):raise ValueError('Unparsed suffix '+repr(s[pos:]))
  self.t.append('<END>');self.i=0
 def peek(self):return self.t[self.i]
 def pop(self,expected=None):
  s=self.peek()
  if expected is not None and s!=expected:raise ValueError(f'Expected {expected}, got {s} near {self.t[max(0,self.i-4):self.i+4]}')
  self.i+=1;return s
 def parse(self):
  a=self.expr();self.pop('<END>');return a
 def expr(self,minimum=0):
  tok=self.pop()
  if tok in ('!','-','+','Not'):a=('unary',tok,self.expr(80))
  elif tok=='(':
   a=self.expr();self.pop(')')
  elif tok=='{':
   fields=[]
   while self.peek()!='}':
    k=self.pop();self.pop(':');fields.append((k,self.expr(2)))
    if self.peek()!=',':break
    self.pop(',')
   self.pop('}');a=('record',fields)
  elif tok=='[':
   vals=[]
   while self.peek()!=']':
    vals.append(self.expr(2))
    if self.peek()!=',':break
    self.pop(',')
   self.pop(']');a=('array',vals)
  elif tok.startswith('"'):a=('literal',tok[1:-1].replace('""','"'))
  elif tok[0].isdigit():a=('literal',float(tok) if '.' in tok else int(tok))
  elif tok in ('true','false'):a=('literal',tok=='true')
  elif re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',tok):a=('id',tok)
  else:raise ValueError('Unexpected '+tok)
  prec={';':1,'As':3,'||':10,'Or':10,'&&':20,'And':20,'=':30,'<>':30,'<':30,'>':30,'<=':30,'>=':30,'in':30,'exactin':30,'&':40,'+':50,'-':50,'*':60,'/':60}
  while True:
   op=self.peek()
   if op=='.':self.pop();a=('get',a,self.pop());continue
   if op=='(':
    self.pop();args=[]
    while self.peek()!=')':
     args.append(self.expr(0))
     if self.peek()!=',':break
     self.pop(',')
    self.pop(')');a=('call',a,args);continue
   if op not in prec or prec[op]<minimum:break
   self.pop()
   if op==';' and self.peek() in ('<END>',')'):break
   b=self.expr(prec[op]+1);a=('bin',op,a,b)
  return a
def parse(s):return Parser(s).parse()
def blank(v):return v is None or v==''
def string(v):return '' if v is None else (str(int(v)) if isinstance(v,float) and v.is_integer() else str(v))
class Engine:
 def __init__(self,props=None):self.state={};self.controls=props or {};self.overrides={};self.log=[]
 def prop(self,n,k):
  if (n,k) in self.overrides:return self.overrides[n,k]
  if k=='Text' and k not in self.controls[n] and 'Default' in self.controls[n]:k='Default'
  if k=='Selected' and 'Items' in self.controls[n]:
   default=self.prop(n,'Default');return {'Value':default}
  if k not in self.controls[n]:return None
  return self.run(self.controls[n][k],{'Self':('control',n)})
 def run(self,s,env=None):return self.eval(parse(s),env or {})
 def eval(self,a,e):
  tag=a[0]
  if tag=='literal':return a[1]
  if tag=='id':
   n=a[1]
   if n in e:return e[n]
   if n in self.state:return self.state[n]
   if n in self.controls:return ('control',n)
   if n.startswith('col'):return []
   if n.startswith('var'):return None
   if n in ['DisplayMode','NotificationType','SortOrder']:return ('enum',n)
   raise ValueError('Undefined '+n)
  if tag=='get':
   v=self.eval(a[1],e)
   if v is None:return None
   if isinstance(v,tuple) and v[0]=='control':return self.prop(v[1],a[2])
   if isinstance(v,tuple) and v[0]=='enum':return v[1]+'.'+a[2]
   return v.get(a[2])
  if tag=='record':return {k:self.eval(v,e) for k,v in a[1]}
  if tag=='array':return [{'Value':self.eval(v,e)} for v in a[1]]
  if tag=='unary':
   v=self.eval(a[2],e);return not v if a[1] in ['!','Not'] else (-v if a[1]=='-' else v)
  if tag=='bin':
   op=a[1];l=self.eval(a[2],e)
   if op==';':return self.eval(a[3],e)
   if op in ['&&','And']:return bool(l) and bool(self.eval(a[3],e))
   if op in ['||','Or']:return bool(l) or bool(self.eval(a[3],e))
   r=self.eval(a[3],e)
   if op=='&':return string(l)+string(r)
   if op=='=':return l==r
   if op=='<>':return l!=r
   if op in ['in','exactin']:return string(l).lower() in string(r).lower() if op=='in' else l in r
   return {'+':lambda:l+r,'-':lambda:l-r,'*':lambda:l*r,'/':lambda:l/r,'<':lambda:l<r,'>':lambda:l>r,'<=':lambda:l<=r,'>=':lambda:l>=r}[op]()
  if tag!='call' or a[1][0]!='id':raise ValueError('Unsupported AST '+str(a)[:120])
  f=a[1][1];args=a[2];ev=lambda n:self.eval(n,e)
  if f=='With':return self.eval(args[1],e|ev(args[0]))
  if f=='If':
   for i in range(0,len(args)-1,2):
    if ev(args[i]):return ev(args[i+1])
   return ev(args[-1]) if len(args)%2 else None
  if f=='IfError':
   try:return ev(args[0])
   except Exception:raise # Do not conceal local-evaluator limitations as app error handling.
  if f=='Coalesce':
   for arg in args:
    v=ev(arg)
    if not blank(v):return v
   return None
  if f in ['ForAll','Filter','LookUp','Concat']:
   src=args[0];alias=None
   if src[0]=='bin' and src[1]=='As':alias=src[3][1];src=src[2]
   out=[]
   for row in ev(src):
    scope=e|row|{'ThisRecord':row}
    if alias:scope[alias]=row
    if f in ['Filter','LookUp']:
     if self.eval(args[1],scope):
      if f=='LookUp':return self.eval(args[2],scope) if len(args)>2 else row
      out.append(row)
    else:out.append(self.eval(args[1],scope))
   if f=='Concat':return (ev(args[2]) if len(args)>2 else '').join(map(string,out))
   return None if f=='LookUp' else out
  if f=='Set':self.state[args[0][1]]=ev(args[1]);return None
  if f in ['ClearCollect','Collect']:
   n=args[0][1];values=[]
   for arg in args[1:]:
    v=ev(arg);values.extend(v if isinstance(v,list) else [v])
   self.state[n]=values if f=='ClearCollect' else self.state.get(n,[])+values
   return self.state[n]
  if f=='RemoveIf':
   n=args[0][1];self.state[n]=[r for r in self.state[n] if not self.eval(args[1],e|r)];return self.state[n]
  if f=='Reset':
   n=args[0][1]
   self.overrides.pop((n,'Text'),None);self.overrides.pop((n,'Selected'),None);return None
  if f in ['Notify','SetFocus']:self.log.append((f,[ev(x) for x in args]));return True
  if f=='Select':raise ValueError('Select dispatch is not implemented')
  if f=='Switch':
   v=ev(args[0])
   for i in range(1,len(args)-1,2):
    if v==ev(args[i]):return ev(args[i+1])
   return ev(args[-1]) if len(args)%2==0 else None
  vals=[ev(x) for x in args]
  if f=='Table':return [row for v in vals for row in (v if isinstance(v,list) else [v])]
  if f=='Text':
   v=vals[0];fmt=vals[1] if len(vals)>1 else ''
   if isinstance(v,(datetime.datetime,datetime.date)):
    fmt=fmt.replace('yyyy','%Y').replace('yy','%y').replace('mm','%m').replace('dd','%d').replace('hh','%H').replace('ss','%S');return v.strftime(fmt)
   if fmt and re.fullmatch('0+',fmt):return str(int(v)).zfill(len(fmt))
   if fmt=='#,##0':return f'{v:,.0f}'
   return string(v)
  if f=='Date':return datetime.date(*vals)
  if f=='Now':return datetime.datetime(2026,9,11,12,0)
  if f=='Sequence':return [{'Value':i} for i in range(1,vals[0]+1)]
  if f=='Blank':return None
  if f=='First':return vals[0][0] if vals[0] else None
  if f=='Last':return vals[0][-1] if vals[0] else None
  if f=='FirstN':return vals[0][:int(vals[1])]
  if f=='LastN':return vals[0][-int(vals[1]):] if vals[1]>0 else []
  if f=='CountRows':return len(vals[0])
  if f=='IsBlank':return blank(vals[0])
  if f=='IsEmpty':return not vals[0]
  if f=='Trim':return ' '.join(string(vals[0]).split())
  if f=='Lower':return string(vals[0]).lower()
  if f=='Value':return float(vals[0])
  if f=='Left':return vals[0][:int(vals[1])]
  if f=='Char':return chr(vals[0])
  if f=='Mod':return vals[0]%vals[1]
  if f=='Max':return max(vals)
  if f=='Min':return min(vals)
  if f=='RoundUp':return math.ceil(vals[0]*10**vals[1])/10**vals[1]
  if f=='StartsWith':return string(vals[0]).startswith(vals[1])
  raise ValueError('Unsupported function '+f)
