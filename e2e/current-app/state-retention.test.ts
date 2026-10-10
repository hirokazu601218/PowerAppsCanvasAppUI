import { expect, test, type FrameLocator, type Page } from '@playwright/test';

const ENV = '68e00049-b7e5-eda6-9888-9a3cc493c5be';
const APP = '204a48dc-7f23-43dd-b934-4654a3cfa306';
const STAFF = '009900000011'; // Existing isolated synthetic fixture, never a real employee.
const control = (app: FrameLocator, name: string) => app.locator(`[data-control-name="${name}"]`);
test.describe.configure({ retries: 0 });
test.use({ video: 'off', screenshot: 'off', trace: 'off' });

async function open(page: Page): Promise<FrameLocator> {
  const configured = process.env.CANVAS_APP_URL;
  if (!configured) throw new Error('CANVAS_APP_URL is required');
  const url = new URL(configured);
  if (url.protocol !== 'https:' || url.hostname !== 'apps.powerapps.com' ||
      url.pathname !== `/play/e/${ENV}/a/${APP}`) throw new Error('Unexpected trial environment or App ID');
  await page.setViewportSize({ width: 1366, height: 768 });
  await page.goto(url.toString(), { waitUntil: 'domcontentloaded', timeout: 60_000 });
  const app = page.frameLocator('iframe[name="fullscreen-app-host"]');
  const home = app.getByRole('button', { name: '職員マスタ検索', exact: true });
  const deadline = Date.now() + 60_000;
  while (Date.now() < deadline) {
    for (const frame of page.frames().filter(f => /\/consent\//.test(f.url()) || /consent/i.test(f.name()))) {
      if (await frame.getByRole('button', { name: /^(Allow|許可)$/ }).isVisible().catch(() => false)) {
        throw new Error('BLOCKED: unexpected connection consent requires owner approval');
      }
    }
    if (await home.isVisible().catch(() => false)) break;
    await page.waitForTimeout(250);
  }
  await expect(home).toBeVisible();
  await home.click();
  await expect(app.getByRole('searchbox', { name: '氏名・職員番号・項目を検索' })).toBeVisible({ timeout: 60_000 });
  return app;
}

async function search(app: FrameLocator, text: string) {
  await app.getByRole('searchbox', { name: '氏名・職員番号・項目を検索' }).fill(text);
  await app.getByRole('button', { name: '検索', exact: true }).click();
}
async function selectStaff(app: FrameLocator) {
  await search(app, STAFF);
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*1件/);
  await expect(control(app, 'lblPersonSub111')).toContainText(`職員番号：${STAFF}`);
}
async function payroll(app: FrameLocator) {
  await selectStaff(app);
  await app.getByRole('button', { name: '支給明細画面', exact: true }).click();
  await expect(control(app, 'lblPayrollStaff')).toContainText(STAFF);
}
async function month(app: FrameLocator, value: string) {
  await control(app, 'ddPayrollMonth').click();
  // Canvas classic dropdown exposes flyout values as text, not reliably role=option.
  const choice = app.getByText(value, { exact: true }).last();
  await expect(choice).toBeVisible();
  await choice.click();
}
async function allBasis(app: FrameLocator, pattern: string | RegExp) {
  for (let i = 0; i < 8; i++) await expect(control(app, `lblPayDeductionBasis${i}`)).toHaveText(pattern);
}

test('UT-STATE-SEARCH-001 検索確定値と0件クリアを区別する', async ({ page }) => {
  const app = await open(page);
  await selectStaff(app);
  await app.getByRole('searchbox', { name: '氏名・職員番号・項目を検索' }).fill('未確定の入力');
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*1件/);
  await expect(control(app, 'lblPersonSub111')).toContainText(STAFF);
  await search(app, '999999999999');
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*0件/);
  await expect(control(app, 'lblPersonSub111')).not.toContainText(STAFF);
  await expect(app.getByRole('button', { name: '支給明細画面', exact: true })).toBeDisabled();
  await app.getByRole('button', { name: 'クリア', exact: true }).click();
  await expect(app.getByRole('searchbox', { name: '氏名・職員番号・項目を検索' })).toHaveValue('');
  await expect(control(app, 'lblListTitle111')).not.toHaveText(/職員一覧\s*0件/);
});

