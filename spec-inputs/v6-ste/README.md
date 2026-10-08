# Teacher Error Trainer: reviewed English specification

This package replaces v5. It contains the specification, data contracts, source instructions, and reference algorithms.
It does not contain an application or an approved language corpus. Application release remains blocked.

The teacher listens to prepared audio. The teacher writes the errors in one text box.
The application saves the answer before it contacts the LLM. The teacher waits for the result in the same request.
The result separates detection, classification, correction, and explanation. The application calculates the metrics from resolved decisions.

## Scope

All 122 existing taxonomy IDs remain in scope. The eight existing language domains remain in scope.
The application must support pronunciation and prosody in the first release. Unsupported speech generation must stop the affected case.
The application must not remove a target to obtain a successful result. The application must not replace synthesis with a recording.

The local deployment uses containers. The operator supplies real credentials through local configuration.
No default mock provider, invented exercise, or precomputed success result is permitted. No background assessment process is required.

## Read the package

Read `AGENTS.md` before implementation. Read `docs/authority.md` for document precedence.
Read `docs/change-control.md` for approval requirements. Read `audit/REVIEW.md` for findings and limits.
Read `audit/validation-results.json` for the checks that this review actually completed.

Read the OpenSpec change under `openspec/changes/bootstrap-teacher-error-trainer/`.
The `contracts/` directory defines data fields. The `domain/` directory defines taxonomy, metrics, sources, and providers.
The `docs/` directory gives the corresponding procedures. The `prompts/` directory gives instructions for the LLM.

## Language

The prose uses the SimpleEnglish Strict rules at the revision in `language/source-lock.json`.
Technical terms have definitions in `language/technical-terms.yaml`. Identifiers, formulas, and protected language examples retain their original meaning.
The package does not contain the official ASD-STE100 dictionary. Full dictionary compliance is not established.
A mechanical language check is not a compliance certificate. Read `language/README.md` for its coverage and exclusions.

## Application status

The Compose file is a deployment contract. The application images do not exist in this package.
Do not advertise the package as a working application. Do not replace missing components with stand-ins.
The publisher must build the application and supply real image digests before the operator can start it.

No corpus has an approved media asset in this package. No live provider result is available from this review.
The full-domain release requires actual generated audio, permitted uses, independent reviews, and measured provider results.
The existing numerical thresholds remain documented policy values. They are not measured outcomes or validated teacher norms.

## Review commands

Use Python with the dependencies in `requirements-review.txt`.
From this directory, do the package checks:

```sh
python scripts/review_v6.py
```

This command examines actual package files. It does not create learner recordings, teacher answers, or provider responses.
The report separates structural results from language results and unperformed application tests.
The inventory of excluded v5 test constructions is in `restricted/inherited-tests.json`.
Do not use those constructions as empirical language evidence.
