import copy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts/automation'))
import readme_release


class ReadmeReleaseTests(unittest.TestCase):
    def setUp(self):
        self.receipt={'state':'TESTED_RELEASE','version':'1.14','run_id':123,'issue':23,
                      'published':{'version':'2026-09-16T00:00:00Z'},
                      'gates':dict.fromkeys(('build','auth','import','publish','readback','change_test','p0'),'success')}
        self.text='manual intro\n'+readme_release.START+'\nold\n'+readme_release.END+'\nmanual instructions\n'

    def test_preserves_manual_content_and_is_idempotent(self):
        result=readme_release.render(self.text,self.receipt,'owner/repo')
        self.assertTrue(result.startswith('manual intro\n'))
        self.assertTrue(result.endswith('\nmanual instructions\n'))
        self.assertIn('/tree/v1.14',result)
        self.assertIn('/actions/runs/123',result)
        self.assertEqual(result,readme_release.render(result,self.receipt,'owner/repo'))

    def test_rejects_missing_evidence_and_ambiguous_markers(self):
        for gate in self.receipt['gates']:
            invalid=copy.deepcopy(self.receipt);invalid['gates'][gate]='failure'
            with self.assertRaises(ValueError):readme_release.render(self.text,invalid,'owner/repo')
        for text in ['no markers',self.text+readme_release.START,readme_release.END+readme_release.START]:
            with self.assertRaises(ValueError):readme_release.render(text,self.receipt,'owner/repo')

    def test_publication_uses_documentation_pr_and_exact_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'README.md').write_text(self.text)
            with patch.object(readme_release.subprocess,'run') as run, patch.object(
                    readme_release.subprocess,'check_output',side_effect=['doc-sha\n','https://github.com/owner/repo/pull/10\n']) as output:
                readme_release.publish(root,self.receipt,'owner/repo')
            commands=[call.args[0] for call in run.call_args_list]
            pushes=[c for c in commands if c[:2]==['git','push']]
            self.assertEqual(len(pushes),1)
            self.assertTrue(pushes[0][-1].startswith('HEAD:refs/heads/automation/readme-v1.14-'))
            self.assertIn(['gh','pr','merge','https://github.com/owner/repo/pull/10','--repo','owner/repo',
                           '--merge','--match-head-commit','doc-sha'],commands)
            self.assertIn('--body-file',output.call_args_list[1].args[0])
