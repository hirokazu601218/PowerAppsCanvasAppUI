import { expect, test, type Page } from '@playwright/test';
const ENV = '68e00049-b7e5-eda6-9888-9a3cc493c5be';
const APP = '204a48dc-7f23-43dd-b934-4654a3cfa306';
async function openImport(page: Page) {
  const configured = process.env.CANVAS_APP_URL;
  if (!configured) throw new Error('CANVAS_APP_URL is required');
  const url = new URL(configured);
  if (url.protocol !== 'https:' || url.hostname !== 'apps.powerapps.com' ||
      url.pathname !== `/play/e/${ENV}/a/${APP}`) throw new Error('Unexpected App ID');
  await page.setViewportSize({width:1366,height:768});
  await page.goto(url.toString(), {waitUntil:'domcontentloaded',timeout:60000});
  const screen=page.frameLocator('iframe[name="fullscreen-app-host"]');
  await screen.getByRole('button',{name:'データ一括取込み',exact:true}).click();
  await expect(screen.getByRole('button',{name:'取込を実行',exact:true})).toBeVisible();
  return screen;
}
test('UT-IMP-01 未選択を拒否',async({page})=>{
  const screen=await openImport(page);
  await screen.getByRole('button',{name:'取込を実行',exact:true}).click();
  await expect(screen.getByText('Excelファイルを1件選択してください。',{exact:true})).toBeVisible();
});
test('UT-IMP-05 xlsx以外を拒否',async({page})=>{
  const screen=await openImport(page);
  const chooser=page.waitForEvent('filechooser');
  await screen.getByRole('button',{name:'ファイルを添付',exact:true}).click();
  await (await chooser).setFiles({name:'PoC_invalid.txt',mimeType:'text/plain',buffer:Buffer.from('PoC invalid file')});
  await screen.getByRole('button',{name:'取込を実行',exact:true}).click();
  await expect(screen.getByText('.xlsxファイルを選択してください。',{exact:true})).toBeVisible();
});
test('IT-IMP-03 ホーム往復後も保存済み架空行を表示',async({page})=>{
  const screen=await openImport(page);
  await expect(screen.getByText('TEST-HIRE-001 | 架空 花子',{exact:false}).first()).toBeVisible();
  await expect(screen.getByText(/職員番号: 000000000101.*採用日: 2026-10-01/).first()).toBeVisible();
  await screen.getByRole('button',{name:'ホームへ戻る',exact:true}).click();
  await screen.getByRole('button',{name:'データ一括取込み',exact:true}).click();
  await expect(screen.getByText('TEST-HIRE-001 | 架空 花子',{exact:false}).first()).toBeVisible();
  await expect(screen.getByText(/職員番号: 000000000101.*採用日: 2026-10-01/).first()).toBeVisible();
});
// Normal import, blank staff number, corrupt input and row-write failure are measured
// separately in the manual run record. This suite never imports employee rows.
