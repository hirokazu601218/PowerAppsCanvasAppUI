import {test, expect, type Page, type FrameLocator, type Locator} from '@playwright/test';
import {readFileSync, writeFileSync, mkdirSync} from 'node:fs';
import path from 'node:path';

// Read-only regression against the published app. All state changes below use UI controls.
test.describe.configure({retries: 0});
test.use({video: 'off', ignoreHTTPSErrors: false});
test.setTimeout(120000);
const staffFixture = JSON.parse(readFileSync(path.join(process.env.FIXTURE_ROOT!, 'staff-basic-25.json'),'utf8'));
const payrollFixture = JSON.parse(readFileSync(path.join(process.env.FIXTURE_ROOT!, 'payrollledger-7.json'),'utf8'));
const fields = JSON.parse(readFileSync(path.join(process.env.CONFIG_ROOT!, 'payrollledger-columns.json'),'utf8')).fields;
const out = process.env.OUTPUT_DIRECTORY || 'test-results';
const c = (p:Page) => p.frameLocator('iframe[name="fullscreen-app-host"]');
const ctl = (a:FrameLocator,n:string) => a.locator(`[data-control-name="${n}"]`);
const btn = (a:FrameLocator,n:string) => a.getByRole('button',{name:n,exact:true});
const expectedIds = (dept:string) => staffFixture.filter((s:any)=>s.orgshort===dept).map((s:any)=>s.staffnumber);
async function start(p:Page,w=1366,h=768) {
  await p.setViewportSize({width:w,height:h});
  await p.goto(process.env.CANVAS_APP_URL!,{waitUntil:'domcontentloaded',timeout:60000});
  const a=c(p);
  await expect(ctl(a,'lblHomePrototype')).toContainText('UI検討用 v1.26',{timeout:60000});
  return a;
}
async function home(a:FrameLocator) {await btn(a,'ホーム').first().click(); await expect(ctl(a,'btnHomeStaff')).toBeVisible();await expect(ctl(a,'conStaffNavigation122')).toBeHidden();await expect(ctl(a,'conscrPayrollRoot')).toBeHidden();}
async function staff(a:FrameLocator) {await ctl(a,'btnHomeStaff').getByRole('button').click();await expect(ctl(a,'lblMeta111')).toContainText('v1.26');await expect(ctl(a,'conscrHomeRoot')).toBeHidden();}
async function department(a:FrameLocator,dept:string) {
  if(!await ctl(a,'btnHomeStaff').isVisible()) await home(a);
  await ctl(a,'ddHomeDepartment').click(); await a.getByRole('option',{name:dept,exact:true}).click();
  await staff(a);await expect(ctl(a,'lblMeta111')).toContainText(dept);
}
async function search(a:FrameLocator,q:string) {
  const input=a.getByRole('searchbox',{name:'氏名・職員番号・項目を検索',exact:true});
  await input.fill(q);await btn(a,'検索').click();
}
async function ids(a:FrameLocator) {
  return (await a.getByRole('button',{name:/^009900000\d{3} .* 詳細を表示$/}).allTextContents()).map(s=>s.trim().slice(0,12));
}
async function select(a:FrameLocator,id:string) {
  const s=staffFixture.find((s:any)=>s.staffnumber===id);
  if(!s?.orgshort) throw new Error('Unassigned staff is intentionally unavailable through the department profile');
  await department(a,s.orgshort);await search(a,id);
  await a.getByRole('button',{name:new RegExp('^'+id+' .* 詳細を表示$')}).click();
  await expect(ctl(a,'lblPersonMeta111').or(a.getByText(`職員番号：${id} ／ 所属：${s.orgshort}`,{exact:true})).first()).toBeVisible();
}
async function snapshot(p:Page,a:FrameLocator,name:string) {
  mkdirSync(out,{recursive:true});
  await p.locator('iframe[name="fullscreen-app-host"]').screenshot({path:path.join(out,name+'.png'),mask:[ctl(a,'lblHomeAccount'),ctl(a,'lblStaffAccount122')]});
  const metrics=await a.locator('body').evaluate(el=>({clientWidth:el.ownerDocument.documentElement.clientWidth,clientHeight:el.ownerDocument.documentElement.clientHeight,dpr:window.devicePixelRatio,font:getComputedStyle(el).fontFamily}));
  writeFileSync(path.join(out,name+'-environment.json'),JSON.stringify({viewport:p.viewportSize(),browser:p.context().browser()?.version(),browserZoom:'100% default',osScale:'headless Linux default',...metrics},null,2));
}
async function box(l:Locator){await expect(l).toBeVisible();const b=await l.boundingBox();expect(b).not.toBeNull();return b!;}
async function noOverlap(ls:Locator[]) {
  const bs=[];for(const l of ls)bs.push(await box(l));
  for(let i=0;i<bs.length;i++)for(let j=i+1;j<bs.length;j++){
    const a=bs[i],b=bs[j];expect(Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x)>1&&Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y)>1,`overlap ${i}/${j}`).toBe(false);
  }
  return bs;
}
async function payroll(a:FrameLocator){await ctl(a,await ctl(a,'btnHomePayroll').isVisible()?'btnHomePayroll':'btnStaffPayroll122').getByRole('button').click();await expect(ctl(a,'lblPaySummaryNetValue')).toBeVisible();await expect(ctl(a,'conscrHomeRoot')).toBeHidden();await expect(ctl(a,'conStaffNavigation122')).toBeHidden();}
async function month(a:FrameLocator,value:string){await a.getByRole('button',{name:/^支給対象月\./}).click();await a.getByRole('option',{name:value,exact:true}).click();}

