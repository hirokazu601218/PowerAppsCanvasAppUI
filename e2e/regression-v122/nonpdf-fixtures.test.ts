import {test,expect,type Page,type FrameLocator} from '@playwright/test';
import {writeFileSync} from 'node:fs';
test.describe.configure({retries:0});
test.use({video:'off',ignoreHTTPSErrors:false});
const ctl=(a:FrameLocator,n:string)=>a.locator(`[data-control-name="${n}"]`);
const btn=(a:FrameLocator,n:string)=>a.getByRole('button',{name:n,exact:true});
async function start(page:Page){await page.setViewportSize({width:1366,height:768});await page.goto(process.env.CANVAS_APP_URL!,{waitUntil:'domcontentloaded'});const a=page.frameLocator('iframe[name="fullscreen-app-host"]');await expect(ctl(a,'lblHomePrototype')).toContainText('UI検討用 v1.26',{timeout:60000});return a;}
async function fixture(a:FrameLocator,value:string){await btn(a,'一般 → 管理者に切替').click();await btn(a,'メンテナンス画面').click();await ctl(a,'ddUiFixture124').click();await a.getByRole('option',{name:value,exact:true}).click();await ctl(a,'btnscrMaintenanceHome').getByRole('button').click();await ctl(a,'btnHomeStaff').getByRole('button').click();}
const rows=(a:FrameLocator)=>a.getByRole('button',{name:/^008800000\d{3} .* 詳細を表示$/});
for(const count of [0,1,20,21,40])test(`BOUNDARY-${count} initial count, pages and complete TSV`,async({page})=>{
 const a=await start(page);await fixture(a,`${count}件`);await expect(ctl(a,'lblListTitle111')).toContainText(`${count}件`);await expect(rows(a)).toHaveCount(Math.min(count,20));await expect(btn(a,'前へ')).toBeDisabled();
 if(count===0){await expect(btn(a,'次へ')).toBeDisabled();await expect(ctl(a,'btnExport111').getByRole('button')).toBeDisabled();await expect(ctl(a,'conPerson111')).toBeHidden();return;}
 await expect(ctl(a,'lblPersonSub111')).toContainText('008800000001');
 if(count>20){await btn(a,'次へ').click();await expect(rows(a)).toHaveCount(count-20);await expect(rows(a).first()).toContainText('008800000021');await expect(btn(a,'次へ')).toBeDisabled();await rows(a).last().click();await expect(ctl(a,'lblPersonSub111')).toContainText('008800000'+String(count).padStart(3,'0'));await btn(a,'前へ').click();await expect(rows(a)).toHaveCount(20);await expect(ctl(a,'lblPersonSub111')).toContainText('008800000'+String(count).padStart(3,'0'));}
 else await expect(btn(a,'次へ')).toBeDisabled();
 await ctl(a,'btnExport111').getByRole('button').click();const tsv=await a.getByRole('textbox',{name:'コピー用テキスト。全選択してExcelへ貼り付けできます。',exact:true}).inputValue();const lines=tsv.trim().split('\n');expect(lines).toHaveLength(count+1);expect(lines.every(l=>l.split('\t').length===26)).toBe(true);expect(lines.slice(1).map(l=>l.split('\t')[0])).toEqual(Array.from({length:count},(_,i)=>'008800000'+String(i+1).padStart(3,'0')));await ctl(a,'btnReportClose111').getByRole('button').click();await expect(ctl(a,'btnExport111').getByRole('button')).toBeFocused();
 console.log('BOUNDARY_PASS '+JSON.stringify({count,columns:26,completeRows:count,focusRestored:true}));
});
test('BOUNDARY-SEARCH page reset and selected staff invalidation',async({page})=>{const a=await start(page);await fixture(a,'40件');await btn(a,'次へ').click();await rows(a).last().click();await a.getByRole('searchbox').fill('職員01');await btn(a,'検索').click();await expect(rows(a)).toHaveCount(1);await expect(btn(a,'前へ')).toBeDisabled();await expect(ctl(a,'lblPersonSub111')).toContainText('008800000001');await btn(a,'検索条件をクリア').click();await expect(rows(a)).toHaveCount(20);await expect(btn(a,'前へ')).toBeDisabled();});
test('BOUNDARY-LONG negative zero blank display and untruncated TSV',async({page})=>{const a=await start(page);await fixture(a,'長文・負数');await expect(rows(a)).toHaveCount(3);await expect(ctl(a,'lblName111')).toContainText('非常に長い氏名');for(const [index,daily] of [[0,'-12,345'],[1,'0'],[2,'']] as const){await rows(a).nth(index).click();await expect(ctl(a,'lblCWork1112')).toHaveText(daily);}await rows(a).first().click();await ctl(a,'btnExport111').getByRole('button').click();const tsv=await a.getByRole('textbox',{name:'コピー用テキスト。全選択してExcelへ貼り付けできます。',exact:true}).inputValue();const r=tsv.trim().split('\n').slice(1).map(l=>l.split('\t'));expect(r[0][1]).toBe('表示試験 非常に長い氏名の折返しと全文確認のための職員');expect(r.map(x=>x[10])).toEqual(['-12345','0','']);writeFileSync(`${process.env.OUTPUT_DIRECTORY}/long-fixture.json`,JSON.stringify({name:r[0][1],daily:r.map(x=>x[10])}));});

