// Execute actual TypeScript navigation helpers with synthetic DOM/locator objects.
// This is not Playwright, browser input, Power Fx, or Canvas runtime evidence.
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const {stripTypeScriptTypes}=require('node:module');
function repositoryRoot(){
  if(process.env.PAY_REVIEW_ROOT)return path.resolve(process.env.PAY_REVIEW_ROOT);
  let current=__dirname;
  while(!fs.existsSync(path.join(current,'AGENTS.md'))){
    const parent=path.dirname(current);
    if(parent===current)throw new Error('Run from a candidate checkout or set PAY_REVIEW_ROOT');
    current=parent;
  }
  return current;
}
const sourcePath=process.env.PAY_REVIEW_E2E_SOURCE||path.join(repositoryRoot(),'e2e/current-app/state-retention.test.ts');
const source=fs.readFileSync(sourcePath,'utf8');
const registered=[];
const test=(name,fn)=>registered.push(name);
test.describe={configure(){}};
test.use=()=>{};
function expect(actual,message=''){
  return {
    not:{toBeNull(){assert.notEqual(actual,null,message)},toBe(v){assert.notEqual(actual,v,message)}},
    toBe(v){assert.equal(actual,v,message)},
    toBeDefined(){assert.notEqual(actual,undefined,message)},
    toBeLessThanOrEqual(v){assert.ok(actual<=v,message)},
    toBeGreaterThan(v){assert.ok(actual>v,message)},
    toBeGreaterThanOrEqual(v){assert.ok(actual>=v,message)},
    toEqual(v){assert.equal(JSON.stringify(actual),JSON.stringify(v),message)},
    async toBeVisible(){assert.ok(actual.element,message)},
    async toBeInViewport(){/* Actual helper's clipping checks run; no fake browser pass. */},
  };
}
expect.poll=fn=>({
  async toBeGreaterThanOrEqual(v){for(let i=0;i<20;i++)if(await fn()>=v)return;throw new Error('poll did not settle')},
  not:{async toBe(v){for(let i=0;i<20;i++)if(await fn()!==v)return;throw new Error('offset did not move')}},
});
const context=vm.createContext({test,expect,console,NodeFilter:{SHOW_TEXT:4},innerWidth:800,innerHeight:600,
  getComputedStyle:e=>e.style,window:{scrollX:0,scrollY:0}});
const js=stripTypeScriptTypes(source.replace(/^import .*?;\n/,''));
vm.runInContext(js+'\nglobalThis.reviewHelpers={rootPorts,portGeometry,wheelRoot,reachByRoot};',context);

