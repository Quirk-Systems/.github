---
name: "quirk-artifact-forge"
description: "Produce a generated asset (image, audio, document, dataset slice, model output, code) together with an artifact-manifest.json that binds its bytes to their generator, inputs, source commit, license, and classification, without claiming publication or canon."
---

# Quirk artifact forge

Every generated asset ships with provenance or it does not ship. The
manifest contract is `.quirk/schemas/artifact-manifest.schema.json`; the
example is `templates/artifact-manifest.json`. `Asset` is the canonical
concept (`entity.asset`); `artifact` is the retained alias.

## Procedure

1. **Decide the boundary before generating.** What is the asset for, who
   holds the rights to its inputs, what classification will it carry, and
   which `required_next` gate applies (review, license-clearance, publish)?
   If any input is third-party material, record it or stop.
2. **Generate with recorded inputs.** Keep every prompt, parameter, seed,
   source file, and model identifier. For model outputs, record provider,
   identifier, and version; "an LLM" is not an identity.
3. **Hash the outputs.** `sha256sum <file>` for each output; record media
   type and byte size.
4. **Write the manifest** next to the asset as `<asset>.manifest.json` (or in
   the asset's directory as `artifact-manifest.json`). Fill `source.commit`
   with the 40-character SHA of the repository state that produced it.
5. **Validate**: `python scripts/validate_templates.py --artifact <path>`.
6. **State residue honestly**: what is unverified (a rendered diagram is not
   truth; a generated draft is not reviewed), and what is excluded.
7. Commit asset and manifest together, then the receipt.

## Do

- Set `status: draft` or `candidate` on first commit. `reviewed` is set by a
  reviewer's change, not by the producer.
- Prefer deterministic generation (fixed seeds, pinned tool versions) so the
  manifest can be reproduced.
- Apply the brand quality bar to the asset itself: identity, structure,
  naming, specificity, energy, leverage, utility (see `quirk-brand-system`
  where available). Stylish but unusable fails; useful but anonymous fails.

## Don't → Do instead

- Don't commit binaries without a manifest → write the manifest first, then the bytes.
- Don't claim the asset is published, canonical, or licensed for a use the
  rights holder has not granted → list the gate under `authority.required_next`.
- Don't embed credentials, private transcripts, or personal data in inputs →
  reference them by classification and keep them outside the repository.
- Don't let the asset redefine a Quirk concept in its title or copy → use the
  registry ID and mark semantic impact.

## Reference

`templates/artifact-manifest.json`, `docs/QUIRK_SEMANTIC_GOVERNANCE.md`
(Asset/Artifact invariant), `docs/governance/INTEROPERABILITY.md` §5 for the
digest and timestamp formats.
