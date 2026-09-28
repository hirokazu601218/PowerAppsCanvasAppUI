import { expect, test, type FrameLocator, type Page } from '@playwright/test';
const LABELS: Record<string, string[]> = {
  "work": [
    "職員番号",
    "氏名",
    "適用開始日",
    "適用終了日",
    "異動区分",
    "発令事由区分",
    "日額単価",
    "勤務時間開始",
    "勤務時間終了",
    "１日あたりの勤務時間",
    "超勤基礎単価（参考）",
    "支出科目名",
    "辞令案",
    "辞令コメント",
    "その他備考"
  ],
  "social": [
    "職員番号",
    "氏名",
    "職員雇用区分",
    "生年月日",
    "4/1時点年齢",
    "3/1時点年齢",
    "介護徴収該当",
    "厚生年金免除該当",
    "後期高齢者徴収該当",
    "厚生徴収開始月",
    "厚生徴収終了月日",
    "厚生_級",
    "厚生月額",
    "二以上_該当",
    "二以上_通知額_厚生年金保険",
    "企業年金_該当",
    "企業年金通知額",
    "短期徴収開始月日",
    "短期徴収終了月日",
    "長期徴収開始月",
    "長期徴収終了月日",
    "等級改定日",
    "短期_級",
    "短期月額",
    "長期_級",
    "長期月額"
  ],
  "tax": [
    "職員番号",
    "氏名",
    "適用開始日",
    "適用終了日",
    "税表区分",
    "扶養控除対象人数",
    "雇用保険加入区分",
    "共済貯金月額",
    "共済貸付月額"
  ],
  "resident": [
    "職員番号",
    "氏名",
    "期間区分",
    "住民税月額",
    "自治体コード",
    "納付先自治体"
  ]
};

const ENV = '68e00049-b7e5-eda6-9888-9a3cc493c5be';
const APP = '204a48dc-7f23-43dd-b934-4654a3cfa306';
const STAFF = process.env.SCR002_HISTORY_FIXTURE_STAFF;

async function open(page: Page): Promise<FrameLocator> {
  const configured = process.env.CANVAS_APP_URL;
  if (!configured) throw new Error('CANVAS_APP_URL is required');
  const url = new URL(configured);
  if (url.protocol !== 'https:' || url.hostname !== 'apps.powerapps.com' ||
      url.pathname !== `/play/e/${ENV}/a/${APP}`) throw new Error('Unexpected App ID');
  await page.setViewportSize({ width: 1366, height: 768 });
  await page.goto(url.toString(), { waitUntil: 'domcontentloaded', timeout: 60_000 });
  const screen = page.frameLocator('iframe[name="fullscreen-app-host"]');
  await screen.getByRole('button', { name: '職員マスタ検索', exact: true }).click();
  await expect(screen.getByRole('searchbox', { name: '氏名・職員番号・項目を検索' }))
    .toBeVisible({ timeout: 60_000 });
  return screen;
}

async function selectFixture(screen: FrameLocator) {
  if (!STAFF || !/^[0-9]{12}$/.test(STAFF)) throw new Error('12-digit isolated fixture staff required');
  await screen.getByRole('button', { name: new RegExp(`${STAFF} .*詳細を表示`) }).click();
  await expect(screen.getByText(`職員番号：${STAFF}`, { exact: false })).toBeVisible();
}

async function expectFields(page: Page, screen: FrameLocator, key: string) {
  const columns = LABELS[key];
  if (!columns) throw new Error(`Missing field contract: ${key}`);
  const labels = screen.getByRole('list', { name: 'Gallery' }).last();
  await expect(labels).toBeVisible();
  await expect(labels.getByText(columns[2], { exact: true })).toBeVisible({ timeout: 30_000 });
  const found = new Set<string>();
  const box = await labels.boundingBox();
  if (!box) throw new Error('Detail gallery is not visible');
  for (let attempt = 0; attempt < 10 && found.size < columns.length; attempt++) {
    for (const label of columns) {
      if (await labels.getByText(label, { exact: true }).count()) found.add(label);
    }
    if (found.size === columns.length) break;
    await page.mouse.move(box.x + Math.min(box.width - 24, 300),
      Math.min(box.y + 180, 650));
    await page.mouse.wheel(0, 420);
    await page.waitForTimeout(200);
  }
  expect([...found].sort(), `Missing visible/scrollable fields: ${columns.filter(x => !found.has(x))}`)
    .toEqual([...columns].sort());
}

