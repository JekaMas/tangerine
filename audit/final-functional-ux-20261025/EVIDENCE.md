# Evidence locations and exact limits

- `data/final-functional-ux-20261025/browser-observations.json`: observed DOM values
  after actual CUA pointer/keyboard/navigation actions, media clock and recovery.
- `data/final-functional-ux-20261025/screens/`: original route/selected/error/result
  JPEG screenshots (the original CUA bytes, with matching .jpg extensions). Final result captures retain the existing attempt identity.
- `data/final-functional-ux-20261025/*.ax.txt`: actual browser accessibility states.
- `data/final-functional-ux-20261025/dag-native-final.json`: native Go and JS
  execution events, case selection and command records after fixture repair.
- `data/final-functional-ux-20261025/dag-contract-final.json`: assertions over the
  actual browser observations. This executor does not launch a substitute browser.
- `data/final-functional-ux-20261025/request-error.log`: five exact native JS
  presentation observations, reused because their helper/test input is unchanged.
- `data/final-functional-ux-20261025/*-final.json`: selected native HTTP record
  readbacks; no private authentication token is exported by these endpoints.
- `data/final-functional-ux-20261025/web-build-*.log`, `go-lint.log`,
  `openspec-strict.json`, `dag-validate-final.json`, `discovery-final.json`:
  build/structural checks, distinct from behavioral or visual acceptance.
- `audit/linguistic-fullness-20261023/RECONCILIATION.json`: retained all-category
  native and semantic contrast receipts. No new linguistic-gold claim.
- `audit/category-realization-20261025/COVERAGE.json`: retained actual finite
  audio/listener evidence, including failures, false alarms and unknowns.
- `data/whole-flow-demo-20261025/tangerine-demo.mp4`: prior real whole-flow demo.
  Its UI predates these visual changes; it is not a new video of this revision.

Network-blocked negatives concern the browser transport path. They do not claim
an actual PostgreSQL or provider outage. The controlled pending request was
cancelled before inference. The malformed advanced/report cases dispatched no
POST. Saving the experiment did not run it. Cleanup was preview-only.
