import { mkdirSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

export function render(title) {
  const escaped = title.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
  return `<!doctype html><title>${escaped}</title><button>Count: 0</button><script>
    let count = 0;
    document.querySelector('button').onclick = (event) => { event.target.textContent = 'Count: ' + ++count; };
  </script>`;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  mkdirSync('dist', { recursive: true });
  writeFileSync('dist/index.html', render('Ubuntu preflight'));
}
