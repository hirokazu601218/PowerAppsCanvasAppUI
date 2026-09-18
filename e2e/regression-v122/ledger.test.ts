import {test,expect,type Locator} from '@playwright/test';
import {writeFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
test.describe.configure({retries:0});
test.use({video:'off',ignoreHTTPSErrors:false});
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


test('AUT-LEDGER-117 six zoom levels, aligned controls and actual two-page A4 PDF',async({page})=>{
  test.setTimeout(180_000);
  // Observe only locally generated PDF blobs; never collect network/auth payloads.
  await page.addInitScript(()=>{
    const original=URL.createObjectURL.bind(URL);
    (window as any).__ledgerPdfs=[];
    const capture=(data:any,depth=0)=>{
      if(depth>5||data==null)return;
      if(typeof data==='string'){
        if(data.startsWith('{') || data.startsWith('[')){try{capture(JSON.parse(data),depth+1);}catch{}return;}
        if(data.startsWith('%PDF-')){
          const bytes=Uint8Array.from(data,(c:string)=>c.charCodeAt(0)&255);capture(bytes,depth+1);return;
        }
        if(data.startsWith('data:application/pdf;base64,')) (window as any).__ledgerPdfs.push(data);
        else if(data.startsWith('JVBERi0')) (window as any).__ledgerPdfs.push('data:application/pdf;base64,'+data);
        return;
      }
      const bytes=Array.isArray(data)&&data.length>5&&data.slice(0,5).join(',')==='37,80,68,70,45'?new Uint8Array(data):data instanceof ArrayBuffer?new Uint8Array(data):ArrayBuffer.isView(data)?new Uint8Array(data.buffer,data.byteOffset,data.byteLength):null;
      if(bytes){
        if(bytes.length>5 && String.fromCharCode(...bytes.slice(0,5))==='%PDF-'){
          const reader=new FileReader();reader.onload=()=>{(window as any).__ledgerPdfs.push(reader.result);};
          reader.readAsDataURL(new Blob([bytes.slice()],{type:'application/pdf'}));
        }
        return;
      }
      if(typeof data==='object')for(const value of Object.values(data).slice(0,50))capture(value,depth+1);
    };
    // The built-in PDF viewer may receive the PDF by postMessage without a blob URL.
    // Retain only values with an actual PDF header; no other message data is stored.
    window.addEventListener('message',event=>capture(event.data));
    URL.createObjectURL=(blob:Blob|MediaSource)=>{
      if(blob instanceof Blob){
        void blob.slice(0,5).text().then(header=>{
          if(header!=='%PDF-')return;
          const reader=new FileReader();reader.onload=()=>{(window as any).__ledgerPdfs.push(reader.result);};reader.readAsDataURL(blob);
        });
      }
      return original(blob);
    };
  });
  await page.setViewportSize({width:1366,height:1000});
  await page.goto(process.env.CANVAS_APP_URL!,{waitUntil:'domcontentloaded',timeout:60000});
  const c=page.frameLocator('iframe[name="fullscreen-app-host"]');
  const ctl=(n:string)=>c.locator(`[data-control-name="${n}"]`);
  await expect(c.locator('[data-control-name="lblHomePrototype"]')).toContainText(/UI検討用 v1\.(22|23)/,{timeout:60000});
  await c.getByRole('button',{name:'職員マスタ検索',exact:true}).click();
  await c.getByRole('searchbox',{name:'氏名・職員番号・項目を検索',exact:true}).fill('009900000011');
  await c.getByRole('button',{name:'検索',exact:true}).click();
  await c.getByRole('button',{name:'009900000011 試験 同姓同名 詳細を表示',exact:true}).click();
  await c.getByRole('button',{name:'選択職員の認定簿を表示',exact:true}).click();
  await expect(ctl('lblLedger_employee_name111')).toHaveText('試験 同姓同名');
  await expect(c.getByText('PDF用紙',{exact:true})).toHaveCount(0);
  const zoom=ctl('ddLedgerPaper111');
  const records=[];
  for(const percent of [50,75,100,125,150,200]){
    await zoom.click();
    const option=c.getByRole('option',{name:`${percent}%`,exact:true});
    await expect(option).toHaveCount(1);await option.click();
    await expect.poll(async()=>(await rectangle(ctl('conLedgerSheet1111'))).width).toBeCloseTo(1122*percent/100,0);
    const sheet=await rectangle(ctl('conLedgerSheet1111'));
    const header=await rectangle(ctl('conLedgerHeader111'));
    for(const name of ['lblLedgerTitle111','lblLedgerStaff111','btnLedgerClose111','btnLedgerFit111','btnLedgerZoom111','lblLedgerPaper111','ddLedgerPaper111','btnLedgerPdf111','lblLedgerStatus111']){
      const box=await rectangle(ctl(name));
      expect(box.x).toBeGreaterThanOrEqual(sheet.x-1);
      expect(box.x+box.width).toBeLessThanOrEqual(sheet.x+sheet.width+1);
      expect(box.x+box.width).toBeLessThanOrEqual(header.x+header.width+1);
    }
    await expect(ctl('lblLedger_employee_name111')).toHaveText('試験 同姓同名');
    records.push({percent,sheet,header});
    await page.locator('iframe[name="fullscreen-app-host"]').screenshot({mask:[ctl('lblStaffAccount122')],path:`${process.env.OUTPUT_DIRECTORY}/ledger-${percent}.png`});
  }
  expect(await hasBackground(ctl('conLedgerHeader111'),'rgb(255, 255, 255)')).toBe(true);
  expect(await ctl('btnLedgerClose111').evaluate(el=>[el,...el.querySelectorAll('*')].some(n=>getComputedStyle(n).color==='rgb(15, 108, 189)'))).toBe(true);
  writeFileSync(`${process.env.OUTPUT_DIRECTORY}/ledger-zoom-measurements.json`,JSON.stringify(records,null,2));
  // Generate at 200%: print size must remain independent of screen zoom.
  await c.getByRole('button',{name:'PDF関数（表示）',exact:true}).click();
  await expect(ctl('lblLedgerStatus111')).toContainText('PDFを作成しました',{timeout:90000});
  let pdf='';
  await expect.poll(async()=>{
    for(const frame of page.frames()){
      const found=await frame.evaluate(()=>(window as any).__ledgerPdfs?.at(-1)).catch(()=>undefined);
      if(found)pdf=found;
    }
    return pdf.length;
  },{timeout:15000}).toBeGreaterThan(0);
  const path=`${process.env.OUTPUT_DIRECTORY}/ledger-A4-landscape.pdf`;
  writeFileSync(path,Buffer.from(pdf.split(',')[1],'base64'));
  const result=execFileSync('python',['-c',`import json,sys\nfrom pypdf import PdfReader\nr=PdfReader(sys.argv[1]);assert len(r.pages)==2, f'Expected 2 pages, got {len(r.pages)}'\nboxes=[[float(p.mediabox.width),float(p.mediabox.height)] for p in r.pages]\nassert all(abs(w-841.89)<1 and abs(h-595.28)<1 for w,h in boxes),boxes\nprint(json.dumps({'pages':len(r.pages),'points':boxes}))`,path],{encoding:'utf8'});
  writeFileSync(`${process.env.OUTPUT_DIRECTORY}/ledger-pdf-check.json`,result);
  await page.locator('iframe[name="fullscreen-app-host"]').screenshot({mask:[ctl('lblStaffAccount122')],path:`${process.env.OUTPUT_DIRECTORY}/ledger-pdf-preview.png`});
  await c.getByRole('button',{name:'PDFプレビューから帳票に戻る',exact:true}).click();
  await c.getByRole('button',{name:'表示倍率を100%に戻す',exact:true}).click();
  await expect.poll(async()=>(await rectangle(ctl('conLedgerSheet1111'))).width).toBeCloseTo(1122,0);
  await ctl('btnLedgerClose111').getByRole('button').click();
  await expect(ctl('conLedgerModal111')).toBeHidden();
});
