import { expect, test } from '@playwright/test';

const CANVAS_FRAME = 'iframe[name="fullscreen-app-host"]';

test.describe('ステップ7：GitHubソース自動反映', () => {
  test('隔離アプリに承認済みの一時表示が反映される', async ({ page }) => {
    await page.setViewportSize({ width: 1366, height: 768 });

    const appUrl = process.env.CANVAS_APP_URL;
    if (!appUrl) {
      throw new Error('CANVAS_APP_URL is required');
    }

    await page.goto(appUrl, {
      waitUntil: 'domcontentloaded',
      timeout: 60_000,
    });

    const canvas = page.frameLocator(CANVAS_FRAME);
    await canvas.getByText('非常勤職員マスタ検索', { exact: true }).waitFor({
      state: 'visible',
      timeout: 60_000,
    });

    const temporaryLabel = canvas.getByText(
      'v1.11 ／ 自動反映テスト中',
      { exact: true },
    );
    await expect(temporaryLabel).toBeVisible({ timeout: 30_000 });

    await page.screenshot({
      path: 'test-results/step7-temporary-label.png',
      fullPage: true,
    });
  });
});
