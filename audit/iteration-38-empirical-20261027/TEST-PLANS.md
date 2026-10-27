# I38 independent literal plans (unexecuted until materialized)

| Property | Positive input and expected result | Negative input and expected result |
|---|---|---|
| P1 catalogue | Published completed FCE import with train/dev/test files -> three named separate choices retaining that import/release. | Unpublished/incomplete import -> not offered as an accepted population; no reports deleted or practice gate. |
| P2 writing | Four sentences: A+B, A, B, no-error; one selected annotator, token counts5,4,3,2 -> four source-annotated sentence windows,14 tokens, four errors, two occurrences per source label. | Explicit absent annotator -> zero source-annotated windows, unknown rates; invalid/noop/withheld stay separately accounted. |
| P3 mappings | R:VERB:SVA -> subject–verb agreement; M:DET with correction'a' -> article omission; preserve exact event/span and derived rule/version. | M:DET with correction'this' -> ambiguous/unmapped, not article omission; unknown native tag and uncertain phone -> no invented category or absence. |
| P4 speech | Three manual phone utterances; source s/d/a events plus unchanged phones -> native operation counts in their own utterance denominator, actual phone exposure retained. | Automatic alignments, silence, same-phone stress-only differences and annotator comments -> no invented mistake events; unavailable/uncertain phoneme category stays unassigned; source audio realization not claimed. |
| P5 coverage | JFLEG1501 originals/6004 alternative references; SpeechOcean5000 rated/5245 recordings; actual contextual supplement views -> honest descriptive counts. | Four correction alternatives are not four mistakes; ratings and ASR are not localized error labels; DRAL versions/views do not become independent learners. |
| P6 relationships | Four fully annotated windows A+B,A,B,none -> native support1/4, conditional1/2 in both directions, lift1, with four-event denominator. | Zero annotated windows -> unknown rates, not zero; two labels on one event do not manufacture a distinct-event pair. |
| P7 persistence | Create, reopen and reuse a saved report -> frozen observations and source/mapping lineage, even after test-owned source rows change; zero model receipts. | Source/input read failure retains prior saved report and inputs; recovery does not recalculate saved reports or repeat corpus identity checks. |
| P8 usability | Select named real source, create/reopen/download report; human category/label names, understandable counts/unknowns, keyboard and1280/390/320 reflow. | Controlled503 read -> logged bounded retry, then authored recovery with retained state; no raw error/ID/JSON in ordinary output and no unintended model action. |

Actual source expectations additionally use the retained native inventories and
fresh independent streaming count/oracle observations of the chosen report
population. This plan is not source data or execution evidence.