test('BOUNDARY-PRESERVE page two selection and pending input survive sidebar then clear',async({page})=>{
 const a=await start(page);await fixture(a,'40件');await btn(a,'次へ').click();await rows(a).last().click();
 await a.getByRole('searchbox').fill('未確定入力');
 await btn(a,'職員検索を閉じる').click();await expect(a.getByRole('searchbox')).toBeHidden();
 await expect(ctl(a,'lblPersonSub111')).toContainText('008800000040');
 await btn(a,'職員検索を開く').click();await expect(a.getByRole('searchbox')).toHaveValue('未確定入力');
 await expect(ctl(a,'lblPage111')).toHaveText('2 / 2');await expect(rows(a)).toHaveCount(20);
 await expect(rows(a).last()).toContainText('008800000040');await expect(ctl(a,'lblListTitle111')).toContainText('40件');
 await expect(ctl(a,'galCommute111').getByRole('listitem')).toHaveCount(0);
 await btn(a,'検索条件をクリア').click();await expect(a.getByRole('searchbox')).toHaveValue('');
 await expect(ctl(a,'lblPage111')).toHaveText('1 / 2');await expect(ctl(a,'lblPersonSub111')).toContainText('008800000001');
 await expect(ctl(a,'ddOrg111')).toContainText('すべて');await expect(ctl(a,'ddStatus111')).toContainText('すべて');
 console.log('PAGE_CLEAR_SIDEBAR_PRESERVE_PASS');
});

test('BOUNDARY-LONG-LAYOUT eight size text sidebar conditions preserve full tooltip',async({page})=>{
 const a=await start(page);await fixture(a,'長文・負数');const metrics=[];
 for(const [width,height] of [[1366,768],[1920,1080]]){
  await page.setViewportSize({width,height});
  for(const large of [false,true]){
   if(large)await btn(a,'文字サイズを大きくする').click();
   for(const closed of [false,true]){
    if(closed)await btn(a,'職員検索を閉じる').click();
    for(const [name,text] of [['lblBasicVal1111','表示試験 非常に長い氏名の折返しと全文確認のための職員'],['lblBasicVal2111','表示試験専用の非常に長い組織所属名称・管理部門・担当部門・補足名称']]){
     const label=ctl(a,name);await label.scrollIntoViewIfNeeded();await expect(label).toHaveText(text);
     const m=await label.evaluate(el=>{const content=el.querySelector('.appmagic-label-text')||el;const style=getComputedStyle(content);const titles=[el,...Array.from(el.querySelectorAll('[title]'))].map(e=>e.getAttribute('title')).filter(Boolean);return {text:content.textContent,titles,font:style.fontSize,whiteSpace:style.whiteSpace,height:el.getBoundingClientRect().height};});
     expect(m.titles).toContain(text);expect(m.height).toBeGreaterThan(18);metrics.push({width,height,large,closed,name,...m});
    }
    if(closed)await btn(a,'職員検索を開く').click();
   }
   if(large)await btn(a,'文字サイズを標準に戻す').click();
  }
 }
 writeFileSync(`${process.env.OUTPUT_DIRECTORY}/long-eight-conditions.json`,JSON.stringify(metrics,null,2));console.log('LONG_EIGHT_CONDITIONS_PASS');
});
