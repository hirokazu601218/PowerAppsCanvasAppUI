/**
 * Simulated DOM contract tests, NOT real-browser or visual verification.
 *
 * Run from the repository root:
 *   node --test scripts/review/requirements_portal/test_portal_logic.mjs
 *
 * Requires Node's built-in test runner and Python 3 (standard library only).
 * Override the Python executable with PYTHON if necessary.
 * The minimal mocks deliberately do not model layout, browser history,
 * native focus, touch scrolling, SVG geometry, or Safari/Quick Look behavior.
 */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { test } from 'node:test';
import vm from 'node:vm';

const directory = path.dirname(fileURLToPath(import.meta.url));
const repositoryRoot = path.resolve(directory, '../../..');
const portalRoot = path.join(repositoryRoot, 'docs/requirements/standard-template');
const portalScript = readFileSync(path.join(portalRoot, 'assets/portal.js'), 'utf8');
const contextScript = readFileSync(path.join(portalRoot, 'assets/context.js'), 'utf8');
const fixtures = JSON.parse(execFileSync(
  process.env.PYTHON || 'python3',
  [path.join(directory, 'extract_logic_fixtures.py')],
  { encoding: 'utf8', maxBuffer: 8 * 1024 * 1024 },
));

function mockElement(extra = {}) {
  return Object.assign({
    listeners: {},
    addEventListener(type, callback) {
      (this.listeners[type] ??= []).push(callback);
    },
    emit(type, event = {}) {
      for (const callback of this.listeners[type] || []) callback(event);
    },
    focus() { this.focused = true; },
  }, extra);
}

function createSearchPage(filename, search = '') {
  const fixture = fixtures[filename];
  const items = structuredClone(fixture.items);
  const fields = {
    q: mockElement({ value: '' }),
    reset: mockElement(),
    count: mockElement({ textContent: '' }),
    empty: mockElement({ hidden: true }),
  };
  for (const name of fixture.selects) fields[name] = mockElement({ value: '' });

  const form = mockElement({
    querySelector(selector) {
      if (selector === '[data-reset]') return fields.reset;
      const name = selector.match(/name=(\w+)/)?.[1];
      return fields[name] || null;
    },
  });
  const document = {
    querySelector(selector) {
      return {
        '[data-search-form]': form,
        '[data-result-count]': fields.count,
        '[data-empty]': fields.empty,
      }[selector] || null;
    },
    querySelectorAll(selector) {
      return selector === '[data-search-item]' ? items : [];
    },
  };
  vm.runInNewContext(portalScript, {
    document, location: { search }, URLSearchParams, window: { print() {} },
  });
  return { fields, items, form, visible: () => items.filter(item => !item.hidden) };
}

function searchableText(item) {
  return item.dataset.searchText || item.textContent;
}

test('SIMULATED: all requirement and operation cards display initially', () => {
  const page = createSearchPage('requirements/index.html');
  assert.equal(page.visible().length, fixtures['requirements/index.html'].items.length);
});

test('SIMULATED: I12 query finds the requirement and related operation text', () => {
  const page = createSearchPage('requirements/index.html', '?q=I12');
  assert.ok(page.visible().length > 0);
  assert.ok(page.visible().every(item => searchableText(item).includes('I12')));
});

test('SIMULATED: search normalizes full-width text and case', () => {
  const query = new URLSearchParams({ q: 'ｉ１２' });
  const page = createSearchPage('requirements/index.html', `?${query}`);
  assert.ok(page.visible().length > 0);
  assert.ok(page.visible().every(item => searchableText(item).includes('I12')));
});

test('SIMULATED: operation filter excludes requirement cards', () => {
  const page = createSearchPage('requirements/index.html');
  page.fields.kind.value = 'operation';
  page.form.emit('change');
  assert.ok(page.visible().length > 0);
  assert.ok(page.visible().every(item => item.dataset.kind === 'operation'));
});

test('SIMULATED: empty result, reset, and focus callback', () => {
  const page = createSearchPage('requirements/index.html');
  page.fields.q.value = 'QA_NONEXISTENT_a7d892';
  page.form.emit('input');
  assert.equal(page.visible().length, 0);
  assert.equal(page.fields.empty.hidden, false);
  page.fields.reset.emit('click');
  assert.equal(page.visible().length, page.items.length);
  assert.equal(page.fields.q.focused, true);
});

test('SIMULATED: unset filter includes both unset and partial-unset items', () => {
  const page = createSearchPage('open-items.html');
  page.fields.state.value = 'unset';
  page.form.emit('change');
  assert.ok(page.visible().length > 0);
  assert.ok(page.visible().every(item => item.dataset.states.split(' ').includes('unset')));
  assert.ok(page.visible().some(item => item.dataset.states.includes('partial')));
});

