import { expect, test, type Locator } from '@playwright/test';
import { writeFileSync } from 'node:fs';

test.describe.configure({ retries: 0 });
test.use({ video: 'off', ignoreHTTPSErrors: false });

test('AUT-META-001 approved header value is displayed', async ({ page }) => {
  test.setTimeout(120_000);
  const expected = process.env.EXPECTED_LABEL;
  if (!expected || !process.env.CANVAS_APP_URL) throw new Error('Missing acceptance target');
  await page.setViewportSize({ width: 1366, height: 768 });
  const canvas = page.frameLocator('iframe[name="fullscreen-app-host"]');
  const observed: { load: number; version: string }[]=[];
  // Publishing and player availability are separate. Reopen during readiness only;
  // never accept the old version or rerun failed functional assertions.
  await expect.poll(async()=>{
    await page.goto(process.env.CANVAS_APP_URL!,{waitUntil:'domcontentloaded',timeout:30_000});
    const live=canvas.locator('[data-control-name="lblMeta111"]');
    await expect(live).toHaveCount(1,{timeout:30_000});
    await expect(live).toBeVisible({timeout:5_000});
    const version=(await live.innerText()).replace(/\s+/g,' ').trim();
    observed.push({load:observed.length+1,version});
    writeFileSync(`${process.env.OUTPUT_DIRECTORY}/version-readiness.json`,JSON.stringify(observed,null,2));
    return version;
  },{message:'AUT-META-001: approved header value',timeout:90_000,intervals:[1000,3000,5000]}).toBe(expected);
  const header = canvas.getByText(expected, { exact: true });
  await expect(header, 'AUT-META-001: approved header value').toBeVisible({ timeout: 5_000 });
  await page.screenshot({ path: `${process.env.OUTPUT_DIRECTORY}/approved-label.png`, fullPage: true });
});

test('AUT-SIDEBAR-001 menu icon and sidebar state preservation', async ({ page }) => {
  await page.setViewportSize({width:1366,height:768});
  await page.goto(process.env.CANVAS_APP_URL!, {waitUntil:'domcontentloaded',timeout:60000});
  const c=page.frameLocator('iframe[name="fullscreen-app-host"]');
  const close=()=>c.getByRole('button',{name:'職員検索を閉じる',exact:true});
  const open=()=>c.getByRole('button',{name:'職員検索を開く',exact:true});
  // The recovery runner uses this same test against the last good v1.12.
  const legacy=process.env.EXPECTED_LABEL === 'v1.12 ／ B案・架空25名';
  await expect(close()).toBeVisible({timeout:60000});
  await expect(close()).toHaveText(legacy?'‹':'☰');
  const input=c.getByRole('searchbox',{name:'氏名・職員番号・項目を検索',exact:true});
  await input.fill('同姓同名');
  await c.getByRole('button',{name:'検索',exact:true}).click();
  await expect(c.getByText(/職員一覧\s*2件/)).toBeVisible();
  // The transparent row button owns pointer events above the display labels.
  await c.getByRole('button',{name:'009900000012 試験 同姓同名 詳細を表示',exact:true}).click();
  // Verify the selected employee in the persistent detail summary, not hidden list cells.
  const selected=c.getByText('職員番号：009900000012 ／ 所属：01秘書課',{exact:true});
  await expect(selected).toBeVisible();
  for(let i=0;i<2;i++){
    await close().click();
    await expect(open()).toHaveText(legacy?'›':'☰');
    await expect(input).toBeHidden();
    await expect(selected).toBeVisible();
    await page.screenshot({path:process.env.OUTPUT_DIRECTORY+'/sidebar-closed-'+i+'.png'});
    await open().click();
    await expect(close()).toHaveText(legacy?'‹':'☰');
    await expect(input).toHaveValue('同姓同名');
    await expect(c.getByText(/職員一覧\s*2件/)).toBeVisible();
    await expect(selected).toBeVisible();
  }
  await c.getByRole('button',{name:'検索条件をクリア',exact:true}).click();
  await c.getByRole('button',{name:'次へ',exact:true}).click();
  const pageText=c.getByText('2 / 2',{exact:true});
  await expect(pageText).toBeVisible();
  const before=await pageText.innerText();
  await close().click();
  await open().click();
  await expect(pageText).toHaveText(before);
  await page.screenshot({path:process.env.OUTPUT_DIRECTORY+'/sidebar-expanded.png'});
});

