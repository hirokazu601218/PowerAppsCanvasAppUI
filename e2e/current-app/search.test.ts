import { expect, test, type FrameLocator, type Page } from '@playwright/test';

// Only the read-only, isolated current app may be exercised here.
const ENVIRONMENT_ID = '68e00049-b7e5-eda6-9888-9a3cc493c5be';
const APP_ID = '204a48dc-7f23-43dd-b934-4654a3cfa306';
const FRAME = 'iframe[name="fullscreen-app-host"]';

test.describe.configure({ retries: 0 });
test.use({ video: 'off', screenshot: 'off', trace: 'off' });

async function openStaffSearch(page: Page): Promise<FrameLocator> {
  const value = process.env.CANVAS_APP_URL;
  if (!value) throw new Error('CANVAS_APP_URL is required');
  const url = new URL(value);
  if (
    url.protocol !== 'https:' ||
    url.hostname !== 'apps.powerapps.com' ||
    url.pathname !== `/play/e/${ENVIRONMENT_ID}/a/${APP_ID}`
  ) {
    throw new Error('Refusing to test an unexpected environment or App ID');
  }
  await page.setViewportSize({ width: 1366, height: 768 });
  await page.goto(url.toString(), { waitUntil: 'domcontentloaded', timeout: 60_000 });
  const canvas = page.frameLocator(FRAME);
  const homeLink = canvas.getByRole('button', { name: '職員マスタ検索', exact: true });
  const heading = canvas.getByText('非常勤職員マスタ検索', { exact: true });
  await expect.poll(async () => await homeLink.isVisible() || await heading.isVisible(), {
    timeout: 60_000,
  }).toBe(true);
  if (await homeLink.isVisible()) await homeLink.click();
  await expect(heading).toBeVisible({ timeout: 30_000 });
  return canvas;
}

async function searchSameName(canvas: FrameLocator): Promise<void> {
  const input = canvas.getByRole('searchbox', {
    name: '氏名・職員番号・項目を検索', exact: true,
  });
  await expect(input).toBeVisible();
  await input.fill('同姓同名');
  await canvas.getByRole('button', { name: '検索', exact: true }).click();
  await expect(canvas.getByText(/職員一覧\s*2件/)).toBeVisible({ timeout: 30_000 });
  await expect(canvas.getByRole('button', {
    name: '009900000011 試験 同姓同名 詳細を表示', exact: true,
  })).toBeVisible();
  await expect(canvas.getByRole('button', {
    name: '009900000012 試験 同姓同名 詳細を表示', exact: true,
  })).toBeVisible();
}

test('UT-SRCH-001 検索部品は入力を受けて架空の2名を表示する', async ({ page }) => {
  const canvas = await openStaffSearch(page);
  await searchSameName(canvas);
});

test('IT-SRCH-DETAIL-001 検索結果の選択が詳細へ反映される', async ({ page }) => {
  const canvas = await openStaffSearch(page);
  await searchSameName(canvas);
  await canvas.getByRole('button', {
    name: '009900000012 試験 同姓同名 詳細を表示', exact: true,
  }).click();
  await expect(canvas.getByText('職員基本情報', { exact: true })).toBeVisible();
  // Both list rows are still present. The selected number must also be visible in the right detail area.
  await expect.poll(async () => {
    for (const candidate of await canvas.getByText('009900000012', { exact: true }).all()) {
      const box = await candidate.boundingBox();
      if (box && box.width > 0 && box.x >= 360) return true;
    }
    return false;
  }, { timeout: 30_000, message: 'selected staff number in the detail area' }).toBe(true);
});
