import { test, expect } from '@playwright/test';
test('lightweight published UI: initial fetch, search, selection, tabs and responsive layout', async ({ page }) => {
 test.setTimeout(180000);
 const url=process.env.CANVAS_APP_URL;
 if(!url) throw new Error('CANVAS_APP_URL required');
 await page.setViewportSize({width:1366,height:768});
 await page.goto(url,{waitUntil:'domcontentloaded',timeout:60000});
 const app=page.frameLocator('iframe[name="fullscreen-app-host"]');
 await expect(app.getByText(/UI検討用 v1\.27/)).toBeVisible({timeout:90000});
 await app.getByRole('button',{name:'職員マスタ検索',exact:true}).click();
 await expect(app.getByText(/職員一覧\s*7件/)).toBeVisible({timeout:30000});
 await expect(app.getByText(/取得日時：\d{4}/)).toBeVisible();
 await app.getByRole('searchbox',{name:'氏名・職員番号・項目を検索'}).fill('不存在LT');
 await app.getByRole('button',{name:'検索',exact:true}).click();
 await expect(app.getByText(/職員一覧\s*0件/)).toBeVisible();
 await expect(app.getByText('職員を選択してください',{exact:true})).toBeVisible();
 await expect(app.getByRole('button',{name:'支給明細画面',exact:true})).toBeDisabled();
 await app.getByRole('button',{name:'検索条件をクリア',exact:true}).click();
 await expect(app.getByText(/職員一覧\s*7件/)).toBeVisible();
 await app.getByRole('button',{name:'試験 同姓同名 009900000011 詳細を表示',exact:true}).click();
 await expect(app.getByText(/職員番号：009900000011/)).toBeVisible();
 await app.getByRole('button',{name:'勤務条件',exact:true}).click();
 await expect(app.getByText('W-11-CURRENT',{exact:true}).first()).toBeVisible();
 const initialTime=await app.getByText(/取得日時：/).innerText();
 for(const [tab,value] of [['勤務条件','W-11-CURRENT'],['社会保険','S-11-2026'],['税固定控除','T-11-2026'],['通勤','TK-910004']]){
  await app.getByRole('button',{name:tab,exact:true}).click();
  await expect(app.getByText(value,{exact:true}).first()).toBeVisible();
  await expect(app.getByText(/取得日時：/)).toHaveText(initialTime);
 }
 await app.getByRole('button',{name:'給与',exact:true}).click();
 await expect(app.getByText('項目（163項目）',{exact:true})).toBeVisible();
 await expect(app.getByText('1 レコード',{exact:true})).toBeVisible();
 const expectedPayrollGuid=url.includes('204a48dc-7f23-43dd-b934-4654a3cfa306')?'4114e036-1b88-5e36-bd25-b32a64b2965e':'69142286-20d0-5ffe-b458-7d3810c6bc1f';
 const payrollHead=app.getByText('2026/04/23 / 5',{exact:false});
 await expect(payrollHead).toBeVisible();
 await expect(payrollHead).toHaveText('2026/04/23 / 5 '+expectedPayrollGuid,{useInnerText:true});
 await expect(app.getByRole('textbox',{name:'表示開始月',exact:true})).toHaveValue(new Date().getFullYear()+'/01');
 await app.getByRole('button',{name:'基本情報',exact:true}).click();
 for(const width of [900,1100,1366,1600,1920]){
  await page.setViewportSize({width,height:width===1920?1080:768});
  for(const big of [false,true]){
   const toggle=app.getByRole('button',{name:big?'文字サイズを大きくする':'文字サイズを標準に戻す',exact:true});
   if(await toggle.count())await toggle.click();
   for(const tab of ['基本情報','勤務条件','通勤','社会保険','税固定控除','給与'])await expect(app.getByRole('button',{name:tab,exact:true})).toBeVisible();
   await expect(app.getByText(/職員番号：009900000011/)).toBeVisible();
   await page.screenshot({path:`test-results/lightweight-${width}-${big?'large':'normal'}.png`});
  }
 }
 await app.getByRole('button',{name:'ホーム',exact:true}).click();
 await expect(app.getByText(/UI検討用 v1\.27/)).toBeVisible();
});