for(let run=1;run<=3;run++) test(`SMK-01-${run} fresh session, search, selection, sidebar, zero, clear, ledger`,async({page})=>{
 const a=await start(page);await expect(btn(a,'メンテナンス画面')).toBeDisabled();await staff(a);
 await expect(ctl(a,'lblListTitle111')).toContainText('7件');await expect.poll(()=>ids(a)).toEqual(expectedIds('03会計課'));
 await search(a,'');await expect.poll(()=>ids(a)).toEqual(expectedIds('03会計課'));
 await search(a,'同姓同名');await expect.poll(()=>ids(a)).toEqual(['009900000011']);
 await btn(a,'009900000011 試験 同姓同名 詳細を表示').click();
 await btn(a,'職員検索を閉じる').click();await expect(a.getByRole('searchbox')).toBeHidden();
 await btn(a,'職員検索を開く').click();await expect(a.getByRole('searchbox')).toHaveValue('同姓同名');
 await expect.poll(()=>ids(a)).toEqual(['009900000011']);
 await search(a,'009900000004');await expect.poll(()=>ids(a)).toEqual(['009900000004']);
 await btn(a,'009900000004 試験 退職 詳細を表示').click();
 await search(a,'999ZZZ');await expect(ctl(a,'lblListTitle111')).toContainText('0件');
 await expect.poll(()=>ids(a)).toEqual([]);await expect(ctl(a,'btnExport111').getByRole('button')).toBeDisabled();
 const certificate=ctl(a,'btnCertificate111').getByRole('button');
 if(await certificate.isVisible())await expect(certificate).toBeDisabled();else await expect(certificate).toBeHidden();
 await expect(ctl(a,'conLedgerModal111')).toBeHidden();
 await expect(ctl(a,'btnStaffPayroll122').getByRole('button')).toBeDisabled();
 await btn(a,'検索条件をクリア').click();await expect.poll(()=>ids(a)).toEqual(expectedIds('03会計課'));
 await expect(btn(a,'前へ')).toBeDisabled();await expect(btn(a,'次へ')).toBeDisabled();
 await btn(a,'009900000004 試験 退職 詳細を表示').click();await btn(a,'選択職員の認定簿を表示').click();
 await expect(ctl(a,'lblLedger_employee_number111')).toHaveText('009900000004');
 await ctl(a,'conLedgerSheet2111').scrollIntoViewIfNeeded();await expect(ctl(a,'conLedgerSheet2111')).toBeInViewport({ratio:0.2});
 await ctl(a,'btnLedgerClose111').getByRole('button').click();
 await snapshot(page,a,`smoke-${run}`);
});

