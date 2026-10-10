import { expect, test, type FrameLocator, type Page } from '@playwright/test';

const ENV = '68e00049-b7e5-eda6-9888-9a3cc493c5be';
const APP = '204a48dc-7f23-43dd-b934-4654a3cfa306';
const STAFF = '009900000011'; // Existing isolated synthetic fixture, never a real employee.
const control = (app: FrameLocator, name: string) => app.locator(`[data-control-name="${name}"]`);
test.describe.configure({ retries: 0 });
test.use({ video: 'off', screenshot: 'off', trace: 'off' });

async function open(page: Page): Promise<FrameLocator> {
  const configured = process.env.CANVAS_APP_URL;
  if (!configured) throw new Error('CANVAS_APP_URL is required');
  const url = new URL(configured);
  if (url.protocol !== 'https:' || url.hostname !== 'apps.powerapps.com' ||
      url.pathname !== `/play/e/${ENV}/a/${APP}`) throw new Error('Unexpected trial environment or App ID');
  await page.setViewportSize({ width: 1366, height: 768 });
  await page.goto(url.toString(), { waitUntil: 'domcontentloaded', timeout: 60_000 });
  const app = page.frameLocator('iframe[name="fullscreen-app-host"]');
  const home = app.getByRole('button', { name: '職員マスタ検索', exact: true });
  const deadline = Date.now() + 60_000;
  while (Date.now() < deadline) {
    for (const frame of page.frames().filter(f => /\/consent\//.test(f.url()) || /consent/i.test(f.name()))) {
      if (await frame.getByRole('button', { name: /^(Allow|許可)$/ }).isVisible().catch(() => false)) {
        throw new Error('BLOCKED: unexpected connection consent requires owner approval');
      }
    }
    if (await home.isVisible().catch(() => false)) break;
    await page.waitForTimeout(250);
  }
  await expect(home).toBeVisible();
  await home.click();
  await expect(app.getByRole('searchbox', { name: '氏名・職員番号・項目を検索' })).toBeVisible({ timeout: 60_000 });
  return app;
}

async function search(app: FrameLocator, text: string) {
  await app.getByRole('searchbox', { name: '氏名・職員番号・項目を検索' }).fill(text);
  await app.getByRole('button', { name: '検索', exact: true }).click();
}
async function selectStaff(app: FrameLocator) {
  await search(app, STAFF);
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*1件/);
  await expect(control(app, 'lblPersonSub111')).toContainText(`職員番号：${STAFF}`);
}
async function payroll(app: FrameLocator) {
  await selectStaff(app);
  await app.getByRole('button', { name: '支給明細画面', exact: true }).click();
  await expect(control(app, 'lblPayrollStaff')).toContainText(STAFF);
}
async function month(app: FrameLocator, value: string) {
  await control(app, 'ddPayrollMonth').click();
  // Canvas classic dropdown exposes flyout values as text, not reliably role=option.
  const choice = app.getByText(value, { exact: true }).last();
  await expect(choice).toBeVisible();
  await choice.click();
}
async function allBasis(app: FrameLocator, pattern: string | RegExp) {
  for (let i = 0; i < 8; i++) await expect(control(app, `lblPayDeductionBasis${i}`)).toHaveText(pattern);
}

async function waitForPayrollGeometry(app: FrameLocator) {
  let previous = ''; let stable = 0;
  await expect.poll(async () => {
    const snapshot = await control(app, 'conscrPayrollRoot').evaluate(root =>
      ['conPaySummary', 'conPayBody', 'conPayDeductions', 'conPayDeduction7'].map(name => {
        const el = root.querySelector(`[data-control-name="${name}"]`) as HTMLElement | null;
        if (!el) return null;
        const rect = el.getBoundingClientRect();
        return [name, rect.x, rect.y, rect.width, rect.height, el.scrollHeight];
      }));
    const signature = JSON.stringify(snapshot);
    stable = snapshot.every(Boolean) && signature === previous ? stable + 1 : 0;
    previous = signature;
    return stable;
  }, { timeout: 10_000, intervals: [100, 150, 250] }).toBeGreaterThanOrEqual(2);
}

