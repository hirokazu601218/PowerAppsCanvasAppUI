import sys
import unittest
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts/automation'))
from staff_data_contract import employment_status, validate, work_minutes


class StaffContractTests(unittest.TestCase):
    def test_status_boundaries(self):
        today = date(2026, 9, 16)
        for hire, leave, expected in [
            (None, None, '採用前'),
            (None, '2026-01-01', '採用前'),
            ('2026-09-17', None, '採用前'),
            ('2026-09-16', None, '在籍'),
            ('2026-04-01', '2026-09-16', '在籍'),
            ('2026-04-01', '2026-09-15', '退職')]:
            with self.subTest(hire=hire, leave=leave):
                self.assertEqual(employment_status(hire, leave, today), expected)

    def test_required_and_duplicate_keys(self):
        good = {'staffnumber': '000123456789', 'taxclass': '甲'}
        self.assertTrue(validate([good]))
        for row in [dict(good, staffnumber='00123456789'), dict(good, staffnumber=''),
                    dict(good, staffnumber='１２３４５６７８９０１２'), dict(good, taxclass='')]:
            with self.assertRaises(ValueError):
                validate([row])
        with self.assertRaises(ValueError):
            validate([good, good])

    def test_duration_and_optional_insurance(self):
        self.assertEqual(work_minutes('7:45'), 465)
        self.assertEqual(work_minutes('8:00'), 480)
        self.assertIsNone(work_minutes(''))
        with self.assertRaises(ValueError):
            work_minutes('7:60')
        good = {'staffnumber': '000123456789', 'taxclass': '乙', 'pension': None}
        self.assertTrue(validate([good]))
        with self.assertRaises(ValueError):
            validate([dict(good, pension='登録')])

    def test_invalid_dates_and_numbers(self):
        good = {'staffnumber': '000123456789', 'taxclass': '甲'}
        for updates in [{'hiredate': '2026-02-30'}, {'hiredate': '2026-04-01', 'leavedate': '2026-03-31'},
                        {'workminutes': True}, {'dailyrate': -1}, {'dailyrate': 1.5}]:
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                validate([dict(good, **updates)])


if __name__ == '__main__':
    unittest.main()