test('SRCH-04..12 / DATA-01 / PAGE-02 filters, all authorized records, repeated search',async({page})=>{
 const a=await start(page);await staff(a);
 for(const q of ['  同姓同名  ','同姓同名']){await search(a,q);await expect.poll(()=>ids(a)).toEqual(['009900000011']);}
 for(const q of ['   ','']){await search(a,q);await expect.poll(()=>ids(a)).toEqual(expectedIds('03会計課'));}
 await search(a,'同姓同名');await a.getByRole('searchbox').fill('009900000004');
 await expect.poll(()=>ids(a)).toEqual(['009900000011']);await btn(a,'検索').click();await expect.poll(()=>ids(a)).toEqual(['009900000004']);
 await btn(a,'検索').dblclick();await expect.poll(()=>ids(a)).toEqual(['009900000004']);
 for(const dept of ['01秘書課','02総務課','03会計課']){await department(a,dept);await expect.poll(()=>ids(a)).toEqual(expectedIds(dept));}
 await ctl(a,'ddOrg111').click();await a.getByRole('option',{name:'02総務課',exact:true}).click();await btn(a,'検索').click();
 await expect.poll(()=>ids(a)).toEqual([]);await btn(a,'検索条件をクリア').click();
 for(const [status,values] of [['退職',['009900000004','009900000020']],['在籍',['009900000011','009900000014','009900000017']]] as const){
  await ctl(a,'ddStatus111').click();await a.getByRole('option',{name:status,exact:true}).click();await btn(a,'検索').click();await expect.poll(()=>ids(a)).toEqual(values);
 }
 await search(a,'同姓同名');await expect.poll(()=>ids(a)).toEqual(['009900000011']);
 await btn(a,'検索条件をクリア').click();
 await expect(a.getByRole('searchbox')).toHaveValue('');await expect.poll(()=>ids(a)).toEqual(expectedIds('03会計課'));
 await search(a,'管理部 会計課');await expect.poll(()=>ids(a)).toEqual(expectedIds('03会計課').filter((s:string)=>s!=='009900000004'));
 await snapshot(page,a,'search-filters');
});

