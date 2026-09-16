import { test, expect } from '@playwright/test';
test.describe.configure({ retries: 0 });
test.use({ video: 'off', ignoreHTTPSErrors: false });
test('HYBRID-001 histories, zero values, payroll and same-name ledger isolation',async({page})=>{
  test.setTimeout(180000);
  await page.setViewportSize({width:1366,height:1000});
  await page.goto(process.env.CANVAS_APP_URL!,{waitUntil:'domcontentloaded'});
  const c=page.frameLocator('iframe[name="fullscreen-app-host"]');
  const control=(n:string)=>c.locator(`[data-control-name="${n}"]`);
  await expect(c.getByText('v1.17 ／ Dataverse・25名',{exact:true})).toBeVisible({timeout:60000});
  const select=async(id:string)=>{
    await c.getByRole('searchbox',{name:'氏名・職員番号・項目を検索',exact:true}).fill(id);
    await c.getByRole('button',{name:'検索',exact:true}).click();
    await c.getByRole('button',{name:new RegExp('^'+id+' .* 詳細を表示$')}).click();
  };
  await select('009900000003');
  for(const [section,count] of [['Work',3],['Commute',1],['Social',1],['Tax',1],['Payroll',2]] as const){
    await expect(control('lblSection'+section+'111')).toContainText(`${count}件（内蔵テスト）`);
  }
  await expect(control('galWork111')).toContainText('15,000');
  await control('btnPayrollOpen111').getByRole('button').click();
  await expect(control('galPayrollModal111')).toContainText('職員03専用・9月・合成テスト');
  await expect(control('galPayrollModal111')).toContainText('職員03専用・8月・合成テスト');
  await control('btnPayClose111').getByRole('button').click();
  for(const n of [11,12]){
    await select('0099000000'+n);
    await control('btnCertificate111').getByRole('button').click();
    await expect(control('conLedgerModal111')).toBeVisible();
    await expect(control('conLedgerModal111')).toContainText('0099000000'+n);
    await expect(control('conLedgerModal111')).toContainText('架空'+n+'駅');
    await expect(control('conLedgerModal111')).not.toContainText('架空'+(n===11?12:11)+'駅');
    await page.screenshot({path:`test-results/hybrid-ledger-${n}.png`});
    await control('btnLedgerClose111').getByRole('button').click();
  }
  await select('009900000005');
  await expect(control('lblSectionPayroll111')).toContainText('1件');
  await expect(control('galPayroll111')).toContainText('0');
  await select('009900000001');
  await expect(control('lblSectionWork111')).toContainText('0件');
  await expect(control('btnCertificate111').getByRole('button')).toBeDisabled();
  await control('btnPayrollOpen111').getByRole('button').click();
  await expect(control('btnPayExport111').getByRole('button')).toBeDisabled();
  await expect(control('galPayrollModal111')).not.toContainText('職員03専用');
  await control('btnPayClose111').getByRole('button').click();
  await page.screenshot({path:'test-results/hybrid-empty.png'});
});
