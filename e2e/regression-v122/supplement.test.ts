import {test,expect,type Page,type FrameLocator} from '@playwright/test';
import {writeFileSync} from 'node:fs';
test.describe.configure({retries:0});
test.use({video:'off',ignoreHTTPSErrors:false});
const ctl=(a:FrameLocator,n:string)=>a.locator(`[data-control-name="${n}"]`);
const btn=(a:FrameLocator,n:string)=>a.getByRole('button',{name:n,exact:true});
async function start(page:Page){
 await page.setViewportSize({width:1366,height:768});await page.goto(process.env.CANVAS_APP_URL!,{waitUntil:'domcontentloaded',timeout:60000});
 const a=page.frameLocator('iframe[name="fullscreen-app-host"]');
 await expect(ctl(a,'lblHomePrototype')).toContainText('UI検討用 v1.23',{timeout:60000});return a;
}
async function staff(a:FrameLocator){await ctl(a,'btnHomeStaff').getByRole('button').click();await expect(ctl(a,'conscrHomeRoot')).toBeHidden();await expect(ctl(a,'lblListTitle111')).toContainText('7件');}
async function search(a:FrameLocator,q:string){await a.getByRole('searchbox').fill(q);await btn(a,'検索').click();await expect(ctl(a,'lblListTitle111')).toContainText('1件');}
const out=process.env.OUTPUT_DIRECTORY!;

test('SUPPLEMENT-INIT three reloads clear prior search, selection and PDF',async({page})=>{
 test.setTimeout(180000);let a=await start(page);await staff(a);
 for(let i=0;i<3;i++){
  await search(a,'同姓同名');await btn(a,'009900000011 試験 同姓同名 詳細を表示').click();
  await btn(a,'選択職員の認定簿を表示').click();await expect(ctl(a,'conLedgerModal111')).toBeVisible();
  a=await start(page);await expect(btn(a,'メンテナンス画面')).toBeDisabled();
  await ctl(a,'btnHomePayroll').getByRole('button').click();await expect(ctl(a,'lblPayrollStaff')).toContainText('未選択');await expect(ctl(a,'lblPaySummaryNetValue')).toHaveText('—');
  await ctl(a,'btnscrPayrollHome').getByRole('button').click();await expect(ctl(a,'btnHomeStaff')).toBeVisible();await staff(a);
  await expect(a.getByRole('searchbox')).toHaveValue('');await expect(ctl(a,'lblPersonSub111')).toContainText('009900000004');
  await expect(ctl(a,'conLedgerModal111')).toBeHidden();await expect(ctl(a,'pdfLedger111')).toBeHidden();
 }
});

test('SUPPLEMENT-CLIPBOARD denied write keeps manual TSV fallback',async({page})=>{
 await page.addInitScript(()=>{
  (window as any).__testClipboardDenials=0;
  if(navigator.clipboard)Object.defineProperty(navigator.clipboard,'writeText',{configurable:true,value:()=>{
   (window as any).__testClipboardDenials++;
   return Promise.reject(new DOMException('Synthetic clipboard permission denial','NotAllowedError'));
  }});
 });
 const a=await start(page);await staff(a);await btn(a,'検索結果をTSVで出力').click();
 await ctl(a,'btnCopy111').getByRole('button').click();
 await expect(a.getByText('コピーできません。下のテキスト欄から手動コピーしてください',{exact:true})).toBeVisible();
 const tsv=await a.getByRole('textbox',{name:'コピー用テキスト。全選択してExcelへ貼り付けできます。',exact:true}).inputValue();
 expect(tsv.trim().split('\n')).toHaveLength(8);expect(tsv).toContain('009900000011');
 let count=0;for(const frame of page.frames())count+=await frame.evaluate(()=>(window as any).__testClipboardDenials||0).catch(()=>0);
 expect(count).toBeGreaterThan(0);
 writeFileSync(`${out}/clipboard-denied.json`,JSON.stringify({injection:'browser Clipboard.writeText NotAllowedError; no app variable or auth changes',denials:count,manualRows:tsv.trim().split('\n').length}));
});

