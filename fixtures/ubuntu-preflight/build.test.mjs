import assert from 'node:assert/strict';
import { test } from 'node:test';
import { render } from './build.mjs';

test('untrusted title cannot terminate the title element', () => {
  const html = render('</title><script>bad()</script>&');
  assert.ok(html.includes('&lt;/title&gt;&lt;script&gt;bad()&lt;/script&gt;&amp;'));
  assert.equal(html.match(/<script>/g).length, 1);
});
