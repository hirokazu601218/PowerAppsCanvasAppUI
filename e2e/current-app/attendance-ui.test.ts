import { expect, test, type Page } from '@playwright/test';

async function open(page: Page) {
  const value = process.env.CANVAS_APP_URL;
  if (!value) throw new Error('CANVAS_APP_URL is required');
  const url = new URL(value);
  if (url.hostname !== 'apps.powerapps.com' || !url.pathname.endsWith('/a/204a48dc-7f23-43dd-b934-4654a3cfa306')) throw new Error('Unexpected app');
  await page.goto(value, { waitUntil: 'domcontentloaded', timeout: 60000 });
  const app = page.frameLocator('iframe[name="fullscreen-app-host"]');
  await expect(app.getByRole('button', { name: '勤務時間報告画面', exact: true })).toBeVisible();
  // Existing owner-provided flow connections require Player consent after release.
  const consent = page.frameLocator('iframe[src*="/consent/"]');
  const allow = consent.getByRole('button', { name: /^(Allow|許可)$/ });
  try { await allow.waitFor({ state: 'visible', timeout: 10000 }); }
  catch { /* Already consented sessions do not show this dialog. */ }
  if (await allow.isVisible()) await allow.click();
  return app;
}

test('UT-SCR003-VIEW-001 正式勤務報告画面の初期状態と取込入口', async ({ page }) => {
  const app = await open(page);
  await app.getByRole('button', { name: '勤務時間報告画面', exact: true }).click();
  await expect(app.getByText('勤務時間報告書 ｜ SCR-003', { exact: true })).toBeVisible();
  await expect(app.getByText('局と勤務月を選択してください', { exact: true })).toBeVisible();
  await expect(app.getByRole('button', { name: '報告', exact: true })).toBeDisabled();
  await app.getByRole('button', { name: 'Excel取込', exact: true }).click();
  await expect(app.getByRole('button', { name: 'ファイルを添付', exact: true })).toBeVisible();
  await expect(app.getByRole('button', { name: '取込実行', exact: true })).toBeVisible();
});

test('UT-SCR006-MONTH-001 対象月設定と解除の入口', async ({ page }) => {
  const app = await open(page);
  await app.getByRole('button', { name: '一般 → 管理者に切替', exact: true }).click();
  await app.getByRole('button', { name: 'メンテナンス画面', exact: true }).click();
  await expect(app.getByText('勤務報告対象月の設定', { exact: true })).toBeVisible();
  await expect(app.getByRole('button', { name: '対象月に設定', exact: true })).toBeVisible();
  await expect(app.getByRole('button', { name: '対象月から外す', exact: true })).toBeVisible();
});

test('IT-SCR003-READBACK-001 保存済み架空10件と勤務期間を再表示', async ({ page }) => {
  const app = await open(page);
  await app.getByRole('button', { name: '勤務時間報告画面', exact: true }).click();
  // Power Apps renders month/bureau and status in one text container.
  const report = app.getByRole('listitem').filter({ hasText: /2026\/08\s+秘書課/ });
  await expect(report).toHaveCount(1);
  await report.click();
  await expect(app.getByText('勤務期間：2026/08/01 ～ 2026/08/31', { exact: false })).toBeVisible();
  for (let n = 1; n <= 10; n++) {
    const staff = app.getByText(String(n).padStart(12, '0'), { exact: true });
    await staff.scrollIntoViewIfNeeded();
    await expect(staff).toBeVisible();
  }
  await expect(app.getByText('33.167', { exact: true })).toBeVisible();
  await expect(app.getByText('年次休暇：8/28 5.25h、8/31', { exact: true })).toBeVisible();
});
