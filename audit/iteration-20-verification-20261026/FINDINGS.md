# Findings and sibling dispositions

| Finding | Demonstrated cause and effect | Single repair owner | Evidence and disposition |
|---|---|---|---|
| V20-01 · P2 | Refresh and checking progress independently deliver attempt/results snapshots. A late old checking result removes primary60; an old pre-submit draft can restore editable input after submission. | `useListening` owns one read-delivery version for Refresh, foreground readback and the progress adapter. Writes supersede outstanding pre-write reads. | Accepted-source CUA baseline reproduces all three failures. Current actual CUA keeps60 and the submitted read-only answer. The final progress probe holds later successful polls until after observation. Resolved. |
| V20-02 · P2 | Multiple queued native seeking events consume the expected seek too early; a queued old pause arrives after the next Play with paused=false. Both cancel the latest range and allow playback beyond its end. | `passageReplay` retains the expected position until seek completion; pause/ended cancellation observes current media state. Disposal owns every listener. | Actual stored-WAV diagnostic controls import the production owner. Before repair playback passes16.5s; current rapid replacement/queued pause stop16.220/16.237s for an end16.000s. Ordinary UI wiring and end stops are verified separately. Resolved. |

`data/iteration-20-verification-20261026/baseline.json` retains counterexamples;
`observations.json` and `requests.jsonl` retain the current observations.

Sibling checks are resolved or explicitly bounded:

- **Manual Refresh, progress and write finalizers:** one delivery owner, including
  obsolete parse failures and reads started before Submit. A current failure
  keeps accepted data. The separate progress module reports safe diagnostics
  and cannot cancel/retry the foreground write.
- **Draft Save/Refresh/reopen:** dirty text survives three failed attempt reads,
  recovered Refresh and the exact explicit Save. Save remains enabled during
  the read failure. Controlled HTTP proves UI transitions; native persistence
  remains its unchanged earlier evidence.
- **Read failure/recovery:** three transient503 attempts use the existing shared
  transport owner, then authored guidance. Unreadable successful payloads log a
  safe kind and offer explicit Refresh. Neither path displays a private backend
  string, replays a write or starts an LLM operation. No repeated schema/data
  validation was added.
- **Current versus queued pause/ended:** deterministic owner tests preserve the
  new range for obsolete events and cancel it for genuine current events. Old
  ended is a sibling lifecycle test, not a claimed new native reproduction.
- **Own seek completion versus manual seek:** duplicate own events retain the
  end stop; later native Home seeking cancels it. The full recording reaches
  its actual25.875-second end. Old play-promise failure/completion and disposal
  cases remain registered and execute against the repaired owner.
- **Media failure:** a real media403 cancels playback and shows authored guidance
  while retaining answer/score. Refresh and Replay recover the same stored
  recording. A bare synthetic error with no current resource failure is not a
  demonstrated product defect; genuine error cancellation remains intentional.
- **UI/typography:** current completed, draft, checking and uncertain views,
  keyboard replay, next-practice/return and responsive widths have no remaining
  issue. Results/CSS remain unchanged; no cosmetic rewrite or learner gate is
  necessary. Missing timing remains explicit and optional explanation stays
  separate from the primary score.

The review found no further in-scope defect after repair. It is self-review using
independently authored requirements and literal expectations, not independent
human approval or a full-release/provider qualification.
