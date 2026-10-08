# Current repository drift

The current owning source was inspected at 6b625ef82b096e143867573d0624d7d79d778b07. The archive’s unavailable-repository statement is obsolete. Inspection is read-only and does not establish runtime acceptance.

| File | SHA-256 | Finding |
|---|---|---|
| services/api/internal/app/migrations/001_foundation.sql | 63c28682c5dbf0e99664a7a8ad52cb3dc6dbcdedc6e65b7f9a13ba2ecac98113 | Historical account/session/catalog foundation; v2 unimplemented. |
| services/api/internal/app/http.go | adf910a3a6debbe7a89356a4c817accabcfddf089a4ed95d158d5dbe08966400 | Historical account/session/catalog foundation; v2 unimplemented. |
| services/api/internal/app/storage.go | d6d40492e37bc7a28d2130f0e1dc483567a0b7bf9fb3cb8fe393e3f658f7ce81 | Historical account/session/catalog foundation; v2 unimplemented. |
| services/api/internal/app/security.go | 0b3a7cde8abc582788cd5596420741fbe3240861bbb93eb212380077122eaf2b | Historical account/session/catalog foundation; v2 unimplemented. |

See specification/v2/docs/migration-compatibility.md for the fresh/existing compatibility draft. Exact reference DDL inconsistencies remain FRC-010. No app code, SQL execution, Docker, provider inference or source acquisition occurred. Existing receipts retain original hashes and proof boundaries.
