"""Local, limited preflight for the emitted Canvas YAML; NOT the Studio validator.

Property names: Microsoft Learn control-button, control-text-box,
control-text-input, control-drop-down, control-gallery, control-timer,
control-horizontal-container. GroupContainer serialized layout names and current
version additionally grounded in the user's Studio PA2105/PA2108 diagnostics.
No Power Fx execution or authentication performed.
"""
from pathlib import Path
from copy import deepcopy
from collections import Counter
from itertools import combinations
import yaml,re,json,hashlib

BASE=Path(__file__).resolve().parents[1]
SRC=BASE/'src/staff-master'
class StrictLoader(yaml.SafeLoader):pass
def strict_mapping(loader,node,deep=False):
    out={}
    for kn,vn in node.value:
        key=loader.construct_object(kn,deep=deep)
        if key in out:raise ValueError('Duplicate YAML key: '+key)
        out[key]=loader.construct_object(vn,deep=deep)
    return out
StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,strict_mapping)
def read(p):return yaml.load(p.read_text(),Loader=StrictLoader)
def index(children):
    out={};parents={}
    def visit(items,parent=None):
        assert isinstance(items,list)
        for obj in items:
            assert isinstance(obj,dict) and len(obj)==1
            name,c=next(iter(obj.items()));assert name not in out,name
            assert set(c)<=set('Control Variant Properties Children'.split()),name
            assert isinstance(c['Properties'],dict)
            out[name]=c;parents[name]=parent
            if 'Children' in c:visit(c['Children'],name)
    visit(children)
    return out,parents

# Independent, documented allowlists for the seven controls used in this file.
# These are not Microsoft's complete/versioned Source Code schema.
S=lambda text:set(text.split())
geo=S('X Y Width Height Visible')
border=S('BorderColor BorderStyle BorderThickness')
font=S('Font FontWeight Size Color Italic Underline Strikethrough')
pad=S('PaddingLeft PaddingRight PaddingTop PaddingBottom')
radius=S('RadiusTopLeft RadiusTopRight RadiusBottomLeft RadiusBottomRight')
states=S('DisabledBorderColor DisabledColor DisabledFill FocusedBorderColor FocusedBorderThickness HoverBorderColor HoverColor HoverFill PressedBorderColor PressedColor PressedFill')
allowed={
 'Classic/Button@2.2.0':geo|border|font|pad|radius|states|S('Text OnSelect Fill Align VerticalAlign DisplayMode Tooltip TabIndex AutoDisableOnSelect ContentLanguage'),
 'Label@2.5.1':geo|border|font|pad|states|S('Text OnSelect Fill Align VerticalAlign DisplayMode Tooltip TabIndex AutoHeight Wrap LineHeight Live Role Overflow'),
 'Classic/TextInput@2.3.2':geo|border|font|pad|radius|states|S('Text Default HintText Mode OnChange OnSelect Fill Align DisplayMode AccessibleLabel Tooltip TabIndex DelayOutput Clear EnableSpellCheck Format MaxLength Reset LineHeight VirtualKeyboardMode'),
 'Classic/DropDown@2.3.1':geo|border|font|pad|states|S('Default Items OnChange OnSelect Fill DisplayMode AccessibleLabel Tooltip TabIndex AllowEmptySelection ChevronBackground ChevronFill ChevronDisabledBackground ChevronDisabledFill ChevronHoverBackground ChevronHoverFill SelectionColor SelectionFill Reset'),
 'Gallery@2.15.0':geo|border|S('Items Default OnSelect Fill AccessibleLabel ItemAccessibleLabel Selectable ShowNavigation ShowScrollbar TemplateFill TemplatePadding TemplateSize WrapCount DelayItemLoading DisplayMode LoadingSpinner LoadingSpinnerColor NavigationStep Transition'),
 'Timer@2.1.0':geo|border|font|pad|radius|states|S('AutoStart AutoPause Duration OnTimerStart OnTimerEnd Repeat Reset Start Value Text Fill DisplayMode Tooltip TabIndex'),
 'GroupContainer@1.5.0':geo|border|radius|pad|S('Fill DropShadow FillPortions AlignInContainer LayoutAlignItems LayoutDirection LayoutGap LayoutJustifyContent LayoutMinHeight LayoutMinWidth LayoutOverflowX LayoutOverflowY LayoutWrap'),
}
def lint(children):
    nodes,_=index(children);errors=[];warnings=[]
    for name,c in nodes.items():
        control=c['Control']
        if control=='GroupContainer@1.3.0':
            warnings.append((name,'older GroupContainer 1.3.0; target 1.5.0'));control='GroupContainer@1.5.0'
        if control not in allowed:errors.append((name,'unknown control '+control));continue
        for p in sorted(set(c['Properties'])-allowed[control]):errors.append((name,'unknown property '+p))
        for p,v in c['Properties'].items():
            if not isinstance(v,str) or not v.startswith('='):errors.append((name,'non-formula property '+p))
        if control.startswith('GroupContainer') and c.get('Variant') not in ['AutoLayout','ManualLayout']:errors.append((name,'unsupported container variant'))
    return errors,warnings