// Only move the actual user-scrollable body. scrollIntoView can move overflow:hidden
// ancestors and conceal the very container clipping this regression must detect.
async function scrollPayrollBodyToEnd(app: FrameLocator) {
  const result = await control(app, 'conPayBody').evaluate(body => {
    const candidates = [body, ...Array.from(body.querySelectorAll('*'))] as HTMLElement[];
    const scroller = candidates.find(el =>
      el.closest('[data-control-name]') === body &&
      ['auto', 'scroll'].includes(getComputedStyle(el).overflowY) &&
      el.scrollHeight > el.clientHeight + 1);
    if (!scroller) return null;
    scroller.scrollTop = scroller.scrollHeight;
    return { clientHeight: scroller.clientHeight, scrollHeight: scroller.scrollHeight,
      scrollTop: scroller.scrollTop };
  });
  expect(result, 'a user-scrollable body exists').not.toBeNull();
  expect(Math.abs(result!.scrollTop - (result!.scrollHeight - result!.clientHeight))).toBeLessThanOrEqual(1);
}

async function assertLastDeductionReachable(app: FrameLocator) {
  await scrollPayrollBodyToEnd(app);
  for (const name of ['lblPayDeductionName7', 'lblPayDeductionBasis7', 'lblPayDeductionAmount7']) {
    const label = control(app, name);
    await expect(label).toBeInViewport({ ratio: 0.99 });
    const geometry = await label.evaluate(el => {
      const rect = el.getBoundingClientRect();
      const clippingViolations: string[] = [];
      const check = (box: DOMRect, start: HTMLElement | null, kind: string) => {
        for (let ancestor = start; ancestor; ancestor = ancestor.parentElement) {
          const style = getComputedStyle(ancestor);
          const bounds = ancestor.getBoundingClientRect();
          const scaleX = ancestor.offsetWidth ? bounds.width / ancestor.offsetWidth : 1;
          const scaleY = ancestor.offsetHeight ? bounds.height / ancestor.offsetHeight : 1;
          const left = bounds.left + ancestor.clientLeft * scaleX;
          const top = bounds.top + ancestor.clientTop * scaleY;
          const right = left + ancestor.clientWidth * scaleX;
          const bottom = top + ancestor.clientHeight * scaleY;
          const owner = ancestor.getAttribute('data-control-name') || ancestor.tagName;
          if (['auto', 'scroll', 'hidden', 'clip'].includes(style.overflowY) &&
              (box.top < top - 1 || box.bottom > bottom + 1)) clippingViolations.push(`${kind}:${owner}:vertical`);
          if (['auto', 'scroll', 'hidden', 'clip'].includes(style.overflowX) &&
              (box.left < left - 1 || box.right > right + 1)) clippingViolations.push(`${kind}:${owner}:horizontal`);
        }
      };
      check(rect, el.parentElement, 'field');
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      let textRects = 0;
      while (walker.nextNode()) {
        const node = walker.currentNode; const parent = node.parentElement;
        if (!node.textContent?.trim() || !parent) continue;
        const style = getComputedStyle(parent);
        if (style.display === 'none' || style.visibility === 'hidden') continue;
        const range = document.createRange(); range.selectNodeContents(node);
        for (const textRect of Array.from(range.getClientRects())) {
          if (textRect.width <= 0 || textRect.height <= 0) continue;
          textRects += 1; check(textRect, parent, 'text');
        }
      }
      return { clippingViolations, textRects, height: rect.height, width: rect.width };
    });
    expect(geometry.height).toBeGreaterThan(0); expect(geometry.width).toBeGreaterThan(0);
    expect(geometry.textRects, `${name} has rendered text to inspect`).toBeGreaterThan(0);
    expect(geometry.clippingViolations, `${name} must not be clipped by any ancestor`).toEqual([]);
  }
}

