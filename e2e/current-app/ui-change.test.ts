import { expect, test, type Page } from '@playwright/test';
async function open(page: Page) {
 const value=process.env.CANVAS_APP_URL;
 if (!value || !new URL(value).pathname.endsWith('/a/204a48dc-7f23-43dd-b934-4654a3cfa306')) throw new Error('Unexpected app');
 await page.setViewportSize({width:1366,height:768});
 await page.goto(value,{waitUntil:'domcontentloaded'});
 const app=page.frameLocator('iframe[name="fullscreen-app-host"]');
 await expect(app.getByRole('button',{name:'職員マスタ検索',exact:true})).toBeVisible();
 return app;
}
test('UT-SCR001-TILES-001 四つの角丸正方形とPoC導線',async ({page})=>{
 const app=await open(page);
 const names=['職員マスタ検索','勤務時間報告','期末勤勉支給率登録','メンテナンス'];
 const boxes=[];
 for(const name of names){ const button=app.getByRole('button',{name,exact:true}); await expect(button).toBeVisible(); const b=await button.boundingBox(); expect(b).not.toBeNull(); boxes.push(b!); }
 for(const b of boxes){ expect(Math.abs(b.width-b.height)).toBeLessThan(3); expect(Math.abs(b.y-boxes[0].y)).toBeLessThan(3); }
 for(let i=1;i<boxes.length;i++) expect(boxes[i].x).toBeGreaterThanOrEqual(boxes[i-1].x+boxes[i-1].width);
 const poc=await app.getByRole('button',{name:'PoCデータ一括取込',exact:true}).boundingBox();
 expect(poc!.y).toBeGreaterThanOrEqual(boxes[0].y+boxes[0].height);
 await expect(app.getByRole('button',{name:'支給明細画面',exact:true})).toHaveCount(0);
});
test('UT-SCR002-BORDER-001 ヘッダー境界線と画面ID枠',async ({page})=>{
 const app=await open(page); await app.getByRole('button',{name:'職員マスタ検索',exact:true}).click();
 const header=app.locator('[data-control-name="conHeader111"]');
 const id=app.locator('[data-control-name="lblStaffScreenId111"]');
 await expect(id).toBeVisible(); await expect(id).toHaveCSS('border-top-width','0px');
 const color=await header.evaluate(el=>getComputedStyle(el).backgroundColor);
 for(const name of ['lblApp111','lblMeta111']) await expect(app.locator(`[data-control-name="${name}"]`)).toHaveCSS('border-top-color',color);
});
