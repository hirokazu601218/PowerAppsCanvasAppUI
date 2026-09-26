"""Keep the approved display name when packing current or historical sources."""
import re
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape


def normalize_display_name(path, display_name):
    if not isinstance(display_name, str) or not display_name.strip():
        raise ValueError('display name must be nonempty')
    text=path.read_text(encoding='utf-8-sig')
    root=ET.fromstring(text)
    if root.tag!='CanvasApp' or len(root.findall('DisplayName'))!=1:
        raise ValueError('expected one CanvasApp DisplayName')
    pattern=r'<DisplayName>[^<]*</DisplayName>'
    if len(re.findall(pattern,text))!=1:
        raise ValueError('ambiguous DisplayName serialization')
    updated=re.sub(pattern,lambda _:f'<DisplayName>{escape(display_name)}</DisplayName>',text)
    path.write_text(updated,encoding='utf-8-sig')
