import {createHash} from 'node:crypto';
export function classify(currentText, manifest) {
 const hash=createHash('sha256').update(currentText).digest('hex');
 if(hash===manifest.targetSha256) return {state:'ALREADY_APPLIED',write:false,hash};
 if(hash===manifest.baseSha256) return {state:'APPLY',write:true,hash};
 return {state:'BASELINE_MISMATCH',write:false,hash};
}
