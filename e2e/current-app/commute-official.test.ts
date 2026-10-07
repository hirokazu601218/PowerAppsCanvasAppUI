import { expect, test, type Page } from '@playwright/test';

async function reports(page: Page) {
  const configured=process.env.CANVAS_APP_URL;
  if(!configured) throw Error('CANVAS_APP_URL is required');
  const u=new URL(configured);
  if(u.hostname!=='apps.powerapps.com'||u.pathname!=='/play/e/68e00049-b7e5-eda6-9888-9a3cc493c5be/a/204a48dc-7f23-43dd-b934-4654a3cfa306') throw Error('Unexpected app');
  await page.goto(configured,{waitUntil:'domcontentloaded'});
  const app=page.frameLocator('iframe[name="fullscreen-app-host"]');
  await expect(app.getByRole('button',{name:'職員マスタ検索',exact:true})).toBeVisible({timeout:60000});
  await app.getByRole('button',{name:'職員マスタ検索',exact:true}).click();
  await expect(app.locator('[data-control-name="lblPersonSub111"]')).toContainText('009900000004',{timeout:30000});
  await app.getByRole('button',{name:'通勤',exact:true}).click();
  const normalButton=app.getByRole('button',{name:'認定簿表示',exact:true});
  await expect(normalButton).toHaveCount(1);
  await expect(app.getByRole('button',{name:'新様式（受入テスト）',exact:true})).toHaveCount(0);
  await expect(normalButton).toBeEnabled({timeout:30000});
  const freshPromise=page.waitForEvent('popup');await normalButton.click();const fresh=await freshPromise;
  await expect(fresh.locator('#print')).toBeEnabled({timeout:30000});
  return {fresh,app};
}

test('UT-COM-FORM-001 新様式の71表示欄と公式2ページの枠に収まる',async({page})=>{
  const {fresh}=await reports(page);
  await expect(fresh.locator('.official-page')).toHaveCount(2);
  await expect(fresh.locator('svg.official-form')).toHaveCount(2);
  await expect(fresh.locator('[data-field]')).toHaveCount(71);
  expect(await fresh.locator('[data-field],.official-page').evaluateAll(es=>es.filter(e=>e.scrollWidth>e.clientWidth+1||e.scrollHeight>e.clientHeight+1).length)).toBe(0);
  await expect(fresh.locator('[data-field="staff"]')).toHaveText('009900000004');
  await expect(fresh.locator('[data-field="total"]')).toHaveText('16,800');
});

test('IT-COM-CUTOVER-001 通常入口だけが新様式を別タブで開き選択認定を表示する',async({page})=>{
  const {fresh,app}=await reports(page);const url=new URL(fresh.url());
  expect(url.pathname).toBe('/WebResources/new_reports/commute-ledger-official-v102.html');
  expect(url.searchParams.getAll('id')).toHaveLength(1);
  expect(url.searchParams.get('id')).toBe('d3f72e11-eaad-58c0-a9df-a13a0df938cd');
  await expect(app.locator('[data-control-name="galDetailFields111"]')).toContainText('TK-910003');
  await expect(fresh.locator('#status')).toContainText('TK-910003');
  await expect(fresh.locator('[data-field="staff"]')).toHaveText('009900000004');
  await expect(fresh.locator('[data-field="name"]')).toHaveText('試験　退職');
  await expect(fresh.locator('[data-field="total"]')).toHaveText('16,800');
});

test('UT-COM-OVERFLOW-001 新様式の枠超過を印刷前に検知し表示を消す',async({page})=>{
  const {fresh}=await reports(page);
  // DOM-only test perturbation; no Dataverse write. Exercises the unchanged print handler.
  await fresh.locator('[data-field="r1_remarks"]').evaluate(e=>{e.textContent='長文'.repeat(500);});
  await fresh.locator('#print').click();
  await expect(fresh.locator('#print')).toBeDisabled();await expect(fresh.locator('#report')).toBeHidden();
  await expect(fresh.locator('#status')).toContainText('文字が枠内に収まらない');
});

test('IT-COM-PRINT-001 通常入口の新様式をA4横2ページPDFへ出力する',async({page})=>{
  const {fresh}=await reports(page);
  for(const p of [fresh]){
    const pdf=await p.pdf({preferCSSPageSize:true,printBackground:true});
    await test.info().attach('commute-cutover.pdf',{body:pdf,contentType:'application/pdf'});
    const boxes=[...pdf.toString('latin1').matchAll(/\/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*\]/g)];
    expect(boxes.length).toBeGreaterThan(0);
    for(const box of boxes){expect(Number(box[1])).toBeCloseTo(842,0);expect(Number(box[2])).toBeCloseTo(595,0);}
    expect(pdf.subarray(0,5).toString()).toBe('%PDF-');
    expect((pdf.toString('latin1').match(/\/Type\s*\/Page\b/g)||[]).length).toBe(2);
    await expect(p.locator('#print')).toBeEnabled();
  }
});
