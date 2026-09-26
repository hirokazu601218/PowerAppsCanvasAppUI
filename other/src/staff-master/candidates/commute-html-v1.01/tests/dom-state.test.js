// Simulated DOM: verifies fail-closed state transitions, not browser layout/auth.
const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const fixture=require('./commute-6.json')[2];
function page({overflow=false,search='?id='+fixture.id,status=200}={}){
 const handlers={},printHandlers={},classes=new Set(),fields=[{dataset:{field:'name'},textContent:'old',clientHeight:10,scrollHeight:overflow?20:10,clientWidth:20,scrollWidth:20}],state={prints:0,calls:0};
 const report={hidden:true,querySelectorAll:q=>q==='[data-field]'?fields:[{clientHeight:700,scrollHeight:700,clientWidth:1000,scrollWidth:1000}]};
 const button={disabled:true,addEventListener:(e,f)=>printHandlers[e]=f};
 const msg={textContent:'',setAttribute:()=>{}};
 const document={getElementById:id=>({report,print:button,status:msg}[id]),body:{classList:{add:v=>classes.add(v),remove:v=>classes.delete(v)}},fonts:{ready:Promise.resolve()},addEventListener:(e,f)=>handlers[e]=f};
 const window={document,location:{protocol:'https:',search},requestAnimationFrame:f=>f(),print:()=>state.prints++,addEventListener:(e,f)=>handlers[e]=f,fetch:async()=>{state.calls++;return{ok:status===200,status,headers:{get:()=> 'application/json'},json:async()=>state.calls===1?{...fixture.data,crb3c_commuteid:fixture.id,_crb3c_staffbasicid_value:fixture.parent_id}:{crb3c_staffbasicid:fixture.parent_id,crb3c_staffnumber:fixture.data.crb3c_staffnumber,crb3c_fullname:fixture.data.crb3c_fullname,crb3c_orgshort:'架空所属'}};}};
 vm.runInNewContext(fs.readFileSync(require.resolve('../src/report.js'),'utf8'),{window,URLSearchParams,Intl,Date,AbortController,setTimeout,clearTimeout});
 return {handlers,printHandlers,report,button,msg,fields,classes,state};
}
test('valid data becomes ready and allows print only after both reads',async()=>{const p=page();assert.equal(p.report.hidden,true);await p.handlers.DOMContentLoaded();assert.equal(p.state.calls,2);assert.equal(p.report.hidden,false);assert.equal(p.fields[0].textContent,fixture.data.crb3c_fullname);assert.equal(p.button.disabled,false);p.printHandlers.click();assert.equal(p.state.prints,1);});
test('overflow suppresses report and clears fields; no incorrect printable page',async()=>{const p=page({overflow:true});await p.handlers.DOMContentLoaded();assert.equal(p.report.hidden,true);assert.equal(p.button.disabled,true);assert.equal(p.fields[0].textContent,'');assert.equal(p.classes.has('ready'),false);assert.match(p.msg.textContent,/収まらない/);});
test('unselected and HTTP-denied pages never become ready',async()=>{for(const options of [{search:''},{status:403},{status:404}]){const p=page(options);await p.handlers.DOMContentLoaded();assert.equal(p.report.hidden,true);assert.equal(p.button.disabled,true);assert.equal(p.classes.has('ready'),false);if(options.search==='')assert.equal(p.state.calls,0);}});
test('resize/font overflow detected before printing clears previous valid data',async()=>{const p=page();await p.handlers.DOMContentLoaded();p.fields[0].scrollHeight=100;p.handlers.beforeprint();assert.equal(p.report.hidden,true);assert.equal(p.fields[0].textContent,'');assert.equal(p.classes.has('ready'),false);});