test('UT-SCR002-WORK-56-001 勤務条件15列', async ({ page }) => {
  if (!STAFF) throw new Error('BLOCKED: 隔離4表の架空行とSCR002_HISTORY_FIXTURE_STAFFが必要');
  const screen = await open(page); await selectFixture(screen);
  await screen.getByRole('button', { name: '勤務条件', exact: true }).click();
  await expectFields(page, screen, 'work');
  const details = screen.getByRole('list', { name: 'Gallery' }).last();
  await expect(details.getByRole('listitem').nth(6).getByText('0', { exact: true })).toBeVisible();
  await expect(details.getByRole('listitem').nth(14).getByText('架空試験-その他備考')).toHaveCount(0);
});

test('UT-SCR002-SOCIAL-56-001 社会保険26列', async ({ page }) => {
  if (!STAFF) throw new Error('BLOCKED: 隔離4表の架空行とSCR002_HISTORY_FIXTURE_STAFFが必要');
  const screen = await open(page); await selectFixture(screen);
  await screen.getByRole('button', { name: '社会保険', exact: true }).click();
  await expectFields(page, screen, 'social');
});

test('UT-SCR002-TAX-56-001 税固定控除9列と住民税6列', async ({ page }) => {
  if (!STAFF) throw new Error('BLOCKED: 隔離4表の架空行とSCR002_HISTORY_FIXTURE_STAFFが必要');
  const screen = await open(page); await selectFixture(screen);
  await screen.getByRole('button', { name: '税固定控除', exact: true }).click();
  await screen.getByText(/履歴 過去/).click();
  await expectFields(page, screen, 'tax');
  await screen.getByText(/履歴 登録済/).click();
  await expectFields(page, screen, 'resident');
});

test('UT-SCR002-HISTORY-LOAD-001 0件へ切り替え時に前職員の履歴が残らない', async ({ page }) => {
  if (!STAFF) throw new Error('BLOCKED: 隔離4表の架空行とSCR002_HISTORY_FIXTURE_STAFFが必要');
  const screen = await open(page); await selectFixture(screen);
  await screen.getByRole('button', { name: '勤務条件', exact: true }).click();
  await expectFields(page, screen, 'work');
  await screen.getByRole('button', { name: /009900000004 .*詳細を表示/ }).click();
  await expect(screen.getByText('登録されている履歴はありません')).toBeVisible();
});

test('IT-SCR002-HISTORY-TABS-001 定義列を各タブで切り替える', async ({ page }) => {
  if (!STAFF) throw new Error('BLOCKED: 隔離4表の架空行とSCR002_HISTORY_FIXTURE_STAFFが必要');
  const screen = await open(page); await selectFixture(screen);
  for (const [tab, key] of [['勤務条件', 'work'], ['社会保険', 'social'], ['税固定控除', 'tax']]) {
    await screen.getByRole('button', { name: tab, exact: true }).click();
    if (key === 'tax') await screen.getByText(/履歴 過去/).click();
    await expectFields(page, screen, key);
  }
});

test('IT-SCR002-HISTORY-SWITCH-001 職員切替後に本人の履歴のみ表示', async ({ page }) => {
  if (!STAFF) throw new Error('BLOCKED: 隔離4表の架空行とSCR002_HISTORY_FIXTURE_STAFFが必要');
  const screen = await open(page); await selectFixture(screen);
  await screen.getByRole('button', { name: '社会保険', exact: true }).click();
  await expectFields(page, screen, 'social');
  await screen.getByRole('button', { name: /009900000004 .*詳細を表示/ }).click();
  await expect(screen.getByText('登録されている履歴はありません')).toBeVisible();
  await selectFixture(screen);
  await expectFields(page, screen, 'social');
});