test('IT-STATE-RETURN-001 支給明細往復で確定検索結果と未確定入力を混同しない', async ({ page }) => {
  const app = await open(page);
  await selectStaff(app);
  const keyword = app.getByRole('searchbox', { name: '氏名・職員番号・項目を検索' });
  await keyword.fill('未確定の入力');
  for (let i = 0; i < 2; i++) {
    await app.getByRole('button', { name: '支給明細画面', exact: true }).click();
    await expect(control(app, 'lblPayrollStaff')).toContainText(STAFF);
    await app.getByRole('button', { name: '職員マスタ検索', exact: true }).click();
    await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*1件/);
    await expect(control(app, 'lblPersonSub111')).toContainText(STAFF);
    await expect(keyword).toHaveValue('未確定の入力');
  }
  await search(app, '999999999999');
  await app.getByRole('button', { name: 'ホーム', exact: true }).click();
  await app.getByRole('button', { name: '職員マスタ検索', exact: true }).click();
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*0件/);
  await expect(control(app, 'lblPersonSub111')).not.toContainText(STAFF);
});

test('UT-STATE-HISTORY-001 複数履歴の2行目を選び本人の税固定控除を表示する', async ({ page }) => {
  const app = await open(page); await selectStaff(app);
  await app.getByRole('button', { name: '税固定控除', exact: true }).click();
  await expect(control(app, 'galHistory111').getByText(/履歴 登録済/)).toBeVisible();
  await control(app, 'galHistory111').getByText(/履歴 過去 2026\/09\/01/).click();
  await expect(control(app, 'galDetailFields111')).toContainText('税表区分');
  await expect(control(app, 'galDetailFields111')).toContainText('架空試験-税表区分');
  await expect(control(app, 'galDetailFields111')).not.toContainText('納付先自治体');
});

test('IT-STATE-HISTORY-TABS-001 区分別に選んだ履歴をタブと画面往復で保持する', async ({ page }) => {
  const app = await open(page); await selectStaff(app);
  await app.getByRole('button', { name: '税固定控除', exact: true }).click();
  await control(app, 'galHistory111').getByText(/履歴 過去 2026\/09\/01/).click();
  for (const tab of ['基本情報', '勤務条件', '社会保険']) {
    await app.getByRole('button', { name: tab, exact: true }).click();
    await app.getByRole('button', { name: '税固定控除', exact: true }).click();
    await expect(control(app, 'galDetailFields111')).toContainText('架空試験-税表区分');
    await expect(control(app, 'galDetailFields111')).not.toContainText('納付先自治体');
  }
  await app.getByRole('button', { name: '支給明細画面', exact: true }).click();
  await app.getByRole('button', { name: '職員マスタ検索', exact: true }).click();
  await expect(control(app, 'galDetailFields111')).toContainText('架空試験-税表区分');
});

test('UT-STATE-HISTORY-EMPTY-001 職員切替と0件で前職員の履歴を残さない', async ({ page }) => {
  const app = await open(page); await selectStaff(app);
  await app.getByRole('button', { name: '税固定控除', exact: true }).click();
  await control(app, 'galHistory111').getByText(/履歴 過去 2026\/09\/01/).click();
  await search(app, '009900000004');
  await app.getByRole('button', { name: '勤務条件', exact: true }).click();
  await expect(app.getByText('登録されている履歴はありません')).toBeVisible();
  await expect(control(app, 'galDetailFields111')).toBeHidden();
  await search(app, '999999999999');
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*0件/);
  await expect(control(app, 'galHistory111')).toBeHidden();
  await expect(control(app, 'galDetailFields111')).toBeHidden();
  await selectStaff(app);
  await app.getByRole('button', { name: '税固定控除', exact: true }).click();
  await expect(control(app, 'galDetailFields111')).toContainText('納付先自治体');
  await expect(control(app, 'galDetailFields111')).not.toContainText('架空試験-税表区分');
});

test('UT-STATE-PAYROLL-001 未登録と再計算前は8根拠を失効し登録済み0円を区別する', async ({ page }) => {
  const app = await open(page); await payroll(app);
  await month(app, '2026/09');
  await app.getByRole('button', { name: '再計算', exact: true }).click();
  await expect(control(app, 'lblPaySummaryNetValue')).toHaveText('151,800 円');
  await expect(control(app, 'lblPayDeductionBasis5')).toContainText('165,550');
  await month(app, '2026/10');
  await allBasis(app, '算定根拠　—');
  await expect(control(app, 'lblPaySummaryNetValue')).toHaveText('—');
  await expect(control(app, 'lblPayState')).toHaveText('勤務時間報告が未登録です');
  await month(app, '2026/09');
  await allBasis(app, '算定根拠　—');
  await expect(control(app, 'lblPayState')).toContainText('再計算してください');
  await app.getByRole('button', { name: '再計算', exact: true }).click();
  await expect(control(app, 'lblPayDeductionBasis5')).toContainText('165,550');
  await month(app, '2026/11');
  await allBasis(app, '算定根拠　—');
  await app.getByRole('button', { name: '再計算', exact: true }).click();
  await allBasis(app, '登録済み0円（仮例）');
  await expect(control(app, 'lblPaySummaryNetValue')).toHaveText('0 円');
});

