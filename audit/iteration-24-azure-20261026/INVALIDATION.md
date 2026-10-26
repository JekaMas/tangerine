# Inputs and proof boundaries

Changed semantic input: Azure ssml text operations now remain mixed text instead
of becoming sentence tags. Old native Azure SSML expectations are invalidated;
new target/continuity and text/phoneme/prosody/pause/escaping cases exercise this
owner. Six directly related hosted acoustic/SSML/unsupported-operation cases pass.
Other provider code, stored audio, model contexts, prompts and score arithmetic
did not change; retain their prior observations without new calls.

The new comparison helper, atomic saved-response/piece reuse, exact native input/
output journal and loopback player need their own tests. Eleven compiler/policy/
transport/capture/resume cases plus two HTTP-player cases are implemented.
Constructed F0 resource metadata and PCM fixtures prove their native boundary;
they never establish an actual Azure account, voice, mistake or full live pair.
The original negative case reuses test_non_f0_overage_negative directly.

Original positive live and review cases are executable but explicitly skip while
actual access/media is unavailable. A runner exit0 with those skips is not I24
acceptance. Keep I24.1–I24.3 unchecked; no completed iteration or acceptance
receipt is issued from this partial work.

Baseline red-contracts.log has two actual sentence/mixed-content assertion
failures. The first combined green command also had an unrelated test-loader
failure (wrong hosted class and missing test-helper PYTHONPATH); its passing
observations are not relabelled a green command. Corrected sibling selection and
final directly affected observations are retained separately. Native test root
and PYTHONPATH are now explicit in run_contracts.py.

Ports8767/8768 already belonged to existing comparison servers. Initial owned
binds failed; neither server was stopped or changed. Disposable players use OS
assigned ports. The waiting view/font/layout are observed; disclosure activation
attempts returned unchanged state, so no keyboard/refresh-effect/playback pass is
claimed. An authentication-modal/input-delivery cause is only a hypothesis;
no speculative product or browser-security patch follows. Retest actual player
interactions after the protected sign-in/access prerequisite is resolved.

The exact original shared material is now versioned as material.json beside the
helper. Its bytes are unchanged; new tests and a fresh checkout no longer depend
on an ignored prior-run file. Source loading/helper dependencies and the live
oracle path changed, so the I24 selection is reobserved after this final fixture
binding. The unchanged waiting-view layout observations remain valid.
