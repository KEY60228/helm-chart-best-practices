# Helm Chart Best-Practice Review: `<chart-name>`

**Chart version reviewed:** `<x.y.z>`
**Date:** `<YYYY-MM-DD>`
**Reviewer:** `<agent/tool>` with the `helm-chart-best-practices` skill

> Authoritative reference: <https://helm.sh/docs/chart_best_practices/>

## Summary

| Severity | Count |
| --- | --- |
| Must fix | `<n>` |
| Should fix | `<n>` |
| Consider | `<n>` |

`<one-paragraph overall impression — is the chart solid, mostly there, or needs significant rework?>`

## Mechanical checks

- `helm lint`: `<pass / fail (excerpt)>`
- `helm template`: `<renders cleanly / error excerpt>`
- Recommended-label coverage: `<n missing across m resources>`

## Findings

### Must fix

#### 1. `<short title>`

- **File:** `<path:line>`
- **Rule:** `<one-line restatement>` (see `references/<chapter>.md`)
- **Quote:** `"<exact phrasing from the upstream guide, if applicable>"`
- **Why it matters:** `<one or two sentences>`
- **Suggested patch:**

  ```diff
  - <bad line>
  + <fixed line>
  ```

`<repeat for each must-fix finding>`

### Should fix

`<same structure as above>`

### Consider

`<same structure as above>`

## Next steps

- [ ] Address all "Must fix" items before the next release.
- [ ] Open follow-up issues for the "Should fix" list.
- [ ] Optional: ask the skill to apply patches automatically (refactor mode).
