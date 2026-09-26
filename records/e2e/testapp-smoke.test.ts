import { expect, test } from '@playwright/test';

const TEST_VALUE = 'ChatGPT自動テスト成功';
const CANVAS_FRAME = 'iframe[name="fullscreen-app-host"]';

test.describe('TestApp smoke test', () => {
  test('input, execute, and result display work end-to-end', async ({ page }) => {
    const appUrl = process.env.CANVAS_APP_URL;
    if (!appUrl) {
      throw new Error('CANVAS_APP_URL is required');
    }

    await page.goto(appUrl, {
      waitUntil: 'domcontentloaded',
      timeout: 60_000,
    });

    const canvas = page.frameLocator(CANVAS_FRAME);
    await canvas.getByText('TestApp公開', { exact: true }).waitFor({
      state: 'visible',
      timeout: 60_000,
    });

    const input = canvas.getByPlaceholder('テキストを入力してください', {
      exact: true,
    });
    await input.waitFor({ state: 'visible', timeout: 30_000 });
    await input.fill(TEST_VALUE, { timeout: 30_000 });

    const button = canvas.getByRole('button', { name: '実行', exact: true });
    await button.waitFor({ state: 'visible', timeout: 30_000 });
    await button.click({ force: true, timeout: 30_000 });

    await expect(
      canvas.getByText(`入力結果：${TEST_VALUE}`, { exact: true }),
    ).toBeVisible({ timeout: 30_000 });

    await page.screenshot({
      path: 'test-results/testapp-smoke-success.png',
      fullPage: true,
    });
  });
});
