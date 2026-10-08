"""Build task-derived recovery specs; never reconstruct missing v6 originals."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CHANGE = "implement-teacher-error-trainer"
C = ROOT / "openspec/changes" / CHANGE

# Each tuple is an observable property with a separately falsifiable accepted
# and rejected case. These are task-derived IDs, not the missing original IDs.
ROWS = [
    ("source-and-decisions", "SRC-01", "Preserve supplied source bytes", "retain all nine imports and their original hashes, distinguishing historical validation from current receipts", "compare every destination with its supplied SHA-256", "reject a modified import or a historical receipt presented as current", "audit/import-manifest.json"),
    ("source-and-decisions", "SRC-02", "Keep missing original contracts explicit", "preserve the 122-category scope and identify missing taxonomy, schemas, prompts, validation policy and reference code without inventing them", "resolve a recovered original contract to authenticated provenance", "block semantic use when an ID or contract has no original source", "audit/completeness.md"),
    ("source-and-decisions", "DEC-01", "Separate owner decisions", "keep DEC-001 through DEC-008 separate and unapproved until each exact scope has a real owner message; continue independent work", "apply one scoped approved decision only to its dependent operation", "refuse approval inheritance across decision IDs or invented messages", "audit/open-decisions.json"),
    ("source-and-decisions", "APR-01", "Protect restricted evidence", "require exact scoped approval for artificial linguistic cases and substitutes, and never manufacture human approvals or real corpus observations", "run a separately approved restricted case within its scope", "refuse an unapproved artificial teacher answer or changed substitute", "docs/change-control.md"),
    ("local-runtime", "RUN-01", "Run the prescribed real services", "use Next.js, Go API, PostgreSQL, private MinIO and Python speech in Compose, with only 127.0.0.1:3000 published", "build the real services and connect the browser through port 3000", "reject host exposure for API, database, storage or speech", "deploy/local/compose.yaml"),
    ("local-runtime", "RUN-02", "Gate startup on initialization", "wait for healthy dependencies and successful migration, private media initialization and account initialization before web readiness", "start from empty persistent volumes with successful one-shot initialization", "keep dependent services unavailable after failed migration or initialization", "deploy/local/compose.yaml"),
    ("local-runtime", "RUN-03", "Keep the exercise bank truthful", "read published exercises from PostgreSQL and display an empty library when none exist, without successful placeholder exercises", "read an actually published exercise from the database", "show an empty state for zero rows and never synthesize a demonstration", "services/api/internal/app"),
    ("local-runtime", "RUN-04", "Authenticate local accounts", "initialize the local owner idempotently, hash passwords, persist expiring sessions, revoke on logout and require authentication for protected data", "log in with a configured account and read its session", "reject wrong passwords, expired/revoked sessions and unauthorized requests", "services/api/internal/app"),
    ("local-runtime", "RUN-05", "Enforce same-origin access", "proxy browser API requests on the same origin and reject cross-origin mutations without exposing provider keys or backend credentials", "send an authenticated mutation from the configured local origin", "reject a cross-origin mutation and keep credentials out of responses", "services/web"),
    ("local-runtime", "RUN-06", "Persist and recover real data", "retain PostgreSQL and private media after restart and provide a restorable backup with matching hashes", "restart then restore a backup and read original rows and media hashes", "detect missing media, incomplete backup or incompatible migration", "deploy/local"),
    ("local-runtime", "RUN-07", "Report actual readiness", "distinguish liveness from dependency readiness and return non-success when database, private media or speech is unavailable", "report ready after real dependencies and migrations are available", "report unavailable when any required dependency fails", "services/api/internal/app"),
    ("domain-scoring", "DOM-01", "Retain the full taxonomy", "retain all 122 original category IDs, key versions, protected illustrations, variety, register and intended-context constraints", "accept an original category valid in the declared context", "reject unknown categories and context-incompatible error labels", "domain/error-taxonomy.v1.yaml"),
    ("domain-scoring", "DOM-02", "Scope evidence ownership", "bind evidence to the exact exercise, unit, revision and audio SHA-256 and authorize the reader, rather than accepting global ID membership", "accept evidence owned by the selected exercise revision and audio", "reject existing evidence borrowed from another exercise, unit, revision or audio", "contracts/evidence.schema.json"),
    ("domain-scoring", "DOM-03", "Preserve exact Unicode claims", "extract quoted claims with half-open Unicode codepoint offsets in the original answer, preserving repeated text, normalization and retractions", "resolve a quoted repeated Unicode span to its exact occurrence", "reject byte/UTF-16 offsets, normalized-text drift and an untraceable quote", "contracts/claim-extraction.schema.json"),
    ("domain-scoring", "DOM-04", "Separate distinct claim outcomes", "deduplicate repeated assertions, preserve explicit retractions, require review for contradictions and keep unresolved classification separate from detection", "score resolved distinct assertions with retracted claims excluded as specified", "route contradictory/unresolved groups to review without final ratios", "docs/scoring-v1.md"),
    ("domain-scoring", "DOM-05", "Represent exact ratios and N/A", "store exact numerator and denominator, use null with no_opportunities or no_assertions for zero denominators, and round displayed percentages half-up to one decimal", "produce an exact ratio and independently expected display percentage", "return N/A for zero denominators and reject invalid or negative counters", "services/speech/metrics.py"),
    ("domain-scoring", "DOM-06", "Aggregate from raw decisions", "pool raw counters for aggregate metrics, provide domain breakdowns and never average percentages or publish a composite for unresolved claims", "recalculate pooled counters across differently sized exercises", "reject percentage averaging and final metrics for unresolved evidence", "services/speech/metrics.py"),
    ("domain-scoring", "DOM-07", "Preserve auxiliary and unobserved metrics", "retain all 15 auxiliary formulas and keep teacher talk time, spoken pronunciation, classroom management and real engagement null in this listening-only mode", "report an auxiliary value with observed counts and method provenance", "keep unobserved teacher behavior null and refuse unsupported acoustic comparisons", "domain/metrics.v1.yaml"),
    ("author-review-publication", "AUT-01", "Support author preparation", "let authors prepare monologues/dialogues with context, voices, rate and planned errors, then obtain source text, key and real synthetic audio", "prepare an authorized case and retain its real provider output", "refuse unsupported hard constraints or failed synthesis without a fabricated asset", "services/web"),
    ("author-review-publication", "REV-01", "Require independent blind review", "require two distinct qualified humans to listen without the planned key before comparing their own annotations with the key; require verified phonetics competence for acoustic cases", "retain two independent blind annotations and qualifying competence", "reject one person using two accounts, early key disclosure or missing acoustic qualification", "services/api/internal/review"),
    ("author-review-publication", "REV-02", "Resolve disagreement without erasure", "retain initial disagreement and use a third qualified adjudicator or leave the recording unpublished", "retain initial labels and a separate adjudication decision", "refuse publication with unresolved disagreement or overwritten initial labels", "services/api/internal/review"),
    ("author-review-publication", "PUB-01", "Publish immutable reviewed versions", "publish only after every required gate and create a new unapproved version whenever audio or key changes", "publish a qualifying reviewed revision with immutable key/audio hashes", "reject approval reuse after key/audio mutation and edits to published revisions", "services/api/internal/publication"),
    ("author-review-publication", "DSP-01", "Version disputed results", "show original teacher answer and evidence during disputes and append adjudicated result versions without deleting earlier results", "append a reviewed result linked to the preserved original", "reject unauthorized adjudication or replacement/deletion of result history", "services/api/internal/disputes"),
    ("provider-integration", "PRV-01", "Use the retained real profiles", "use gpt-4.1-2025-04-14, Azure registered voices, whisper-1 and Azure Pronunciation Assessment without silent fallback", "call the configured profile and retain its exact returned metadata", "fail the affected call on missing credentials or unavailable profile without substitution", "domain/providers.v1.yaml"),
    ("provider-integration", "PRV-02", "Retain real call receipts", "record profile, prompt/schema versions, input hash, output/error, duration and usage for each real call without leaking credentials", "reconcile a real call with its versioned secret-safe receipt", "reject a receipt missing versions, hashes or real provenance", "services/api/internal/providers"),
    ("provider-integration", "PRV-03", "Verify acoustic realization", "verify that intended grammar, phonetic substitutions, voice differences and tempo occur in the actual audio, not merely the request parameters", "retain real audio and qualified listening evidence for each required target", "fail an unrealized acoustic target and preserve its category in scope", "audit/decisions/DEC-007.md"),
    ("provider-integration", "PRV-04", "Bound advisory speech assessment", "treat ASR timing and Azure scores as advisory, use prosody assessment only for supported en-US, and never infer an observed replacement phone from a low score", "retain supported advisory output with its declared scope", "refuse phoneme-gold or non-en-US prosody claims from the advisory profile", "services/speech"),
    ("teacher-workflow", "TCH-01", "Save original submissions first", "save the original Russian/English free answer and SHA-256 before provider processing and restrict attempts to authorized published exercises", "submit to a published exercise and read back the identical saved answer", "reject unpublished/foreign exercises and preserve the answer after provider failure", "services/api/internal/attempts"),
    ("teacher-workflow", "TCH-02", "Separate blind extraction and audits", "extract claims without the key, map with the key in a separate request, audit consistency separately, calculate numbers in code and generate grounded feedback only afterwards", "trace a real attempt through all separately versioned stages", "reject key leakage into blind extraction or numbers invented by feedback", "services/api/internal/attempts"),
    ("teacher-workflow", "TCH-03", "Distinguish processing outcomes", "persist ready, needs_review and technical_error outcomes distinctly and display confirmed/missed errors, false positives, corrections, explanations, domain metrics and exercise evidence", "display a saved ready result with source evidence and raw counters", "display needs_review or technical_error without a fake final score", "services/web"),
    ("teacher-workflow", "TCH-04", "Keep synchronous bounded processing", "use a common 270-second overall bound across API/proxy/browser with cancellation, no queue or WebSocket, and explicit user-triggered retries using the same saved answer", "complete synchronously within the overall deadline and explicitly retry saved content", "cancel on the overall deadline and prevent automatic retry/background execution", "services/api/internal/attempts"),
    ("corpus-validation", "COR-01", "Protect source permissions", "acquire exact corpus releases only with scope-specific permission, preserve raw hashes in quarantine and keep corpora out of normal startup and public images", "import a permitted immutable release with actual legal/source receipts", "deny unapproved uses, guessed mirrors or startup corpus downloads", "docs/corpus-acquisition.md"),
    ("corpus-validation", "COR-02", "Normalize safely and transparently", "reject traversal, external links, executable content, unbounded decompression and command execution; preserve original tokens, annotators, source scales and transformations with invalid rows quarantined", "import a bounded archive and retain accepted/rejected provenance", "quarantine unsafe archives, invalid offsets or unknown scales rather than guess", "services/api/internal/corpus"),
    ("corpus-validation", "COR-03", "Cover every category honestly", "cover all 122 leaves and required controls using independently reviewed real synthesis, and keep the inherited 732 floor pending DEC-002 rather than treating it as a resolved counting rule", "reconcile per-leaf assets, observations and controls under approved counting", "refuse coverage when a variant becomes an error or counts have no approved unit", "domain/validation-policy.yaml"),
    ("corpus-validation", "COR-04", "Collect real teacher answers", "retain real answers and independent pre-model labels for correct, partial, vague, repeated, contradictory, false, alternative and off-key observations", "retain permitted real answers and independently adjudicated claims", "leave missing classes missing instead of filling them with invented real answers", "data/gold"),
    ("corpus-validation", "COR-05", "Keep splits and thresholds frozen", "group related learners/speakers/scripts/derivatives into one development, calibration or holdout split, prohibit holdout prompt tuning and fix approved thresholds before seeing results", "evaluate untouched holdout with real denominators and fixed policy", "block fresh-independent claims after overlap, holdout reuse or post-result threshold tuning", "data/manifests"),
    ("corpus-validation", "COR-06", "Measure semantic performance", "measure mapping precision, decision coverage, correction agreement and repeatability with real denominators, preserved initial disagreement and the fixed approved policy", "publish measured results with authentic populations and denominators", "reject zero-selected, missing-class or invented performance receipts", "audit/acceptance"),
    ("release-acceptance", "REL-01", "Deliver fixed build artifacts", "deliver source, Dockerfiles, working Compose, fixed dependencies, inspected image references/digests, migrations and exact startup instructions", "build and inspect the actual images used by the documented command", "block release for missing builds, moving image tags or invented digests", "deploy/local"),
    ("release-acceptance", "REL-02", "Prove the complete browser cycle", "demonstrate real author, independent reviewers and teacher flows with real providers, persistent answers, no early key leakage and no browser secrets", "complete one real published case end to end through the browser", "demonstrate that provider failure preserves the answer without a fake result", "tests/acceptance"),
    ("release-acceptance", "REL-03", "Verify portability and restore", "actually verify amd64 and arm64 builds/runs plus database/media restart and backup restoration with source-bound acceptance reports", "restore and run each architecture with matching hashes and rows", "block portability or recovery claims for an untested architecture or failed restore", "audit/acceptance"),
]

def core_formulas():
    source = (ROOT / "domain/metrics.v1.yaml").read_text()
    block = source.split("metrics:\n", 1)[1].split("auxiliary_metrics:\n", 1)[0]
    return [
        (m.group(1), re.search(r"^  formula: (.+)$", m.group(2), re.M).group(1))
        for m in re.finditer(r"^- id: (\S+)\n(.*?)(?=^- id: |\Z)", block, re.M | re.S)
    ]

def build():
    if (C / 'evidence/retained-native-results.json').exists():
        raise SystemExit('Recovery artifacts already have implementation evidence; update the existing change explicitly instead of regenerating it.')
    rows = list(ROWS)
    rows = [row for row in rows if row[1] != 'DEC-01']
    for decision in json.loads((ROOT / 'audit/open-decisions.json').read_text()):
        rows.append(('source-and-decisions', decision['id'], 'Resolve ' + decision['subject'],
            'require a separately scoped real owner decision for ' + decision['id'] + ': ' + decision['required_action'] + ' While unresolved: ' + decision['runtime_rule'],
            'admit only the exact approved ' + decision['id'] + ' property and matching evidence',
            'refuse an unapproved, changed, expired or borrowed ' + decision['id'] + ' decision',
            'audit/decisions/' + decision['id'] + '.md'))
    for i, (metric, formula) in enumerate(core_formulas(), 1):
        rows.append(("domain-scoring", f"MET-{i:02d}", f"Preserve {metric}",
                     f"calculate {metric} using the exact retained formula `{formula}` from domain/metrics.v1.yaml, with exact counters and N/A behavior",
                     f"calculate an independently specified exact arithmetic case for {metric}",
                     f"reject invalid counters and return N/A for the zero denominator of {metric}", "services/speech/metrics.py"))
    assert len(core_formulas()) == 27
    auxiliary = (ROOT / 'domain/metrics.v1.yaml').read_text().split('auxiliary_metrics:\n', 1)[1]
    for i, match in enumerate(re.finditer(r'^- id: (\S+)\n(.*?)(?=^- id: |\Z)', auxiliary, re.M | re.S), 1):
        metric = match.group(1)
        formula = re.search(r'^  formula: (.+)$', match.group(2), re.M).group(1)
        rows.append(('domain-scoring', f'AUX-{i:02d}', 'Preserve ' + metric,
            f'retain the auxiliary formula `{formula}` for {metric} with its declared observation/method limits; unavailable observations remain null',
            'calculate ' + metric + ' from actual permitted observations using the approved method, or preserve its specified null value',
            'reject an invented observation or unsupported measurement for ' + metric,
            'domain/metrics.v1.yaml'))
    inventory = []
    for cap in sorted({row[0] for row in rows}):
        path = C / "specs" / cap / "spec.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        text = f"# {cap} specification\n\n## Purpose\n\nPreserve the observable {cap.replace('-', ' ')} requirements of Teacher Error Trainer with explicit rejection and evidence boundaries.\n\n## ADDED Requirements\n\n"
        for _, rid, title, statement, positive, negative, owner in [x for x in rows if x[0] == cap]:
            scenario = f"{rid} supported and rejected inputs"
            text += f"### Requirement: {rid} {title}\n\nThe system SHALL {statement}.\n\n#### Scenario: {scenario}\n\n- **WHEN** the authorized operation receives supported inputs or a violating input\n- **THEN** it SHALL {positive}, and SHALL {negative}\n\n"
            inventory.append(dict(id=rid, capability=cap, title=f"{rid} {title}", statement=statement,
                                  scenario=scenario, positive=positive, negative=negative, owner=owner,
                                  source="attached task and supplied registries; task-derived recovery ID"))
        path.write_text(text)
    (C / "property-inventory.json").write_text(json.dumps(inventory, indent=2) + "\n")
    sys.path.insert(0, str(ROOT / ".agents/workflow/scripts"))
    from requirement_tests import parse_delta_specs
    specs = parse_delta_specs(C)
    graph = dict(schema_version=2, change=CHANGE, requirements=[], properties=[], cases=[], commands=[])
    markers = []
    for row in inventory:
        spec = specs[row['capability'], row['title']]
        rid, pid = row['id'], row['id'] + '.P1'
        graph['requirements'].append(dict(id=rid, capability=row['capability'], title=row['title'], fingerprint=spec['fingerprint']))
        graph['properties'].append(dict(id=pid, requirement_id=rid, statement=row['statement'], scenarios=[row['scenario']], owner=row['owner'], oracle="The retained source requirement and separately recorded accepted/rejected observations, not model agreement.", source_globs=[row['owner'] + '/**' if '.' not in Path(row['owner']).name else row['owner']]))
        for polarity in ['positive', 'negative']:
            tid = f"planned::{rid}::{polarity}"
            markers.append(tid)
            graph['cases'].append(dict(id=f"{pid}.{polarity.upper()}", property_id=pid, polarity=polarity,
                scenario=row['scenario'], scenario_fingerprint=spec['scenario_fingerprints'][row['scenario']],
                setup="Use the actual owner at " + row['owner'] + " with the case described here: " + row[polarity],
                observable=row[polarity], red_expectation="A violating implementation admits the forbidden outcome or fails to preserve the required source fact.",
                green_expectation="The actual owner satisfies the separately specified " + polarity + " observation.",
                test_id=tid, command_id='pending', state='planned', source_path='tests/acceptance/test_full_scope.py', source_sha256=None,
                invalidation_dependencies=[row['owner'], 'domain/metrics.v1.yaml' if rid.startswith('MET-') else 'docs/authority.md'],
                substitution={'classification':'UNDECIDED', 'note':'Boundary/data contract must be resolved before implementation; no artificial linguistic data authorized.'}))
    graph['commands'].append(dict(id='pending', runner='command', argv=['python3','scripts/require_full_scope.py'], cwd='.', env={}, timeout_seconds=30, authority='local', expected_markers=markers))
    (C / 'verification.json').write_text(json.dumps(graph, indent=2) + '\n')
    props = [x['id'] for x in graph['properties']]
    (C / 'discovery.json').write_text(json.dumps(dict(schema_version=1, change=CHANGE,
        scope={'property_ids':props, 'test_ids':markers}, reviews=[dict(id='initial-source-inventory',
        question='Which supplied contracts exist and which implementation owners must be created?', property_ids=props, test_ids=markers,
        searches=[dict(kind='exact',status='completed',query='Read all nine explicitly supplied files and list referenced original paths',outcome='No application or referenced taxonomy/contracts/prompts are supplied.',results=[dict(path='audit/import-manifest.json',classification='reusable_unchanged',reason='Byte-preserved supplied source inventory'),dict(path='domain/metrics.v1.yaml',classification='interface_dependency',reason='Retained arithmetic formulas'),dict(path='audit/open-decisions.json',classification='unresolved',reason='Eight separately blocked properties')]),
                  dict(kind='semantic',status='not_applicable',query='Find existing Tangerine production owners',outcome='New empty repository; no existing implementation to discover.',reason='Owners do not exist; paths are authored from the task.'),
                  dict(kind='jetbrains-index',status='not_applicable',query='Locate known Tangerine symbols',outcome='No pre-existing Tangerine symbols or index.',reason='New repository; no symbol operation would resolve source gaps.')],
        disposition='current_change',rationale='Deliver the expressly requested project with recovered task requirements; do not guess missing original contracts.')]), indent=2)+'\n')
    print(json.dumps({'requirements':len(inventory),'properties':len(props),'cases':len(markers),'status':'planned; no behavior results'}))

if __name__ == '__main__':
    build()