test('UT-STATE-SEARCH-001 検索確定値と0件クリアを区別する', async ({ page }) => {
  const app = await open(page);
  await selectStaff(app);
  await app.getByRole('searchbox', { name: '氏名・職員番号・項目を検索' }).fill('未確定の入力');
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*1件/);
  await expect(control(app, 'lblPersonSub111')).toContainText(STAFF);
  await search(app, '999999999999');
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*0件/);
  await expect(control(app, 'lblPersonSub111')).not.toContainText(STAFF);
  await expect(app.getByRole('button', { name: '支給明細画面', exact: true })).toBeDisabled();
  await app.getByRole('button', { name: 'クリア', exact: true }).click();
  await expect(app.getByRole('searchbox', { name: '氏名・職員番号・項目を検索' })).toHaveValue('');
  await expect(control(app, 'lblListTitle111')).not.toHaveText(/職員一覧\s*0件/);
});

test('IT-STATE-RETURN-001 支給明細往復で確定検索結果と未確定入力を混同しない', async ({ page }) => {
  const app = await open(page);
  await selectStaff(app);
  const keyword = app.getByRole('searchbox', { name: '氏名・職員番号・項目を検索' });
  await keyword.fill('未確定の入力');
  for (let i = 0; i < 2; i++) {
    await app.getByRole('button', { name: '支給明細画面', exact: true }).click();
    await expect(control(app, 'lblPayrollStaff')).toContainText(STAFF);
    await app.getByRole('button', { name: '職員マスタ検索', exact: true }).click();
    await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*1件/);
    await expect(control(app, 'lblPersonSub111')).toContainText(STAFF);
    await expect(keyword).toHaveValue('未確定の入力');
  }
  await search(app, '999999999999');
  await app.getByRole('button', { name: 'ホーム', exact: true }).click();
  await app.getByRole('button', { name: '職員マスタ検索', exact: true }).click();
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*0件/);
  await expect(control(app, 'lblPersonSub111')).not.toContainText(STAFF);
});

test('UT-STATE-HISTORY-001 複数履歴の2行目を選び本人の税固定控除を表示する', async ({ page }) => {
  const app = await open(page); await selectStaff(app);
  await app.getByRole('button', { name: '税固定控除', exact: true }).click();
  await expect(control(app, 'galHistory111').getByText(/履歴 登録済/)).toBeVisible();
  await control(app, 'galHistory111').getByText(/履歴 過去 2026\/09\/01/).click();
  await expect(control(app, 'galDetailFields111')).toContainText('税表区分');
  await expect(control(app, 'galDetailFields111')).toContainText('架空試験-税表区分');
  await expect(control(app, 'galDetailFields111')).not.toContainText('納付先自治体');
});

test('IT-STATE-HISTORY-TABS-001 区分別に選んだ履歴をタブと画面往復で保持する', async ({ page }) => {
  const app = await open(page); await selectStaff(app);
  await app.getByRole('button', { name: '税固定控除', exact: true }).click();
  await control(app, 'galHistory111').getByText(/履歴 過去 2026\/09\/01/).click();
  for (const tab of ['基本情報', '勤務条件', '社会保険']) {
    await app.getByRole('button', { name: tab, exact: true }).click();
    await app.getByRole('button', { name: '税固定控除', exact: true }).click();
    await expect(control(app, 'galDetailFields111')).toContainText('架空試験-税表区分');
    await expect(control(app, 'galDetailFields111')).not.toContainText('納付先自治体');
  }
  await app.getByRole('button', { name: '支給明細画面', exact: true }).click();
  await app.getByRole('button', { name: '職員マスタ検索', exact: true }).click();
  await expect(control(app, 'galDetailFields111')).toContainText('架空試験-税表区分');
});

test('UT-STATE-HISTORY-EMPTY-001 職員切替と0件で前職員の履歴を残さない', async ({ page }) => {
  const app = await open(page); await selectStaff(app);
  await app.getByRole('button', { name: '税固定控除', exact: true }).click();
  await control(app, 'galHistory111').getByText(/履歴 過去 2026\/09\/01/).click();
  await search(app, '009900000004');
  await app.getByRole('button', { name: '勤務条件', exact: true }).click();
  await expect(app.getByText('登録されている履歴はありません')).toBeVisible();
  await expect(control(app, 'galDetailFields111')).toBeHidden();
  await search(app, '999999999999');
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*0件/);
  await expect(control(app, 'galHistory111')).toBeHidden();
  await expect(control(app, 'galDetailFields111')).toBeHidden();
  await selectStaff(app);
  await app.getByRole('button', { name: '税固定控除', exact: true }).click();
  await expect(control(app, 'galDetailFields111')).toContainText('納付先自治体');
  await expect(control(app, 'galDetailFields111')).not.toContainText('架空試験-税表区分');
});

