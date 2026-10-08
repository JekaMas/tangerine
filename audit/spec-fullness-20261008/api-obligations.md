# Full API and operator-operation obligations

This inventory follows existing author/reviewer/teacher/dispute/corpus/provider/release flows. It defines required coverage, not invented endpoint paths. For each row, specify transport, method/path/operation ID, complete request/response/error shapes, authentication/resource/state guards, defaults/ranges, revision/idempotency semantics and atomic audit/effects. Some operator rows may remain documented CLI procedures.

| ID | Actor | Required operation | Data contract obligation | Flow |
|---|---|---|---|---|
| API-001 | session | Local login | account credentials → session/cookie | authentication |
| API-002 | session | Local logout | current session → revoked token | authentication |
| API-003 | session | Read authenticated identity/roles | session → safe role/tenant view | authentication |
| API-004 | teacher | List published exercises | filters/page → public list | pre-submit |
| API-005 | teacher | Open/start exercise and freeze task | case/version → public context/task and frozen attempt | pre-submit |
| API-006 | teacher | Read protected audio HEAD/GET/Range | asset permission/range → bytes/headers | media |
| API-007 | teacher | Acknowledge provider disclosure | disclosure version → authenticated acknowledgment | consent |
| API-008 | teacher | Record accepted playback event | event identity → deduplicated telemetry | telemetry |
| API-009 | teacher | Submit frozen answer | answer/idempotency/case policy → saved attempt and synchronous outcome | submission |
| API-010 | teacher | Read attempt status/original answer | owned attempt → permitted status/answer view | recovery |
| API-011 | teacher | Read original/current result | owned attempt/revision → result and provenance | results |
| API-012 | teacher | Explicitly recover/retry failed attempt | attempt/revision → current-lease evaluation | recovery |
| API-013 | teacher | Read approved result-linked evidence/media interval | result/evidence permission → scoped view | results |
| API-014 | teacher | Submit dispute or plausible key defect | attempt/result/evidence → saved dispute | dispute |
| API-015 | author | Create/read/update/version blueprint | closed blueprint/revision → immutable version | preparation |
| API-016 | author | Select frozen taxonomy/voices/capabilities | authorized registry version → authoring options | preparation |
| API-017 | author | Compile candidate with recorded attempt budget | blueprint/source permissions → candidate/failure | generation |
| API-018 | author | Read candidate and attempt/provenance records | candidate permission → private source/key view | generation |
| API-019 | author | Request linguistic audit | candidate/input contract → advisory findings | generation |
| API-020 | author | Submit typed render plan | candidate/plan/profile → render plan version | render |
| API-021 | author | Generate or explicitly retry audio | plan/revision/counter → immutable audio/evidence | render |
| API-022 | author | Read protected draft audio and evidence | case/role → private media/evidence | render |
| API-023 | author | Measure mechanical QC and independent ASR/PA | audio/method → gates/evidence | verification |
| API-024 | author | Revise draft context/key/corrections | draft revision → distinct valid payload/version | revision |
| API-025 | author | Request independent review | rendered case → needs_review assignments | review |
| API-026 | reviewer | List/read permitted review assignment | reviewer identity → pre-key public audio/context | blind review |
| API-027 | reviewer | Save/freeze blind observations | independent annotation → immutable pre-key submission | blind review |
| API-028 | reviewer | Disclose/read planned key after blind submit | phase guard → post-key private view | key review |
| API-029 | reviewer | Submit key/correction/unit review | review/evidence/hash → authenticated decisions | key review |
| API-030 | reviewer | Read retained pre-adjudication disagreement | assignment → permitted independent labels | adjudication |
| API-031 | reviewer | Third-person adjudication | conflict/evidence → resolved decision or blocking | adjudication |
| API-032 | publisher | Validate final publication eligibility | case/revision/gates → immutable verification report | publication |
| API-033 | publisher | Publish immutable version | verified revision → published case/audit | publication |
| API-034 | publisher | Quarantine a case with evidence | case/revision/reason → blocked new assignments | quarantine |
| API-035 | publisher | Reopen case for renewed review | quarantined revision → needs_review | quarantine |
| API-036 | publisher | Retire published case | case/revision → historical-only availability | retirement |
| API-037 | adjudicator | Read original dispute/answer/key/evidence | authorized dispute → private immutable evidence | dispute |
| API-038 | adjudicator | Resolve disputed semantic decision | dispute/revision/evidence → adjudication | dispute |
| API-039 | adjudicator | Append result revision under explicit request | old result/new approved decisions → new result revision | dispute |
| API-040 | operator | Register/check exact source use permission | source/use/agreement → denied or approved scope | corpus |
| API-041 | operator | Register immutable full release manifest | complete components/hashes → release record | corpus |
| API-042 | operator | Quarantine/validate/import full release | release/parser → faithful records/import report | corpus |
| API-043 | operator | Freeze source groups and splits | groups/policy → immutable split manifests | corpus |
| API-044 | operator | Register approved first-party gold | case/reviews/count policy → gold record/version | gold |
| API-045 | operator | Collect and independently annotate teacher answers | real answer/permission → frozen multi-rater gold | gold |
| API-046 | operator | Calculate full-source and122-leaf coverage | manifest/count rule → deficits and coverage report | validation |
| API-047 | operator | Run acceptance against frozen heldout configuration | fixed gold/profiles → real denominators/gates | validation |
| API-048 | administrator | Manage account roles/disable/qualifications | authorized actual people → roles/qualification evidence | administration |
| API-049 | administrator | Select/version provider role bindings | approved explicit config → frozen registry | administration |
| API-050 | administrator | Read costs/limits/provider receipts safely | authorized scope → usage/evidence without secrets | administration |
| API-051 | administrator | Read privileged audit and approval records | actor/resource scope → permitted history | administration |
| API-052 | operator | Back up/validate/restore complete DB/media | snapshot manifest → compatible restored state | recovery |
| API-053 | operator | Migration/private bucket/account initialization | configuration/compatibility → real readiness | startup |
| API-054 | operator | Health/readiness and unavailable dependency status | bounded service checks → safe health states | startup |
| API-055 | operator | Package and start released two-architecture deployment | actual images/manifest/secrets → reproducible local startup | release |
| API-056 | speech | API-to-speech render/QC/advisory requests | authorized immutable asset/plan → typed outcome | internal API |

No complete route/schema contract currently closes this inventory. Fifteen domain/LLM schemas do not define a product API. Positive closure covers every row with declared transport and guards. Negative closure rejects omitted operations, undefined payloads and any forbidden disclosure or state transition.
