#!/usr/bin/env python3
"""Compatibility entrypoint for the purpose-built Quick Look reading sheet.

The old implementation concatenated 62 documents. DOT-002 replaces that behavior
with the same generator as the portal so the concise reading sheet cannot drift.
This does not make Quick Look an interactive browser.
"""
import argparse
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    command = ['node', 'scripts/review/generate_requirements_html.mjs']
    if args.check:
        command.append('--check')
    subprocess.run(command, cwd=ROOT, check=True)
    output = ROOT / 'docs/requirements/standard-template/index-mobile.html'
    print(f'Purpose-built static reading sheet: {output.stat().st_size} bytes')


if __name__ == '__main__':
    main()
