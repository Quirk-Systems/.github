import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testMatch: 'browser.spec.ts',
  timeout: 30_000,
  retries: 0,
  reporter: 'line',
  projects: [
    { name: 'chromium', use: devices['Desktop Chrome'] },
    { name: 'firefox', use: devices['Desktop Firefox'] },
    { name: 'webkit', use: devices['Desktop Safari'] },
  ],
});
