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
  const searchInput = canvas.getByRole('searchbox', {
    name: '氏名・職員番号・項目を検索', exact: true,
  });
  await expect.poll(async () => await homeLink.isVisible() || await searchInput.isVisible(), {
    timeout: 60_000,
  }).toBe(true);
  if (!(await searchInput.isVisible())) await homeLink.click();
  await expect(searchInput).toBeVisible({ timeout: 30_000 });
  return canvas;
}

async function searchSameName(canvas: FrameLocator): Promise<void> {
  const input = canvas.getByRole('searchbox', {
    name: '氏名・職員番号・項目を検索', exact: true,
  });
  await expect(input).toBeVisible();
  await input.fill('');
  await input.pressSequentially('同姓同名', { delay: 80 });
  // Commit the modern input's pending value before the button reads Text.
  await input.press('Tab');
  await expect(input).toHaveValue('同姓同名');
  const searchButton = canvas.getByRole('button', { name: '検索', exact: true });
  await searchButton.click();
  // The current app limits the dedicated test user's view to 03会計課.
  try {
    await expect(canvas.getByText(/職員一覧\s*1件/)).toBeVisible({ timeout: 30_000 });
  } catch (error) {
    const title = await canvas.locator('[data-control-name="lblListTitle111"]')
      .innerText({ timeout: 5_000 }).catch(() => '');
    // Only publish a synthetic row's presence and the numeric result count.
    console.log('Search diagnostics:', JSON.stringify({
      count: title.match(/職員一覧\s*([0-9０-９]+)件/)?.[1] ?? null,
      row004: await canvas.getByRole('button', { name: /009900000004/ }).isVisible(),
      row011: await canvas.getByRole('button', { name: /009900000011/ }).isVisible(),
      row012: await canvas.getByRole('button', { name: /009900000012/ }).isVisible(),
      keywordEntered: await input.inputValue() === '同姓同名',
      searchButtonIsExpected: await searchButton.evaluate(element =>
        element.closest('[data-control-name]')?.getAttribute('data-control-name') === 'btnSearch111'),
    }));
    throw error;
  }
  await expect(canvas.getByRole('button', {
    name: '009900000011 試験 同姓同名 詳細を表示', exact: true,
  })).toBeVisible();
  await expect(canvas.getByRole('button', {
    name: '009900000012 試験 同姓同名 詳細を表示', exact: true,
  })).toHaveCount(0);
}

test('UT-SRCH-001 検索部品は入力を受けて所属内の架空の1名を表示する', async ({ page }) => {
  const canvas = await openStaffSearch(page);
  await searchSameName(canvas);
});

test('IT-SRCH-DETAIL-001 検索結果の選択が詳細へ反映される', async ({ page }) => {
  const canvas = await openStaffSearch(page);
  await searchSameName(canvas);
  await canvas.getByRole('button', {
    name: '009900000011 試験 同姓同名 詳細を表示', exact: true,
  }).click();
  await expect(canvas.getByText('職員基本情報', { exact: true })).toBeVisible();
  // Check the detail summary, not a matching number inside the search result row.
  await expect(canvas.locator('[data-control-name="lblPersonSub111"]'))
    .toHaveText(/職員番号：009900000011\s*／\s*所属：03会計課/, { timeout: 30_000 });
});