async function rectangle(locator: Locator) {
  await expect(locator).toHaveCount(1);
  await expect(locator).toBeVisible();
  const box=await locator.boundingBox();
  expect(box).not.toBeNull();
  return box!;
}

async function hasBackground(locator: Locator, color: string) {
  return locator.evaluate((root,wanted)=>[root,...root.querySelectorAll('*')]
    .some(el=>getComputedStyle(el).backgroundColor===wanted),color);
}

test('AUT-LAYOUT-001 responsive basic fields, density and canvas-width preservation',async ({page})=>{
  test.setTimeout(180_000);
  const current=process.env.EXPECTED_LABEL==='v1.16 ／ Dataverse・25名';
  expect(['v1.16 ／ Dataverse・25名']).toContain(process.env.EXPECTED_LABEL);
  await page.setViewportSize({width:1366,height:1000});
  await page.goto(process.env.CANVAS_APP_URL!,{waitUntil:'domcontentloaded',timeout:60000});
  const c=page.frameLocator('iframe[name="fullscreen-app-host"]');
  const control=(name:string)=>c.locator(`[data-control-name="${name}"]`);
  await expect(c.getByText(process.env.EXPECTED_LABEL!,{exact:true})).toBeVisible({timeout:60000});
  const records:unknown[]=[];
  // Independent field order and data oracle; never derive values from the app source.
  const keys=['職員番号','氏名','組織・所属（正式名称）','組織名略称','生年月日','性別','採用日','退職日','在籍状態'];
  const values=['009900000001','試験 採用予定','','','','','','','採用前'];
  for(const large of [false,true]){
    if(large)await c.getByRole('button',{name:'文字サイズを大きくする',exact:true}).click();
    for(const width of [900,1100,1366,1600,1920]){
      await page.setViewportSize({width,height:1000});
      // The hosted player reserves one CSS pixel for its frame; measure the app.
      await expect.poll(async()=> Math.abs((await rectangle(control('conStaffMaster111'))).width-width)).toBeLessThan(1.1);
      const basic=await rectangle(control('conBasic111'));
      const columns=current?Math.max(1,Math.min(6,Math.floor((basic.width-16)/(large?252:220))))
        :(basic.width>=900?3:basic.width>=560?2:1);
      const rowHeight=current?(large?72:64):(large?104:96);
      const cells=[];
      for(let i=0;i<9;i++){
        const key=control(`lblBasicKey${i}111`),val=control(`lblBasicVal${i}111`);
        await expect(key).toHaveText(keys[i]);await expect(val).toHaveText(values[i]);
        const k=await rectangle(key),v=await rectangle(val);
        expect(Math.abs(k.x-v.x)).toBeLessThan(1.1);
        expect(Math.abs(k.width-v.width)).toBeLessThan(1.1);
        expect(Math.abs(v.y-k.y-k.height)).toBeLessThan(1.1);
        expect(v.height).toBe(current?(large?28:24):64);
        expect(k.x).toBeGreaterThanOrEqual(basic.x);
        expect(k.x+k.width).toBeLessThanOrEqual(basic.x+basic.width+1);
        expect(v.y+v.height).toBeLessThanOrEqual(basic.y+basic.height+1);
        if(i>=columns)expect(Math.abs(k.y-cells[i-columns].y-rowHeight)).toBeLessThan(1.1);
        if(i%columns!==0){expect(Math.abs(k.y-cells[i-1].y)).toBeLessThan(1.1);expect(k.x).toBeGreaterThanOrEqual(cells[i-1].x+cells[i-1].width-1);}
        cells.push(k);
      }
      expect(basic.height).toBe(52+Math.ceil(9/columns)*rowHeight);
      if(current&&width===1920&&!large)expect(columns).toBe(6);
      const main=await rectangle(control('conMain111')),header=await rectangle(control('conHeader111'));
      const margin=current?16:0;
      expect(Math.abs(header.x-main.x-margin)).toBeLessThan(1.1);
      expect(Math.abs(main.width-header.width-2*margin)).toBeLessThan(1.1);
      // At design/canvas width no extra margin is deducted from business data.
      if(width===1366){expect(header.width).toBe(main.width-2*margin);expect(basic.width).toBe(main.width-430);}
      const name=await rectangle(control('lblName111')),badge=await rectangle(control('lblBadge111'));
      if(current){expect(Math.abs(badge.x-name.x-name.width-8)).toBeLessThan(1.1);expect(Math.abs(badge.y+badge.height/2-name.y-name.height/2)).toBeLessThan(1.1);}
      expect(badge.x+badge.width).toBeLessThanOrEqual((await rectangle(control('conPerson111'))).x+(await rectangle(control('conPerson111'))).width);
      records.push({width,large,columns,basic,header,name,badge,cells});
      if(width===1366||width===1920){await control('conHeader111').scrollIntoViewIfNeeded();await page.screenshot({path:`${process.env.OUTPUT_DIRECTORY}/layout-${width}-${large?'large':'standard'}.png`});}
    }
    // Closing the search panel recalculates columns from the newly available width.
    await c.getByRole('button',{name:'職員検索を閉じる',exact:true}).click();
    const expanded=await rectangle(control('conBasic111'));
    expect(expanded.width).toBeGreaterThan(1700);
    if(current){const a=await rectangle(control('lblBasicKey0111')),b=await rectangle(control('lblBasicKey5111'));expect(Math.abs(a.y-b.y)).toBeLessThan(1.1);}
    await c.getByRole('button',{name:'職員検索を開く',exact:true}).click();
  }
  writeFileSync(`${process.env.OUTPUT_DIRECTORY}/layout-measurements.json`,JSON.stringify(records,null,2));
});

