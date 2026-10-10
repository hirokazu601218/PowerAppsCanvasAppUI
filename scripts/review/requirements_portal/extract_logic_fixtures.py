#!/usr/bin/env python3
"""Read the generated HTML as data for simulated-DOM tests; no browser involved.

Uses Python's standard library only. Prints JSON for test_portal_logic.mjs.
"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PORTAL = ROOT / "docs/requirements/standard-template"
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


def dataset_key(attribute):
    return re.sub(r"-([a-z])", lambda match: match[1].upper(), attribute[5:])


class SearchFixtureParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []
        self.selects = []
        self.depth = 0
        self.current = None
        self.item_depth = None

    def handle_starttag(self, tag, pairs):
        attributes = dict(pairs)
        if tag == "select" and attributes.get("name"):
            self.selects.append(attributes["name"])
        if "data-search-item" in attributes:
            if self.current is not None:
                raise ValueError("Nested search items are unsupported by the fixture parser")
            self.current = {
                "dataset": {
                    dataset_key(key): value or ""
                    for key, value in attributes.items()
                    if key.startswith("data-")
                },
                "textContent": "",
            }
            self.item_depth = self.depth
        if tag not in VOID_TAGS:
            self.depth += 1

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        self.depth -= 1
        if self.current is not None and self.depth == self.item_depth:
            self.current["textContent"] = " ".join(self.current["textContent"].split())
            self.items.append(self.current)
            self.current = None
            self.item_depth = None

    def handle_data(self, data):
        if self.current is not None:
            self.current["textContent"] += " " + data

    def handle_startendtag(self, tag, pairs):
        self.handle_starttag(tag, pairs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)


fixtures = {}
for filename in ("requirements/index.html", "open-items.html"):
    parser = SearchFixtureParser()
    parser.feed((PORTAL / filename).read_text(encoding="utf-8"))
    parser.close()
    if parser.current is not None or not parser.items:
        raise ValueError(f"Incomplete or empty fixture: {filename}")
    fixtures[filename] = {"items": parser.items, "selects": parser.selects}
print(json.dumps(fixtures, ensure_ascii=False))
