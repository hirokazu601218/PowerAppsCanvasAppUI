import { expect, test, type FrameLocator, type Locator, type Page } from '@playwright/test';

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
    const snapshot = await control(app, 'conscrPayrollRoot').evaluate(root => {
      const boxes = [root, ...['conPaySummary', 'conPayBody', 'conPayDeductions', 'conPayDeduction7']
        .map(name => root.querySelector(`[data-control-name="${name}"]`))].map(el => {
        if (!el) return null; // Collapsed controls may be unmounted by the Player.
        const rect = el.getBoundingClientRect(); const node = el as HTMLElement;
        return [rect.x, rect.y, rect.width, rect.height, node.scrollWidth, node.scrollHeight];
      });
      const offsets = [root, ...Array.from(root.querySelectorAll('*'))]
        .map(el => [el.scrollLeft, el.scrollTop]);
      return { boxes, offsets };
    });
    const signature = JSON.stringify(snapshot);
    stable = snapshot.boxes.slice(0, 3).every(Boolean) && signature === previous ? stable + 1 : 0;
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

async function assertControlUnclipped(label: Locator, name: string) {
  await expect(label).toBeInViewport({ ratio: 0.99 });
  const geometry = await label.evaluate(el => {
    const rect = el.getBoundingClientRect();
    const clippingViolations: string[] = [];
    const check = (box: DOMRect, start: HTMLElement | null, kind: string) => {
      if (box.left < -1 || box.right > innerWidth + 1 || box.top < -1 || box.bottom > innerHeight + 1) {
        clippingViolations.push(`${kind}:iframe-viewport`);
      }
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

async function assertLastDeductionReachable(app: FrameLocator) {
  await scrollPayrollBodyToEnd(app);
  await waitForPayrollGeometry(app);
  for (const name of ['lblPayDeductionName7', 'lblPayDeductionBasis7', 'lblPayDeductionAmount7']) {
    await assertControlUnclipped(control(app, name), name);
  }
}

// r6 is an UNAPPROVED UI EXCEPTION PROPOSAL. These two candidate tests do not
// authorize application/save/publication. CSS viewport cases cannot pass the
// separate real Chrome 200% zoom gate; that gate remains NOT_RUN.
// Pointer reachability below is NOT keyboard acceptance. Real Tab traversal of
// all five buttons/month and focus-induced clipping checks remain a NOT_RUN gate.
// Only real wheel input may pan the proposed root. No scrollIntoView, focus(),
// hover(), DOM style changes, or assignments to hidden-ancestor scroll offsets.
type RootPorts = { x: Locator; y: Locator; indexes: number[] };

async function rootPorts(app: FrameLocator): Promise<RootPorts> {
  const root = control(app, 'conscrPayrollRoot');
  const indexes = await root.evaluate(root => {
    const nodes = [root, ...Array.from(root.querySelectorAll('*'))] as HTMLElement[];
    const owned = (el: HTMLElement) => el.closest('[data-control-name]') === root &&
      ['conscrPayrollHeader', 'conPayrollTargets', 'conPaySummary', 'conPayBody']
        .every(name => el.querySelector(`[data-control-name="${name}"]`));
    return (['overflowX', 'overflowY'] as const).map(axis => {
      const eligible = nodes.map((el, index) => ({ el, index })).filter(({ el }) => owned(el) &&
        el.clientWidth > 0 && el.clientHeight > 0 && ['auto', 'scroll'].includes(getComputedStyle(el)[axis]));
      // Prefer the wrapper that really overflows, rather than an auto wrapper with no range.
      return (eligible.find(({ el }) => axis === 'overflowX' ? el.scrollWidth > el.clientWidth + 1 :
        el.scrollHeight > el.clientHeight + 1) ?? eligible[0])?.index ?? -1;
    });
  });
  expect(indexes.every(index => index >= 0),
    'proposed fallback needs root-owned, user-scrollable X and Y ports containing all four children').toBe(true);
  const nodes = root.locator('xpath=descendant-or-self::*');
  return { x: nodes.nth(indexes[0]), y: nodes.nth(indexes[1]), indexes };
}

async function scrollOffsets(app: FrameLocator) {
  return control(app, 'conscrPayrollRoot').evaluate(root => {
    const nodes = [root, ...Array.from(root.querySelectorAll('*'))];
    for (let ancestor = root.parentElement; ancestor; ancestor = ancestor.parentElement) nodes.push(ancestor);
    return nodes.map(node => [node.scrollLeft, node.scrollTop]);
  });
}

async function portGeometry(port: Locator, page: Page) {
  const box = await port.boundingBox(); expect(box).not.toBeNull();
  const local = await port.evaluate(node => {
    const el = node as HTMLElement; const rect = el.getBoundingClientRect();
    const scaleX = el.offsetWidth ? rect.width / el.offsetWidth : 1;
    const scaleY = el.offsetHeight ? rect.height / el.offsetHeight : 1;
    let left = rect.left + el.clientLeft * scaleX; let top = rect.top + el.clientTop * scaleY;
    let right = left + el.clientWidth * scaleX; let bottom = top + el.clientHeight * scaleY;
    for (let ancestor = el.parentElement; ancestor; ancestor = ancestor.parentElement) {
      const style = getComputedStyle(ancestor); const bounds = ancestor.getBoundingClientRect();
      const sx = ancestor.offsetWidth ? bounds.width / ancestor.offsetWidth : 1;
      const sy = ancestor.offsetHeight ? bounds.height / ancestor.offsetHeight : 1;
      const x = bounds.left + ancestor.clientLeft * sx; const y = bounds.top + ancestor.clientTop * sy;
      if (['auto', 'scroll', 'hidden', 'clip'].includes(style.overflowX)) {
        left = Math.max(left, x); right = Math.min(right, x + ancestor.clientWidth * sx);
      }
      if (['auto', 'scroll', 'hidden', 'clip'].includes(style.overflowY)) {
        top = Math.max(top, y); bottom = Math.min(bottom, y + ancestor.clientHeight * sy);
      }
    }
    return { left: Math.max(left, 0), top: Math.max(top, 0), right: Math.min(right, innerWidth),
      bottom: Math.min(bottom, innerHeight), rectX: rect.x, rectY: rect.y,
      rectWidth: rect.width, rectHeight: rect.height, scaleX, scaleY,
      x: el.scrollLeft, y: el.scrollTop, maxX: el.scrollWidth - el.clientWidth,
      maxY: el.scrollHeight - el.clientHeight };
  });
  // Translation below assumes no extra CSS scale on the outer iframe. Fail
  // explicitly instead of sending input to an incorrect main-page coordinate.
  // This guard is not evidence for the separate real Chrome 200% zoom gate.
  expect(Math.abs(box!.width - local.rectWidth),
    'BLOCKED: unsupported outer iframe horizontal CSS transform; local and main widths must match').toBeLessThanOrEqual(1);
  expect(Math.abs(box!.height - local.rectHeight),
    'BLOCKED: unsupported outer iframe vertical CSS transform; local and main heights must match').toBeLessThanOrEqual(1);
  // boundingBox is already in MAIN-page coordinates, including iframe offsets.
  const offsetX = box!.x - local.rectX; const offsetY = box!.y - local.rectY;
  const viewport = page.viewportSize(); expect(viewport).not.toBeNull();
  return { ...local, offsetX, offsetY,
    left: Math.max(0, local.left + offsetX), top: Math.max(0, local.top + offsetY),
    right: Math.min(viewport!.width, local.right + offsetX),
    bottom: Math.min(viewport!.height, local.bottom + offsetY) };
}

async function assertPlayerReceivesPointer(page: Page, point: { x: number; y: number }) {
  expect(await page.locator('iframe[name="fullscreen-app-host"]').evaluate((frame, point) =>
    document.elementFromPoint(point.x, point.y) === frame, point),
  'main-page pointer must hit the Player iframe, not an overlay').toBe(true);
}

async function wheelRoot(page: Page, app: FrameLocator, ports: RootPorts, axis: 'x' | 'y', delta: number) {
  const port = ports[axis]; const bounds = await portGeometry(port, page);
  const maximum = axis === 'x' ? bounds.maxX : bounds.maxY;
  const requested = Math.max(0, Math.min(maximum, bounds[axis] + delta)) - bounds[axis];
  expect(Math.abs(requested), `root ${axis} must have available user-scroll range`).toBeGreaterThan(0.5);
  expect(bounds.right - bounds.left).toBeGreaterThan(4);
  expect(bounds.bottom - bounds.top).toBeGreaterThan(4);
  let point: { x: number; y: number } | undefined;
  // Prefer the outer padding; never wheel over a nested scrollable control.
  for (const fy of [0.01, 0.5, 0.99, 0.25, 0.75]) {
    for (const fx of [0.01, 0.5, 0.99, 0.25, 0.75]) {
      const x = bounds.left + 2 + (bounds.right - bounds.left - 4) * fx;
      const y = bounds.top + 2 + (bounds.bottom - bounds.top - 4) * fy;
      const hit = await port.evaluate((node, point) => {
        const target = document.elementFromPoint(point.x, point.y);
        if (!target || !node.contains(target)) return false;
        for (let el = target; el && el !== node; el = el.parentElement!) {
          const style = getComputedStyle(el);
          if (point.axis === 'x' && ['auto', 'scroll'].includes(style.overflowX) && el.scrollWidth > el.clientWidth + 1) return false;
          if (point.axis === 'y' && ['auto', 'scroll'].includes(style.overflowY) && el.scrollHeight > el.clientHeight + 1) return false;
        }
        return true;
      }, { x: x - bounds.offsetX, y: y - bounds.offsetY, axis });
      if (hit) { point = { x, y }; break; }
    }
    if (point) break;
  }
  expect(point, `a visible wheel target routes ${axis} input only to the root`).toBeDefined();
  await assertPlayerReceivesPointer(page, point!);
  const before = await scrollOffsets(app);
  const outerBefore = await page.evaluate(() => [window.scrollX, window.scrollY]);
  await page.mouse.move(point!.x, point!.y);
  await page.mouse.wheel(axis === 'x' ? requested : 0, axis === 'y' ? requested : 0);
  await expect.poll(async () => port.evaluate((node, axis) => axis === 'x' ? node.scrollLeft : node.scrollTop, axis),
    { timeout: 5_000 }).not.toBe(bounds[axis]);
  await waitForPayrollGeometry(app);
  const after = await scrollOffsets(app);
  expect(after.length, 'wheel input must not replace controls').toBe(before.length);
  after.forEach((offset, index) => {
    if (!ports.indexes.includes(index)) expect(offset, `non-root scroll offset ${index} must not move`).toEqual(before[index]);
  });
  expect(await page.evaluate(() => [window.scrollX, window.scrollY]), 'outer Player must not scroll').toEqual(outerBefore);
  const settled = await portGeometry(port, page);
  expect((settled[axis] - bounds[axis]) * Math.sign(requested), 'root moved in requested direction').toBeGreaterThan(0.5);
}

async function reachByRoot(page: Page, app: FrameLocator, ports: RootPorts, name: string) {
  const target = control(app, name);
  await expect(target).toBeVisible();
  for (let attempt = 0; attempt < 8; attempt++) {
    const box = await target.boundingBox(); expect(box).not.toBeNull();
    const x = await portGeometry(ports.x, page); const y = await portGeometry(ports.y, page);
    expect(box!.width, `${name} must fit at some horizontal pan position`).toBeLessThanOrEqual(x.right - x.left + 1);
    expect(box!.height, `${name} must fit at some vertical pan position`).toBeLessThanOrEqual(y.bottom - y.top + 1);
    const dx = box!.x < x.left - 1 ? box!.x - x.left :
      box!.x + box!.width > x.right + 1 ? box!.x + box!.width - x.right : 0;
    const dy = box!.y < y.top - 1 ? box!.y - y.top :
      box!.y + box!.height > y.bottom + 1 ? box!.y + box!.height - y.bottom : 0;
    if (Math.abs(dx) <= 1 && Math.abs(dy) <= 1) {
      await assertControlUnclipped(target, name);
      return target;
    }
    if (Math.abs(dx) > 1) await wheelRoot(page, app, ports, 'x', dx / x.scaleX);
    if (Math.abs(dy) > 1) await wheelRoot(page, app, ports, 'y', dy / y.scaleY);
  }
  throw new Error(`${name} remained clipped after root-only wheel navigation`);
}

async function pointerPoint(page: Page, target: Locator) {
  const box = await target.boundingBox(); expect(box).not.toBeNull();
  const point = { x: box!.x + box!.width / 2, y: box!.y + box!.height / 2 };
  const viewport = page.viewportSize(); expect(viewport).not.toBeNull();
  expect(point.x).toBeGreaterThan(0); expect(point.x).toBeLessThan(viewport!.width);
  expect(point.y).toBeGreaterThan(0); expect(point.y).toBeLessThan(viewport!.height);
  expect(await target.evaluate(el => {
    const rect = el.getBoundingClientRect();
    const hit = document.elementFromPoint(rect.x + rect.width / 2, rect.y + rect.height / 2);
    return !!hit && el.contains(hit);
  }), 'target receives pointer events, without implicit scrolling').toBe(true);
  await assertPlayerReceivesPointer(page, point);
  await page.mouse.move(point.x, point.y);
  return point;
}

// Only these three buttons change the in-memory display. Never click a save,
// data-write, export, or unlisted control in the proposed fallback tests.
async function clickDisplayAction(page: Page, app: FrameLocator, ports: RootPorts,
  name: 'btnPayEarnings' | 'btnPayDeductions' | 'btnPayRecalculate') {
  const target = await reachByRoot(page, app, ports, name);
  await expect(target.getByRole('button')).toBeEnabled();
  const point = await pointerPoint(page, target);
  await page.mouse.click(point.x, point.y);
  await waitForPayrollGeometry(app);
}

async function selectMonthByRoot(page: Page, app: FrameLocator, ports: RootPorts, value: string) {
  const dropdown = await reachByRoot(page, app, ports, 'ddPayrollMonth');
  const point = await pointerPoint(page, dropdown);
  await page.mouse.click(point.x, point.y);
  const choice = app.getByText(value, { exact: true }).last();
  await assertControlUnclipped(choice, `month option ${value}`);
  const choicePoint = await pointerPoint(page, choice);
  await page.mouse.click(choicePoint.x, choicePoint.y);
  await waitForPayrollGeometry(app);
}

// Independent display fixture expectations; these are mock values, not validated payroll policy.
const deductionFixture = [
  ['共済短期掛金', '短期・月額 200,000円 × 仮率4.50%', '9,000 円'],
  ['子ども・子育て支援掛金', '算定基礎額 200,000円 × 仮率0.10%', '200 円'],
  ['退職等年金掛金', '適用区分：対象外（仮例）', '0 円'],
  ['厚生年金保険料', '厚生年金・月額 200,000円 × 仮率9.00%', '18,000 円'],
  ['雇用保険料', '対象賃金 200,000円 × 仮率0.50%', '1,000 円'],
  ['所得税', '税額表参照（仮）：被課税金額165,550円・甲欄・扶養0人。表示用の仮値', '3,000 円'],
  ['住民税', '税額通知書の当月額（仮）を適用', '7,000 円'],
  ['貯金預入', '本人申込額（仮）：毎月10,000円', '10,000 円'],
];

async function allDeductionsByRoot(page: Page, app: FrameLocator, ports: RootPorts, zero: boolean) {
  for (let i = 0; i < deductionFixture.length; i++) {
    const expected = [deductionFixture[i][0], zero ? '登録済み0円（仮例）' : deductionFixture[i][1],
      zero ? '0 円' : deductionFixture[i][2]];
    for (const [part, field] of ['Name', 'Basis', 'Amount'].entries()) {
      const name = `lblPayDeduction${field}${i}`;
      // Every one of the 24 field AND text rectangles is checked separately.
      // Simultaneous full-row visibility is not required by the pan proposal.
      await expect(await reachByRoot(page, app, ports, name)).toHaveText(expected[part]);
    }
  }
}

async function fallbackControls(page: Page, app: FrameLocator, ports: RootPorts, zero: boolean) {
  for (const name of ['btnscrPayrollHome', 'btnPayrollSearch', 'btnPayEarnings', 'btnPayDeductions', 'btnPayRecalculate']) {
    const target = await reachByRoot(page, app, ports, name);
    await expect(target.getByRole('button')).toBeEnabled();
    await pointerPoint(page, target); // Reachability only; navigation is tested separately.
  }
  await pointerPoint(page, await reachByRoot(page, app, ports, 'ddPayrollMonth'));
  await expect(await reachByRoot(page, app, ports, 'lblPayrollStaff')).toContainText(STAFF);
  const amounts = zero ? ['0 円', '0 円', '0 円'] : ['200,000 円', '48,200 円', '151,800 円'];
  for (const [index, kind] of ['Gross', 'Deduct', 'Net'].entries()) {
    await expect(await reachByRoot(page, app, ports, `lblPaySummary${kind}Value`)).toHaveText(amounts[index]);
  }
}

async function collapseAndExpand(page: Page, app: FrameLocator, ports: RootPorts) {
  const expanded = await ports.y.evaluate(el => el.scrollHeight);
  await clickDisplayAction(page, app, ports, 'btnPayEarnings');
  await expect(control(app, 'conPayEarnings')).toBeHidden();
  const earningsClosed = await ports.y.evaluate(el => el.scrollHeight);
  expect(earningsClosed).toBeLessThan(expanded);
  await clickDisplayAction(page, app, ports, 'btnPayDeductions');
  await expect(control(app, 'conPayDeductions')).toBeHidden();
  expect(await ports.y.evaluate(el => el.scrollHeight)).toBeLessThan(earningsClosed);
  await clickDisplayAction(page, app, ports, 'btnPayEarnings');
  await clickDisplayAction(page, app, ports, 'btnPayDeductions');
  await expect(control(app, 'conPayEarnings')).toBeVisible();
  await expect(control(app, 'conPayDeductions')).toBeVisible();
  expect(Math.abs(await ports.y.evaluate(el => el.scrollHeight) - expanded)).toBeLessThanOrEqual(1);
  await allDeductionsByRoot(page, app, ports, false);
}

async function exerciseFallback(page: Page, app: FrameLocator, horizontal: boolean) {
  await waitForPayrollGeometry(app);
  const ports = await rootPorts(app);
  const initialY = await portGeometry(ports.y, page);
  expect(initialY.maxY, 'fallback root has genuine vertical scroll range').toBeGreaterThan(1);
  const initialX = await portGeometry(ports.x, page);
  if (horizontal) expect(initialX.maxX, 'narrow root has genuine horizontal scroll range').toBeGreaterThan(1);
  // A wide-short root may also need a small horizontal pan because its vertical
  // scrollbar consumes a gutter while each child retains Parent.Width.
  if (initialX.maxX > 1) {
    if (initialX.x > 1) await wheelRoot(page, app, ports, 'x', -initialX.x);
    expect((await portGeometry(ports.x, page)).x, 'root left edge is reachable').toBeLessThanOrEqual(1);
    await wheelRoot(page, app, ports, 'x', initialX.maxX);
    const right = await portGeometry(ports.x, page);
    expect(Math.abs(right.x - right.maxX), 'root right edge is reachable').toBeLessThanOrEqual(1);
    await wheelRoot(page, app, ports, 'x', -right.x);
    expect((await portGeometry(ports.x, page)).x, 'root can return to its left edge').toBeLessThanOrEqual(1);
  } else expect(Math.abs(initialX.x), 'no horizontal range means zero horizontal offset').toBeLessThanOrEqual(1);
  const summaryBefore = await control(app, 'conPaySummary').boundingBox(); expect(summaryBefore).not.toBeNull();
  await wheelRoot(page, app, ports, 'y', initialY.y > 1 ? -initialY.y : Math.min(160, initialY.maxY));
  const summaryAfter = await control(app, 'conPaySummary').boundingBox(); expect(summaryAfter).not.toBeNull();
  expect(Math.abs(summaryAfter!.y - summaryBefore!.y), 'proposed exception lets summary move with root').toBeGreaterThan(1);
  // Verify the body is not a competing scrollport in root fallback.
  expect(await control(app, 'conPayBody').evaluate(body => [body, ...Array.from(body.querySelectorAll('*'))]
    .filter(el => el.closest('[data-control-name]') === body)
    .some(el => ['auto', 'scroll'].includes(getComputedStyle(el).overflowY) && el.scrollHeight > el.clientHeight + 1)),
  'fallback body must not remain user-scrollable').toBe(false);
  for (const value of ['2026/11', '2026/09']) {
    await selectMonthByRoot(page, app, ports, value);
    await clickDisplayAction(page, app, ports, 'btnPayRecalculate');
    await fallbackControls(page, app, ports, value === '2026/11');
    await allDeductionsByRoot(page, app, ports, value === '2026/11');
  }
  await collapseAndExpand(page, app, ports);
  // Leave nonzero offsets for the small -> normal passive-reset regression.
  expect((await portGeometry(ports.y, page)).y).toBeGreaterThan(1);
  const finalX = await portGeometry(ports.x, page);
  if (finalX.maxX - finalX.x > 1) await wheelRoot(page, app, ports, 'x', finalX.maxX - finalX.x);
  if (finalX.maxX > 1) expect((await portGeometry(ports.x, page)).x).toBeGreaterThan(1);
}

async function assertNormalRestored(page: Page, app: FrameLocator, size = { width: 1366, height: 768 }) {
  await page.setViewportSize(size);
  await waitForPayrollGeometry(app);
  const rootOffsets = () => control(app, 'conscrPayrollRoot').evaluate(root =>
    [root, ...Array.from(root.querySelectorAll('*'))]
      .filter(el => el.closest('[data-control-name]') === root).map(el => [el.scrollLeft, el.scrollTop]));
  // Do not reset these programmatically: the actual layout must clamp both axes.
  for (const pair of await rootOffsets()) for (const offset of pair) expect(Math.abs(offset)).toBeLessThanOrEqual(1);
  const summary = control(app, 'conPaySummary');
  await assertControlUnclipped(summary, 'normal fixed summary');
  const before = await summary.boundingBox(); expect(before).not.toBeNull();
  await assertLastDeductionReachable(app);
  await assertControlUnclipped(summary, 'normal fixed summary after body scroll');
  const after = await summary.boundingBox(); expect(after).not.toBeNull();
  expect(Math.abs(after!.y - before!.y)).toBeLessThanOrEqual(1);
  for (const pair of await rootOffsets()) for (const offset of pair) expect(Math.abs(offset)).toBeLessThanOrEqual(1);
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

test('UT-STATE-SUMMARY-REFLOW-001 未承認提案のCSS幅450/683はroot両軸、960は固定サマリー', async ({ page }) => {
  test.setTimeout(300_000);
  test.info().annotations.push({ type: 'proposal', description: 'UNAPPROVED r6 root-pan UI exception; owner approval required before application' },
    { type: 'real-Chrome-200-percent', description: 'NOT_RUN: CSS viewport only, not browser zoom evidence' },
    { type: 'keyboard-acceptance', description: 'NOT_RUN: pointer reachability only; actual Tab traversal and focus-clipping checks for all five buttons/month remain required' });
  const app = await open(page); await payroll(app);
  for (const width of [450, 683]) {
    await page.setViewportSize({ width, height: 768 });
    await exerciseFallback(page, app, true);
    await assertNormalRestored(page, app); // 100% size -> small -> 100% size, no offset mutation.
  }
  await assertNormalRestored(page, app, { width: 960, height: 768 });
});

test('UT-STATE-SUMMARY-SHORT-001 未承認提案のCSS590×378と1366×320から通常表示へ復帰する', async ({ page }) => {
  test.setTimeout(300_000);
  test.info().annotations.push({ type: 'proposal', description: 'UNAPPROVED r6 short-height root-scroll exception; owner approval required before application' },
    { type: 'real-Chrome-200-percent', description: 'NOT_RUN: 590x378 CSS viewport approximates one observation only; real Chrome 100 -> 200 -> 100 remains a separate gate' },
    { type: 'keyboard-acceptance', description: 'NOT_RUN: pointer reachability only; actual Tab traversal and focus-clipping checks for all five buttons/month remain required' });
  const app = await open(page); await payroll(app);
  for (const size of [{ width: 590, height: 378 }, { width: 1366, height: 320 }]) {
    await page.setViewportSize(size);
    await exerciseFallback(page, app, size.width < 750);
    await assertNormalRestored(page, app, { width: 1366, height: 768 });
  }
});
