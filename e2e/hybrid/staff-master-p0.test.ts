import { expect, test, type Locator } from '@playwright/test';

test.describe.configure({ retries: 0 });
test.use({ video: 'off', ignoreHTTPSErrors: false });

const CANVAS_FRAME = 'iframe[name="fullscreen-app-host"]';

type Rect = {
  x: number;
  y: number;
  width: number;
  height: number;
};

async function firstRenderedBox(locator: Locator): Promise<Rect | null> {
  for (const candidate of await locator.all()) {
    const box = await candidate.boundingBox();
    if (box && box.width > 0 && box.height > 0) {
      return box;
    }
  }
  return null;
}

function boxesOverlap(a: Rect, b: Rect, tolerance = 1): boolean {
  const overlapX =
    Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x);
  const overlapY =
    Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y);
  return overlapX > tolerance && overlapY > tolerance;
}

async function scrollWidestHorizontalContainer(body: Locator) {
  return body.evaluate(() => {
    const scrollingElement = document.scrollingElement as HTMLElement | null;
    const candidates = Array.from(document.querySelectorAll<HTMLElement>('*'))
      .filter((element) => {
        const style = window.getComputedStyle(element);
        const permitsHorizontalScroll =
          style.overflowX === 'auto' || style.overflowX === 'scroll';
        return (
          permitsHorizontalScroll &&
          element.clientWidth >= 100 &&
          element.scrollWidth - element.clientWidth > 10
        );
      });

    if (
      scrollingElement &&
      scrollingElement.scrollWidth - scrollingElement.clientWidth > 10
    ) {
      candidates.push(scrollingElement);
    }

    const target = candidates.sort(
      (a, b) =>
        b.scrollWidth -
        b.clientWidth -
        (a.scrollWidth - a.clientWidth),
    )[0];

    if (!target) {
      return {
        found: false,
        moved: false,
        before: 0,
        after: 0,
        maximum: 0,
      };
    }

    const before = target.scrollLeft;
    const maximum = target.scrollWidth - target.clientWidth;
    target.scrollLeft = maximum;
    if (target.scrollLeft === before && maximum > 0) {
      target.scrollLeft = -maximum;
    }
    target.dispatchEvent(new Event('scroll', { bubbles: true }));

    return {
      found: true,
      moved: Math.abs(target.scrollLeft - before) > 1,
      before,
      after: target.scrollLeft,
      maximum,
    };
  });
}

