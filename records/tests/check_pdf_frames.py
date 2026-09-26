"""Compare generated PDF frame geometry with embedded blank templates (not field positions)."""
import base64
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/testing/regression-v123-remaining/evidence'
SOURCE = ROOT / 'src/screen-ui/v1.23/studio-readback/Screen1.pa.yaml'


def controls(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key.startswith('imgLedgerPage'):
                yield key, child
            yield from controls(child)
    elif isinstance(value, list):
        for child in value:
            yield from controls(child)


def bounds(gray):
    y, x = np.where(gray < 120)
    return [int(x.min()), int(y.min()), int(x.max()), int(y.max())]


def groups(indices):
    result = []
    for y in indices:
        if not result or y > result[-1][-1] + 1:
            result.append([int(y)])
        else:
            result[-1].append(int(y))
    return [float(np.mean(group)) for group in result]


pages = []
for number, (_, control) in enumerate(sorted(controls(yaml.safe_load(SOURCE.read_text()))), 1):
    raw = base64.b64decode(control['Properties']['Image'].split('base64,', 1)[1].rstrip('"'))
    blank = Image.open(io.BytesIO(raw)).convert('L')
    # Canvas paper is 1122 x 794 logical px; PDF renderer rounds physical width to 1123.
    fitted = ImageOps.contain(blank, (1122, 794), Image.Resampling.LANCZOS)
    template = Image.new('L', (1123, 794), 255)
    template.paste(fitted, ((1122-fitted.width)//2, (794-fitted.height)//2))
    expected = np.asarray(template)
    actual = np.asarray(Image.open(OUT/f'ledger-rendered-{number}.png').convert('L'))
    assert actual.shape == expected.shape
    eb, ab = bounds(expected), bounds(actual)
    left, right = eb[0], eb[2] + 1
    expected_profile = ((255-expected[:, left:right])/255).sum(axis=1)
    actual_profile = ((255-actual[:, left:right])/255).sum(axis=1)
    reference = groups(np.where((expected[:, left:right] < 120).mean(axis=1) > .7)[0])
    matches = []
    for line in reference:
        lo, hi = max(0, int(line)-3), min(794, int(line)+4)
        rows = np.arange(lo, hi)
        e = expected_profile[lo:hi]
        a = actual_profile[lo:hi]
        ecenter, acenter = float(np.average(rows, weights=e)), float(np.average(rows, weights=a))
        matches.append({'reference_y':line, 'expected_centroid':ecenter, 'actual_centroid':acenter,
                        'difference_px':abs(ecenter-acenter), 'ink_mass_ratio':float(a.sum()/e.sum())})
    max_distance = max(m['difference_px'] for m in matches)
    differences = [abs(a-b) for a,b in zip(eb,ab)]
    passed = max(differences) <= 96/25.4 and max_distance <= 96/25.4 and all(m['ink_mass_ratio'] > .5 for m in matches)
    pages.append({'page':number,'template_sha256':hashlib.sha256(raw).hexdigest(),
                  'expected_ink_bounds':eb,'actual_ink_bounds':ab,'bounds_difference_px':differences,
                  'rule_matches':matches,'maximum_rule_centroid_difference_px':max_distance,
                  'frame_within_1mm':passed})
result = {'method':'96dpi Fit template, ink bounds and grayscale integrated horizontal-rule centroids in +/-3px windows',
          'tolerance_px':96/25.4,
          'limitations':['Frame geometry only. Does not certify all 69 overlaid field positions or a formally approved paper choice.',
                         'Initial binary row threshold missed an antialiased rule on page 2; grayscale integration retains split-row ink instead.'],
          'pages':pages}
(OUT/'pdf-visual-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
assert all(p['frame_within_1mm'] for p in pages), result
print(json.dumps({'status':'PASS','scope':'frame geometry only','maximum_differences_px':[p['maximum_rule_centroid_difference_px'] for p in pages]}))
