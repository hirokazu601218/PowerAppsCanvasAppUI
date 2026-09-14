import { expect, test } from '@playwright/test';

const CANVAS_FRAME = 'iframe[name="fullscreen-app-host"]';

test.describe('職員マスタ検索 v1.11 P0', () => {
  test('初期表示、氏名検索、条件クリアが動作する', async ({ page }) => {
    const appUrl = process.env.CANVAS_APP_URL;
    if (!appUrl) {
      throw new Error('CANVAS_APP_URL is required');
    }

    await page.goto(appUrl, {
      waitUntil: 'domcontentloaded',
      timeout: 60_000,
    });

    const canvas = page.frameLocator(CANVAS_FRAME);
    await canvas.getByText(/職員マスタ|職員検索/).first().waitFor({
      state: 'visible',
      timeout: 60_000,
    });

    // INIT-01: 初期表示は25名で、先頭の山田 太郎が表示される。
    await expect(canvas.getByText(/25\s*名/).first()).toBeVisible({
      timeout: 30_000,
    });
    await expect(canvas.getByText('山田 太郎', { exact: true }).first()).toBeVisible({
      timeout: 30_000,
    });

    // SRCH-02: 氏名「山田」で検索すると山田姓の2名に絞られる。
    const keywordInput = canvas.locator('input[type="text"]:visible').first();
    await keywordInput.waitFor({ state: 'visible', timeout: 30_000 });
    await keywordInput.fill('山田');

    const searchButton = canvas.getByRole('button', { name: '検索', exact: true });
    await searchButton.waitFor({ state: 'visible', timeout: 30_000 });
    await searchButton.click({ force: true });

    await expect(canvas.getByText(/2\s*名/).first()).toBeVisible({
      timeout: 30_000,
    });
    await expect(canvas.getByText('山田 太郎', { exact: true }).first()).toBeVisible();
    await expect(canvas.getByText('山田 花子', { exact: true }).first()).toBeVisible();

    // ZERO-03: 条件クリアで25名表示へ戻る。
    const clearButton = canvas.getByRole('button', { name: /クリア/ }).first();
    await clearButton.waitFor({ state: 'visible', timeout: 30_000 });
    await clearButton.click({ force: true });
    await expect(canvas.getByText(/25\s*名/).first()).toBeVisible({
      timeout: 30_000,
    });

    await page.screenshot({
      path: 'test-results/staff-master-p0-success.png',
      fullPage: true,
    });
  });
});
