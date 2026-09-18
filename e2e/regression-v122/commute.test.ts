// Published v1.19 acceptance: six real Dataverse fixture records and zero-child cases.
import {test, expect} from '@playwright/test';
import {readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
test.describe.configure({retries: 0});
test.use({video: 'off', ignoreHTTPSErrors: false});

test('COM-APP-001 six Dataverse records, chosen recognition, dates, money and blank routes', async ({page}) => {
  test.setTimeout(240000);
  await page.setViewportSize({width: 1366, height: 1000});
  await page.goto(process.env.CANVAS_APP_URL!, {waitUntil: 'domcontentloaded'});
  const app = page.frameLocator('iframe[name="fullscreen-app-host"]');
  const ctl = (name: string) => app.locator(`[data-control-name="${name}"]`);
  await expect(app.locator('[data-control-name="lblHomePrototype"]')).toContainText('UI検討用 v1.23',{timeout:60000});
  await app.locator('[data-control-name="btnHomeStaff"]').getByRole('button').click();
  const selectStaff = async (id: string) => {
    await app.getByRole('button',{name:'ホーム',exact:true}).first().click();
    await app.locator('[data-control-name="ddHomeDepartment"]').click();
    const dept=id.endsWith('004')||id.endsWith('011')?'03会計課':id.endsWith('012')||id.endsWith('002')?'01秘書課':'02総務課';
    await app.getByRole('option',{name:dept,exact:true}).click();
    await app.locator('[data-control-name="btnHomeStaff"]').getByRole('button').click();
    await app.getByRole('searchbox', {name: '氏名・職員番号・項目を検索', exact: true}).fill(id);
    await app.getByRole('button', {name: '検索', exact: true}).click();
    await app.getByRole('button', {name: new RegExp('^' + id + ' .* 詳細を表示$')}).click();
  };
  const cases = [
    {staff: '009900000003', id: 'TK-910001', year: '8', month: '4', total: '1,300', pass: '7,800', other: '0', from: '架空03駅'},
    {staff: '009900000003', id: 'TK-910002', year: '8', month: '10', total: '1,400', pass: '8,400', other: '0', from: '架空03駅'},
    {staff: '009900000004', id: 'TK-910003', year: '7', month: '4', total: '16,800', pass: '0', other: '16,800', from: '架空04駅'},
    {staff: '009900000011', id: 'TK-910004', year: '8', month: '4', total: '0', pass: '', other: '', from: ''},
    {staff: '009900000013', id: 'TK-910005', year: '8', month: '4', total: '0', pass: '', other: '', from: ''},
    {staff: '009900000025', id: 'TK-910006', year: '81', month: '4', total: '0', pass: '', other: '', from: ''},
  ];
  const staffFixture=JSON.parse(readFileSync(path.join(process.env.FIXTURE_ROOT!,'staff-basic-25.json'),'utf8'));
  const commuteFixture=JSON.parse(readFileSync(path.join(process.env.FIXTURE_ROOT!,'commute-6.json'),'utf8'));
  const map=JSON.parse(readFileSync(path.resolve(process.env.FIXTURE_ROOT!,'../../src/staff-master/patches/v1.18/ledger-field-map.json'),'utf8'));
  expect(map).toHaveLength(69);
  const observed=[];
  const formatted=(value:any,format:string)=>{
    if(value==null)return '';
    if(format==='text')return String(value).normalize('NFKC');
    if(format==='amount')return Number(value).toLocaleString('en-US',{maximumFractionDigits:0});
    if(format==='decimal')return Number(value).toLocaleString('en-US',{useGrouping:false,maximumFractionDigits:4});
    if(format==='integer')return String(Math.round(Number(value)));
    if(format==='paymonth')return String(value)+'月';
    const [year,month,day]=String(value).split('-').map(Number);
    if(format==='year')return String(year>=2019?year-2018:year);
    if(format==='era_year')return (year>=2019?'令和'+(year-2018):String(year))+'年';
    if(format==='month')return String(month);
    if(format==='start_month')return String(month)+'月から';
    if(format==='day')return String(day);
    throw new Error('Unknown independent field format '+format);
  };
  for (const item of cases) {
    await selectStaff(item.staff);
    await expect(ctl('lblSectionCommute111')).toContainText(item.staff.endsWith('003') ? '2件' : '1件');
    await expect(ctl('lblSectionCommute111')).not.toContainText('内蔵テスト');
    await app.getByRole('listitem', {name: new RegExp('^' + item.id + ' ')}).click();
    await ctl('btnCertificate111').getByRole('button').click();
    await expect(ctl('conLedgerModal111')).toBeVisible();
    await expect(ctl('lblLedgerStaff111')).toContainText(item.id);
    await expect(ctl('lblLedger_employee_number111')).toHaveText(item.staff);
    for (const date of ['event_date', 'submitted_date', 'accepted_date']) {
      await expect(ctl('lblLedger_' + date + '_year111')).toHaveText(item.year);
      await expect(ctl('lblLedger_' + date + '_month111')).toHaveText(item.month);
      await expect(ctl('lblLedger_' + date + '_day111')).toHaveText('1');
    }
    for (const [field, value] of [['monthly_amount_total', item.total], ['route_1_season_amount', item.pass], ['route_1_other_amount', item.other], ['route_1_section_from', item.from]]) {
      await expect(ctl('lblLedger_' + field + '111')).toHaveText(value);
    }
    for (const route of [2, 3, 4]) {
      for (const field of ['transport', 'section_from', 'section_to', 'season_amount', 'monthly_amount']) {
        await expect(ctl(`lblLedger_route_${route}_${field}111`)).toHaveText('');
      }
    }
    const staff=staffFixture.find((s:any)=>s.staffnumber===item.staff);
    const commute=commuteFixture.find((s:any)=>s.data.crb3c_recognitionid===item.id).data;
    const staffValues:any={Name:staff.fullname,StaffId:staff.staffnumber,Org:staff.orgshort};
    const values=[];
    for(const field of map){
      const expected=formatted(field.source==='staff'?staffValues[field.column]:commute[field.column],field.format);
      const label=ctl(`lblLedger_${field.field}111`);await expect(label).toHaveText(expected);
      values.push({field:field.field,value:await label.innerText()});
    }
    observed.push({staff:item.staff,recognition:item.id,values});
    await page.locator('iframe[name="fullscreen-app-host"]').screenshot({path: `test-results/commute-${item.id}.png`,mask:[ctl('lblStaffAccount122')]});
    await ctl('btnLedgerClose111').getByRole('button').click();
  }
  writeFileSync(path.join(process.env.OUTPUT_DIRECTORY!,'commute-all-69-fields.json'),JSON.stringify(observed,null,2));
  // The same-name user 012 and pre-hire user 001 have no commute record.
  for (const id of ['009900000012', '009900000002']) {
    await selectStaff(id);
    await expect(ctl('lblSectionCommute111')).toContainText('0件');
    await expect(ctl('btnCertificate111').getByRole('button')).toBeDisabled();
    await expect(ctl('conLedgerModal111')).toBeHidden();
    await expect(ctl('galCommute111')).not.toContainText('TK-910006');
  }
  await app.getByRole('button', {name: 'Dataverseの最新データを読み込む', exact: true}).click();
  await expect(app.getByText('職員一覧 8件', {exact: true})).toBeVisible();
  await selectStaff('009900000003');
  await expect(ctl('galCommute111')).toContainText('TK-910001');
  await expect(ctl('galCommute111')).toContainText('TK-910002');
  console.log('COMMUTE_SIX_RECORDS_AND_ZERO_CASES_PASSED');
});