test('CORE-DETAIL / SEL-03 / OUT-04 163 payroll fields and cross-department same-name isolation',async({page})=>{
 test.setTimeout(240000);const a=await start(page);
 for(const suffix of ['003','004','011','012']){
  const id='009900000'+suffix;await select(a,id);
  const rows=payrollFixture.filter((r:any)=>r.data.crb3c_staffnumber===id).map((r:any)=>r.data).sort((a:any,b:any)=>b.crb3c_payment_date.localeCompare(a.crb3c_payment_date));
  await expect(ctl(a,'lblSectionPayroll111')).toContainText(`${rows.length}件`);
  await ctl(a,'btnPayrollOpen111').getByRole('button').click();await expect(ctl(a,'lblPayrollModalTitle111')).toContainText(id);
  for(let i=0;i<fields.length;i++){
   const values=rows.map((r:any)=>r[fields[i].logical_name]==null?'':typeof r[fields[i].logical_name]==='number'?r[fields[i].logical_name].toLocaleString('en-US',{maximumFractionDigits:10}):String(r[fields[i].logical_name]));
   await expect(ctl(a,`lblCPayrollModal111${i}`)).toHaveText(values);
  }
  await ctl(a,'lblCPayrollModal111162').first().scrollIntoViewIfNeeded();await expect(ctl(a,'lblCPayrollModal111162').first()).toBeInViewport({ratio:0.5});
  await snapshot(page,a,`payroll-163-${suffix}`);
  await ctl(a,'btnPayExport111').getByRole('button').click();
  const tsv=await a.getByRole('textbox',{name:'コピー用テキスト。全選択してExcelへ貼り付けできます。',exact:true}).inputValue();
  const exported=tsv.split('\n').map(line=>line.split('\t'));
  expect(exported).toHaveLength(fields.length);
  const first=rows[0];
  for(let i=0;i<fields.length;i++){
   const value=first[fields[i].logical_name];
   const expected=value==null?'':typeof value==='number'?value.toLocaleString('en-US',{maximumFractionDigits:10}):String(value);
   expect(exported[i],`TSV field ${fields[i].logical_name}`).toEqual([fields[i].display_name,expected]);
  }
  console.log('PAYROLL_TSV_ALL_FIELDS '+JSON.stringify({id,fields:exported.length,exactValues:true}));
  await ctl(a,'btnReportClose111').getByRole('button').click();await expect(ctl(a,'conPayrollBackdrop111')).toBeHidden();
 }
 await select(a,'009900000025');await expect(ctl(a,'lblSectionPayroll111')).toContainText('0件');
 await ctl(a,'btnPayrollOpen111').getByRole('button').click();await expect(ctl(a,'btnPayExport111').getByRole('button')).toBeDisabled();
 await expect(ctl(a,'lblEmptyPayrollModal111')).toBeVisible();await expect(ctl(a,'galPayrollModal111')).not.toContainText('令和08年');
});

test('OUT-01/02/05 search TSV contains authorized employees and output pagination',async({page})=>{
 const a=await start(page);await staff(a);await btn(a,'検索結果をTSVで出力').click();
 const text=a.getByRole('textbox',{name:'コピー用テキスト。全選択してExcelへ貼り付けできます。',exact:true});
 const tsv=await text.inputValue();expect(tsv.trim().split('\n')).toHaveLength(8);
 for(const id of expectedIds('03会計課'))expect(tsv).toContain(id);expect(tsv).not.toContain('009900000012');
 await expect(btn(a,'前頁')).toBeDisabled();await btn(a,'次頁').click();await expect(ctl(a,'lblReportPage111')).toContainText('2 / 2');await expect(btn(a,'次頁')).toBeDisabled();
 await btn(a,'前頁').click();await expect(ctl(a,'lblReportPage111')).toContainText('1 / 2');
 await ctl(a,'btnReportClose111').getByRole('button').click();await search(a,'同姓同名');await btn(a,'検索結果をTSVで出力').click();
 expect((await text.inputValue()).trim().split('\n')).toHaveLength(2);await snapshot(page,a,'search-export');
});

test('DETAIL-01/02/03 histories, blank and zero fields, refresh',async({page})=>{
 const a=await start(page);await select(a,'009900000003');
 for(const [section,count] of [['Work',3],['Social',1],['Tax',1]])await expect(ctl(a,'lblSection'+section+'111')).toContainText(`${count}件`);
 await expect(ctl(a,'galWork111')).toContainText('15,000');await expect(ctl(a,'galWork111')).toContainText('現行');await expect(ctl(a,'galWork111')).toContainText('過去');await expect(ctl(a,'galWork111')).toContainText('予定');
 await ctl(a,'lblSectionPayroll111').scrollIntoViewIfNeeded();await expect(ctl(a,'conPerson111')).toBeInViewport({ratio:1});
 await btn(a,'Dataverseの最新データを読み込む').click();await expect(ctl(a,'lblListTitle111')).toContainText('8件');
 await select(a,'009900000012');await expect(ctl(a,'lblSectionCommute111')).toContainText('0件');await expect(ctl(a,'btnCertificate111').getByRole('button')).toBeDisabled();
 await snapshot(page,a,'history-isolation');
});

