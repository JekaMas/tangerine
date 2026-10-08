# Human evidence and gold records

A person record is a local attestation about an actual human.
The operator supplies identity and competence evidence and names the actual attester.
The system does not infer identity from a login or create a second person by changing a name.

## Qualifications and conflicts

Accept a relevant teaching/linguistics qualification document or a documented competence assessment.
A job title alone is not sufficient. Acoustic cases require phonetics competence in at least one counted reviewer.
Use issuer expiry when it exists. Do not invent expiry for an undated permanent qualification.
Re-attest current competence, conflicts, and independence for every review.
The two counted reviewers must be different people. Neither can be a case author.
They cannot see the key or the other blind submission before their own blind submission.
Record known aliases, prior exposure, collaboration, and other conflicts. Unresolved identity or conflict evidence blocks the review.

## Blind review

A reviewer first receives final audio, public context, task purpose, and an empty observation form.
The response has no planned unit IDs, target count, target categories, or corrections.
The reviewer records every observed defect, permitted control, uncertainty, and interval independently.
The API saves exact annotation text, server time, and a canonical submission hash.
Only then can the reviewer request key disclosure. Save that disclosure as an immutable event.
A later note creates a separate post-key record. It cannot change the blind submission.

After disclosure, the reviewer maps observations to planned units, identifies unplanned defects, and checks all accepted corrections.
Unresolved unplanned defects block publication because the key is incomplete.
Every target and control needs two explicit final approvals on the exact key and final audio.
A third distinct qualified adjudicator resolves disagreement with recorded evidence and reasoning.
Publication still needs two explicit final approvals after adjudication.
An adjudicator is not a model, an automated report, or a fabricated person entry.

## Real teacher-answer gold

Collect the teacher's real answer with declared consent and intended uses.
Store original bytes, case/key/audio identities, component requirements, requested language, and exposure history.
Two independent annotators label claims and mappings before they see model results.
Preserve each rater's original labels, uncertainty, and normalization.
An adjudication record supplies the final label set without replacing the originals.
Include correct, partial, vague, repeated, contradictory, retracted, false-positive, wrong-repair, acceptable-alternative, and off-key cases when they actually occur.
Do not invent real answers to fill an absent stratum. Missing strata block the relevant acceptance claim.

## Coverage counts

An asset is one unique byte payload. A stimulus is one presented recording/context pair.
An observation is one reviewed target event inside a stimulus. A pair is two independently prepared contrasting stimuli.
A pair family groups its script, speaker, content derivatives, and corresponding observations.
One recording with five targets remains one stimulus and one asset, not five independent recordings.
The required floor remains six distinct stimuli per taxonomy leaf and 732 distinct stimuli in total.
Each leaf needs one pair in development, one in calibration, and one in holdout.
For an error leaf, the pair has a target defect and a matched permitted control.
For an acceptable-variant leaf, both members are acceptable under the disclosed context. Do not relabel either as an error.
Count a stimulus toward the 732 floor only once, even if it covers several leaves.
Every counted item needs the final-audio approvals and source-rights records.

## Difficulty protocol for the first release

Difficulty calculation is implemented in the first release. Labels require actual evidence, not author intuition.
A study freezes its target, language, variety, component requirements, scoring version, and eligible population before collection.
Count one first-exposure attempt per genuine participant for the target. Keep dependent repeats out of the denominator.
For a unit, success means a supported detection of that exact error, or correct explicit acceptance of that control.
For a whole exercise, success means a completed composite of at least 80 under the frozen required components.
Report the study kind so these two populations cannot be mixed.
Require at least 100 eligible independent participants. Record exclusions and recruitment criteria.
Use p=k/n and a two-sided Wilson interval with z=1.959963984540054.

```text
center = (p + z*z/(2*n)) / (1 + z*z/n)
half = z*sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)
lower = center-half
upper = center+half
```

Label easy only when lower>=0.80.
Label medium only when lower>=0.50 and upper<0.80.
Label hard only when lower>=0.20 and upper<0.50.
Label expert only when upper<0.20.
Otherwise show unrated with `interval_crosses_band` or `insufficient_population`.
These bands and sample floors are explicit engineering policy candidates. They are not validated teacher norms.
A label does not change detection credit, severity weights, or corpus CEFR metadata.