test('UT-STATE-SUMMARY-001 最後の貯金預入までスクロールしてもサマリーを固定する', async ({ page }) => {
  const app = await open(page); await payroll(app);
  const summary = control(app, 'conPaySummary');
  const targets = control(app, 'conPayrollTargets');
  const before = await summary.boundingBox();
  const targetBefore = await targets.boundingBox();
  expect(before).not.toBeNull(); expect(targetBefore).not.toBeNull();
  await control(app, 'lblPayDeductionName7').scrollIntoViewIfNeeded();
  await expect(control(app, 'lblPayDeductionName7')).toBeInViewport();
  await expect(summary).toBeInViewport();
  const after = await summary.boundingBox(); const targetAfter = await targets.boundingBox();
  expect(after).not.toBeNull(); expect(targetAfter).not.toBeNull();
  expect(Math.abs(after!.y - before!.y)).toBeLessThanOrEqual(1);
  expect(Math.abs(targetAfter!.y - targetBefore!.y)).toBeLessThanOrEqual(1);
  expect(after!.y).toBeGreaterThanOrEqual(targetAfter!.y + targetAfter!.height - 1);
  expect(await control(app, 'conPayBody').boundingBox()).not.toBeNull();
});


test('IT-STATE-PAGE-001 内蔵40件の2ページ目と職員選択を往復後も保持する', async ({ page }) => {
  const app = await open(page);
  await app.getByRole('button', { name: 'ホーム', exact: true }).click();
  const demoAdmin = app.getByRole('button', { name: '一般 → 管理者に切替', exact: true });
  if (await demoAdmin.isVisible()) await demoAdmin.click(); // Existing in-memory demo switch, not a Dataverse role.
  await app.getByRole('button', { name: 'メンテナンス', exact: true }).click();
  await control(app, 'ddUiFixture124').click();
  await app.getByText('40件', { exact: true }).last().click();
  await app.getByRole('button', { name: 'ホーム', exact: true }).click();
  await app.getByRole('button', { name: '職員マスタ検索', exact: true }).click();
  await search(app, '008800000');
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*40件/);
  await app.getByRole('button', { name: '次へ', exact: true }).click();
  await expect(control(app, 'lblPage111')).toHaveText('2 / 2');
  await app.getByRole('button', { name: /008800000021 .*詳細を表示/ }).click();
  await expect(control(app, 'lblPersonSub111')).toContainText('008800000021');
  await app.getByRole('button', { name: '支給明細画面', exact: true }).click();
  await app.getByRole('button', { name: '職員マスタ検索', exact: true }).click();
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*40件/);
  await expect(control(app, 'lblPage111')).toHaveText('2 / 2');
  await expect(control(app, 'lblPersonSub111')).toContainText('008800000021');
  await expect(app.getByRole('button', { name: /008800000021 .*詳細を表示/ })).toBeVisible();
  await search(app, '008800000040');
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*1件/);
  await expect(control(app, 'lblPage111')).toHaveText('1 / 1');
  await search(app, '999999999999');
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*0件/);
  await expect(control(app, 'lblPage111')).toHaveText('1 / 1');
  // A fresh Player discards the in-memory display fixture. This is not a
  // Dataverse 40-row performance/delegation test and creates no data rows.
  const fresh = await open(page);
  await expect(control(fresh, 'lblListTitle111')).toHaveText(/職員一覧\s*7件/, { timeout: 30_000 });
  await expect(fresh.getByRole('searchbox', { name: '氏名・職員番号・項目を検索' })).toHaveValue('');
  await expect(fresh.getByRole('button', { name: /009900000004 .*詳細を表示/ })).toBeVisible();
  await expect(fresh.getByRole('button', { name: /008800000021 .*詳細を表示/ })).toHaveCount(0);
});

test('UT-STATE-SUMMARY-NARROW-001 幅900高さ600でも固定領域と末尾到達を両立する', async ({ page }) => {
  const app = await open(page); await payroll(app);
  await page.setViewportSize({ width: 900, height: 600 });
  const summary = control(app, 'conPaySummary');
  await expect(summary).toBeInViewport();
  const before = await summary.boundingBox(); expect(before).not.toBeNull();
  await control(app, 'lblPayDeductionName7').scrollIntoViewIfNeeded();
  await expect(control(app, 'lblPayDeductionName7')).toBeInViewport();
  await expect(summary).toBeInViewport();
  const after = await summary.boundingBox(); expect(after).not.toBeNull();
  expect(Math.abs(after!.y - before!.y)).toBeLessThanOrEqual(1);
  const body = await control(app, 'conPayBody').boundingBox(); expect(body).not.toBeNull();
  expect(body!.height).toBeGreaterThan(0);
  expect(body!.y).toBeGreaterThanOrEqual(after!.y + after!.height - 1);
});
