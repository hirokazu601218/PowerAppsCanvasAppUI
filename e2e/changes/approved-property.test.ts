import { expect, test } from '@playwright/test';

test('AUT-META-001 approved header value is displayed', async ({ page }) => {
  const expected = process.env.EXPECTED_LABEL;
  if (!expected || !process.env.CANVAS_APP_URL) throw new Error('Missing acceptance target');
  await page.setViewportSize({ width: 1366, height: 768 });
  await page.goto(process.env.CANVAS_APP_URL, { waitUntil: 'domcontentloaded', timeout: 60_000 });
  const canvas = page.frameLocator('iframe[name="fullscreen-app-host"]');
  await expect(canvas.getByText('非常勤職員マスタ検索', { exact: true })).toBeVisible({ timeout: 60_000 });
  const header = canvas.getByText(expected, { exact: true });
  // A short assertion for a static label; browser retries are disabled by the runner.
  await expect(header, 'AUT-META-001: approved header value').toBeVisible({ timeout: 5_000 });
  await page.screenshot({ path: `${process.env.OUTPUT_DIRECTORY}/approved-label.png`, fullPage: true });
});

test('AUT-SIDEBAR-001 menu icon and sidebar state preservation', async ({ page }) => {
  await page.setViewportSize({width:1366,height:768});
  await page.goto(process.env.CANVAS_APP_URL!, {waitUntil:'domcontentloaded',timeout:60000});
  const c=page.frameLocator('iframe[name="fullscreen-app-host"]');
  const close=()=>c.getByRole('button',{name:'職員検索を閉じる',exact:true});
  const open=()=>c.getByRole('button',{name:'職員検索を開く',exact:true});
  // The recovery runner uses this same test against the last good v1.12.
  const legacy=process.env.EXPECTED_LABEL === 'v1.12 ／ B案・架空25名';
  await expect(close()).toBeVisible({timeout:60000});
  await expect(close()).toHaveText(legacy?'‹':'☰');
  const input=c.getByRole('searchbox',{name:'氏名・職員番号・項目を検索',exact:true});
  await input.fill('山田');
  await c.getByRole('button',{name:'検索',exact:true}).click();
  await expect(c.getByText(/職員一覧\s*2件/).first()).toBeVisible();
  await c.getByText('山田 花子',{exact:true}).first().click();
  for(let i=0;i<2;i++){
    await close().click();
    await expect(open()).toHaveText(legacy?'›':'☰');
    await expect(input).toBeHidden();
    await expect(c.getByText('00990000002',{exact:true}).first()).toBeVisible();
    await page.screenshot({path:process.env.OUTPUT_DIRECTORY+'/sidebar-closed-'+i+'.png'});
    await open().click();
    await expect(close()).toHaveText(legacy?'‹':'☰');
    await expect(input).toHaveValue('山田');
    await expect(c.getByText(/職員一覧\s*2件/).first()).toBeVisible();
    await expect(c.getByText('00990000002',{exact:true}).first()).toBeVisible();
  }
  await c.getByRole('button',{name:'検索条件をクリア',exact:true}).click();
  await c.getByRole('button',{name:'次へ',exact:true}).click();
  const pageText=c.getByText('2 / 2',{exact:true});
  await expect(pageText).toBeVisible();
  const before=await pageText.innerText();
  await close().click();
  await open().click();
  await expect(pageText).toHaveText(before);
  await page.screenshot({path:process.env.OUTPUT_DIRECTORY+'/sidebar-expanded.png'});
});