test('SCR-001..006 navigation, dummy registration, recalculation, zero and missing month',async({page})=>{
 const a=await start(page);await payroll(a);await expect(btn(a,'再計算')).toBeDisabled();await expect(ctl(a,'lblPaySummaryNetValue')).toHaveText('—');
 await select(a,'009900000011');await payroll(a);await expect(ctl(a,'lblPaySummaryNetValue')).toHaveText('151,800 円');
 await ctl(a,'btnPayEarnings').getByRole('button').click();await expect(ctl(a,'conPayEarnings')).toBeHidden();
 await ctl(a,'btnPayDeductions').getByRole('button').click();await expect(ctl(a,'conPayDeductions')).toBeHidden();
 await expect(ctl(a,'lblPaySummaryNetValue')).toHaveText('151,800 円');
 await ctl(a,'btnPayEarnings').getByRole('button').click();await ctl(a,'btnPayDeductions').getByRole('button').click();
 await month(a,'2026/10');await expect(ctl(a,'lblPayState')).toContainText('未登録');await expect(ctl(a,'lblPaySummaryNetValue')).toHaveText('—');
 await month(a,'2026/11');await btn(a,'再計算').click();await expect(ctl(a,'lblPaySummaryNetValue')).toHaveText('0 円');
 await month(a,'2026/09');await expect(ctl(a,'lblPaySummaryNetValue')).toHaveText('—');await btn(a,'再計算').click();
 await home(a);await btn(a,'勤務時間報告画面').click();await a.getByRole('button',{name:/^欠勤時間（分）\./}).click();await a.getByRole('option',{name:'1',exact:true}).click();
 await btn(a,'月分を登録（仮）').click();await expect(ctl(a,'lblAttendanceSummary')).toContainText('0.016667');
 await home(a);await payroll(a);await expect(ctl(a,'lblPaySummaryNetValue')).toHaveText('153,029 円');await expect(ctl(a,'lblPayAbsence')).toContainText('約');
 await home(a);await btn(a,'期末勤勉支給率登録画面').click();await a.getByRole('textbox',{name:'期末手当支給率（パーセント）',exact:true}).fill('105');await a.getByRole('textbox',{name:'勤勉手当支給率（パーセント）',exact:true}).fill('95');await btn(a,'登録（仮）').click();
 await expect(ctl(a,'lblBonusSaved')).toContainText('期末 105% ／ 勤勉 95%');
 await home(a);await expect(btn(a,'メンテナンス画面')).toBeDisabled();await ctl(a,'btnHomeRole').getByRole('button').click();await btn(a,'メンテナンス画面').click();
 await btn(a,'仮入力を初期化').click();await home(a);await payroll(a);await expect(ctl(a,'lblPaySummaryNetValue')).toHaveText('—');
 await snapshot(page,a,'screens-flow');
});

test('PERF-02 twenty search/selection/sidebar/zero/clear cycles retain correct state',async({page})=>{
 test.setTimeout(240000);const a=await start(page);await staff(a);const timings=[];
 for(let i=0;i<20;i++){
  const t=Date.now();await search(a,'同姓同名');await expect.poll(()=>ids(a)).toEqual(['009900000011']);await btn(a,'009900000011 試験 同姓同名 詳細を表示').click();
  await btn(a,'職員検索を閉じる').click();await btn(a,'職員検索を開く').click();await search(a,'999ZZZ');await expect.poll(()=>ids(a)).toEqual([]);
  await btn(a,'検索条件をクリア').click();await expect.poll(()=>ids(a)).toEqual(expectedIds('03会計課'));timings.push(Date.now()-t);
 }
 writeFileSync(path.join(out,'twenty-cycles.json'),JSON.stringify({cycles:timings.length,milliseconds:timings},null,2));
});

