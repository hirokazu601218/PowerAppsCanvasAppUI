// Additional fixed synthetic inputs for local print-layout checking.
const fs=require('node:fs'),path=require('node:path'),api=require('../src/report.js');
const records=require('./commute-6.json');
const base=fs.readFileSync(path.join(__dirname,'../src/layout.html'),'utf8');
const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function write(name,r){const v=api.model({...r.data,crb3c_commuteid:r.id,_crb3c_staffbasicid_value:r.parent_id},{crb3c_staffbasicid:r.parent_id,crb3c_staffnumber:r.data.crb3c_staffnumber,crb3c_fullname:r.data.crb3c_fullname,crb3c_orgshort:'試験所属'},r.id);fs.writeFileSync(path.join(__dirname,'../qa/'+name+'.html'),base.replace(/(<span[^>]*data-field="([^"]+)"[^>]*>)(<\/span>)/g,(_,a,k,z)=>a+esc(v[k]||'')+z));}
records.forEach(r=>write(r.data.crb3c_recognitionid,r));
const multi=structuredClone(records[0]);for(let i=2;i<=4;i++) for(const [k,v] of Object.entries(multi.data)) if(k.startsWith('crb3c_route1_')) multi.data[k.replace('route1','route'+i)]=v;
write('four-routes',multi);
const long=structuredClone(multi);long.data.crb3c_fullname='長'.repeat(50);long.data.crb3c_route1_operator='経'.repeat(100);long.data.crb3c_route1_from='住'.repeat(100);long.data.crb3c_route1_remarks='備'.repeat(255);write('overflow-expected',long);
