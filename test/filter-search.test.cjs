const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const test = require('node:test');
const { Script } = require('node:vm');

const script = new Script(readFileSync(join(__dirname, '../extension/filter-search.js'), 'utf8'));
const base = 'https://www.google.com/search';
const search = (q) => `${base}?${new URLSearchParams({ q })}`;

function redirect(href) {
  const calls = [];
  script.runInNewContext({ URL, location: { href, replace: (url) => calls.push(url) } });
  assert.ok(calls.length <= 1);
  return calls.length ? new URL(calls[0]) : null;
}

test('adds an exclusion and keeps the original host, parameters, and fragment', () => {
  const url = redirect('https://www.google.com.au/search?q=caf%C3%A9+%26+tea&start=10&hl=en#section');
  assert.equal(url.hostname, 'www.google.com.au');
  assert.equal(url.searchParams.get('q'), 'café & tea -site:reddit.com');
  assert.equal(url.searchParams.get('start'), '10');
  assert.equal(url.searchParams.get('hl'), 'en');
  assert.equal(url.hash, '#section');
  assert.equal(redirect(url.href), null);
});

test('skips searches that already have the filter, including mixed case', () => {
  assert.equal(redirect(search('-SITE:Reddit.COM repair')), null);
});

test('does not mistake a quoted literal or longer domain for the filter', () => {
  for (const q of ['"-site:reddit.com" repair', 'repair -site:reddit.com.example']) {
    assert.equal(redirect(search(q)).searchParams.get('q'), `${q} -site:reddit.com`);
  }
});

test('keeps the filter outside an unfinished quoted phrase', () => {
  const url = redirect(search('repair "quoted -site:reddit.com'));
  assert.equal(url.searchParams.get('q'), '-site:reddit.com repair "quoted -site:reddit.com');
  assert.equal(redirect(url.href), null);
});

test('leaves empty queries and unrelated paths alone', () => {
  for (const href of [base, search('   '), `${base}ing?q=repair`, 'https://www.google.com/?q=repair']) {
    assert.equal(redirect(href), null);
  }
});
