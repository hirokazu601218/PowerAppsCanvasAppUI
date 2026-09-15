import { expect, test } from '@playwright/test';

test('AUT-META-001 approved header value is displayed', async ({ page }) => {
  const expected = process.env.EXPECTED_LABEL;
  if (!expected || !process.env.CANVAS_APP_URL) throw new Error('Missing acceptance target');
  await page.setViewportSize({ width: 1366, height: 768 });
  await page.goto(process.env.CANVAS_APP_URL, { waitUntil: 'domcontentloaded', timeout: 60_000 });
  const canvas = page.frameLocator('iframe[name="fullscreen-app-host"]');
  await expect(canvas.getByText('非常勤職員マスタ検索', { exact: true })).toBeVisible({ timeout: 60_000 });
  const header = canvas.getByText(expected, { exact: true });
  // A short assertion for a static label; browser retries are disabled by the runner.
  await expect(header, 'AUT-META-001: approved header value').toBeVisible({ timeout: 5_000 });
  await page.screenshot({ path: `${process.env.OUTPUT_DIRECTORY}/approved-label.png`, fullPage: true });
});