test('SUPPLEMENT-KEYBOARD full closed-sidebar Tab circuit and reopening',async({page})=>{
 const a=await start(page);await staff(a);const toggle=ctl(a,'btnSidebarToggle111').getByRole('button');
 await toggle.focus();await page.keyboard.press('Enter');await expect(a.getByRole('searchbox')).toBeHidden();
 const seen=[];let returned=false;
 for(let i=0;i<100;i++){
  await page.keyboard.press('Tab');
  const focused=await a.locator('body').evaluate(el=>el.ownerDocument.activeElement?.closest('[data-control-name]')?.getAttribute('data-control-name')||'outside-app');
  seen.push(focused);
  expect(['txtKeyword111','ddOrg111','ddStatus111','btnSearch111','btnClear111','btnRow111','btnPrev111','btnNext111']).not.toContain(focused);
  if(focused==='btnSidebarToggle111'){returned=true;break;}
 }
 expect(returned).toBe(true);await page.keyboard.press('Enter');await expect(a.getByRole('searchbox')).toBeVisible();
 let inputReached=false;for(let i=0;i<30;i++){await page.keyboard.press('Tab');if(await a.getByRole('searchbox').evaluate(el=>el===el.ownerDocument.activeElement)){inputReached=true;break;}}
 expect(inputReached).toBe(true);await page.keyboard.type('同姓同名');
 writeFileSync(`${out}/keyboard-sidebar-circuit.json`,JSON.stringify({seen,inputReached}));
});

test('SUPPLEMENT-PERF ten starts and twenty measured searches selections and toggles',async({page})=>{
 test.setTimeout(360000);let a:FrameLocator;const raw:any={startup:[],search:[],selection:[],close:[],open:[]};
 for(let i=0;i<10;i++){const t=Date.now();a=await start(page);raw.startup.push(Date.now()-t);}
 await staff(a!);
 for(let i=0;i<20;i++){
  let t=Date.now();await search(a!,'同姓同名');raw.search.push(Date.now()-t);
  t=Date.now();await btn(a!,'009900000011 試験 同姓同名 詳細を表示').click();await expect(ctl(a!,'lblPersonSub111')).toContainText('009900000011');raw.selection.push(Date.now()-t);
  t=Date.now();await btn(a!,'職員検索を閉じる').click();await expect(a!.getByRole('searchbox')).toBeHidden();raw.close.push(Date.now()-t);
  t=Date.now();await btn(a!,'職員検索を開く').click();await expect(a!.getByRole('searchbox')).toBeVisible();raw.open.push(Date.now()-t);
  await btn(a!,'検索条件をクリア').click();await expect(ctl(a!,'lblListTitle111')).toContainText('7件');
 }
 const limits:any={startup:30000,search:2000,selection:2000,close:1000,open:1000};const p95:any={};
 for(const key of Object.keys(raw)){const sorted=[...raw[key]].sort((a:number,b:number)=>a-b);p95[key]=sorted[Math.ceil(sorted.length*.95)-1];}
 writeFileSync(`${out}/performance-remaining.json`,JSON.stringify({method:'nearest-rank p95; starts include navigation; authenticated context; no sleeps',raw,p95,limits},null,2));
 writeFileSync(`${out}/performance-remaining.csv`,'operation,iteration,milliseconds\n'+Object.entries(raw).flatMap(([k,values]:any)=>values.map((v:number,i:number)=>`${k},${i+1},${v}`)).join('\n'));
 console.log('PERFORMANCE_P95 '+JSON.stringify(p95));
 for(const key of Object.keys(limits))expect.soft(p95[key],`${key} p95 milliseconds`).toBeLessThanOrEqual(limits[key]);
});
