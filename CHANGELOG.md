# Changelog

## Unreleased — 2026-10-08

- Add a closed `ubuntu-image` choice to reusable validation: the existing
  `ubuntu-latest` default, explicit Ubuntu 24.04 retention, or Ubuntu 26.04
  preflight. Invalid choices fail before dependency setup; arbitrary or
  self-hosted runner selection is impossible.
- Check out and verify the exact PR head, record the OS/image, and bound shared
  validation to 20 minutes. Add an npm fixture through the real reusable
  workflow on Ubuntu 24 and 26, including Chromium, Firefox, and WebKit.
- Add an Ubuntu 26 system-Python governance/semantic probe without setup-python.
- Add runner-choice rejection and stale-head regression coverage. Preserve
  governance gates, action pins, legacy lint exemptions, and owner authority.
- No existing consumer pin is changed. Hosted fixture proof establishes only
  the tested fixture and image; downstream apps require their own preflight.
  Revert this change to remove the input and fixture jobs.

- Pin the inherited Bun setup action to the verified v2.2.0 commit. Hosted
  policy rejected its floating v2 tag even for the npm fixture's skipped step;
  fix the workflow rather than changing the organization's full-SHA protection.
- Resolve setup-node cache lockfiles from the declared working directory. The
  real nested npm fixture exposed the inherited root-only cache lookup failure
  on both Ubuntu images; lockfile patterns cover npm, yarn, and pnpm.
