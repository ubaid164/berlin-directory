const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const test = require('node:test');
const path = require('node:path');
const code = fs.readFileSync(path.join(__dirname, '../content/safety-notice.js'), 'utf8');

function start(seen = true) {
  let opened = false;
  let prevented = 0;
  let back = 0;
  let stored = seen ? 'understood' : null;
  const navigations = [];
  const handlers = {};
  const controls = {};
  const context = { hidden: true, textContent: '' };
  const dialog = {
    get open() { return opened; },
    showModal() { opened = true; },
    close() { opened = false; handlers.close?.(); },
    querySelector(selector) {
      if (selector === '[data-safety-context]') return context;
      return { addEventListener(event, action) { controls[selector] = action; } };
    },
    addEventListener(event, action) { handlers[event] = action; }
  };
  vm.runInNewContext(code, {
    document: {
      getElementById() { return dialog; },
      querySelectorAll(selector) {
        return [{ addEventListener(event, action) { controls[selector] = action; } }];
      },
      documentElement: { classList: { add() {}, remove() {} } },
      referrer: 'https://example.org/'
    },
    window: {
      history: { length: 2, back() { back++; } },
      location: { search: '', assign(url) { navigations.push(url); } },
      open(url, target, features) { navigations.push({ url, target, features }); }
    },
    sessionStorage: { getItem() { return stored; }, setItem(key, value) { stored = value; } },
    URLSearchParams
  });
  return {
    click(selector) { controls[selector]({ preventDefault() { prevented++; } }); },
    dialog, navigations, context,
    get prevented() { return prevented; },
    get back() { return back; }
  };
}
const whatsapp = 'a[href="https://wa.me/491636557013"]';

test('WhatsApp waits for acknowledgement even after the first-visit notice was dismissed', () => {
  const state = start();
  assert.equal(state.dialog.open, false);
  state.click(whatsapp);
  assert.equal(state.prevented, 1);
  assert.equal(state.dialog.open, true);
  assert.equal(state.navigations.length, 0);
  assert.match(state.context.textContent, /WhatsApp/);
  state.click('[data-safety-understand]');
  assert.equal(state.dialog.open, false);
  assert.deepEqual(state.navigations, [{ url: 'https://wa.me/491636557013', target: '_blank', features: 'noopener,noreferrer' }]);
});
test('Go Back cancels WhatsApp without leaving the site', () => {
  const state = start();
  state.click(whatsapp);
  state.click('[data-safety-back]');
  assert.equal(state.dialog.open, false);
  assert.equal(state.navigations.length, 0);
  assert.equal(state.back, 0);
});
test('Demo group opens the notice and never opens a destination', () => {
  const state = start();
  state.click('[data-safety-demo]');
  assert.equal(state.dialog.open, true);
  assert.match(state.context.textContent, /demonstration/);
  state.click('[data-safety-understand]');
  assert.equal(state.navigations.length, 0);
});
test('Cancelled contact cannot leak into a later demo or footer notice', () => {
  const state = start();
  state.click(whatsapp);
  state.dialog.close();
  state.click('[data-safety-demo]');
  state.click('[data-safety-understand]');
  state.click('[data-open-safety-notice]');
  state.click('[data-safety-understand]');
  assert.equal(state.navigations.length, 0);
});
test('Initial visit still opens automatically and its Go Back action returns to the previous page', () => {
  const state = start(false);
  assert.equal(state.dialog.open, true);
  state.click('[data-safety-back]');
  assert.equal(state.back, 1);
});
