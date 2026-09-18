// Published v1.19 acceptance: six real Dataverse fixture records and zero-child cases.
import {test, expect} from '@playwright/test';
test.describe.configure({retries: 0});
test.use({video: 'off', ignoreHTTPSErrors: false});

test('COM-APP-001 six Dataverse records, chosen recognition, dates, money and blank routes', async ({page}) => {
  test.setTimeout(240000);
  await page.setViewportSize({width: 1366, height: 1000});
  await page.goto(process.env.CANVAS_APP_URL!, {waitUntil: 'domcontentloaded'});
  const app = page.frameLocator('iframe[name="fullscreen-app-host"]');
  const ctl = (name: string) => app.locator(`[data-control-name="${name}"]`);
  await expect(app.locator('[data-control-name="lblHomePrototype"]')).toContainText(/UI検討用 v1\.(22|23)/,{timeout:60000});
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
    await page.locator('iframe[name="fullscreen-app-host"]').screenshot({path: `test-results/commute-${item.id}.png`,mask:[ctl('lblStaffAccount122')]});
    await ctl('btnLedgerClose111').getByRole('button').click();
  }
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
