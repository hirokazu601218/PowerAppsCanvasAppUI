"""Limited layout/data-flow model, NOT Power Apps rendering or compilation."""
import functools
import fx_check
fx_check.parse = functools.lru_cache(maxsize=4096)(fx_check.parse)

class ModelEngine(fx_check.Engine):
    def __init__(self, nodes, parents, width=1366, height=768):
        super().__init__({n:c['Properties'] for n,c in nodes.items()})
        self.nodes=nodes; self.parents=parents; self.rows={}
        self.controls['__screen']={'Width':f'={width}','Height':f'={height}'}
        self.parents['__screen']=None
    def prop(self,n,k):
        if (n,k) in self.overrides:return self.overrides[n,k]
        if k=='TemplateWidth':return self.prop(n,'Width')-2*(self.prop(n,'TemplatePadding') or 0)
        if k=='TemplateHeight':return self.prop(n,'TemplateSize')
        if k=='Selected' and self.nodes.get(n,{}).get('Control','').startswith('Gallery'):
            return self.prop(n,'Default') or ((self.prop(n,'Items') or [None])[0])
        if k=='Text' and k not in self.controls[n] and 'Default' in self.controls[n]: k='Default'
        if k=='Selected' and 'Items' in self.controls[n]:return {'Value':self.prop(n,'Default')}
        if k not in self.controls[n]:
            return {'Visible':True,'PaddingLeft':0,'PaddingTop':0,'PaddingRight':0,'PaddingBottom':0}.get(k)
        env={'Self':('control',n),'Parent':('control',self.parents.get(n) or '__screen')}
        p=self.parents.get(n)
        while p:
            if p in self.rows:
                env['ThisItem']=self.rows[p];break
            p=self.parents.get(p)
        return self.run(self.controls[n][k],env)
    def eval(self,a,e):
        if a[0]=='id' and a[1] in ['FontWeight','Align','VerticalAlign','DropShadow','LayoutOverflow','LayoutDirection','LayoutAlignItems','LayoutJustifyContent','Live','ButtonAppearance','Appearance','TextInputType','TriggerOutput','ImagePosition','Color','Icon','BorderStyle']:
            return ('enum',a[1])
        if a[0]=='call' and a[1]==('id','ColorValue'):return self.eval(a[2][0],e)
        if a[0]=='call' and a[1]==('id','RGBA'):return tuple(self.eval(x,e) for x in a[2])
        return super().eval(a,e)
    def rect(self,n):
        return tuple(self.prop(n,k) or 0 for k in ['X','Y','Width','Height'])
