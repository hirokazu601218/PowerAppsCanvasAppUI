import {test,expect} from '@playwright/test';
test.describe.configure({retries:0});
test.use({video:'off',ignoreHTTPSErrors:false});
test('PAY-APP-001 all seven Dataverse rows, employee isolation, empty/zero, adjustments and export',async({page})=>{
 test.setTimeout(240000);
 await page.setViewportSize({width:1366,height:1000});
 await page.goto(process.env.CANVAS_APP_URL!,{waitUntil:'domcontentloaded'});
 const app=page.frameLocator('iframe[name="fullscreen-app-host"]');
 const ctl=(n:string)=>app.locator(`[data-control-name="${n}"]`);
 await expect(app.getByText('v1.19 ／ Dataverse・25名',{exact:true})).toBeVisible({timeout:60000});
 const select=async(id:string)=>{await app.getByRole('searchbox',{name:'氏名・職員番号・項目を検索',exact:true}).fill(id);await app.getByRole('button',{name:'検索',exact:true}).click();await app.getByRole('button',{name:new RegExp('^'+id+' .* 詳細を表示$')}).click();};
 const cases=[['003',3,'253,000','243,000'],['004',1,'230,000','220,000'],['011',1,'240,000','230,000'],['012',1,'260,000','250,000'],['005',1,'0','0']] as const;
 for(const [suffix,count,gross,net] of cases){
  const id='009900000'+suffix; await select(id);
  await expect(ctl('lblSectionPayroll111')).toContainText(`${count}件（Dataverse）`);
  await expect(ctl('lblCPayroll11110').first()).toHaveText(gross);
  await expect(ctl('lblCPayroll11113').first()).toHaveText(net);
  await ctl('btnPayrollOpen111').getByRole('button').click();
  await expect(ctl('lblPayrollModalTitle111')).toContainText(id);
  await expect(ctl('lblSectionPayrollModal111')).toContainText(`${count}件（Dataverse）`);
  await expect(ctl('lblCPayrollModal11110').first()).toHaveText(gross);
  await expect(ctl('lblCPayrollModal11113').first()).toHaveText(net);
  if(suffix==='003'){
   await expect(ctl('lblCPayrollModal1111')).toHaveText(['令和08年06月23日','令和08年05月23日','令和08年04月23日']);
   await expect(ctl('lblCPayrollModal1113')).toHaveText(['-2,000','5,000','0']);
   await expect(ctl('lblCPayrollModal11110')).toHaveText(['253,000','260,000','250,000']);
   await expect(ctl('lblCPayrollModal11113')).toHaveText(['243,000','250,000','240,000']);
  }
  await page.screenshot({path:`test-results/payroll-${suffix}.png`});
  await ctl('btnPayClose111').getByRole('button').click();
 }
 for(const suffix of ['001','025']){
  await select('009900000'+suffix);
  await expect(ctl('lblSectionPayroll111')).toContainText('0件（Dataverse）');
  await ctl('btnPayrollOpen111').getByRole('button').click();
  await expect(ctl('btnPayExport111').getByRole('button')).toBeDisabled();
  await expect(ctl('lblEmptyPayrollModal111')).toBeVisible();
  await expect(ctl('galPayrollModal111')).not.toContainText('令和08年');
  await ctl('btnPayClose111').getByRole('button').click();
 }
 await app.getByRole('button',{name:'Dataverseの最新データを読み込む',exact:true}).click();
 await select('009900000003');
 await ctl('btnPayrollOpen111').getByRole('button').click();
 await ctl('btnPayExport111').getByRole('button').click();
 await expect(app.getByRole('textbox',{name:'コピー用テキスト。全選択してExcelへ貼り付けできます。',exact:true})).toHaveValue(/令和08年06月23日/);
 await expect(app.getByRole('textbox',{name:'コピー用テキスト。全選択してExcelへ貼り付けできます。',exact:true})).toHaveValue(/現金支給額\t243,000/);
 await expect(app.getByRole('textbox',{name:'コピー用テキスト。全選択してExcelへ貼り付けできます。',exact:true})).toHaveValue(/-2,000/);
 await page.screenshot({path:'test-results/payroll-export.png'});
 console.log('PAYROLL_SEVEN_ROWS_ZERO_ISOLATION_REFRESH_EXPORT_PASSED');
});
