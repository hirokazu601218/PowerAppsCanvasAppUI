"""Exercise real transaction error handling with offline deployment substitutes."""
import ast
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/automation'))
import releases


class DriverTests(unittest.TestCase):
    def exercise(self,scenario):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'project'
            for path in ['config/apps/staff-master.json','automation/change.json','automation/release.json','automation/run.json']:
                dest=root/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/path).read_bytes())
            req=json.loads((root/'automation/run.json').read_text());req['mode']='release'
            (root/'automation/run.json').write_text(json.dumps(req))
            cfg=json.loads((root/'config/apps/staff-master.json').read_text())
            env={'RUNNER_TEMP':temp,'POWER_PLATFORM_TEST_ENVIRONMENT_URL':cfg['target']['dataverse_url'],
                 'POWER_PLATFORM_TARGET_APP_ID':cfg['target']['app_id'],'GITHUB_SHA':'offline-fixture'}
            tree=ast.parse((ROOT/'scripts/automation/run_pipeline.py').read_text())
            index=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.Try))
            scope={'__file__':str(root/'scripts/automation/run_pipeline.py')}
            with patch.dict(os.environ,env,clear=True),patch.object(releases,'last_good',return_value='baseline'),patch('subprocess.check_output',return_value=''):
                exec(compile(ast.Module(body=tree.body[:index],type_ignores=[]),'driver','exec'),scope)
                calls=[]
                def command(*args,**kwargs):
                    if scenario=='auth':raise RuntimeError('auth rejected')
                def attempt(*args):
                    scope['TOUCHED']=True;scope['STAGE']='p0'
                    return {'promotable':False}
                def restore():
                    calls.append('restore');scope['RESTORE_ATTEMPTED']=True
                    if scenario=='restore_failure':raise RuntimeError('restore rejected')
                    scope['RESTORED']=True;scope['SUMMARY']['restoration']={'state':'RESTORED'}
                scope.update(command=command,attempt=attempt,restore=restore)
                with self.assertRaises((RuntimeError,ValueError)):
                    exec(compile(ast.Module(body=tree.body[index:],type_ignores=[]),'driver','exec'),scope)
            result=json.loads((root/'artifacts/automation/result.json').read_text())
            return result,calls

    def test_auth_failure_does_not_touch_or_restore_app(self):
        result,calls=self.exercise('auth')
        self.assertEqual(result['state'],'BLOCKED');self.assertEqual(calls,[])

    def test_failed_p0_restores_instead_of_promoting(self):
        result,calls=self.exercise('p0')
        self.assertEqual(result['state'],'RESTORED_AFTER_FAILURE');self.assertEqual(calls,['restore'])

    def test_restore_failure_stops_without_a_second_deployment(self):
        result,calls=self.exercise('restore_failure')
        self.assertEqual(result['state'],'RESTORE_FAILED');self.assertEqual(calls,['restore'])