test('AUT-LIST-001 selected row coverage, subtle separators and keyboard selection',async ({page})=>{
  const current=process.env.EXPECTED_LABEL==='v1.16 ／ Dataverse・25名';
  await page.setViewportSize({width:1366,height:900});
  await page.goto(process.env.CANVAS_APP_URL!,{waitUntil:'domcontentloaded',timeout:60000});
  const c=page.frameLocator('iframe[name="fullscreen-app-host"]');
  await expect(c.getByText(process.env.EXPECTED_LABEL!,{exact:true})).toBeVisible({timeout:60000});
  const input=c.getByRole('searchbox',{name:'氏名・職員番号・項目を検索',exact:true});
  await input.fill('同姓同名');await c.getByRole('button',{name:'検索',exact:true}).click();
  // Power Apps appends ". Selected." to the accessible row name on selection.
  const row=c.getByRole('listitem',{name:/^試験 同姓同名、在籍、職員番号009900000012、01秘書課/});
  const firstRow=c.getByRole('listitem',{name:/^試験 同姓同名、在籍、職員番号009900000011、03会計課/});
  await expect(row).toHaveCount(1);await expect(firstRow).toHaveCount(1);
  const select=row.getByRole('button',{name:'009900000012 試験 同姓同名 詳細を表示',exact:true});
  await expect(select).toHaveCount(1);await select.focus();await page.keyboard.press('Enter');
  await expect(c.getByText('職員番号：009900000012 ／ 所属：01秘書課',{exact:true})).toBeVisible();
  const org=row.locator('[data-control-name="lblListC2111"]');
  await expect(org).toHaveCount(1);
  await expect.poll(()=>hasBackground(org,'rgb(220, 234, 255)')).toBe(true);
  await expect.poll(()=>hasBackground(firstRow.locator('[data-control-name="lblListC2111"]'),'rgb(255, 255, 255)')).toBe(true);
  const o=await rectangle(org),s=await rectangle(row.locator('[data-control-name="lblListC3111"]'));
  if(current)expect(Math.abs(o.x+o.width-s.x-s.width)).toBeLessThan(1.1);
  for(const target of [firstRow,row]){
    const divider=target.locator('[data-control-name="lblListC0111"]');
    const d=await rectangle(divider),button=await rectangle(target.locator('[data-control-name="btnRow111"]'));
    if(current){expect(d.height).toBe(1);expect(Math.abs(d.width-button.width)).toBeLessThan(1.1);expect(Math.abs(d.y+d.height-button.y-button.height)).toBeLessThan(1.1);expect(await hasBackground(divider,'rgb(226, 232, 240)')).toBe(true);}
  }
  await page.screenshot({path:`${process.env.OUTPUT_DIRECTORY}/list-selection-and-separators.png`});
});
