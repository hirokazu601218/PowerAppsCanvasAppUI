import { expect, test } from '@playwright/test';
import {
  clickCanvasButton,
  fillCanvasInput,
} from 'power-platform-playwright-toolkit';

const TEST_VALUE = 'ChatGPT自動テスト成功';
const CANVAS_FRAME = 'iframe[name="fullscreen-app-host"]';

const SELECTORS = {
  screen: '[data-control-name="Screen1"]',
  input: '[data-control-name="TextInput1"] input',
  button: '[data-control-name="Button1"]',
  result: '[data-control-name="Text1"]',
};

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
    await canvas.locator(SELECTORS.screen).waitFor({
      state: 'visible',
      timeout: 60_000,
    });

    const input = canvas.locator(SELECTORS.input);
    await input.waitFor({ state: 'visible', timeout: 30_000 });
    await fillCanvasInput(page, input, TEST_VALUE);

    const button = canvas.locator(SELECTORS.button);
    await button.waitFor({ state: 'visible', timeout: 30_000 });
    await clickCanvasButton(button);

    await expect(canvas.locator(SELECTORS.result)).toContainText(
      `入力結果：${TEST_VALUE}`,
      { timeout: 30_000 },
    );

    await page.screenshot({
      path: 'test-results/testapp-smoke-success.png',
      fullPage: true,
    });
  });
});
