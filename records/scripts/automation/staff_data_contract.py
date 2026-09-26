"""Validation for synthetic staff fixtures; no remote writes."""
import re
from datetime import date, datetime, timedelta, timezone


def employment_status(hire, leave, today=None):
    today = today or datetime.now(timezone(timedelta(hours=9))).date()
    if not hire or date.fromisoformat(hire) > today:
        return '採用前'
    return '退職' if leave and date.fromisoformat(leave) < today else '在籍'


def work_minutes(text):
    if text in ('', None):
        return None
    match = re.fullmatch(r'([0-9]+):([0-5][0-9])', text)
    if not match:
        raise ValueError('勤務時間はH:mm形式')
    return int(match[1]) * 60 + int(match[2])


def validate(rows):
    seen = set()
    for row in rows:
        number = row.get('staffnumber')
        if not isinstance(number, str) or not re.fullmatch(r'[0-9]{12}', number):
            raise ValueError('職員番号は必須の12桁数字文字列')
        if number in seen:
            raise ValueError('職員番号重複')
        seen.add(number)
        if row.get('taxclass') not in ('甲', '乙'):
            raise ValueError('税表区分は甲または乙必須')
        for name, limit in {'fullname': 50, 'lastname': 30, 'firstname': 30,
                            'email': 254, 'orgshort': 50, 'orgfull': 100,
                            'employmenttype': 30, 'commutemethod': 200}.items():
            value = row.get(name)
            if value is not None and (not isinstance(value, str) or len(value) > limit):
                raise ValueError('文字列型または最大長違反: ' + name)
        if row.get('email') and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', row['email']):
            raise ValueError('メール形式不正')
        for name, choices in {'sex': ('男', '女'), 'workregistered': ('登録', '未登録'),
                              'commuteregistered': ('登録', '未登録')}.items():
            if row.get(name) not in (None, '', *choices):
                raise ValueError('選択肢不正: ' + name)
        for name in ('birthdate', 'hiredate', 'leavedate'):
            if row.get(name):
                date.fromisoformat(row[name])
        if row.get('hiredate') and row.get('leavedate') and row['leavedate'] < row['hiredate']:
            raise ValueError('退職日は採用日以降')
        for name in ('pension', 'employmentinsurance', 'mutualshort', 'mutuallong'):
            if row.get(name) not in (None, '', '加入', '未加入'):
                raise ValueError('保険区分は加入/未加入/空欄')
        for name in ('dailyrate', 'workminutes', 'passamount', 'onewayfare'):
            value = row.get(name)
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError('金額・勤務分数は非負整数')
    return True
