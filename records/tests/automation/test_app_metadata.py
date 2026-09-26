import ast
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import Mock

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/automation'))
import app_metadata


class AppMetadataTests(unittest.TestCase):
    def test_name_only_changes_and_xml_is_escaped(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'app.meta.xml'
            before='<CanvasApp><Name>fixed_schema</Name><DisplayName>old</DisplayName><Status>Ready</Status></CanvasApp>'
            path.write_text(before,encoding='utf-8-sig')
            app_metadata.normalize_display_name(path,'A & B')
            self.assertEqual(path.read_text(encoding='utf-8-sig'),before.replace('>old<','>A &amp; B<'))

    def test_ambiguous_or_empty_names_fail_without_writing(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'app.meta.xml'
            for xml,name in [('<CanvasApp/>','new'),('<CanvasApp><DisplayName>a</DisplayName><DisplayName>b</DisplayName></CanvasApp>','new'),('<CanvasApp><DisplayName>a</DisplayName></CanvasApp>','')]:
                path.write_text(xml)
                with self.assertRaises(ValueError):app_metadata.normalize_display_name(path,name)
                self.assertEqual(path.read_text(),xml)

    def test_pack_of_old_tag_uses_current_name_without_changing_source(self):
        tree=ast.parse((ROOT/'scripts/automation/run_pipeline.py').read_text())
        pack=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='pack')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'old-tag';folder=root/'powerapps/solution-src/CanvasApps';folder.mkdir(parents=True)
            (folder/'app.msapp').write_bytes(b'unchanged payload')
            original='<CanvasApp><Name>fixed_schema</Name><DisplayName>old</DisplayName></CanvasApp>'
            (folder/'app.meta.xml').write_text(original)
            def command(args,log):Path(args[args.index('--zipfile')+1]).write_bytes(b'packed fixture')
            bridge=Mock();bridge.require=lambda condition,message: self.assertTrue(condition,message);bridge.digest=lambda data:'hash'
            scope=dict(Path=Path,shutil=shutil,app_metadata=app_metadata,CFG={'display_name':'自動開発_職員マスタ検索'},bridge=bridge,command=command)
            exec(compile(ast.Module(body=[pack],type_ignores=[]),'pack-fixture','exec'),scope)
            dest=Path(temp)/'result';scope['pack'](root,dest)
            self.assertIn('自動開発_職員マスタ検索',(dest/'solution/CanvasApps/app.meta.xml').read_text(encoding='utf-8-sig'))
            self.assertEqual((folder/'app.meta.xml').read_text(),original)
            self.assertEqual((dest/'solution/CanvasApps/app.msapp').read_bytes(),b'unchanged payload')
