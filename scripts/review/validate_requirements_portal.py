#!/usr/bin/env python3
"""Validate the static portal without pretending to run a browser.

The optional --baseline checks preservation and document placement against a
verified checkout. It does not require Git metadata or contact a remote service.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from lxml import html

ROOT = Path(__file__).resolve().parents[2]
PORTAL = ROOT / 'docs/requirements/standard-template'
REVIEW = ROOT / 'docs/review/pay-html-001'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(text):
    return re.sub(r'\s+', ' ', text).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    checks = []

    def check(condition, name, details=None):
        checks.append({'name': name, 'status': 'PASS' if condition else 'FAIL',
                       'details': details})

    sections = json.loads((PORTAL / 'requirements-data.json').read_text())
    supplements = json.loads((PORTAL / 'section-supplements.json').read_text())
    supplement_by_id = {item['id']: item for item in supplements['sections']}
    effective_sections = json.loads(json.dumps(sections))
    for section in effective_sections['sections']:
        if section['id'] in supplement_by_id:
            section.update(supplement_by_id[section['id']])
    portal = json.loads((PORTAL / 'portal-data.json').read_text())
    template = json.loads((PORTAL / 'template-detail-map.json').read_text())
    model = json.loads((REVIEW / 'data/model.json').read_text())
    pages = {p.resolve(): html.fromstring(p.read_text())
             for folder in (PORTAL, REVIEW) for p in folder.rglob('*.html')}
    known_ids = {p: set(tree.xpath('//@id')) for p, tree in pages.items()}
    link_errors, duplicates, dependency_errors = [], [], []
    link_count = 0

    for path, tree in pages.items():
        identifiers = tree.xpath('//@id')
        if len(identifiers) != len(set(identifiers)):
            duplicates.append(str(path.relative_to(ROOT)))
        for url in tree.xpath('//@href|//@src'):
            parsed = urlsplit(url)
            if parsed.scheme or parsed.netloc:
                continue
            link_count += 1
            target = ((path.parent / unquote(parsed.path)).resolve()
                      if parsed.path else path)
            if not target.exists():
                link_errors.append([str(path.relative_to(ROOT)), url, 'file'])
            elif parsed.fragment and target in pages:
                if unquote(parsed.fragment) not in known_ids[target]:
                    link_errors.append([str(path.relative_to(ROOT)), url, 'anchor'])
        for url in tree.xpath('//script/@src|//link[@rel="stylesheet"]/@href|//img/@src'):
            if urlsplit(url).scheme not in ('', 'data') or url.startswith('//'):
                dependency_errors.append([str(path.relative_to(ROOT)), url])

    check(not link_errors, 'All relative files and anchors resolve', link_errors)
    check(not duplicates, 'HTML IDs are unique per page', duplicates)
    check(not dependency_errors, 'No external runtime assets or CDN', dependency_errors)
    check(len(sections['sections']) == 140, 'All 140 legacy IDs retained')
    check(portal['coverage'] == {
        'headings': 140, 'content': 109, 'documented': 10,
        'partial': 51, 'unset': 48,
    }, 'Coverage includes thirteen evidence-backed corrections, without counting template examples')

    missing_content = []
    for section in effective_sections['sections']:
        page = (PORTAL / 'sections' / f"{section['id']}.html").resolve()
        text = normalize(pages[page].text_content())
        for field in ('title', 'text', 'missing'):
            if section[field] and normalize(section[field]) not in text:
                missing_content.append([section['id'], field])
        if 'section-' + section['id'] not in known_ids[page]:
            missing_content.append([section['id'], 'stable anchor'])
    check(not missing_content, 'All effective section body and remaining-unknown text retained', missing_content)

    supplement_errors = []
    for supplement in supplements['sections'] + supplements.get('template_sections', []):
        for reference in supplement['source_refs']:
            source_lines = (ROOT / reference['path']).read_text().split('\n')
            actual_quote = '\n'.join(source_lines[reference['line'] - 1:reference['end_line']])
            if actual_quote != reference['quote'] or digest(ROOT / reference['path']) != reference['sha256']:
                supplement_errors.append([supplement['id'], 'canonical quote changed', reference['path']])
            filename = reference['path'].replace('/', '--').removesuffix('.md') + '.html'
            target = (PORTAL / 'sources' / filename).resolve()
            if 'L' + str(reference['line']) not in known_ids[target]:
                supplement_errors.append([supplement['id'], reference])
        folder = 'template-sections' if supplement.get('section_kind') == 'template_extra' else 'sections'
        target = (PORTAL / folder / f"{supplement['id']}.html").resolve()
        # Explicitly choose the supplemental namespace to avoid legacy 3.14.1.
        if supplement in supplements.get('template_sections', []):
            target = (PORTAL / 'template-sections' / f"{supplement['id']}.html").resolve()
        for field in ('text', 'missing', 'state'):
            if normalize(supplement[field]) not in normalize(pages[target].text_content()):
                supplement_errors.append([supplement['id'], folder, field])
    check(not supplement_errors and len(supplements['sections']) == 13
          and len(supplements.get('template_sections', [])) == 7,
          'All 20 supplements retain body/unknowns and exact canonical quotes', supplement_errors)


    check(len(template['effective_outline']) == 321,
          'Full official effective outline has 321 paragraphs')
    core = [item for item in template['effective_outline'] if item['level'] <= 3]
    extras = [item for item in template['additional_outline_items']
              if item['type'] == 'template_detail_heading']
    check(len(core) == 148 and len(extras) == 8,
          '148 official core headings and 8 supplemental heading pages')
    template_text = normalize(pages[(PORTAL / 'template-details.html').resolve()].text_content())
    extra_errors = []
    for item in extras:
        page = (PORTAL / 'template-sections' / f"{item['source_outline_id']}.html").resolve()
        if page not in pages or item['title'] not in pages[page].text_content():
            extra_errors.append(item['source_outline_id'])
        if item['title'] not in template_text:
            extra_errors.append(item['source_outline_id'] + ':mapping')
    check(not extra_errors, 'Supplemental headings are visible and linked', extra_errors)
    for collection, expected in [('additional_details', 166), ('table_schemas', 56),
                                 ('illustrations', 11), ('authoring_guidance', 132)]:
        items = template[collection]
        failures = []
        for item in items:
            visible = item.get('label') or item.get('caption') or item.get('text') or item.get('title')
            if visible and normalize(visible) not in template_text:
                failures.append(item.get('id'))
        check(len(items) == expected and not failures,
              f'{collection}: all {expected} items have visible content', failures)

    migration = pages[(PORTAL / 'sections/3.14.1.html').resolve()]
    heading = normalize(' '.join(migration.xpath('//h1//text()')))
    check('3.14.2 移行計画の作成' == heading,
          'Legacy migration-plan ID retains its meaning and shows official position')
    check('section-3.14.1' in known_ids[(PORTAL / 'index.html').resolve()],
          'Old index hash remains available')

    contract_fields = ['origin_tab', 'origin_mode', 'destination_tab', 'destination_mode',
                       'control', 'method', 'row_scope', 'visible', 'enabled', 'preconditions',
                       'validation', 'process', 'retained', 'reset', 'success', 'failure',
                       'cancel', 'unsaved']
    operation_errors = []
    for operation in model['operations']:
        page = (PORTAL / 'operations' / f"{operation['id']}.html").resolve()
        tree = pages[page]
        text = normalize(tree.text_content())
        for field in contract_fields:
            if normalize(operation[field]) not in text:
                operation_errors.append([operation['id'], field])
        for field in ['reads', 'writes', 'acceptance', 'notes', 'roles']:
            for value in operation[field]:
                if normalize(value) not in text:
                    operation_errors.append([operation['id'], field, value])
    check(not operation_errors, 'All 100 operation contracts retain every field', operation_errors)

    flow_errors = []
    for workflow in model['workflows']:
        new = pages[(PORTAL / 'workflows' / f"{workflow['id']}.html").resolve()]
        old = pages[(REVIEW / 'workflows' / f"{workflow['id'].lower()}.html").resolve()]
        for attribute in ('data-edge-id', 'data-node-id'):
            original = set(old.xpath(f'//svg//@{attribute}'))
            generated = set(new.xpath(f'//svg//@{attribute}'))
            if original != generated:
                flow_errors.append([workflow['id'], attribute])
        text = normalize(new.text_content())
        for step in workflow['steps']:
            if normalize(step['detail']) not in text:
                flow_errors.append([workflow['id'], step['id'], 'detail'])
        for edge in workflow['edges']:
            if normalize(edge['label']) not in text:
                flow_errors.append([workflow['id'], edge, 'condition'])
    check(not flow_errors, 'All 15 connected workflow diagrams and textual paths retained', flow_errors)

    source_errors = []
    for source in portal['sources']:
        if digest(ROOT / source['path']) != source['sha256']:
            source_errors.append([source['path'], 'hash'])
    for requirement in portal['requirements']:
        if not requirement['source_resolved']:
            source_errors.append([requirement['id'], 'unresolved'])
        for reference in requirement['source_refs']:
            filename = reference['path'].replace('/', '--')
            if filename.endswith('.md'):
                filename = filename[:-3]
            target = (PORTAL / 'sources' / (filename + '.html')).resolve()
            if 'L' + str(reference['line']) not in known_ids[target]:
                source_errors.append([requirement['id'], reference])
    check(not source_errors, 'Source hashes and 253 exact excerpt anchors resolve', source_errors)

    fixtures = {
        'requirements/I12.html': '確定',
        'requirements/I8.html': '表示要件は確定・取得方式未設定',
        'requirements/PAYREQ-07.html': '確定（未設定の方式は別記）',
        'operations/OP-PAY-CALCULATE.html': '操作・配置は提案（業務要件は別）',
    }
    status_errors = []
    for filename, expected in fixtures.items():
        tree = pages[(PORTAL / filename).resolve()]
        actual = tree.xpath('//dl[contains(@class,"status-grid")]/div[2]/dd/text()')
        if actual != [expected]:
            status_errors.append([filename, expected, actual])
    check(not status_errors, 'Canonical decision and layout categories remain independent', status_errors)

    old_review_pages = [tree for path, tree in pages.items() if path.is_relative_to(REVIEW)]
    check(len(old_review_pages) == 46 and all(
        tree.xpath('//a[@data-context-return]') and
        any('standard-template' in link for link in tree.xpath('//@href'))
        for tree in old_review_pages), 'All 46 original review pages link back to requirements')

    mobile = pages[(PORTAL / 'index-mobile.html').resolve()]
    check(not mobile.xpath('//script|//iframe|//a|//link|//*[@src]') and
          (PORTAL / 'index-mobile.html').stat().st_size < 100_000,
          'Quick Look fallback is a bounded, dependency-free reading sheet')
    check('未実施' in pages[(PORTAL / 'reading-guide.html').resolve()].text_content(),
          'Browser and iPhone verification limits are explicit')

    # DOT-002 integration guards: expose the approved prose, not just its heading.
    screen_source = (ROOT / 'docs/requirements/screen-requirements.md').read_text()
    approval = screen_source.split('## DOT-001：SCR005-UI-004／015の承認A追補\n\n')[1].strip()
    approval = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', approval)
    approval_pages = ['requirements/SCR005-UI-004.html',
                      'requirements/SCR005-UI-015.html', 'screens/SCR-005.html']
    check(all(normalize(approval) in normalize(pages[(PORTAL / name).resolve()].text_content())
              for name in approval_pages),
          'Approval A full body is visible from both requirements and SCR-005')
    status_text = pages[(PORTAL / 'sources/docs--handoff--STATUS.html').resolve()].text_content()
    check('DOT-001 文書・HTML整合' in status_text and '7節' in status_text,
          'Selected STATUS includes latest DOT-001 and declares its scope')
    input_hash_errors = [source['path'] for source in sections['metadata']['sources']
                         if digest(ROOT / source['path']) != source['sha256']]
    check(not input_hash_errors, 'All requirements-data canonical file hashes match', input_hash_errors)
    record_folder = ROOT / 'records/changes/dot-001/manual-20261010-handoff'
    check(all((record_folder / name).is_file() for name in
              ['QA-REPORT.md', 'record.json', 'player38-sanitized.json',
               'published38-source-summary.json']), 'All four DOT-001 handoff records retained')
    check(portal['metadata']['live38_included'] is True
          and portal['metadata']['source_commit'] == model['metadata']['source_sha'],
          'DOT-001 observation provenance agrees with paired display model')

    preservation_file = ROOT / sections['metadata'].get('preservation_manifest', 'records/changes/dot-002/manual-20261010-integration/canonical-preservation-baseline.json')
    check(preservation_file.is_file(), 'Declared canonical preservation baseline exists')
    if preservation_file.is_file():
        frozen = json.loads(preservation_file.read_text())
        preservation_errors = [item['path'] for item in frozen['files']
                               if digest(ROOT / item['path']) != item['sha256']]
        check(not preservation_errors, 'All frozen canonical and historical inputs preserved', preservation_errors)

    publication = sections['metadata'].get('publication')
    if publication:
        capture = json.loads((ROOT / publication['record_path']).read_text())
        source_text = pages[(PORTAL / 'sources.html').resolve()].text_content()
        check(digest(ROOT / publication['record_path']) == publication['record_sha256']
              and publication['lastPublishTime'] == capture['publication']['lastPublishTime']
              and publication['download_sha256'] == capture['publication']['download_sha256']
              and publication['run_status'] == capture['status'] == 'FAIL'
              and publication == model['metadata']['publication'] == portal['metadata']['app_publication']
              and publication['lastPublishTime'] in source_text
              and publication['download_sha256'] in source_text
              and '旧v25画面SHA guard不一致でFAIL' in source_text,
              'P/H capture succeeds independently of failed legacy guard; model, source, and record agree')

    changed_files = []
    if args.baseline:
        baseline = args.baseline.resolve()
        protected = [source['path'] for source in portal['sources']]
        protected += ['docs/requirements/standard-template/requirements-data.json',
                      'docs/review/pay-html-001/data/model.json']
        modified = [name for name in protected if not (baseline / name).is_file() or
                    digest(ROOT / name) != digest(baseline / name)]
        check(not modified, 'Canonical inputs remain byte-identical to selected DOT-001 integration baseline', modified)
        for path in sorted(ROOT.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts or '.git' in path.parts:
                continue
            relative = str(path.relative_to(ROOT))
            previous = baseline / relative
            if not previous.exists() or digest(path) != digest(previous):
                changed_files.append(relative)
        module_path = ROOT / 'scripts/governance/validate_document_placement.py'
        spec = importlib.util.spec_from_file_location('document_placement', module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        try:
            placement = module.validate(ROOT, [('', name) for name in changed_files])
            check(True, 'Document placement validates explicit changed-file list', placement)
        except Exception as error:
            check(False, 'Document placement validates explicit changed-file list', str(error))

    report = {
        'method': 'Static HTML/source checks only. NOT browser or iPhone validation.',
        'source_commit': portal['metadata']['source_commit'],
        'pages': len(pages), 'relative_links': link_count,
        'checks': checks, 'changed_files': changed_files,
        'result': 'PASS_STATIC' if all(c['status'] == 'PASS' for c in checks) else 'FAIL_STATIC',
    }
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.report:
        args.report.write_text(text)
    print(text)
    return 0 if report['result'] == 'PASS_STATIC' else 1


if __name__ == '__main__':
    sys.exit(main())
