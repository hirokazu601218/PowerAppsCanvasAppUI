#!/usr/bin/env node

import { readFile, writeFile } from 'node:fs/promises';

const [, , inputPath, outputPath] = process.argv;

if (!inputPath || !outputPath) {
  console.error('Usage: node tools/patch-v111-studio-compat.mjs <input.yaml> <output.yaml>');
  process.exit(2);
}

let yaml = await readFile(inputPath, 'utf8');

const galleryItemsPattern = /CountRows\((gal(?:Work|Commute|Social|Resident|Tax|Payroll|PayrollModal)111)\.Items\)/g;
const galleryItemsMatches = [...yaml.matchAll(galleryItemsPattern)].length;
const selfItemsPattern = /CountRows\(Self\.Items\)/g;
const selfItemsMatches = [...yaml.matchAll(selfItemsPattern)].length;
const setFocusPattern = /SetFocus\(([^)]+)\)/g;
const setFocusMatches = [...yaml.matchAll(setFocusPattern)].length;

if (galleryItemsMatches !== 7 || selfItemsMatches !== 1 || setFocusMatches !== 8) {
  throw new Error(
    `Unexpected v1.11 signature: gallery.Items=${galleryItemsMatches}, ` +
      `Self.Items=${selfItemsMatches}, SetFocus=${setFocusMatches}`,
  );
}

yaml = yaml
  .replace(galleryItemsPattern, 'CountRows($1.AllItems)')
  .replace(
    selfItemsPattern,
    'If(Coalesce(varResultsReady111,false),CountRows(colResult111),25)',
  )
  .replace(setFocusPattern, 'Set(varFocusCompat111,true)');

if (/CountRows\([^\n)]*\.Items\)/.test(yaml) || /SetFocus\(/.test(yaml)) {
  throw new Error('Compatibility replacement was incomplete');
}

await writeFile(outputPath, yaml, 'utf8');
console.log(
  `Created ${outputPath}: 8 gallery count fixes and ${setFocusMatches} focus fallbacks`,
);
