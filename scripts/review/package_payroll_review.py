#!/usr/bin/env python3
"""Package only authored review artifacts and their already-versioned source references.
No repository history, hidden directories, credentials, Office originals or real data.
"""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile
ROOT=Path(__file__).resolve().parents[2]
REVIEW=ROOT/'docs/review/pay-html-001'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    model=json.loads((REVIEW/'data/model.json').read_text())
    paths={p for p in REVIEW.rglob('*') if p.is_file() and not any(x.startswith('.') for x in p.relative_to(REVIEW).parts)}
    paths.update(ROOT/s['path'] for s in model['sources'] if s['path'] != 'docs/operations/library-materials-index.md')
    paths.update((ROOT/'scripts/review').glob('*.py'))
    paths.update((ROOT/'tests/review').glob('*.py'))
    manifest=[]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        def put(name,content):
            info=zipfile.ZipInfo(name,date_time=(2026,10,9,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;archive.writestr(info,content)
        for path in sorted(paths):
            relative=path.relative_to(ROOT).as_posix()
            if path.suffix.lower() in {'.xlsx','.xls','.csv','.pdf','.msapp','.zip'}:raise ValueError('Unexpected original/artifact type: '+relative)
            content=path.read_bytes()
            # Portable source copies omit storage metadata unnecessary for review.
            if relative == 'config/dataverse/payrollledger-columns.json':
                source_copy=json.loads(content)
                source_copy.pop('source_library_id',None)
                content=(json.dumps(source_copy,ensure_ascii=False,indent=2)+'\n').encode()
            if relative == 'docs/handoff/STATUS.md':
                sha=model['metadata']['source_sha']
                url=f'https://github.com/hirokazu601218/PowerAppsCanvasAppUI/blob/{sha}/docs/handoff/STATUS.md'
                content=(
                    '# 現在の作業と読取り対象（参照案内）\n\n'
                    'この配布用コピーでは、作業履歴の全文を省略しています。\n'
                    f'元mainコミット: `{sha}`\n\n'
                    f'[リポジトリの参照元を開く]({url})\n\n'
                    '対象部分は2026-10-08人給連携、2026-10-07給与・通勤、2026-10-01画面構成です。'
                    'レビューの要件・設計の根拠は同梱の正本参照ファイルと各HTMLの出典一覧で確認してください。\n'
                    'この案内は正本の代替ではありません。\n'
                ).encode()
            put(relative,content)
            manifest.append({'path':relative,'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content)})
        put('START.html','''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PAY-HTML-001 入口</title><main><h1>非常勤給与アプリ レビューHTML</h1><p>非正本・未承認のレビュー資料です。実処理は行いません。</p><p><a href="docs/review/pay-html-001/index.html">4種類のレビュー資料を開く</a></p><p>ZIPを展開し、このSTART.htmlをブラウザーで開いてください。外部ネットワークは不要です。参照元のコピーを同じ階層で同梱しています。給与簿項目台帳のコピーでは保管先識別子を省略し、作業状況の履歴全文は元コミットの参照案内に置き換えています。正本は元コミットのリポジトリです。</p></main></html>'''.encode())
        put('artifact-manifest.json',(json.dumps({'version':model['metadata']['version'],'source_sha':model['metadata']['source_sha'],'files':manifest},ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'output':str(args.output),'files':len(manifest)+2,'bytes':args.output.stat().st_size,'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()},ensure_ascii=False))
if __name__=='__main__':main()