test('UT-STATE-PAYROLL-001 未登録と再計算前は8根拠を失効し登録済み0円を区別する', async ({ page }) => {
  const app = await open(page); await payroll(app);
  await month(app, '2026/09');
  await app.getByRole('button', { name: '再計算', exact: true }).click();
  await expect(control(app, 'lblPaySummaryNetValue')).toHaveText('151,800 円');
  await expect(control(app, 'lblPayDeductionBasis5')).toContainText('165,550');
  await month(app, '2026/10');
  await allBasis(app, '算定根拠　—');
  await expect(control(app, 'lblPaySummaryNetValue')).toHaveText('—');
  await expect(control(app, 'lblPayState')).toHaveText('勤務時間報告が未登録です');
  await month(app, '2026/09');
  await allBasis(app, '算定根拠　—');
  await expect(control(app, 'lblPayState')).toContainText('再計算してください');
  await app.getByRole('button', { name: '再計算', exact: true }).click();
  await expect(control(app, 'lblPayDeductionBasis5')).toContainText('165,550');
  await month(app, '2026/11');
  await allBasis(app, '算定根拠　—');
  await app.getByRole('button', { name: '再計算', exact: true }).click();
  await allBasis(app, '登録済み0円（仮例）');
  await expect(control(app, 'lblPaySummaryNetValue')).toHaveText('0 円');
});

test('UT-STATE-SUMMARY-001 最後の貯金預入までスクロールしてもサマリーを固定する', async ({ page }) => {
  const app = await open(page); await payroll(app);
  await waitForPayrollGeometry(app);
  const summary = control(app, 'conPaySummary');
  const targets = control(app, 'conPayrollTargets');
  await expect(summary).toBeInViewport({ ratio: 0.99 });
  const before = await summary.boundingBox();
  const targetBefore = await targets.boundingBox();
  expect(before).not.toBeNull(); expect(targetBefore).not.toBeNull();
  await assertLastDeductionReachable(app);
  await expect(summary).toBeInViewport({ ratio: 0.99 });
  const after = await summary.boundingBox(); const targetAfter = await targets.boundingBox();
  expect(after).not.toBeNull(); expect(targetAfter).not.toBeNull();
  expect(Math.abs(after!.y - before!.y)).toBeLessThanOrEqual(1);
  expect(Math.abs(targetAfter!.y - targetBefore!.y)).toBeLessThanOrEqual(1);
  expect(after!.y).toBeGreaterThanOrEqual(targetAfter!.y + targetAfter!.height - 1);
  expect(await control(app, 'conPayBody').boundingBox()).not.toBeNull();
});


