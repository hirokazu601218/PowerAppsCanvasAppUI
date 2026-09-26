// Generate an escaped fixed fixture for layout review; never queries Dataverse.
const fs=require('node:fs'), path=require('node:path'), api=require('../src/report.js');
const r=require('./commute-6.json')[2];
const values=api.model({...r.data,crb3c_commuteid:r.id,_crb3c_staffbasicid_value:r.parent_id},{crb3c_staffbasicid:r.parent_id,crb3c_staffnumber:r.data.crb3c_staffnumber,crb3c_fullname:r.data.crb3c_fullname,crb3c_orgshort:'03会計課'},r.id);
const escape=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let html=fs.readFileSync(path.join(__dirname,'../src/layout.html'),'utf8').replace(/(<span[^>]*data-field="([^"]+)"[^>]*>)(<\/span>)/g,(_,a,k,z)=>a+escape(values[k]||'')+z).replace('id="print" disabled','id="print" onclick="window.print()"').replace('認定データを読み込んでいます…','固定架空データ TK-910003・レイアウト検証専用／実データ接続なし');
fs.mkdirSync(path.join(__dirname,'../qa'),{recursive:true});fs.writeFileSync(path.join(__dirname,'../qa/layout-fixture.html'),html);
