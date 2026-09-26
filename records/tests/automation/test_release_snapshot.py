import copy
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(SOURCE/'scripts/automation'))
import readme_release
import release_snapshot
import releases
import repair_v114_readme


class ReleaseSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'repo';self.root.mkdir()
        self.origin=Path(self.temp.name)/'origin.git'
        subprocess.run(['git','init','--bare',str(self.origin)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        self.git('init','-b','main');self.git('config','user.name','Test');self.git('config','user.email','test@example.invalid')
        self.git('remote','add','origin',str(self.origin))
        self.target={'environment_id':'isolated','app_id':'test-only'}
        self.request={'mode':'release','issue':29,'request':'fixture','approved':True}
        self.gates=dict.fromkeys(('build','auth','import','publish','readback','change_test','p0'),'success')
        self.write('README.md','manual\n'+readme_release.START+'\nlatest v1.13\n'+readme_release.END+'\nfooter\n')
        self.write('.gitignore','artifacts/\n')
        self.write('app.txt','v1.13 payload')
        self.write('automation/change.json',json.dumps({'candidate_version':'1.14'}))
        self.write('automation/run.json',json.dumps(self.request))
        self.write('automation/release.json',json.dumps({'last_success_version':'1.13'}))
        self.write('config/apps/staff-master.json',json.dumps({'target':self.target,'display_name':'自動開発_職員マスタ検索'}))
        self.write('scripts/automation/finalize_release.py',(SOURCE/'scripts/automation/finalize_release.py').read_text())
        self.commit('baseline');base=self.git('rev-parse','HEAD')
        self.git('tag','-a','v1.13','-m',json.dumps({'state':'TESTED_RELEASE','version':'1.13','main_commit':base,'target':self.target,'run_id':1}))
        self.git('checkout','-b','candidate');self.write('app.txt','v1.14 payload');self.commit('candidate')
        self.candidate=self.git('rev-parse','HEAD')
        self.git('checkout','main');self.git('merge','--no-ff','candidate','-m','tested merge')
        self.main=self.git('rev-parse','HEAD')
        self.git('push','origin','main','--tags')
        self.published={'app_id':'test-only','status':'Ready','version':'2026-09-16T00:00:00Z','draft_version':'2026-09-16T00:00:00Z'}
        self.package=b'original tested package'
        self.receipt={'schema':1,'state':'TESTED_RELEASE','version':'1.14','main_commit':self.main,
                      'candidate_commit':self.candidate,'target':self.target,'run_id':123,'issue':29,
                      'published':self.published,'gates':self.gates,'package_sha256':hashlib.sha256(self.package).hexdigest()}

    def git(self,*args):
        return subprocess.check_output(['git',*args],cwd=self.root,text=True,stderr=subprocess.DEVNULL).strip()

    def write(self,path,text):
        path=self.root/path;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)

    def commit(self,message):
        self.git('add','.');self.git('commit','-m',message)

    def snapshot(self,receipt=None):
        self.git('checkout','-b','docs')
        self.write('README.md',readme_release.render((self.root/'README.md').read_text(),receipt or self.receipt,'owner/repo'))
        self.commit('README');return self.git('rev-parse','HEAD')

    def test_correct_snapshot_keeps_tested_payload_and_is_a_rollback_point(self):
        head=self.snapshot();receipt=release_snapshot.create_receipt(self.root,self.receipt,head,'owner/repo','docs')
        self.assertEqual(release_snapshot.verify(self.root,receipt,head)['changed_files'],['README.md'])
        self.assertEqual(self.git('show',f'{head}:app.txt'),'v1.14 payload')
        self.git('tag','-a','v1.14',head,'-m',json.dumps(receipt))
        self.assertEqual(releases.last_good(self.root,self.target,'fallback'),'v1.14')
        bad=copy.deepcopy(receipt);bad['version']='1.15'
        self.git('tag','-a','v1.15',head,'-m',json.dumps(bad))
        self.assertEqual(releases.last_good(self.root,self.target,'fallback'),'v1.14')

    def test_old_readme_version_is_rejected_even_with_matching_digest(self):
        old=copy.deepcopy(self.receipt);old['version']='1.13'
        head=self.snapshot(old)
        with self.assertRaisesRegex(ValueError,'README and tag versions differ'):
            release_snapshot.create_receipt(self.root,self.receipt,head,'owner/repo','docs')

    def test_non_readme_change_cannot_be_promoted_as_documentation(self):
        self.snapshot();self.write('app.txt','untested payload');self.commit('bad change')
        with self.assertRaisesRegex(ValueError,'other than README'):
            release_snapshot.create_receipt(self.root,self.receipt,self.git('rev-parse','HEAD'),'owner/repo','docs')

    def test_failed_gate_wrong_run_and_digest_are_rejected(self):
        head=self.snapshot();receipt=release_snapshot.create_receipt(self.root,self.receipt,head,'owner/repo','docs')
        for key in ['gate','run','digest']:
            bad=copy.deepcopy(receipt)
            if key=='gate':bad['gates']['p0']='failure'
            if key=='run':bad['run_id']=999
            if key=='digest':bad['readme_sha256']='wrong'
            with self.assertRaises(ValueError):release_snapshot.verify(self.root,bad,head)

    def exercise_finalizer(self,merged=False):
        evidence=Path(self.temp.name)/'evidence';(evidence/'release-candidate').mkdir(parents=True,exist_ok=True)
        (evidence/'release-candidate/solution.zip').write_bytes(self.package)
        (evidence/'release-candidate/published.json').write_text(json.dumps(self.published))
        (evidence/'result.json').write_text(json.dumps({'state':'RELEASE_CANDIDATE_PASSED','commit':self.candidate,
            'target':self.target,'request':self.request,'attempts':[{'name':'release-candidate','gates':self.gates,
            'package_sha256':self.receipt['package_sha256']}]}))
        actual_output=subprocess.check_output;actual_run=subprocess.run;calls=[]
        def output(args,**kwargs):
            calls.append(args)
            if args[:2]==['gh','api']:
                return json.dumps({'workflow_runs':[{'id':123,'head_sha':self.candidate,'status':'completed','conclusion':'success',
                    'path':'.github/workflows/staff-master-transaction.yml','event':'push','run_attempt':1}]})
            if args[:3]==['gh','pr','list']:
                if merged:
                    head=actual_output(['git','rev-parse','v1.14^{commit}'],cwd=self.root,text=True).strip()
                    return json.dumps([{'url':'https://github.com/owner/repo/pull/30','state':'MERGED','headRefOid':head}])
                return '[]'
            if args[:3]==['gh','pr','create']:
                raise subprocess.CalledProcessError(1,args,stderr='GitHub Actions is not permitted to create or approve pull requests')
            return actual_output(args,**kwargs)
        def run(args,**kwargs):
            calls.append(args)
            if args[:3]==['gh','run','download']:
                shutil.copytree(evidence,Path(args[args.index('--dir')+1]),dirs_exist_ok=True)
                return subprocess.CompletedProcess(args,0)
            if args[:3]==['gh','issue','comment']:return subprocess.CompletedProcess(args,0)
            if args[0]=='git':
                kwargs.setdefault('stdout',subprocess.DEVNULL);kwargs.setdefault('stderr',subprocess.DEVNULL)
            return actual_run(args,**kwargs)
        env={'GITHUB_REPOSITORY':'owner/repo','GITHUB_SHA':self.main,'GITHUB_REF':'refs/heads/main',
             'GITHUB_STEP_SUMMARY':str(Path(self.temp.name)/'summary.md')}
        with patch.dict(os.environ,env),patch('subprocess.check_output',side_effect=output),patch('subprocess.run',side_effect=run):
            runpy.run_path(str(self.root/'scripts/automation/finalize_release.py'),run_name='__main__')
        return calls

    def test_real_git_finalizer_prepares_readme_before_tag_and_reuses_it_on_resume(self):
        calls=self.exercise_finalizer()
        receipt=json.loads(self.git('for-each-ref','--format=%(contents)','refs/tags/v1.14'))
        head=self.git('rev-parse','v1.14^{commit}');old_object=self.git('rev-parse','v1.14')
        self.assertNotEqual(head,self.main)
        self.assertEqual(receipt['main_commit'],self.main)
        self.assertEqual(receipt['candidate_commit'],self.candidate)
        self.assertEqual(release_snapshot.verify(self.root,receipt,head)['state'],'VERIFIED')
        tag_index=next(i for i,c in enumerate(calls) if c[:3]==['git','tag','-a'])
        commit_index=next(i for i,c in enumerate(calls) if c[:2]==['git','commit'])
        self.assertLess(commit_index,tag_index)
        self.assertEqual(json.loads((self.root/'artifacts/release/readme-update.json').read_text())['state'],'PENDING_WORK_PR')
        # Same original request after Work merged the PR must not recreate the tag.
        self.exercise_finalizer(merged=True)
        self.assertEqual(self.git('rev-parse','v1.14'),old_object)
        self.assertEqual(json.loads((self.root/'artifacts/release/readme-update.json').read_text())['state'],'MERGED')

    def test_finalizer_does_not_tag_a_stale_readme(self):
        original=readme_release.render
        def stale(text,receipt,repo):
            wrong=copy.deepcopy(receipt);wrong['version']='1.13'
            return original(text,wrong,repo)
        with patch.object(readme_release,'render',side_effect=stale):
            with self.assertRaisesRegex(ValueError,'README and tag versions differ'):
                self.exercise_finalizer()
        self.assertEqual(self.git('tag','--list','v1.14'),'')
        self.assertEqual(self.git('ls-remote','origin','refs/tags/v1.14'),'')

    def exercise_repair(self,old_object):
        actual_run=subprocess.run
        def run(args,**kwargs):
            if args[:3]==['gh','issue','comment']:return subprocess.CompletedProcess(args,0)
            if args[0]=='git':
                kwargs.setdefault('stdout',subprocess.DEVNULL);kwargs.setdefault('stderr',subprocess.DEVNULL)
            return actual_run(args,**kwargs)
        env={'GITHUB_REPOSITORY':'owner/repo','GITHUB_REF':'refs/heads/main','GITHUB_RUN_ID':'456',
             'GITHUB_STEP_SUMMARY':str(Path(self.temp.name)/'repair-summary.md')}
        with patch.dict(os.environ,env),patch.multiple(repair_v114_readme,REPO='owner/repo',OLD_TAG=old_object,
                OLD_MAIN=self.main,__file__=str(self.root/'scripts/automation/repair_v114_readme.py')),patch('subprocess.run',side_effect=run):
            repair_v114_readme.main()

    def old_v114(self):
        self.git('tag','-a','v1.14',self.main,'-m',json.dumps(self.receipt))
        self.git('push','origin','refs/tags/v1.14')
        return self.git('rev-parse','v1.14')

    def test_repair_archives_exact_original_and_changes_only_readme_idempotently(self):
        original=self.old_v114();self.exercise_repair(original)
        corrected=self.git('rev-parse','v1.14')
        self.assertNotEqual(corrected,original)
        self.assertEqual(self.git('rev-parse','refs/tags/archive/v1.14-before-readme-fix'),original)
        self.assertEqual(self.git('diff','--name-only',self.main,'v1.14'), 'README.md')
        self.assertEqual(self.git('rev-parse','main'),self.main)
        self.assertEqual(releases.last_good(self.root,self.target,'fallback'),'v1.14')
        self.exercise_repair(original)
        self.assertEqual(self.git('rev-parse','v1.14'),corrected)

    def test_repair_remote_tag_race_rejects_both_archive_and_overwrite(self):
        original=self.old_v114();other=self.git('rev-parse','v1.13')
        subprocess.run(['git','--git-dir',str(self.origin),'update-ref','refs/tags/v1.14',other],check=True)
        with self.assertRaises(subprocess.CalledProcessError):self.exercise_repair(original)
        self.assertEqual(self.git('ls-remote','origin','refs/tags/v1.14').split()[0],other)
        self.assertEqual(self.git('ls-remote','origin','refs/tags/archive/v1.14-before-readme-fix'),'')