test('IT-STATE-PAGE-001 内蔵40件の2ページ目と職員選択を往復後も保持する', async ({ page }) => {
  const app = await open(page);
  await app.getByRole('button', { name: 'ホーム', exact: true }).click();
  const demoAdmin = app.getByRole('button', { name: '一般 → 管理者に切替', exact: true });
  if (await demoAdmin.isVisible()) await demoAdmin.click(); // Existing in-memory demo switch, not a Dataverse role.
  await app.getByRole('button', { name: 'メンテナンス', exact: true }).click();
  await control(app, 'ddUiFixture124').click();
  await app.getByText('40件', { exact: true }).last().click();
  await app.getByRole('button', { name: 'ホーム', exact: true }).click();
  await app.getByRole('button', { name: '職員マスタ検索', exact: true }).click();
  await search(app, '008800000');
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*40件/);
  await app.getByRole('button', { name: '次へ', exact: true }).click();
  await expect(control(app, 'lblPage111')).toHaveText('2 / 2');
  await app.getByRole('button', { name: /008800000021 .*詳細を表示/ }).click();
  await expect(control(app, 'lblPersonSub111')).toContainText('008800000021');
  await app.getByRole('button', { name: '支給明細画面', exact: true }).click();
  await app.getByRole('button', { name: '職員マスタ検索', exact: true }).click();
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*40件/);
  await expect(control(app, 'lblPage111')).toHaveText('2 / 2');
  await expect(control(app, 'lblPersonSub111')).toContainText('008800000021');
  await expect(app.getByRole('button', { name: /008800000021 .*詳細を表示/ })).toBeVisible();
  await search(app, '008800000040');
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*1件/);
  await expect(control(app, 'lblPage111')).toHaveText('1 / 1');
  await search(app, '999999999999');
  await expect(control(app, 'lblListTitle111')).toHaveText(/職員一覧\s*0件/);
  await expect(control(app, 'lblPage111')).toHaveText('1 / 1');
  // A fresh Player discards the in-memory display fixture. This is not a
  // Dataverse 40-row performance/delegation test and creates no data rows.
  const fresh = await open(page);
  await expect(control(fresh, 'lblListTitle111')).toHaveText(/職員一覧\s*7件/, { timeout: 30_000 });
  await expect(fresh.getByRole('searchbox', { name: '氏名・職員番号・項目を検索' })).toHaveValue('');
  await expect(fresh.getByRole('button', { name: /009900000004 .*詳細を表示/ })).toBeVisible();
  await expect(fresh.getByRole('button', { name: /008800000021 .*詳細を表示/ })).toHaveCount(0);
});

test('UT-STATE-SUMMARY-NARROW-001 幅900高さ600でも固定領域と末尾到達を両立する', async ({ page }) => {
  const app = await open(page); await payroll(app);
  await page.setViewportSize({ width: 900, height: 600 });
  await waitForPayrollGeometry(app);
  const summary = control(app, 'conPaySummary');
  await expect(summary).toBeInViewport({ ratio: 0.99 });
  const before = await summary.boundingBox(); expect(before).not.toBeNull();
  await assertLastDeductionReachable(app);
  await expect(summary).toBeInViewport({ ratio: 0.99 });
  const after = await summary.boundingBox(); expect(after).not.toBeNull();
  expect(Math.abs(after!.y - before!.y)).toBeLessThanOrEqual(1);
  const body = await control(app, 'conPayBody').boundingBox(); expect(body).not.toBeNull();
  expect(body!.height).toBeGreaterThan(0);
  expect(body!.y).toBeGreaterThanOrEqual(after!.y + after!.height - 1);
});


test('UT-STATE-SUMMARY-WIDE-001 幅1920でも本文末尾全体と固定サマリーを確認する', async ({ page }) => {
  const app = await open(page); await payroll(app);
  await page.setViewportSize({ width: 1920, height: 1080 });
  await waitForPayrollGeometry(app);
  const summary = control(app, 'conPaySummary');
  await expect(summary).toBeInViewport({ ratio: 0.99 });
  const before = await summary.boundingBox();
  expect(before).not.toBeNull(); await assertLastDeductionReachable(app);
  await expect(summary).toBeInViewport({ ratio: 0.99 });
  const after = await summary.boundingBox(); expect(after).not.toBeNull();
  expect(Math.abs(after!.y - before!.y)).toBeLessThanOrEqual(1);
});

test('UT-STATE-SUMMARY-REFLOW-001 200%相当のCSS幅境界を検査する（実ズームは別観測）', async ({ page }) => {
  const app = await open(page); await payroll(app);
  // Horizontal reflow stress only: keeping height768 is NOT a browser 200% zoom test.
  for (const width of [450, 683, 960]) {
    await page.setViewportSize({ width, height: 768 });
    await waitForPayrollGeometry(app);
    const summary = control(app, 'conPaySummary');
    await expect(summary).toBeInViewport({ ratio: 0.99 });
    const before = await summary.boundingBox();
    expect(before).not.toBeNull(); await assertLastDeductionReachable(app);
    await expect(summary).toBeInViewport({ ratio: 0.99 });
    const after = await summary.boundingBox(); expect(after).not.toBeNull();
    expect(Math.abs(after!.y - before!.y)).toBeLessThanOrEqual(1);
  }
});
