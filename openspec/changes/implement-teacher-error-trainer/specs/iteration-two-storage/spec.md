# iteration-two-storage specification

## Purpose

Native storage and asset-lifecycle decomposition of the approved persistence/runtime contracts. All later product owners remain required; these cases do not establish generated keys, scoring, Lab, imports or full user backup/restore.

## ADDED Requirements

### Requirement: I2-01 Typed schema registration and complete document readback

The local storage foundation SHALL implement this behavior through services/api/internal/contracts/contracts.go, preserving the complete approved specification/v2/docs/persistence.md and runtime-and-storage.md obligations. Parent references: RUN-02, SPEC-003.

#### Scenario: I2-01 packet 1

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 1 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

#### Scenario: I2-01 packet 2

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 2 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

### Requirement: I2-02 RFC8785 canonical bytes preserve Unicode and reject ambiguous input

The local storage foundation SHALL implement this behavior through services/api/internal/contracts/contracts.go, preserving the complete approved specification/v2/docs/persistence.md and runtime-and-storage.md obligations. Parent references: SPEC-003.

#### Scenario: I2-02 packet 1

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 1 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

#### Scenario: I2-02 packet 2

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 2 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

### Requirement: I2-03 Immutable documents retain historical versions after head advances

The local storage foundation SHALL implement this behavior through services/api/internal/app/domain.go, preserving the complete approved specification/v2/docs/persistence.md and runtime-and-storage.md obligations. Parent references: SPEC-003, V6-SES-01.

#### Scenario: I2-03 packet 1

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 1 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

#### Scenario: I2-03 packet 2

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 2 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

### Requirement: I2-04 Document nodes references heads and audit commit atomically

The local storage foundation SHALL implement this behavior through services/api/internal/app/domain.go, preserving the complete approved specification/v2/docs/persistence.md and runtime-and-storage.md obligations. Parent references: SPEC-003.

#### Scenario: I2-04 packet 1

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 1 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

#### Scenario: I2-04 packet 2

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 2 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

### Requirement: I2-05 Reference projection resolves the declared exact type scope and digest

The local storage foundation SHALL implement this behavior through services/api/internal/app/domain.go, preserving the complete approved specification/v2/docs/persistence.md and runtime-and-storage.md obligations. Parent references: SPEC-003.

#### Scenario: I2-05 packet 1

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 1 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

#### Scenario: I2-05 packet 2

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 2 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

### Requirement: I2-06 Entity creation and compare-and-swap permit exactly one revision advance

The local storage foundation SHALL implement this behavior through services/api/internal/app/domain.go, preserving the complete approved specification/v2/docs/persistence.md and runtime-and-storage.md obligations. Parent references: SPEC-003.

#### Scenario: I2-06 packet 1

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 1 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

#### Scenario: I2-06 packet 2

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 2 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

### Requirement: I2-07 Idempotency includes the concrete request and preserves completed response

The local storage foundation SHALL implement this behavior through services/api/internal/app/domain.go, preserving the complete approved specification/v2/docs/persistence.md and runtime-and-storage.md obligations. Parent references: RUN-06.

#### Scenario: I2-07 packet 1

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 1 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

#### Scenario: I2-07 packet 2

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 2 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

### Requirement: I2-08 Only complete independently readback-verified private bytes become deliverable

The local storage foundation SHALL implement this behavior through services/api/internal/app/assets.go, preserving the complete approved specification/v2/docs/persistence.md and runtime-and-storage.md obligations. Parent references: RUN-06.

#### Scenario: I2-08 packet 1

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 1 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

#### Scenario: I2-08 packet 2

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 2 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

### Requirement: I2-09 Interrupted native object and multipart writes recover without fabricated completion

The local storage foundation SHALL implement this behavior through services/api/internal/app/multipart.go, preserving the complete approved specification/v2/docs/persistence.md and runtime-and-storage.md obligations. Parent references: RUN-06.

#### Scenario: I2-09 packet 1

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 1 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

#### Scenario: I2-09 packet 2

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 2 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

### Requirement: I2-10 Frozen owner revision guards atomic asset and owner publication

The local storage foundation SHALL implement this behavior through services/api/internal/app/assets.go, preserving the complete approved specification/v2/docs/persistence.md and runtime-and-storage.md obligations. Parent references: SPEC-003.

#### Scenario: I2-10 packet 1

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 1 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

#### Scenario: I2-10 packet 2

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 2 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

### Requirement: I2-11 Explicit orphan preview respects age and historical reference closure

The local storage foundation SHALL implement this behavior through services/api/internal/app/assets.go, preserving the complete approved specification/v2/docs/persistence.md and runtime-and-storage.md obligations. Parent references: RUN-06.

#### Scenario: I2-11 packet 1

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 1 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

#### Scenario: I2-11 packet 2

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 2 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

### Requirement: I2-12 Upgrade backup precedes additive migration and readiness rejects damaged history or shape

Readiness SHALL verify every required column has the PostgreSQL type and size/precision specified by the frozen migration, including Library timestamps. A column retaining its name with an incompatible type SHALL be unavailable while liveness remains successful; restoration SHALL recover readiness. The original migrations SHALL remain unchanged.