test('BUG-SELECTION-001 zero search clears payroll across home navigation and selection changes',async({page})=>{
 const a=await start(page);await select(a,'009900000011');await payroll(a);
 await expect(ctl(a,'lblPaySummaryNetValue')).toHaveText('151,800 円');
 await btn(a,'職員マスタ検索').click();await search(a,'999ZZZ');await expect(ctl(a,'lblListTitle111')).toContainText('0件');
 await home(a);await payroll(a);await expect(ctl(a,'lblPaySummaryNetValue')).toHaveText('—');
 await expect(ctl(a,'lblPayState')).toContainText('対象職員を選択');await expect(btn(a,'再計算')).toBeDisabled();
 await select(a,'009900000004');await home(a);await payroll(a);
 await expect(ctl(a,'lblPayrollStaff')).toContainText('009900000004');
 await snapshot(page,a,'selection-reset');
});

test('ACC-01/02 keyboard search and row selection',async({page})=>{
 const a=await start(page);await staff(a);const input=a.getByRole('searchbox');await input.focus();await page.keyboard.type('同姓同名');
 await btn(a,'検索').focus();await page.keyboard.press('Enter');await expect.poll(()=>ids(a)).toEqual(['009900000011']);
 await btn(a,'009900000011 試験 同姓同名 詳細を表示').focus();await page.keyboard.press('Enter');await expect(btn(a,'支給明細画面')).toBeEnabled();
 await btn(a,'職員検索を閉じる').focus();await page.keyboard.press('Enter');await expect(input).toBeHidden();await page.keyboard.press('Tab');
 const focused=await a.locator(':focus').getAttribute('aria-label');expect(focused).not.toBe('氏名・職員番号・項目を検索');
 await snapshot(page,a,'keyboard');
});

for(const [width,height] of [[1366,768],[1920,1080]])for(const large of [false,true])for(const closed of [false,true])
test(`VIS-01 staff ${width}x${height} ${large?'large':'standard'} ${closed?'closed':'open'}`,async({page})=>{
 const a=await start(page,width,height);await select(a,'009900000003');
 if(large)await btn(a,'文字サイズを大きくする').click();if(closed)await btn(a,'職員検索を閉じる').click();
 await expect.poll(async()=>(await box(ctl(a,'conSearchSidebar111'))).width).toBeCloseTo(closed?48:360,0);
 const sidebarBaseline=await box(ctl(a,'conSearchSidebar111'));
 const personBaseline=await box(ctl(a,'conPerson111'));
 for(let cycle=0;cycle<5;cycle++){
  await btn(a,closed?'職員検索を開く':'職員検索を閉じる').click();
  await expect.poll(async()=>(await box(ctl(a,'conSearchSidebar111'))).width).toBeCloseTo(closed?360:48,0);
  await btn(a,closed?'職員検索を閉じる':'職員検索を開く').click();
  await expect.poll(async()=>Math.abs((await box(ctl(a,'conSearchSidebar111'))).width-sidebarBaseline.width)).toBeLessThan(1);
  await expect.poll(async()=>Math.abs((await box(ctl(a,'conPerson111'))).width-personBaseline.width)).toBeLessThan(1);
  await expect(ctl(a,'lblPersonSub111')).toContainText('009900000003');
 }
 await noOverlap([ctl(a,'conStaffNavigation122'),ctl(a,'conHeader111')]);
 const basic=await box(ctl(a,'conBasic111'));const cells=[];
 for(let i=0;i<9;i++){
  const k=await box(ctl(a,`lblBasicKey${i}111`)),v=await box(ctl(a,`lblBasicVal${i}111`));
  expect(Math.abs(k.x-v.x)).toBeLessThan(1.1);expect(v.y).toBeGreaterThanOrEqual(k.y+k.height-1);
  expect(v.x+v.width).toBeLessThanOrEqual(basic.x+basic.width+1);expect(v.y+v.height).toBeLessThanOrEqual(basic.y+basic.height+1);cells.push({k,v});
 }
 await snapshot(page,a,`staff-${width}-${large}-${closed}`);
 await ctl(a,'lblSectionPayroll111').scrollIntoViewIfNeeded();await expect(ctl(a,'conPerson111')).toBeInViewport({ratio:1});
 await ctl(a,'btnPayrollOpen111').getByRole('button').click();await ctl(a,'lblCPayrollModal111162').first().scrollIntoViewIfNeeded();await expect(ctl(a,'lblCPayrollModal111162').first()).toBeInViewport({ratio:0.5});
 await expect(ctl(a,'btnPayClose111')).toBeInViewport({ratio:1});await snapshot(page,a,`staff-modal-${width}-${large}-${closed}`);
 writeFileSync(path.join(out,`staff-measure-${width}-${large}-${closed}.json`),JSON.stringify({width,height,large,closed,basic,cells},null,2));
});

