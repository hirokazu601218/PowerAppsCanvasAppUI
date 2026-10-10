// Executes the actual reviewed TypeScript helper functions against synthetic DOM
// objects. This is NOT a browser, Playwright run, or Power Apps runtime result.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const {stripTypeScriptTypes} = require('node:module');
function repositoryRoot(){
 if(process.env.PAY_REVIEW_ROOT)return path.resolve(process.env.PAY_REVIEW_ROOT);
 let current=__dirname;
 while(!fs.existsSync(path.join(current,'AGENTS.md'))){const parent=path.dirname(current);if(parent===current)throw new Error('Set PAY_REVIEW_ROOT to the candidate repository root');current=parent}
 return current;
}
const sourcePath = process.env.PAY_REVIEW_E2E_SOURCE || path.join(repositoryRoot(), 'e2e/current-app/state-retention.test.ts');
const source = fs.readFileSync(sourcePath,'utf8');
const registered = [];
const test = (name,fn) => registered.push(name);
test.describe = { configure(){} }; test.use = () => {};
function expect(actual, message='') {
 return {
   not: {toBeNull(){assert.notEqual(actual,null,message);}},
   toBeLessThanOrEqual(v){assert.ok(actual<=v,message)},
   toBeGreaterThan(v){assert.ok(actual>v,message)},
   toEqual(v){assert.deepEqual(actual,v,message)},
   async toBeInViewport(){ /* ancestor checks are isolated; no fake browser pass */ },
 };
}
expect.poll=(fn)=>({async toBeGreaterThanOrEqual(target){for(let i=0;i<20;i++)if(await fn()>=target)return;throw new Error('geometry did not settle')}});
const document = {
 createTreeWalker(el){let i=-1;const nodes=el._texts||[];return {nextNode(){i++;this.currentNode=nodes[i];return i<nodes.length},currentNode:null}},
 createRange(){let node;return {selectNodeContents(n){node=n},getClientRects(){return node.rects()}}},
};
const context = vm.createContext({test,expect,getComputedStyle:e=>e.style,document,NodeFilter:{SHOW_TEXT:4},console});
const js = stripTypeScriptTypes(source.replace(/^import .*?;\n/,''));
vm.runInContext(js+'\nglobalThis.reviewHelpers={waitForPayrollGeometry,scrollPayrollBodyToEnd,assertLastDeductionReachable};',context);