The local storage foundation SHALL implement this behavior through services/api/internal/app/migration.go, preserving the complete approved specification/v2/docs/persistence.md and runtime-and-storage.md obligations. Parent references: RUN-02, I1-03, I1-06.

#### Scenario: I2-12 packet 1

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 1 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

#### Scenario: I2-12 packet 2

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 2 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

### Requirement: I2-13 Real Library browser renders populated error and Refresh recovery states

The local storage foundation SHALL implement this behavior through services/web/app/page.js, preserving the complete approved specification/v2/docs/persistence.md and runtime-and-storage.md obligations. Parent references: I1-04, I1-05.

#### Scenario: I2-13 packet 1

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 1 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

#### Scenario: I2-13 packet 2

- **WHEN** the literal native positive or negative fixture in audit/iteration-2-domain-storage-20261010/CASES.json packet 2 executes
- **THEN** its real SQL/object/browser result SHALL equal the independent stated expectations, with failed operations remaining non-success and no substitution

### Requirement: I2-14 Owned binding and render digest projections ignore only specified identity fields

Saved effective-binding hashes SHALL exclude id and binding_sha256 only. Render-plan hashes SHALL exclude id, schema_version and plan_sha256 only. Other payload changes SHALL fail under the unchanged digest, using independent literal golden expectations. No provider or acoustic observation is implied.

#### Scenario: I2-14 packet 1

- **WHEN** binding identity or model content changes under the independently saved literal digest
- **THEN** the actual contract owner SHALL accept the identity change and reject changed model content

#### Scenario: I2-14 packet 2

- **WHEN** render identity fields or frozen case lineage change under the independently saved literal digest
- **THEN** the actual digest owner SHALL accept the specified identity-field changes and reject changed case lineage


### Requirement: I2-15 Guarded upload progress does not need an additional pool connection

The storage owner SHALL preserve this invariant through services/api/internal/app/assets.go. Parent obligation: I2-08; the approved persistence and runtime/storage contracts remain unchanged.

#### Scenario: I2-15 repair packet 1

- **WHEN** the exact native positive or negative fixture in audit/iterations-1-2-repair-20261010/CASES.json packet 1 executes
- **THEN** the production transaction, native object and independent expected state SHALL agree; rejection SHALL retain prior durable state

#### Scenario: I2-15 repair packet 2

- **WHEN** the exact native positive or negative fixture in audit/iterations-1-2-repair-20261010/CASES.json packet 2 executes
- **THEN** the production transaction, native object and independent expected state SHALL agree; rejection SHALL retain prior durable state


### Requirement: I2-16 Evidence-parent DAG roles and graph invariants apply to every document publication

The storage owner SHALL preserve this invariant through services/api/internal/app/domain.go. Parent obligation: I2-04; the approved persistence and runtime/storage contracts remain unchanged.

#### Scenario: I2-16 repair packet 1

- **WHEN** the exact native positive or negative fixture in audit/iterations-1-2-repair-20261010/CASES.json packet 1 executes
- **THEN** the production transaction, native object and independent expected state SHALL agree; rejection SHALL retain prior durable state

#### Scenario: I2-16 repair packet 2

- **WHEN** the exact native positive or negative fixture in audit/iterations-1-2-repair-20261010/CASES.json packet 2 executes
- **THEN** the production transaction, native object and independent expected state SHALL agree; rejection SHALL retain prior durable state


### Requirement: I2-17 Interrupted multipart failure retains immutable lineage and explicit new-key retry

The storage owner SHALL preserve this invariant through services/api/internal/app/multipart.go. Parent obligation: I2-09; the approved persistence and runtime/storage contracts remain unchanged. Each retry key SHALL belong to exactly one frozen original failure result. An existing independent operation SHALL never be relabelled as a retry.

#### Scenario: I2-17 repair packet 1

- **WHEN** the exact native positive or negative fixture in audit/iterations-1-2-repair-20261010/CASES.json packet 1 executes
- **THEN** the production transaction, native object and independent expected state SHALL agree; rejection SHALL retain prior durable state

#### Scenario: I2-17 repair packet 2

- **WHEN** the exact native positive or negative fixture in audit/iterations-1-2-repair-20261010/CASES.json packet 2 executes
- **THEN** the production transaction, native object and independent expected state SHALL agree; rejection SHALL retain prior durable state


### Requirement: I2-18 Readiness verifies enabled exact immutability guards and recovers after repair

The storage owner SHALL preserve this invariant through services/api/internal/app/storage.go. Parent obligation: I2-12; the approved persistence and runtime/storage contracts remain unchanged.

#### Scenario: I2-18 repair packet 1

- **WHEN** the exact native positive or negative fixture in audit/iterations-1-2-repair-20261010/CASES.json packet 1 executes
- **THEN** the production transaction, native object and independent expected state SHALL agree; rejection SHALL retain prior durable state

#### Scenario: I2-18 repair packet 2

- **WHEN** the exact native positive or negative fixture in audit/iterations-1-2-repair-20261010/CASES.json packet 2 executes
- **THEN** the production transaction, native object and independent expected state SHALL agree; rejection SHALL retain prior durable state

