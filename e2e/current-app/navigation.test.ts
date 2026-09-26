import { expect, test, type FrameLocator, type Page } from '@playwright/test';

const ENVIRONMENT_ID = '68e00049-b7e5-eda6-9888-9a3cc493c5be';
const APP_ID = '204a48dc-7f23-43dd-b934-4654a3cfa306';
const FRAME = 'iframe[name="fullscreen-app-host"]';

test.describe.configure({ retries: 0 });
test.use({ video: 'off', screenshot: 'off', trace: 'off' });

async function openStaffSearch(page: Page): Promise<FrameLocator> {
  const configured = process.env.CANVAS_APP_URL;
  if (!configured) throw new Error('CANVAS_APP_URL is required');
  const url = new URL(configured);
  if (url.protocol !== 'https:' || url.hostname !== 'apps.powerapps.com' ||
      url.pathname !== `/play/e/${ENVIRONMENT_ID}/a/${APP_ID}`) {
    throw new Error('Refusing to test an unexpected environment or App ID');
  }
  await page.setViewportSize({ width: 1366, height: 768 });
  await page.goto(url.toString(), { waitUntil: 'domcontentloaded', timeout: 60_000 });
  const canvas = page.frameLocator(FRAME);
  const homeLink = canvas.getByRole('button', { name: '職員マスタ検索', exact: true });
  await expect(homeLink).toBeVisible({ timeout: 60_000 });
  await homeLink.click();
  await expect(canvas.getByRole('searchbox', {
    name: '氏名・職員番号・項目を検索', exact: true,
  })).toBeVisible({ timeout: 30_000 });
  // The current test user's default scope is 03会計課 (seven synthetic staff).
  await expect(canvas.locator('[data-control-name="lblListTitle111"]'))
    .toHaveText(/職員一覧\s*7件/, { timeout: 30_000 });
  return canvas;
}

test('UT-HOME-001 ホームの職員マスタ検索ボタンで所属内の一覧を開く', async ({ page }) => {
  const canvas = await openStaffSearch(page);
  await expect(canvas.getByRole('button', { name: /009900000004/ })).toBeVisible();
  await expect(canvas.getByRole('button', { name: /009900000011/ })).toBeVisible();
  await expect(canvas.getByRole('button', { name: /009900000012/ })).toHaveCount(0);
});

test('IT-HOME-DETAIL-001 一覧の職員選択を詳細表示へ引き渡す', async ({ page }) => {
  const canvas = await openStaffSearch(page);
  const summary = canvas.locator('[data-control-name="lblPersonSub111"]');
  await expect(summary).toHaveText(/職員番号：009900000004\s*／\s*所属：03会計課/);
  await canvas.getByRole('button', { name: /009900000011 .*詳細を表示/ }).click();
  await expect(summary).toHaveText(/職員番号：009900000011\s*／\s*所属：03会計課/, {
    timeout: 30_000,
  });
});
