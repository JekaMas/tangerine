# Static harness initial failure

The first check.py invocation stopped in phase_null_nonnull_contract. Its deliberately broken negative fixture removed $ref, and the predicate indexed that missing key rather than returning false (KeyError: $ref). The schema itself was unchanged. Changing this test assertion to .get supplies the intended negative-fixture behavior; the shared contract-check command/harness has changed. Earlier partial assertions were not published as a complete passing observation. This is a harness failure, not an application/provider failure.