const screens=[['ホーム','scrHome'],['勤務時間報告画面','scrAttendance'],['期末勤勉支給率登録画面','scrBonus'],['支給明細画面','scrPayroll'],['メンテナンス画面','scrMaintenance']];
for(const [width,height] of [[900,600],[1100,800],[1366,768],[1920,1080]])
test(`VIS-SCREENS all five new screens ${width}x${height}`,async({page})=>{
 test.setTimeout(180000);const a=await start(page,width,height);await select(a,'009900000011');await payroll(a);await home(a);await ctl(a,'btnHomeRole').getByRole('button').click();
 const measurements=[];
 for(const [title,name] of screens){
  if(name!=='scrHome')await btn(a,title).click();
  const root=await box(ctl(a,'con'+name+'Root'));const head=await box(ctl(a,'con'+name+'Header'));const homeButton=await box(ctl(a,'btn'+name+'Home'));
  expect(homeButton.x+homeButton.width).toBeLessThanOrEqual(root.x+root.width+1);expect(homeButton.y+homeButton.height).toBeLessThanOrEqual(head.y+head.height+1);
  if(name==='scrHome'){
   const b=await noOverlap(['btnHomeStaff','btnHomeAttendance','btnHomeBonus','btnHomePayroll','btnHomeMaintenance'].map(n=>ctl(a,n)));
   expect(b[4].y+b[4].height).toBeLessThanOrEqual(root.y+root.height+1);
  }
  if(name==='scrPayroll'){
   await noOverlap(['conPayrollTargets','conPaySummary','conPayActions'].map(n=>ctl(a,n)));
   await noOverlap(['btnPayEarnings','btnPayDeductions','btnPayRecalculate'].map(n=>ctl(a,n)));
   const summary=await box(ctl(a,'conPaySummary'));await ctl(a,'lblPayDeductionAmount7').scrollIntoViewIfNeeded();await expect(ctl(a,'lblPayDeductionAmount7')).toBeInViewport({ratio:0.5});
   expect(Math.abs((await box(ctl(a,'conPaySummary'))).y-summary.y)).toBeLessThan(1.1);
   await expect(ctl(a,'lblPaySummaryNetValue')).toHaveText('151,800 円');
  }
  if(name==='scrAttendance'){await ctl(a,'btnAttendanceRegister').scrollIntoViewIfNeeded();await expect(ctl(a,'btnAttendanceRegister')).toBeInViewport({ratio:1});}
  if(name==='scrBonus'){await ctl(a,'btnBonusSave').scrollIntoViewIfNeeded();await expect(ctl(a,'btnBonusSave')).toBeInViewport({ratio:1});}
  await snapshot(page,a,`${name}-${width}`);measurements.push({name,root,head,homeButton});if(name!=='scrHome')await home(a);
 }
 writeFileSync(path.join(out,`screens-measure-${width}.json`),JSON.stringify({viewport:{width,height},screens:measurements},null,2));
});
