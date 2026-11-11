import { readFileSync } from 'node:fs';
import { test, expect } from '@playwright/test';

test('built fixture executes JavaScript in each bundled browser', async ({ page }) => {
  await page.setContent(readFileSync('dist/index.html', 'utf8'));
  await expect(page).toHaveTitle('Ubuntu preflight');
  await page.getByRole('button', { name: 'Count: 0' }).click();
  await expect(page.getByRole('button')).toHaveText('Count: 1');
});
