import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts/automation'))
import releases


class ReleasesTests(unittest.TestCase):
    def test_only_verified_target_tags_become_rollback_points(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            def git(*args):
                return subprocess.check_output(['git',*args],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
            git('init','-b','main')
            git('config','user.name','Test')
            git('config','user.email','test@example.invalid')
            git('commit','--allow-empty','-m','fixture')
            sha=git('rev-parse','HEAD')
            target={'environment_id':'isolated','app_id':'test-only'}
            self.assertEqual(releases.last_good(root,target,sha),sha)
            git('tag','v9.99')
            git('tag','-a','v8.88','-m','not a release receipt')
            self.assertEqual(releases.last_good(root,target,sha),sha)
            receipt={'state':'TESTED_RELEASE','version':'1.12','main_commit':sha,'target':target,'run_id':1}
            git('tag','-a','v1.12','-m',json.dumps(receipt))
            self.assertEqual(releases.last_good(root,target,sha),'v1.12')
            self.assertEqual(releases.last_good(root,{'app_id':'production'},sha),sha)
            receipt['version']='2.00';receipt['main_commit']='wrong'
            git('tag','-a','v2.00','-m',json.dumps(receipt))
            self.assertEqual(releases.last_good(root,target,sha),'v1.12')