function fixture(height, content, scale=1, textProblem=null) {
 const els = {};
 function make(key, owner, y, h, w=900, parent=null, overflow='visible') {
   const e={key,owner,clientHeight:h,clientWidth:w,clientLeft:0,clientTop:0,offsetWidth:w,offsetHeight:h,
     style:{overflowX:'visible',overflowY:overflow,display:'block',visibility:'visible'},parentElement:parent,tagName:'DIV', _top:0,
     scrollHeight:h,
     getAttribute(k){return k==='data-control-name'?owner:null},
     closest(){let p=this;while(p&&!p.owner)p=p.parentElement;return p},
     querySelectorAll(){return Object.values(els).filter(v=>{for(let p=v.parentElement;p;p=p.parentElement)if(p===this)return true;return false})},
     getBoundingClientRect(){const yy=typeof y==='function'?y():y; return {x:0,y:yy*scale,top:yy*scale,left:0,right:w*scale,bottom:(yy+h)*scale,width:w*scale,height:h*scale}}};
   Object.defineProperty(e,'scrollTop',{get(){return this._top},set(v){this._top=Math.max(0,Math.min(v,this.scrollHeight-this.clientHeight))}});
   els[key]=e;return e;
 }
 const root=make('root','conscrPayrollRoot',0,900);
 const body=make('body','conPayBody',200,500,900,root);
 const scroller=make('scroller',null,200,500,900,body,'auto'); scroller.scrollHeight=600+height+20;
 const ded=make('ded','conPayDeductions',()=>800-scroller.scrollTop,height,860,scroller,'hidden');ded.scrollHeight=content;
 const rowH=content>1000?128:64;
 const row=make('row','conPayDeduction7',()=>800-scroller.scrollTop+content-rowH,rowH,836,ded);
 for(const [name,width] of [['lblPayDeductionName7',260],['lblPayDeductionBasis7',380],['lblPayDeductionAmount7',138]]){
   const label=make(name,name,()=>800-scroller.scrollTop+content-rowH,rowH,width,row);
   label.style.overflowX='hidden';label.style.overflowY='hidden';
   label._texts = textProblem==='missing' ? [] : [{textContent:'Rendered text',parentElement:label,rects(){
    const r=label.getBoundingClientRect();const box={left:r.left+4*scale,top:r.top+4*scale,right:r.left+Math.min(80,width-8)*scale,bottom:r.top+20*scale};
    if(textProblem==='horizontal'&&name==='lblPayDeductionBasis7')box.right=r.right+12*scale;
    if(textProblem==='vertical'&&name==='lblPayDeductionBasis7')box.bottom=r.bottom+12*scale;
    box.width=box.right-box.left;box.height=box.bottom-box.top;return [box];
   }}];
 }
 const app={locator(selector){const name=selector.match(/"([^"]+)"/)[1];const e=Object.values(els).find(v=>v.owner===name);assert.ok(e,name);return {evaluate:async fn=>fn(e)}}};
 return {app,scroller,ded};
}
(async()=>{
 let passed=0;
 for(const scale of [1,0.681]){
  for(const [label,height,content,shouldPass] of [['old_wide',698,728,false],['old_narrow',698,1240,false],['new_wide',728,728,true],['new_narrow',1240,1240,true]]){
   const {app,scroller,ded}=fixture(height,content,scale);
   let error=null;try{await context.reviewHelpers.assertLastDeductionReachable(app)}catch(e){error=e}
   assert.equal(error===null,shouldPass,label+': '+error);
   assert.equal(ded.scrollTop,0,'hidden deduction scroller must never be moved');
   assert.equal(scroller.scrollTop,scroller.scrollHeight-scroller.clientHeight,'actual body reaches end');
   console.log(`${label} scale=${scale}: ${shouldPass?'accepted':'rejected'} as expected`);passed++;
  }
 }
 for(const problem of ['horizontal','vertical','missing']){
   const {app,scroller,ded}=fixture(728,728,1,problem);
   let error=null;try{await context.reviewHelpers.assertLastDeductionReachable(app)}catch(e){error=e}
   assert.notEqual(error,null,`internal text ${problem} must reject despite unclipped field rectangles`);
   assert.equal(ded.scrollTop,0);console.log(`internal_text_${problem}: rejected as expected`);passed++;
 }
 const A=[['conPaySummary',0,100,900,104,104],['conPayBody',0,204,900,500,1200],['conPayDeductions',0,0,848,728,728],['conPayDeduction7',0,664,824,64,64]];
 const B=JSON.parse(JSON.stringify(A));B[1][3]=788;B[2][4]=1240;B[3][4]=128;
 let polls=0;const sequence=[A,B,B,B];
 await context.reviewHelpers.waitForPayrollGeometry({locator(){return {evaluate:async()=>sequence[Math.min(polls++,sequence.length-1)]}}});
 assert.equal(polls,4,'wait must observe two stable repeats after changed geometry');
 console.log('geometry_changed_then_stable: accepted after 4 polls');passed++;
 let missingError=null;try{await context.reviewHelpers.waitForPayrollGeometry({locator(){return {evaluate:async()=>[null,null,null,null]}}})}catch(e){missingError=e}
 assert.notEqual(missingError,null);console.log('geometry_missing: rejected');passed++;
 assert.equal(registered.length,11,'source registers expected suite');
 assert.ok(source.includes('keeping height768 is NOT a browser 200% zoom test'));
 console.log(`PASS: ${passed} helper mock fixtures; ${registered.length} tests registered; no browser executed.`);
})().catch(e=>{console.error(e);process.exitCode=1});
