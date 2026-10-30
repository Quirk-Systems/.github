# Severity

| Rank | Apply when | Review handling |
|---|---|---|
| P0 Critical | Demonstrated immediate catastrophic impact, such as broad credential exposure, destructive data loss, or unrestricted authority bypass | Identify the smallest containment; flag for urgent human attention |
| P1 High | A reachable defect breaks a core workflow, security boundary, or approval/evidence contract with substantial impact | Recommend correction before merge |
| P2 Medium | A reproducible defect causes bounded wrong behavior, reliability loss, or a meaningful regression | State affected users and conditions; recommend correction |
| P3 Low | A confirmed minor defect has limited impact or avoidable maintenance cost | Report concisely; distinguish from optional preferences |

Severity measures demonstrated impact and reachability, not confidence. Record confidence/evidence separately. Missing evidence is a coverage gap unless a specific requirement or broken gate is demonstrated. Do not assign P0 solely because a file uses words such as approval, secret, or authority. Preserve the repository's severity system if it defines one and disclose any mapping.

Example: a grant accepted after expiry can be P1 if it demonstrably permits an otherwise forbidden operation. A document saying expiry should be checked is not evidence that this behavior exists.
