# Iteration 2: domain storage and asset lifecycle

Authorized scope: the second iteration in the user-approved 16-iteration sequence, plus the two iteration 1 verification findings. Exact baseline b41066e. Branch tangerine/iteration-2-domain-storage reuses the clean isolated implementation checkout; canonical unrelated GAPS.md stays untouched.

Production anchors: embedded contracts -> schema registry/003 additive migration -> Go immutable typed-document batch owner -> nodes/reference closure -> revision head/audit transaction. Original text bytes remain distinct private assets; JCS hashes preserve Unicode without normalization. Asset lifecycle hooks reserve with an operation and frozen owner revision -> unique MinIO object -> complete size/hash readback -> locked owner/link/audit transaction. Explicit recovery reuses actual saved bytes; stale owners become orphaned, never playable. Operation idempotency retains saved outcome; conflicting target/body/revision fails without a second effect. No transaction spans an upload/provider call.

Durable lineage: local workspace association, exact schema bytes/hash, immutable document UUID and payload hash, exact scoped node/reference identity, operation request hash, opaque asset key/full-byte SHA/size, owner revision and link audit. Database commit is the finalizer; actual MinIO readback must precede linking. Lifecycle heads are mutable pointers; old text/key/settings/receipt/result payloads remain immutable. Migration preflight preserves legacy data and verifies original-format backup before upgrading existing foundation volumes.

Evidence owners: tests/test_iteration2.py drives actual CLI functions, PostgreSQL, private MinIO and browser boundaries. Constructed schema/Unicode/reference fixtures are not corpus or LLM accuracy evidence. Independent literal packets, scoped sequence dispositions and native outputs populate the existing DAG. Review regressions cover checksum/schema readiness and populated/error/retry Library rendering. Exact I1 dependencies changed by storage/migrations invalidate their existing runtime results; unrelated formula/workflow behavior greens are retained.

Completion: directly affected tests -> full stable iteration selection -> committed candidate -> same full selection --require-clean -> acceptance-record commit. Strict OpenSpec, graph/discovery, pinned Go behavior/race/vet, real web/source builds and original registry/migration preservation are required. No inference, synthesis, model installation, purchase or publication. Later generation, grading, domain UI, full backup/restore and Lab remain required in their own iterations.

Native run 1: 47/52 passed. Five failed fixtures were diagnosed: Chrome uses a
valid alternate 101 handshake reason phrase, and two SQL fixtures omitted the
unchanged original required catalog publication/hash fields. Only those five
fixtures were rerun after driver/input repair and all passed. No production owner
was changed for those corrections. Subsequent owner work adds exact multipart-ID
persistence/abort and streaming readback; that invalidates the asset/migration
receipts for final acceptance and will be revalidated.
