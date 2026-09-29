import { expect, test } from '@playwright/test';
import { readFileSync } from 'node:fs';

test('UT-SCR003-CONTRACT-001 添付Excelの20列と報告単位の設計契約を固定する', () => {
  const spec = JSON.parse(readFileSync('config/dataverse/scr003-attendance-columns.json', 'utf8'));
  expect(spec.target_environment).toBe('StaffMaster-Automation-Test');
  expect(spec.import_contract.sheet).toBe('テストデータ');
  expect(spec.import_contract.excel_table).toBe('TestData');
  expect(spec.import_contract.columns).toEqual([
    '勤務月', '所属部局名', '所属課室名', '所属長氏名', '勤務時間管理員氏名',
    'No', '職員番号', '氏名', '通勤手当日数', '出勤日数',
    '超過勤務時間25', '超過勤務時間100', '超過勤務時間125',
    '超過勤務時間135', '超過勤務時間150', '超過勤務時間160',
    '超過勤務時間175', '休日給135', '欠勤時間', '備考',
  ]);
  const report = spec.entities.find((e: { key: string }) => e.key === 'report');
  const detail = spec.entities.find((e: { key: string }) => e.key === 'detail');
  expect(report.unique_business_key).toEqual(['work_month', 'bureau_key']);
  expect(detail.fields.find((f: { key: string }) => f.key === 'staff_number')).toMatchObject({
    kind: 'text', max_length: 12, required: true,
  });
  expect(detail.fields.find((f: { key: string }) => f.key === 'absence_hours')).toMatchObject({
    kind: 'integer', min: 0,
  });
  expect(spec.import_contract.zero_display).toContain("0");
  expect(spec.entities.map((e: { key: string }) => e.key)).toEqual([
    'report', 'detail', 'target_month',
  ]);
});
