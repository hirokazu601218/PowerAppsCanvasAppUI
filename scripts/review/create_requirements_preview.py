#!/usr/bin/env python3
"""Create a four-page content review PDF, not a browser screenshot.

Reads exact confirmed text from the portal's model and section supplements.
Requires the already installed PyMuPDF and Noto Sans CJK Japanese font.
"""
import argparse
import hashlib
import json
from pathlib import Path

import fitz
from fontTools import subset
from fontTools.ttLib import TTFont
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PORTAL = ROOT / 'docs/requirements/standard-template'
FONT_PATH = Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
INK = (0.09, 0.20, 0.30)
BLUE = (0.04, 0.32, 0.60)
MUTED = (0.32, 0.40, 0.48)
PAPER = (1, 1, 1)
LIGHT = (0.93, 0.96, 0.99)
AMBER = (0.99, 0.95, 0.86)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not FONT_PATH.exists():
        raise SystemExit('Japanese font unavailable; PDF not produced.')

    model = json.loads((ROOT / 'docs/review/pay-html-001/data/model.json').read_text())
    sections = json.loads((PORTAL / 'requirements-data.json').read_text())['sections']
    supplements = json.loads((PORTAL / 'section-supplements.json').read_text())
    supplemental = {item['id']: item for item in supplements['sections']}
    for section in sections:
        if section['id'] in supplemental:
            section.update(supplemental[section['id']])
    by_section = {section['id']: section for section in sections}
    by_operation = {operation['id']: operation for operation in model['operations']}
    portal_data = json.loads((PORTAL / 'portal-data.json').read_text())
    template = json.loads((PORTAL / 'template-detail-map.json').read_text())
    numbering = {item['id']: item['source_outline_id'] for item in template['core_heading_coverage']}

    # Subset with fontTools before embedding. MuPDF's CFF post-subsetter does
    # not support every operator in the full Noto collection.
    characters = Path(__file__).read_text() + json.dumps(model, ensure_ascii=False)
    characters += json.dumps(sections, ensure_ascii=False)
    japanese_font = TTFont(str(FONT_PATH), fontNumber=0)
    subsetter = subset.Subsetter()
    subsetter.populate(text=characters)
    subsetter.subset(japanese_font)
    temporary_font = Path(tempfile.gettempdir()) / 'dot002-preview-japanese.otf'
    japanese_font.save(temporary_font)
    document = fitz.open()
    font = fitz.Font(fontfile=str(temporary_font))
    source_records = []

    def lines(text, width, size):
        result, current = [], ''
        for paragraph in str(text).split('\n'):
            for char in paragraph:
                if current and font.text_length(current + char, fontsize=size) > width:
                    result.append(current)
                    current = char
                else:
                    current += char
            result.append(current)
            current = ''
        return result

    def new_page(number, eyebrow, title):
        page = document.new_page(width=595.28, height=841.89)
        page.insert_font(fontname='Japanese', fontfile=str(temporary_font))
        page.draw_rect(fitz.Rect(0, 0, 595.28, 9), color=None, fill=BLUE)
        page.insert_text((40, 35), eyebrow, fontname='Japanese', fontsize=9, color=BLUE)
        page.insert_text((40, 67), title, fontname='Japanese', fontsize=22, color=INK)
        page.draw_line((40, 783), (555, 783), color=(0.78, 0.83, 0.88), width=0.6)
        page.insert_text((40, 800), 'DOT-002 / 構成確認用PDF / Web画面の見た目の再現ではありません',
                         fontname='Japanese', fontsize=8, color=MUTED)
        page.insert_text((40, 815), 'ブラウザー操作・iPhone表示は未検証。正本は既存Markdown。',
                         fontname='Japanese', fontsize=8, color=MUTED)
        page.insert_text((533, 815), f'{number} / 4', fontname='Japanese', fontsize=8, color=MUTED)
        return page

    def write(page, y, text, size=10.5, color=INK, x=40, width=515, leading=1.65):
        wrapped = lines(text, width, size)
        for line in wrapped:
            if y > 767:
                raise ValueError(f'PDF content overflow on page {page.number + 1}')
            page.insert_text((x, y), line, fontname='Japanese', fontsize=size, color=color)
            y += size * leading
        return y

    def block(page, y, title, body, fill=LIGHT):
        height = 29 + len(lines(body, 487, 10.2)) * 16.5 + 12
        if y + height > 771:
            raise ValueError(f'PDF block overflow: {title}')
        page.draw_rect(fitz.Rect(40, y, 555, y + height), color=None, fill=fill)
        write(page, y + 20, title, size=12, color=BLUE, x=54, width=487)
        write(page, y + 41, body, size=10.2, x=54, width=487, leading=1.61)
        return y + height + 12

    page = new_page(1, 'REQUIREMENTS REVIEW / 2026-10-10', '必要な要件に、迷わずたどり着く')
    y = write(page, 98, 'HTML本文から作成した構成確認用PDF。Web画面の見た目の再現ではありません。',
              size=10, color=MUTED)
    y = block(page, y + 12, '業務利用者の入口',
              '業務の流れ → 画面一覧。どこから始め、何を入力・確認し、何をもって完了するかを読みます。')
    y = block(page, y, '設計・構築者の入口',
              '標準の章立て → 要件ID・操作。担当、対象範囲、前提、データの参照・変更、例外、出典へ進みます。')
    y = block(page, y, '流れをつかむ',
              '給与情報を整える → 勤務実績をそろえる → 計算する → 人給と照合する → 確定後の追給・返納を扱う。')
    y = block(page, y, '仕様・実装・検証を混ぜない',
              '記載の充足、要件の判断、実装の状態、実機の検証を別々に表示します。画面モックはPower Appsの実装・保存・認可の証明ではありません。', fill=AMBER)
    coverage = portal_data['coverage']
    y = write(page, y + 5, f"標準の上位3階層148見出し。既存本文109項目は記載済み{coverage['documented']}、一部設定{coverage['partial']}、要件未設定{coverage['unset']}。", size=10)
    write(page, y + 8, '閲覧入口: docs/requirements/standard-template/index.html', size=9, color=MUTED)
    source_records.append('docs/requirements/standard-template/index.html')

    page = new_page(2, 'REQUIREMENT → SCREEN → SOURCE', '例: 人給連携の要件を確認する')
    y = block(page, 90, '2.5.1 外部インタフェース一覧', by_section['2.5.1']['text'])
    y = block(page, y, 'FUT-JLINK / 人給連携の画面',
              '支給回の状況 / 出力 / 取込・照合の3タブ。支給回を保持してタブを切り替えます。計算版選択を置かず、出力元となる最新版の計算結果と照合します。')
    y = block(page, y, '利用者が確認する流れ',
              '対象とA/Mを指定し、Excel出力前に人数・明細数等を確認します。人給へは利用者が切り替え、給与簿CSVを戻します。差分原因の画面へ戻って訂正し、再計算・再照合します。')
    y = block(page, y, '関連する資料へ、そのまま進む',
              '標準要件2.5.1 → 業務WF-13 → 要件I12 → 操作OP-JLINK-CONFIRM。根拠資料には元要件への戻りリンクと参照元一覧があります。')
    y = block(page, y, '残っている要件未設定', by_section['2.5.1']['missing'], fill=AMBER)
    write(page, y + 1, '出典: sections/2.5.1.html / workflows/WF-13.html / screens/FUT-JLINK.html', size=8.7, color=MUTED)
    source_records.extend(['docs/requirements/standard-template/sections/2.5.1.html',
                           'docs/requirements/standard-template/workflows/WF-13.html'])

    operation = by_operation['OP-JLINK-CONFIRM']
    page = new_page(3, 'OP-JLINK-CONFIRM / I12', '例: 給与班が支給回を確定する')
    y = write(page, 96, '要件I12: 確定。画面配置・物理方式・実機検証の残件は別に扱います。', size=10, color=MUTED)
    y = block(page, y + 10, '担当・対象', ' / '.join(operation['roles']) + '。' + operation['row_scope'])
    for key, title in [('enabled', '実行できる条件'), ('process', '処理する内容'),
                       ('validation', '確定時に検証すること'), ('failure', '失敗時')]:
        y = block(page, y, title, operation[key])
    y = block(page, y, 'この資料で省略しない境界',
              'Excel出力前の確認と、支給回の給与班確定は別です。支給回の確定には確認ダイアログを出しません。表示フィルターで全体の確定条件を狭めません。', fill=AMBER)
    write(page, y + 1, '出典: requirements/I12.html / operations/OP-JLINK-CONFIRM.html', size=9, color=MUTED)
    source_records.append('docs/requirements/standard-template/operations/OP-JLINK-CONFIRM.html')

    page = new_page(4, 'OPEN REQUIREMENTS / READING GUIDE', '未設定を、次の判断につなげる')
    y = write(page, 96, '以下は未設定の例です。確定済みの部分を残し、未設定の条件だけを分けて表示します。', size=10, color=MUTED)
    for section_id in ['3.3.5', '3.4.2', '3.10.2', '3.13.3']:
        section = by_section[section_id]
        y = block(page, y + 7, f"{numbering.get(section_id, section_id)} {section['title']}", section['missing'])
    y = block(page, y + 7, 'iPhoneで詳細を読むには',
              '通常ブラウザー版をSafariでURL閲覧する方式が適しています。今回の成果物は未公開です。URL提供には配置先・閲覧範囲の承認が別途必要です。「ファイル」プレビュー用には、上から読むだけの短い要約を用意しています。', fill=AMBER)
    write(page, y + 5, 'PC: 展開した一式のindex.htmlを通常ブラウザーで開きます。\nこのPDFは全要件・全操作の代替ではありません。', size=10)
    source_records.append('docs/requirements/standard-template/open-items.html')

    document.set_metadata({'title': 'DOT-002 要件定義ポータル 構成確認用PDF',
                           'author': 'dot',
                           'subject': 'Static content preview. Not a browser rendering or interaction test.'})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    document.save(args.output, garbage=4, deflate=True)
    document.close()
    check = fitz.open(args.output)
    assert len(check) == 4
    assert all(page.get_text().strip() for page in check)
    fonts = [font_info for page in check for font_info in page.get_fonts(full=True)]
    assert fonts and all(font_info[0] > 0 for font_info in fonts)
    manifest = {
        'artifact': args.output.name,
        'pages': len(check),
        'method': 'PyMuPDF document layout with embedded Japanese Noto Sans CJK. Not browser rendering.',
        'source_pages': source_records,
        'sha256': hashlib.sha256(args.output.read_bytes()).hexdigest(),
        'font_resources': sorted(set((item[1], item[3]) for item in fonts)),
    }
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
