/* Commute ledger 1.01. Read-only, same-origin Dataverse; no Xrm/opener dependency. */
(function(root) {
  'use strict';
  const GUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  const routeKeys = ['operator','from','to','tickettype','ticketbasis','distancekm','ticketamount','passamount','passmonths','amount','recognitionstart','paymonth','remarks'];
  const months = ['04','05','06','07','08','09','10','11','12','01','02','03'];
  const columns = ['crb3c_commuteid','crb3c_recognitionid','crb3c_staffnumber','_crb3c_staffbasicid_value','crb3c_eventdate','crb3c_submitteddate','crb3c_receiveddate','crb3c_startdate','crb3c_enddate','crb3c_monthlytotal',...months.map(m=>'crb3c_month'+m),...Array.from({length:4},(_,i)=>routeKeys.map(k=>'crb3c_route'+(i+1)+'_'+k)).flat()];
  const blank = v => v === null || v === undefined || v === '';
  function text(v) { return blank(v) ? '' : String(v); }
  function number(v, decimal=false) {
    if(blank(v)) return '';
    if(typeof v !== 'number' || !Number.isFinite(v) || v < 0 || (!decimal && !Number.isSafeInteger(v))) throw new Error('数値項目に不正な値があります。');
    return new Intl.NumberFormat('ja-JP',{maximumFractionDigits:decimal?4:0}).format(v);
  }
  function date(v) {
    if(blank(v)) return '';
    const m = /^(\d{4})-(\d{2})-(\d{2})(?:T00:00:00(?:\.000)?Z)?$/.exec(v);
    if(!m) throw new Error('日付の形式を確認してください。');
    const y=+m[1],mo=+m[2],d=+m[3],utc=new Date(Date.UTC(y,mo-1,d));
    if(utc.getUTCFullYear()!==y || utc.getUTCMonth()!==mo-1 || utc.getUTCDate()!==d) throw new Error('日付が不正です。');
    if(v.slice(0,10)>='2019-05-01') return '令和'+(y-2018)+'年'+mo+'月'+d+'日';
    if(v.slice(0,10)>='1989-01-08') return '平成'+(y-1988)+'年'+mo+'月'+d+'日';
    return y+'年'+mo+'月'+d+'日';
  }
  function idFromSearch(search) {
    const q=new URLSearchParams(search);
    if(q.getAll('id').length!==1 || !GUID.test(q.get('id'))) throw new Error('認定が選択されていません。アプリで通勤の行を選択して開いてください。');
    return q.get('id').toLowerCase();
  }
  function model(c,s,id) {
    if(!c || !s || !GUID.test(id) || text(c.crb3c_commuteid).toLowerCase()!==id.toLowerCase() || !GUID.test(c._crb3c_staffbasicid_value || '') || text(c._crb3c_staffbasicid_value).toLowerCase()!==text(s.crb3c_staffbasicid).toLowerCase() || !/^\d{12}$/.test(s.crb3c_staffnumber || '') || c.crb3c_staffnumber!==s.crb3c_staffnumber) throw new Error('認定と職員の対応を確認できません。帳票は表示しません。');
    if(!/^TK-\d{6}$/.test(c.crb3c_recognitionid || '') || blank(s.crb3c_fullname)) throw new Error('認定IDまたは氏名が未設定・不正です。');
    const out={name:text(s.crb3c_fullname),staff:text(s.crb3c_staffnumber),org:text(s.crb3c_orgshort),recognition:c.crb3c_recognitionid,event:date(c.crb3c_eventdate),submitted:date(c.crb3c_submitteddate),received:date(c.crb3c_receiveddate),start:date(c.crb3c_startdate),end:date(c.crb3c_enddate),total:number(c.crb3c_monthlytotal)};
    for(let i=1;i<=4;i++) {
      const p='crb3c_route'+i+'_';
      for(const k of routeKeys) {
        const v=c[p+k];
        out['r'+i+'_'+k]=['ticketbasis','distancekm'].includes(k)?number(v,true):['ticketamount','passamount','passmonths','amount','paymonth'].includes(k)?number(v):k==='recognitionstart'?date(v):text(v);
      }
      if(out['r'+i+'_passmonths']) out['r'+i+'_passmonths']+='箇月';
      if(out['r'+i+'_paymonth']) out['r'+i+'_paymonth']+='月';
      for(const k of ['passmonths','paymonth']) if(!blank(c[p+k]) && (c[p+k]<1 || c[p+k]>12)) throw new Error('月の値が範囲外です。');
    }
    for(const m of months) out['month'+m]=number(c['crb3c_month'+m]);
    return out;
  }
  async function readRecord(fetcher,path,signal) {
    let r;
    try { r=await fetcher('/api/data/v9.2/'+path,{method:'GET',credentials:'same-origin',cache:'no-store',redirect:'error',headers:{Accept:'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0'},signal}); }
    catch(e) { throw new Error(signal && signal.aborted?'読取りが時間切れになりました。再読込みしてください。':'通信または認証に失敗しました。サインイン状態を確認して再読込みしてください。'); }
    if(r.status===401 || r.status===403) throw new Error('サインインまたは閲覧権限を確認してください。');
    if(r.status===404) throw new Error('対象が存在しないか、閲覧できません。');
    if(!r.ok) throw new Error('データを取得できませんでした。時間をおいて再読込みしてください。');
    if(!(r.headers.get('content-type')||'').includes('application/json')) throw new Error('認証状態を確認できません。アプリから開き直してください。');
    return r.json();
  }
  async function retrieve(fetcher,id,signal) {
    if(!GUID.test(id)) throw new Error('認定の識別子が不正です。');
    const c=await readRecord(fetcher,'crb3c_commutes('+id+')?$select='+columns.join(','),signal);
    if(!GUID.test(c._crb3c_staffbasicid_value || '')) throw new Error('職員への参照がありません。');
    const s=await readRecord(fetcher,'crb3c_staffbasics('+c._crb3c_staffbasicid_value+')?$select=crb3c_staffbasicid,crb3c_staffnumber,crb3c_fullname,crb3c_orgshort',signal);
    return model(c,s,id);
  }
  const api={idFromSearch,model,retrieve,date,number,columns};
  if(typeof module!=='undefined' && module.exports) module.exports=api;
  if(!root.document) return;
  const d=root.document;
  async function start() {
    const report=d.getElementById('report'),status=d.getElementById('status'),print=d.getElementById('print');
    let ready=false;
    function fail(message) {
      ready=false;report.hidden=true;print.disabled=true;d.body.classList.remove('ready');
      for(const el of report.querySelectorAll('[data-field]')) el.textContent='';
      status.textContent=message;status.setAttribute('role','alert');
    }
    function fits() {
      for(const el of report.querySelectorAll('[data-field]')) if(el.scrollHeight>el.clientHeight+1 || el.scrollWidth>el.clientWidth+1) return false;
      for(const el of report.querySelectorAll('.page')) if(el.scrollHeight>el.clientHeight+1 || el.scrollWidth>el.clientWidth+1) return false;
      return true;
    }
    root.addEventListener('beforeprint',()=>{
      if(!ready || !fits()) fail('文字が枠内に収まらないため印刷できません。担当者に確認してください。');
    });
    print.addEventListener('click',()=>{if(ready && fits()) root.print();else fail('文字が枠内に収まらないため印刷できません。');});
    const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),20000);
    try {
      if(root.location.protocol!=='https:') throw new Error('DataverseのHTTPS URLから開いてください。');
      const values=await retrieve(root.fetch.bind(root),idFromSearch(root.location.search),controller.signal);
      for(const el of report.querySelectorAll('[data-field]')) el.textContent=values[el.dataset.field] || '';
      if(d.fonts) await d.fonts.ready;
      report.hidden=false;
      await new Promise(resolve=>root.requestAnimationFrame(()=>root.requestAnimationFrame(resolve)));
      if(!fits()) throw new Error('文字が枠内に収まらないため帳票を表示できません。担当者に確認してください。');
      ready=true;print.disabled=false;d.body.classList.add('ready');
      status.textContent='読取り完了：'+values.recognition+' ／ 適用期間 '+values.start+' ～ '+values.end+'。A4・横・倍率100%・ヘッダーとフッターなしで印刷してください。';
    } catch(e) {fail(e.message || '帳票を表示できませんでした。');}
    finally {clearTimeout(timer);}
  }
  d.addEventListener('DOMContentLoaded',start);
})(typeof window==='undefined'?{}:window);
