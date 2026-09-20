# Move receipt: <bounded action>

Repository: `Quirk-Systems/<name>`  
Actor: @<handle> | agent:<profile or skill name>  
Date: YYYY-MM-DDTHH:MM:SSZ  
Authority effect: **none** (this receipt records an action already authorized elsewhere; it does not authorize the next one)

## Action

<!-- The single bounded consequential action taken. One sentence. -->

## Authority

- Authorizing control: <ruleset | environment approval | owner review | policy reference>
- Authorizing reference: <URL, approval id, or commit>
- Scope granted: <exact scope>
- Scope explicitly not granted:

## Exact subject

- Base commit: `<40-hex>`
- Head or merge commit: `<40-hex>`
- Changed paths or artifact digests:
- Evidence receipt locator: `receipt_id` / `source_repository` / `source_commit` / `source_path` / `receipt_sha256`

## Resulting state

<!-- What changed in the shared world: canonical files, registries, deployments, releases. Cite the exact after-state identifiers. -->

## Reversal

<!-- How this action is reversed or contained, and who can do it. -->

## Residue

<!-- What remains unverified, unknown, or dependent on a later gate. -->