test.describe('職員マスタ検索 v1.18 P0 (Dataverse fixture)', () => {
  test('検索、職員選択、縮小表示、条件クリアが動作する', async ({ page }) => {
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

    // INIT-01: 初期表示は25名で、先頭の試験 採用予定が表示される。
    await expect(canvas.getByText(/職員一覧\s*25件/).first()).toBeVisible({
      timeout: 30_000,
    });
    await expect(canvas.getByText('試験 採用予定', { exact: true }).first()).toBeVisible({
      timeout: 30_000,
    });

    // SRCH-02: 氏名「同姓同名」で検索すると同姓同名姓の2名に絞られる。
    const keywordInput = canvas.getByRole('searchbox', {
      name: '氏名・職員番号・項目を検索',
      exact: true,
    });
    await keywordInput.waitFor({ state: 'visible', timeout: 30_000 });
    await keywordInput.fill('同姓同名');

    const searchButton = canvas.getByRole('button', { name: '検索', exact: true });
    await searchButton.waitFor({ state: 'visible', timeout: 30_000 });
    await searchButton.click({ force: true });

    await expect(canvas.getByText(/職員一覧\s*2件/).first()).toBeVisible({
      timeout: 30_000,
    });
    await expect(canvas.getByRole('button', { name: '009900000011 試験 同姓同名 詳細を表示', exact: true })).toBeVisible();
    const hanakoInList = canvas.getByRole('button', { name: '009900000012 試験 同姓同名 詳細を表示', exact: true });
    await expect(hanakoInList).toBeVisible();

    // SEL-01: 試験 同姓同名を選択し、右側詳細に本人の氏名と職員番号が表示される。
    await hanakoInList.click({ force: true });
    await expect(canvas.getByText('009900000012', { exact: true }).first()).toBeVisible({
      timeout: 30_000,
    });
    await expect
      .poll(
        async () => {
          const names = await canvas
            .getByText('試験 同姓同名', { exact: true })
            .all();
          for (const name of names) {
            const box = await name.boundingBox();
            if (box && box.x >= 360 && box.width > 0 && box.height > 0) {
              return true;
            }
          }
          return false;
        },
        {
          message: '試験 同姓同名の氏名が画面右側の詳細領域に表示されること',
          timeout: 30_000,
        },
      )
      .toBe(true);

    await page.screenshot({
      path: 'test-results/staff-master-hanako-detail.png',
      fullPage: true,
    });

    // VIS-01/VIS-04: 小さいPCウィンドウでも項目が残り、重ならず、
    // 横長の履歴表はスクロールして右端まで到達できる。
    await page.setViewportSize({ width: 900, height: 600 });

    const basicHeading = canvas.getByText('職員基本情報', { exact: true }).first();
    const workHeading = canvas.getByText(/給与・勤務条件履歴/).first();
    await expect(basicHeading).toBeVisible({ timeout: 30_000 });
    await expect(workHeading).toBeVisible({ timeout: 30_000 });
    await workHeading.scrollIntoViewIfNeeded();

    const nonOverlapPairs = [
      ['職員番号', '氏名'],
      ['組織名略称', '生年月日'],
      ['採用日', '退職日'],
      ['適用状態', '適用開始日'],
      ['適用開始日', '適用終了日'],
      ['適用終了日', '日額単価'],
      ['日額単価', '所定勤務時間'],
      ['所定勤務時間', '勤務時間'],
      ['勤務時間', '超勤基礎単価（参考）'],
    ] as const;

    for (const [firstText, secondText] of nonOverlapPairs) {
      const firstBox = await firstRenderedBox(
        canvas.getByText(firstText, { exact: true }),
      );
      const secondBox = await firstRenderedBox(
        canvas.getByText(secondText, { exact: true }),
      );
      expect(firstBox, `${firstText}が縮小画面でも描画されること`).not.toBeNull();
      expect(secondBox, `${secondText}が縮小画面でも描画されること`).not.toBeNull();
      expect(
        boxesOverlap(firstBox!, secondBox!),
        `${firstText}と${secondText}の文字領域が重ならないこと`,
      ).toBe(false);
    }

    const scrollResult = await scrollWidestHorizontalContainer(
      canvas.locator('body'),
    );
    expect(scrollResult.found, '横スクロール可能な領域が存在すること').toBe(true);
    expect(
      scrollResult.moved,
      `横スクロール位置が移動すること: ${JSON.stringify(scrollResult)}`,
    ).toBe(true);

    const farRightHeader = canvas
      .getByText('勤務時間終了', { exact: true })
      .first();
    await farRightHeader.scrollIntoViewIfNeeded();
    await expect(farRightHeader).toBeInViewport({ ratio: 0.5 });

    await page.screenshot({
      path: 'test-results/staff-master-small-viewport.png',
      fullPage: true,
    });

    // ZERO-03: 条件クリアで25名表示へ戻る。
    const clearButton = canvas.getByRole('button', {
      name: '検索条件をクリア',
      exact: true,
    });
    await clearButton.waitFor({ state: 'visible', timeout: 30_000 });
    await clearButton.click({ force: true });
    await expect(canvas.getByText(/職員一覧\s*25件/).first()).toBeVisible({
      timeout: 30_000,
    });

    await page.screenshot({
      path: 'test-results/staff-master-p0-success.png',
      fullPage: true,
    });
  });
});
