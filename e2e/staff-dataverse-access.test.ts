import { expect, test } from '@playwright/test';

test.describe.configure({ retries: 0 });
test.use({ video: 'off', ignoreHTTPSErrors: false });

test('Dataverse v1.15 dedicated-user read access and search regression', async ({ page }) => {
  test.setTimeout(180000);
  const url = process.env.CANVAS_APP_URL;
  if (!url || !url.includes('/a/362ac991-eead-4f07-8373-afdb3ebfdba1')) throw new Error('Unexpected target');
  await page.setViewportSize({ width: 1366, height: 768 });
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  const app = page.frameLocator('iframe[name="fullscreen-app-host"]');
  try {
    await expect(app.getByText('v1.15 ／ Dataverse・25名', { exact: true })).toBeVisible({ timeout: 60000 });
    await expect(app.getByText('職員一覧 25件', { exact: true })).toBeVisible();
    await expect(app.getByRole('button', { name: '009900000001 試験 採用予定 詳細を表示', exact: true })).toBeVisible();
    console.log('DATAVERSE_DEDICATED_USER_ACCESS_PASSED');
    await app.getByRole('button', { name: '次へ', exact: true }).click();
    await expect(app.getByText('2 / 2', { exact: true })).toBeVisible();
    await expect(app.getByRole('button', { name: '次へ', exact: true })).toBeDisabled();
    await expect(app.getByRole('button', { name: /^009900000025 .* 詳細を表示$/ })).toBeVisible();
    await app.getByRole('searchbox', { name: '氏名・職員番号・項目を検索', exact: true }).fill('同姓同名');
    await app.getByRole('button', { name: '検索', exact: true }).click();
    await expect(app.getByText('職員一覧 2件', { exact: true })).toBeVisible();
    for (const id of ['009900000011','009900000012']) {
      await expect(app.getByRole('button', { name: new RegExp('^'+id+' .* 詳細を表示$') })).toBeVisible();
    }
    await app.getByRole('button', { name: /^009900000012 .* 詳細を表示$/ }).click();
    await expect(app.getByText('職員番号：009900000012　／　所属：01秘書課', { exact: true })).toBeVisible();
    await app.getByRole('button', { name: 'Dataverseの最新データを読み込む', exact: true }).click();
    await expect(app.getByText('職員一覧 25件', { exact: true })).toBeVisible();
    await expect(app.getByText('1 / 2', { exact: true })).toBeVisible();
    await app.getByRole('searchbox', { name: '氏名・職員番号・項目を検索', exact: true }).fill('該当しない試験文字列');
    await app.getByRole('button', { name: '検索', exact: true }).click();
    await expect(app.getByText('職員一覧 0件', { exact: true })).toBeVisible();
    await expect(app.getByText('左の職員一覧から職員を選択してください。', { exact: true })).toBeVisible();
    await app.getByRole('button', { name: '検索条件をクリア', exact: true }).click();
    await expect(app.getByText('職員一覧 25件', { exact: true })).toBeVisible();
    console.log('DATAVERSE_SEARCH_REGRESSION_PASSED');
  } finally {
    // Visible synthetic application text only. No cookies, tokens, network or storage state.
    console.log('VISIBLE_PLAYER_TEXT', (await page.locator('body').innerText()).slice(0,16000));
    const rendered = await app.locator('body').innerText({ timeout: 5000 }).catch(() => 'APP_FRAME_UNAVAILABLE');
    console.log('VISIBLE_APP_TEXT', rendered.slice(0,14000));
    await page.screenshot({ path: 'test-results/dataverse-access.png', fullPage: true });
  }
});