test('SIMULATED: text and state filters combine and reset together', () => {
  const page = createSearchPage('open-items.html');
  page.fields.q.value = '給与簿';
  page.fields.state.value = 'unset';
  page.form.emit('input');
  assert.ok(page.visible().length > 0);
  assert.ok(page.visible().every(item => searchableText(item).includes('給与簿')));
  assert.ok(page.visible().every(item => item.dataset.states.split(' ').includes('unset')));
  page.fields.reset.emit('click');
  assert.equal(page.fields.state.value, '');
  assert.equal(page.fields.q.value, '');
  assert.equal(page.visible().length, page.items.length);
});

function createContextPage(query) {
  const base = 'http://qa.invalid/app/docs/requirements/standard-template/';
  const returnLink = { href: `${base}index.html`, textContent: 'fallback' };
  const relatedLink = { href: `${base}sources/other.html#anchor` };
  const document = {
    querySelector() { return { dataset: { portalRoot: '../' } }; },
    querySelectorAll(selector) {
      if (selector === '[data-context-return]') return [returnLink];
      if (selector === 'a[data-keep-context]') return [relatedLink];
      return [];
    },
  };
  const location = {
    href: `${base}sources/source.html${query}`,
    search: query,
    origin: 'http://qa.invalid',
  };
  vm.runInNewContext(contextScript, { document, location, URL, URLSearchParams });
  return { returnLink, relatedLink };
}

test('SIMULATED: section context returns to its exact section anchor', () => {
  const page = createContextPage('?context=section-2.5.1');
  assert.ok(page.returnLink.href.endsWith('/sections/2.5.1.html#section-2.5.1'));
  assert.ok(page.relatedLink.href.includes('context=section-2.5.1'));
  assert.ok(page.relatedLink.href.endsWith('#anchor'));
});

test('SIMULATED: requirement, workflow, screen, and official-template context allowlist', () => {
  const cases = [
    ['req-I12', 'requirements/I12.html#requirement-I12'],
    ['flow-WF-13', 'workflows/WF-13.html#WF-13'],
    ['screen-FUT-JLINK', 'screens/FUT-JLINK.html#FUT-JLINK'],
    ['template-3.14.1', 'template-sections/3.14.1.html#template-3.14.1'],
  ];
  for (const [context, destination] of cases) {
    const page = createContextPage(`?context=${context}`);
    assert.ok(page.returnLink.href.endsWith(destination));
  }
});

test('SIMULATED: external redirect context is not accepted', () => {
  const page = createContextPage('?context=https%3A%2F%2Fexample.invalid');
  assert.ok(page.returnLink.href.endsWith('/index.html'));
  assert.equal(page.returnLink.textContent, 'fallback');
});

test('SIMULATED: SVG zoom bounds, reset, and keyboard-scroll callbacks', () => {
  const canvas = { style: {} };
  const viewport = mockElement({
    left: 0,
    top: 0,
    scrollTo(x, y) { this.left = x; this.top = y; },
    scrollBy(x, y) { this.left += x; this.top += y; },
  });
  const output = { textContent: '' };
  const zoomIn = mockElement();
  const zoomOut = mockElement();
  const fit = mockElement();
  const figure = {
    querySelector(selector) {
      return {
        '.diagram-canvas': canvas,
        '.diagram-viewport': viewport,
        output,
        '[data-zoom-in]': zoomIn,
        '[data-zoom-out]': zoomOut,
        '[data-zoom-fit]': fit,
      }[selector];
    },
  };
  const document = {
    querySelector() { return null; },
    querySelectorAll(selector) { return selector === '[data-figure]' ? [figure] : []; },
  };
  vm.runInNewContext(portalScript, { document, window: { print() {} } });
  assert.equal(output.textContent, '100%');
  assert.equal(zoomOut.disabled, true);
  zoomIn.emit('click');
  assert.equal(canvas.style.width, '150%');
  for (let index = 0; index < 20; index += 1) zoomIn.emit('click');
  assert.equal(output.textContent, '400%');
  assert.equal(zoomIn.disabled, true);
  let prevented = false;
  viewport.emit('keydown', {
    target: viewport,
    key: 'ArrowRight',
    preventDefault() { prevented = true; },
  });
  assert.equal(viewport.left, 80);
  assert.equal(prevented, true);
  fit.emit('click');
  assert.equal(viewport.left, 0);
  assert.equal(viewport.top, 0);
  assert.equal(output.textContent, '100%');
});