function fixture({frameX=137,frameY=83,split=true,hiddenY=false,badNested=false,textOverflow=false,outerScale=1}={}){
  const nodes=[];
  let xPort,yPort;
  function element(name,parent,rect,style={},dimensions={}){
    const initial=rect();
    const e={name,parentElement:parent,tagName:'DIV',style:{overflowX:'visible',overflowY:'visible',display:'block',visibility:'visible',...style},
      clientLeft:0,clientTop:0,clientWidth:initial.width,clientHeight:initial.height,
      offsetWidth:initial.width,offsetHeight:initial.height,scrollWidth:initial.width,scrollHeight:initial.height,_x:0,_y:0,
      getBoundingClientRect(){const b=rect();return {...b,left:b.x,top:b.y,right:b.x+b.width,bottom:b.y+b.height}},
      getAttribute(k){return k==='data-control-name'?name:null},
      contains(other){for(let p=other;p;p=p.parentElement)if(p===this)return true;return false},
      closest(){for(let p=this;p;p=p.parentElement)if(p.name)return p;return null},
      querySelectorAll(){return nodes.filter(n=>n!==this&&this.contains(n))},
      querySelector(selector){const name=selector.match(/"([^"]+)"/)[1];return this.querySelectorAll().find(n=>n.name===name)||null},
      ...dimensions};
    Object.defineProperties(e,{
      scrollLeft:{get(){return this._x},set(v){this._x=Math.max(0,Math.min(v,this.scrollWidth-this.clientWidth))}},
      scrollTop:{get(){return this._y},set(v){this._y=Math.max(0,Math.min(v,this.scrollHeight-this.clientHeight))}},
    });
    nodes.push(e);return e;
  }
  const rootRect=()=>({x:20,y:30,width:400,height:300});
  const host=element(null,null,rootRect,{overflowX:'hidden',overflowY:'hidden'});
  const root=element('conscrPayrollRoot',host,rootRect);
  xPort=element(null,root,rootRect,{overflowX:'auto',overflowY:split?'visible':hiddenY?'hidden':'auto'},
    {scrollWidth:750,scrollHeight:split?300:1900});
  yPort=split?element(null,xPort,()=>({x:20-xPort.scrollLeft,y:30,width:750,height:300}),
    {overflowY:hiddenY?'hidden':'auto'},{scrollHeight:1900}):xPort;
  const position=(x,y,w,h)=>()=>({x:20+x-xPort.scrollLeft,y:30+y-yPort.scrollTop,width:w,height:h});
  element('conscrPayrollHeader',yPort,position(0,0,750,64));
  element('conPayrollTargets',yPort,position(0,64,750,108));
  element('conPaySummary',yPort,position(0,172,750,104));
  const body=element('conPayBody',yPort,position(0,276,750,1600),{overflowY:'hidden'});
  const nested=element(null,body,position(0,276,750,1600),{overflowY:'hidden'},{scrollHeight:1700});
  const deductions=element('conPayDeductions',nested,position(20,500,710,1300),{overflowY:'hidden'});
  const row=element('conPayDeduction7',deductions,position(32,1500,686,128));
  const field=element('lblPayDeductionBasis7',row,position(500,1500,180,128),{overflowX:'hidden',overflowY:'hidden'});
  field.textNodes=[{textContent:'Visible fixture text',parentElement:field,
    rects(){const r=field.getBoundingClientRect();const width=textOverflow?200:150;return [{left:r.x+4,top:r.y+4,right:r.x+4+width,bottom:r.y+24,width,height:20}]}}];
  // A nested independently scrollable control must never be selected as a root port.
  element('nestedUnrelated',body,position(0,400,100,80),{overflowX:'auto',overflowY:'auto'},{scrollWidth:500,scrollHeight:500});
  const frame={tagName:'IFRAME'};
  const appDocument={
    elementFromPoint(x,y){return x>=20&&x<=420&&y>=30&&y<=330?yPort:null},
    createTreeWalker(el){let i=-1;const list=el.textNodes||[];return {currentNode:null,nextNode(){this.currentNode=list[++i];return i<list.length}}},
    createRange(){let n;return {selectNodeContents(value){n=value},getClientRects(){return n.rects()}}},
  };
  const mainDocument={elementFromPoint(x,y){return x>=frameX&&y>=frameY?frame:null}};
  context.document=appDocument;
  function locator(e){
    return {element:e,
      async evaluate(fn,arg){context.document=appDocument;return fn(e,arg)},
      async boundingBox(){const r=e.getBoundingClientRect();return {x:r.x*outerScale+frameX,y:r.y*outerScale+frameY,width:r.width*outerScale,height:r.height*outerScale}},
      locator(selector){assert.equal(selector,'xpath=descendant-or-self::*');const list=[e,...e.querySelectorAll()];return {nth(i){return locator(list[i])}}},
    };
  }
  const app={locator(selector){const name=selector.match(/"([^"]+)"/)[1];const e=nodes.find(e=>e.name===name);assert.ok(e,name);return locator(e)}};
  const wheelCalls=[];
  const page={
    viewportSize(){return {width:800,height:600}},
    locator(selector){assert.ok(selector.includes('fullscreen-app-host'));return {async evaluate(fn,arg){context.document=mainDocument;const value=fn(frame,arg);context.document=appDocument;return value}}},
    async evaluate(fn){return fn()},
    mouse:{async move(x,y){assert.ok(x>=frameX&&y>=frameY)},async wheel(x,y){wheelCalls.push([x,y]);xPort.scrollLeft+=x;yPort.scrollTop+=y;if(badNested)nested.scrollTop+=1}},
  };
  return {app,page,root,xPort,yPort,nested,field,wheelCalls};
}

(async()=>{
  let passed=0;
  for(const split of [false,true]){
    const f=fixture({split});
    const ports=await context.reviewHelpers.rootPorts(f.app);
    assert.equal(ports.x.element,f.xPort);assert.equal(ports.y.element,f.yPort);
    const geom=await context.reviewHelpers.portGeometry(ports.x,f.page);
    assert.equal(geom.left,157);assert.equal(geom.top,113);
    assert.equal(geom.right,557);assert.equal(geom.bottom,413);
    assert.equal(geom.offsetX,137);assert.equal(geom.offsetY,83);
    await context.reviewHelpers.wheelRoot(f.page,f.app,ports,'x',100);
    await context.reviewHelpers.wheelRoot(f.page,f.app,ports,'y',200);
    assert.equal(f.xPort.scrollLeft,100);assert.equal(f.yPort.scrollTop,200);
    assert.equal(f.nested.scrollTop,0);
    console.log(`${split?'split':'combined'}_root_ports_translate_iframe_and_route_wheel: accepted`);passed++;
    await context.reviewHelpers.reachByRoot(f.page,f.app,ports,'lblPayDeductionBasis7');
    assert.ok(f.xPort.scrollLeft>100);assert.ok(f.yPort.scrollTop>200);
    assert.equal(f.nested.scrollTop,0);
    assert.ok(f.wheelCalls.length>=4);
    console.log(`${split?'split':'combined'}_root_ports_reach_field_without_hidden_scroll: accepted`);passed++;
  }
  for(const options of [{hiddenY:true},{badNested:true},{textOverflow:true},{outerScale:0.8}]){
    const f=fixture(options);let failure;
    try{
      const ports=await context.reviewHelpers.rootPorts(f.app);
      await context.reviewHelpers.reachByRoot(f.page,f.app,ports,'lblPayDeductionBasis7');
    }catch(error){failure=error}
    assert.ok(failure,`must reject ${JSON.stringify(options)}`);
    console.log(`${Object.keys(options)[0]}: rejected as expected`);passed++;
  }
  assert.equal(registered.length,12);
  assert.equal((source.match(/type: 'keyboard-acceptance'/g)||[]).length,2);
  assert.ok(source.includes('NOT_RUN: pointer reachability only'));
  console.log(`PASS: ${passed} root-port synthetic fixtures; ${registered.length} cases registered; no browser executed.`);
})().catch(error=>{console.error(error);process.exitCode=1});
