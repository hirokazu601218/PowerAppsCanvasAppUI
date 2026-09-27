import { expect, test, type FrameLocator, type Page } from '@playwright/test';

const ENV = '68e00049-b7e5-eda6-9888-9a3cc493c5be';
const APP = '204a48dc-7f23-43dd-b934-4654a3cfa306';

async function openScreen(page: Page): Promise<FrameLocator> {
  const configured = process.env.CANVAS_APP_URL;
  if (!configured) throw new Error('CANVAS_APP_URL is required');
  const url = new URL(configured);
  if (url.protocol !== 'https:' || url.hostname !== 'apps.powerapps.com' ||
      url.pathname !== `/play/e/${ENV}/a/${APP}`) {
    throw new Error('Unexpected environment or App ID');
  }
  await page.setViewportSize({ width: 1366, height: 768 });
  await page.goto(url.toString(), { waitUntil: 'domcontentloaded', timeout: 60_000 });
  const screen = page.frameLocator('iframe[name="fullscreen-app-host"]');
  await screen.getByRole('button', { name: '職員マスタ検索', exact: true }).click();
  await expect(screen.getByRole('searchbox', { name: '氏名・職員番号・項目を検索' }))
    .toBeVisible({ timeout: 60_000 });
  await expect(screen.getByText('職員一覧 7件')).toBeVisible({ timeout: 30_000 });
  return screen;
}

test('UT-SCR002-HEADER-001 ホームは画面IDの左にあり独立した年月選択はない', async ({ page }) => {
  const screen = await openScreen(page);
  const home = screen.getByRole('button', { name: 'ホーム', exact: true });
  const id = screen.getByText('SCR-002', { exact: true });
  const homeBox = await home.boundingBox();
  const idBox = await id.boundingBox();
  expect(homeBox && idBox && homeBox.x + homeBox.width <= idBox.x).toBeTruthy();
  await expect(screen.getByRole('button', { name: '支給対象月' })).toHaveCount(0);
});

test('UT-SCR002-HISTORY-001 四区分の長文履歴カードを表示せず明細を切り替える', async ({ page }) => {
  const screen = await openScreen(page);
  await screen.getByRole('button', { name: /009900000011 .*詳細を表示/ }).click();
  for (const tab of ['勤務条件', '通勤', '社会保険', '税固定控除']) {
    await screen.getByRole('button', { name: tab, exact: true }).click();
    await expect(screen.getByText('TK-910003 / 毎月精算', { exact: false })).toHaveCount(0);
    await expect(screen.getByText('職員番号：009900000011', { exact: false })).toBeVisible();
  }
});

test('UT-SCR002-PAYROLL-001 給与簿は月指定を維持し先頭行が件数の直下に続く', async ({ page }) => {
  const screen = await openScreen(page);
  await screen.getByRole('button', { name: /009900000011 .*詳細を表示/ }).click();
  await screen.getByRole('button', { name: '給与簿', exact: true }).click();
  await expect(screen.getByText('表示開始月')).toBeVisible();
  await expect(screen.getByText('表示終了月')).toBeVisible();
  const count = await screen.getByText('1 レコード').boundingBox();
  const first = await screen.getByText('給与期間対象年', { exact: true }).boundingBox();
  expect(count && first && first.y >= count.y && first.y - (count.y + count.height) < 100)
    .toBeTruthy();
  await expect(screen.getByText('給与期間開始月日', { exact: true })).toBeVisible();
});

test('IT-SCR002-NAV-001 給与簿から支給明細へ進み同じ職員に戻る', async ({ page }) => {
  const screen = await openScreen(page);
  await screen.getByRole('button', { name: /009900000011 .*詳細を表示/ }).click();
  await screen.getByRole('button', { name: '給与簿', exact: true }).click();
  await screen.getByRole('button', { name: '支給明細画面' }).click();
  await expect(screen.getByText(/009900000011\s+試験\s+同姓同名/)).toBeVisible();
  await screen.getByRole('button', { name: '職員マスタ検索' }).click();
  await expect(screen.getByText(/職員番号：009900000011/)).toBeVisible();
});

test('IT-SCR002-HOME-001 ヘッダーのホームからSCR-001に戻る', async ({ page }) => {
  const screen = await openScreen(page);
  await screen.getByRole('button', { name: 'ホーム', exact: true }).click();
  await expect(screen.getByText('SCR-001', { exact: true })).toBeVisible();
  await expect(screen.getByRole('button', { name: '職員マスタ検索' })).toBeVisible();
});
