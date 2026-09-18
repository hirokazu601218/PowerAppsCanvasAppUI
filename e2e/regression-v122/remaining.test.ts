import {test,expect,type Page,type FrameLocator} from '@playwright/test';
import {readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';

test.describe.configure({retries:0});
test.use({video:'off',ignoreHTTPSErrors:false});
const fixture=JSON.parse(readFileSync(path.join(process.env.FIXTURE_ROOT!,'staff-basic-25.json'),'utf8'));
const history=JSON.parse(readFileSync(path.join(process.env.FIXTURE_ROOT!,'staff-history-synthetic.json'),'utf8'));
const out=process.env.OUTPUT_DIRECTORY!;
const ctl=(a:FrameLocator,n:string)=>a.locator(`[data-control-name="${n}"]`);
const button=(a:FrameLocator,n:string)=>a.getByRole('button',{name:n,exact:true});
async function start(p:Page){
 await p.setViewportSize({width:1366,height:1000});
 await p.goto(process.env.CANVAS_APP_URL!,{waitUntil:'domcontentloaded',timeout:60000});
 const a=p.frameLocator('iframe[name="fullscreen-app-host"]');
 await expect(ctl(a,'lblHomePrototype')).toContainText('UI検討用 v1.23',{timeout:60000});
 return a;
}
async function search(a:FrameLocator,q:string){await a.getByRole('searchbox',{name:'氏名・職員番号・項目を検索',exact:true}).fill(q);await button(a,'検索').click();}
async function ids(a:FrameLocator){return (await a.getByRole('button',{name:/^009900000\d{3} .* 詳細を表示$/}).allTextContents()).map(x=>x.trim().slice(0,12));}
async function select(a:FrameLocator,id:string){
 if(!await ctl(a,'btnHomeStaff').isVisible()){
  await ctl(a,'btnStaffHome122').getByRole('button').click();
  await expect(ctl(a,'btnHomeStaff')).toBeVisible();await expect(ctl(a,'conStaffNavigation122')).toBeHidden();
 }
 const row=fixture.find((s:any)=>s.staffnumber===id);
 await ctl(a,'ddHomeDepartment').click();await a.getByRole('option',{name:row.orgshort,exact:true}).click();
 await ctl(a,'btnHomeStaff').getByRole('button').click();await expect(ctl(a,'conscrHomeRoot')).toBeHidden();
 await search(a,id);await a.getByRole('button',{name:new RegExp('^'+id+' .* 詳細を表示$')}).click();
 await expect(ctl(a,'lblPersonSub111')).toContainText(id);
}
const date=(x:any)=>!x||x==='2099-03-31'?'':String(x).replaceAll('-','/');
const money=(x:any)=>Number(x).toLocaleString('en-US',{maximumFractionDigits:0});
const columns:any={
 Work:[['適用開始日','Start','date'],['適用終了日','End','date'],['日額単価','Daily','money'],['所定勤務時間','Scheduled'],['勤務時間','Hours'],['超勤基礎単価（参考）','Overtime','money'],['異動区分','Change'],['発令事由区分','Reason'],['勤務時間終了','Finish'],['1日あたり勤務時間','DailyHours','decimal']],
 Social:[['職員雇用区分','Category'],['生年月日','Birth'],['4/1時点年齢','AgeApril'],['3/1時点年齢','AgeMarch'],['介護徴収該当','Care'],['厚生年金免除該当','PensionExempt'],['後期高齢者徴収該当','Elderly'],['厚生、級','Grade'],['厚生月額','Monthly','money']],
 Tax:[['適用開始日','Start','date'],['適用終了日','End','date'],['税表区分','TaxClass'],['雇用保険加入区分','Employment'],['共済貯金月額','Saving','money'],['共済貸付月額','Loan','money'],['扶養控除人数','Dependents'],['備考','Note']]
};

test('REMAIN-DETAIL independent nine basic values and all Work Social Tax cells',async({page})=>{
 test.setTimeout(240000);const a=await start(page);const observed=[];
 for(const suffix of ['003','004','011','012','025']){
  const id='009900000'+suffix;await select(a,id);const s=fixture.find((x:any)=>x.staffnumber===id);
  const today=new Date().toLocaleDateString('en-CA',{timeZone:'Asia/Tokyo'});
  const state=!s.hiredate||s.hiredate>today?'採用前':s.leavedate&&s.leavedate<today?'退職':'在籍';
  const expected=[id,s.fullname.normalize('NFKC'),s.orgfull||'',s.orgshort,s.birthdate?.replaceAll('-','/')||'',s.sex||'',s.hiredate?.replaceAll('-','/')||'',s.leavedate?.replaceAll('-','/')||'',state];
  const basic=[];for(let i=0;i<9;i++){await expect(ctl(a,`lblBasicVal${i}111`)).toHaveText(expected[i]);basic.push(await ctl(a,`lblBasicVal${i}111`).innerText());}
  const groups:any={};
  for(const group of ['Work','Social','Tax']){
   const rows=history[group].filter((r:any)=>r.StaffId===id);
   await expect(ctl(a,`lblSection${group}111`)).toContainText(`${rows.length}件`);groups[group]=[];
   for(let i=0;i<columns[group].length;i++){
    const [label,key,format]=columns[group][i];const header=ctl(a,`lblH${group}111${i}`);const cells=ctl(a,`lblC${group}111${i}`);
    await expect(header).toHaveText(label);
    const values=rows.map((r:any)=>format==='date'?date(r[key]):format==='money'?money(r[key]):format==='decimal'?Number(r[key]).toFixed(2):String(r[key]??''));
    await expect(cells).toHaveText(values);
    if(rows.length){
     // Fixture order is explicitly checked before selecting the first row for geometry.
     await expect(cells).toHaveCount(rows.length);await cells.nth(0).scrollIntoViewIfNeeded();
     await expect(cells.nth(0)).toBeInViewport({ratio:0.25});
     const h=await header.boundingBox(),v=await cells.nth(0).boundingBox();expect(h).not.toBeNull();expect(v).not.toBeNull();
     expect(Math.abs(h!.x-v!.x)).toBeLessThanOrEqual(1);expect(Math.abs(h!.width-v!.width)).toBeLessThanOrEqual(1);
    }
    groups[group].push({label,key,values:await cells.allTextContents()});
   }
  }
  observed.push({id,basic,groups});
 }
 writeFileSync(path.join(out,'remaining-detail.json'),JSON.stringify(observed,null,2));
});

test('REMAIN-SEARCH three simultaneous filters plus number and commute-method fields',async({page})=>{
 const a=await start(page);await ctl(a,'btnHomeStaff').getByRole('button').click();
 await ctl(a,'ddOrg111').click();await a.getByRole('option',{name:'03会計課',exact:true}).click();
 await ctl(a,'ddStatus111').click();await a.getByRole('option',{name:'在籍',exact:true}).click();
 await search(a,'同姓同名');await expect.poll(()=>ids(a)).toEqual(['009900000011']);
 await ctl(a,'ddOrg111').click();await a.getByRole('option',{name:'02総務課',exact:true}).click();
 await button(a,'検索').click();await expect.poll(()=>ids(a)).toEqual([]);
 await button(a,'検索条件をクリア').click();
 for(const keyword of ['11100','支給なし']){
  await search(a,keyword);
  const expected=fixture.filter((s:any)=>s.orgshort==='03会計課'&&(keyword==='11100'?s.dailyrate===11100:s.commutemethod==='支給なし')).map((s:any)=>s.staffnumber);
  expect(expected.length).toBeGreaterThan(0);await expect.poll(()=>ids(a)).toEqual(expected);
 }
});

test('REMAIN-SIDEBAR typography roundtrip, dimensions, selection and zero cleanup',async({page})=>{
 const a=await start(page);await select(a,'009900000011');const input=a.getByRole('searchbox');
 await search(a,'同姓同名');await button(a,'009900000011 試験 同姓同名 詳細を表示').click();
 const dimensions=[];const readings=[];
 for(const large of [false,true,false]){
  if(large)await button(a,'文字サイズを大きくする').click();else if(readings.length)await button(a,'文字サイズを標準に戻す').click();
  const font=await ctl(a,'lblBasicVal0111').evaluate(el=>[el,...el.querySelectorAll('*')].filter(n=>[...n.childNodes].some(c=>c.nodeType===3&&c.textContent?.trim())).map(n=>parseFloat(getComputedStyle(n).fontSize)));
  expect(font).toContain(large?16:14);readings.push({large,font});
  const open=await ctl(a,'conSearchSidebar111').boundingBox();const before=await ctl(a,'conPerson111').boundingBox();expect(open).not.toBeNull();const scale=open!.width/360;
  await button(a,'職員検索を閉じる').click();await expect(input).toBeHidden();
  const closed=await ctl(a,'conSearchSidebar111').boundingBox();const after=await ctl(a,'conPerson111').boundingBox();
  expect(Math.abs(closed!.width-48*scale)).toBeLessThan(1);expect(Math.abs(after!.width-before!.width-328*scale)).toBeLessThan(1);
  await expect(ctl(a,'lblPersonSub111')).toContainText('009900000011');
  await button(a,'職員検索を開く').click();await expect(input).toHaveValue('同姓同名');await expect.poll(()=>ids(a)).toEqual(['009900000011']);
  await expect(ctl(a,'lblPage111')).toHaveText('1 / 1');dimensions.push({large,scale,open,closed,before,after});
 }
 await button(a,'選択職員の認定簿を表示').click();await ctl(a,'btnLedgerClose111').getByRole('button').click();
 await search(a,'999ZZZ');await expect.poll(()=>ids(a)).toEqual([]);
 for(const n of ['conPerson111','conBasic111','conLedgerModal111','pdfLedger111','galWork111','galCommute111','galSocial111','galTax111','galPayroll111'])await expect(ctl(a,n)).toBeHidden();
 await expect(ctl(a,'btnExport111').getByRole('button')).toBeDisabled();
 await button(a,'検索条件をクリア').click();await expect.poll(()=>ids(a)).toEqual(fixture.filter((s:any)=>s.orgshort==='03会計課').map((s:any)=>s.staffnumber));
 await expect(ctl(a,'lblPersonSub111')).toContainText('009900000004');
 writeFileSync(path.join(out,'remaining-sidebar.json'),JSON.stringify({dimensions,readings},null,2));
});

test('REMAIN-MODAL background is blocked and close returns keyboard focus',async({page})=>{
 const a=await start(page);await select(a,'009900000011');const observations=[];
 for(const [open,close,modal] of [['btnCertificate111','btnLedgerClose111','conLedgerModal111'],['btnPayrollOpen111','btnPayClose111','conPayrollModal111'],['btnExport111','btnReportClose111','conReport111']]){
  await ctl(a,open).getByRole('button').click();
  const toggle=ctl(a,'btnSidebarToggle111').getByRole('button');
  if(await toggle.isVisible())await expect(toggle).toBeDisabled();
  else await expect(toggle).toBeHidden();
  await expect(ctl(a,close).getByRole('button')).toBeVisible();
  await ctl(a,close).getByRole('button').click();
  await expect(ctl(a,'lblPersonSub111')).toContainText('009900000011');
  const active=()=>a.locator('body').evaluate(el=>el.ownerDocument.activeElement?.closest('[data-control-name]')?.getAttribute('data-control-name')||'none');
  await expect.soft.poll(active,{timeout:5000,message:`${close} should restore focus to ${open}`}).toBe(open);
  const focused=await active();
  observations.push({open,close,focused});
 }
 writeFileSync(path.join(out,'remaining-modal-focus.json'),JSON.stringify(observations,null,2));
});
