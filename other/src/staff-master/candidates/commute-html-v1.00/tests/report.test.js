const assert=require('node:assert/strict');
const test=require('node:test');
const api=require('../src/report.js');
const records=require('./commute-6.json');
function pair(r){return [{...r.data,crb3c_commuteid:r.id,_crb3c_staffbasicid_value:r.parent_id},{crb3c_staffbasicid:r.parent_id,crb3c_staffnumber:r.data.crb3c_staffnumber,crb3c_fullname:r.data.crb3c_fullname,crb3c_orgshort:'試験所属'}];}
test('6 independent fixtures: recognition, names, amounts, zero and NULL',()=>{
 for(const r of records){const [c,s]=pair(r),m=api.model(c,s,r.id);assert.equal(m.recognition,r.data.crb3c_recognitionid);assert.equal(m.staff,r.data.crb3c_staffnumber);assert.equal(m.name,r.data.crb3c_fullname);assert.equal(m.r2_operator,'');}
 const expectations=['1,300','1,400','16,800','0','0','0'];records.forEach((r,i)=>assert.equal(api.model(...pair(r),r.id).total,expectations[i]));
 assert.equal(api.model(...pair(records[2]),records[2].id).r1_ticketbasis,'40');
 assert.equal(api.model(...pair(records[1]),records[1].id).month10,'8,400');
});
test('missing, duplicate, injected and malformed identifiers rejected',()=>{for(const q of ['', '?id=x', '?id='+records[0].id+'&id='+records[1].id, '?id=%27%29%3Balert%281%29'])assert.throws(()=>api.idFromSearch(q));assert.equal(api.idFromSearch('?id='+records[0].id),records[0].id);});
test('different parent, staff or recognition must never render another person',()=>{const [c,s]=pair(records[0]);assert.throws(()=>api.model(c,{...s,crb3c_staffnumber:'009900000012'},records[0].id));assert.throws(()=>api.model({...c,_crb3c_staffbasicid_value:records[2].parent_id},s,records[0].id));assert.throws(()=>api.model(c,s,records[1].id));});
test('NULL distinct from 0; date only and era boundary; no timezone shifts',()=>{assert.equal(api.number(null),'');assert.equal(api.number(0),'0');assert.equal(api.date('2019-04-30'),'平成31年4月30日');assert.equal(api.date('2019-05-01'),'令和1年5月1日');assert.equal(api.date('2099-04-01'),'令和81年4月1日');assert.throws(()=>api.date('2026-02-30'));assert.throws(()=>api.number(-1));assert.throws(()=>api.number('100'));});
test('markup and longest source strings remain literal; no truncation',()=>{const [c,s]=pair(records[0]);s.crb3c_fullname='<img src=x onerror=alert(1)>&';c.crb3c_route1_remarks='備'.repeat(255);const m=api.model(c,s,records[0].id);assert.equal(m.name,s.crb3c_fullname);assert.equal(m.r1_remarks.length,255);const fs=require('node:fs'),src=fs.readFileSync(require.resolve('../src/report.js'),'utf8');assert.ok(src.includes('el.textContent=values[el.dataset.field]'));assert.ok(!src.includes('innerHTML'));});
test('GET only, same origin, minimum columns, no fallback on HTTP/auth failures',async()=>{
 const r=records[0],[c,s]=pair(r),calls=[];
 const fetcher=async(url,opts)=>{calls.push([url,opts]);return {ok:true,status:200,headers:{get:()=> 'application/json'},json:async()=>calls.length===1?c:s};};
 const m=await api.retrieve(fetcher,r.id);assert.equal(m.recognition,'TK-910001');assert.equal(calls.length,2);for(const [url,opts] of calls){assert.ok(url.startsWith('/api/data/v9.2/'));assert.equal(opts.method,'GET');assert.equal(opts.credentials,'same-origin');assert.equal(opts.redirect,'error');assert.equal(opts.cache,'no-store');}
 for(const status of [401,403,404,429,500]) await assert.rejects(()=>api.retrieve(async()=>({ok:false,status}),r.id));
 await assert.rejects(()=>api.retrieve(async()=>{throw Error('offline');},r.id));
 await assert.rejects(()=>api.retrieve(async()=>({ok:true,status:200,headers:{get:()=> 'text/html'}}),r.id));
});
