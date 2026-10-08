# Docker management discrepancy: bounded diagnosis

Expected: actual Compose restart/image inspection completes within its existing bound. Observed: fresh restart timed out at 90 seconds and both architecture cases failed on 15-second container listing. Engine ping/version/list requests timed out or returned HTTP 500, while the application readiness endpoint returned 200. Failures are classified as harness/environment or unresolved, not a proved application defect.

| Hypothesis and mechanism | Predicted discriminator | Actual evidence/disposition |
|---|---|---|
| Container-list failure comes only from Docker API version incompatibility. | Unversioned engine ping should remain responsive even if a versioned list route fails. | Unversioned ping also timed out. A version mismatch alone does not explain all observations; not confirmed. |
| Transient Docker management starvation while the emulated image build is active. | A bounded list query after the build has completed and independent work has finished should recover without source changes. | Post-build observation is retained in audit/docker-control-plane-observation.json; continued timeout would leave this incomplete as a sole cause. No CPU/memory correlation was established. |
| Desktop engine proxy/backend management path is unhealthy independently of application container networking. | Desktop status may report running while engine queries fail and application HTTP succeeds. | Current bounded Desktop status/engine/HTTP observations are retained separately. This distinguishes the boundary, not the underlying cause. Exact owner/cause remains unresolved. |

No confirmed production-code cause supports a speculative app patch. Global Docker restart would affect other projects and has not been used as an automatic cure. Persistent original/restore volumes remain intact. Further recovery needs an operational decision or evidence from Docker's management boundary; do not widen tests or overwrite the failures. A recovery/restart that changes that environment invalidates only the failed management-dependent checks, not unchanged arithmetic/auth/web behavior observations.
