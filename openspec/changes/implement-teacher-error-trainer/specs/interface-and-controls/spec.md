## ADDED Requirements

### Requirement: UX-01 Consistent accessible listening workspace
The application SHALL use one responsive navigation and typography system across
Library, preparation, listening/results, attempts, audio, reviews, sources,
reports, Settings, recovery and cleanup. Existing actions, saved content, failure
states and provider restrictions remain available. Navigation identifies the
current route, works with a keyboard and collapses on narrow screens. Long text
and advanced data do not force page-level horizontal scrolling.

#### Scenario: UX-01 Desktop and narrow route continuity
- **GIVEN** saved and empty/error states on the existing application routes
- **WHEN** a person navigates on a desktop or narrow viewport
- **THEN** content, actions and current-route navigation are readable and usable
- **AND** no route or retained answer is removed and no navigation triggers inference

### Requirement: UX-02 Searchable exact mistake selection
The application SHALL expose registered individual error categories grouped by
family, with search, selected state and clear selection. Exact selection uses the
existing taxonomy, restricts injection to selected leaves and covers each leaf
unless the explicit count is zero. Keep broad-family and advanced controls, with
explicit advanced fields overriding matching simple fields.

#### Scenario: UX-02 Exact categories and valid controls
- **GIVEN** the current registered taxonomy and no selected broad family
- **WHEN** collocation and formality are selected
- **THEN** the saved request has only those two category_ids, each requiring an error
- **AND** searching, clearing and metadata-load failure preserve other form input
- **AND** acceptable style variants are not offered as injected mistakes
- **AND** labels and descriptions come from the application's existing taxonomy
- **AND** choosing exact leaves clears the simple broad-family selection and vice versa
- **AND** explicit advanced fields override matching simple fields while retaining
  the existing admission of compatible targets and families

### Requirement: UX-03 Explicit independent severity
The application SHALL support optional severity_levels in the exercise request,
using only minor, moderate, major and communication_breakdown. Absent or empty
means any. The mutation LLM receives the selection; the existing single new-output
admission accepts true-error units only at a selected severity. Existing weights
1/2/3/4 and native scoring remain unchanged. Save and resume preserve the selection.

#### Scenario: UX-03 Severity request and incompatible output
- **GIVEN** a preparation requesting only minor or moderate errors
- **WHEN** its mutation output is admitted
- **THEN** a minor/moderate unit with its existing weight is accepted
- **AND** a major unit is rejected without changing the saved clean text
- **AND** an omitted selection or explicit zero retains its existing behavior

### Requirement: UX-04 Understandable mistake amounts
The application SHALL offer Automatic, Low, Medium, High and Exact amounts.
Low/Medium/High resolve from requested words at 1/2/4 errors per 100 words using
round-to-nearest and a minimum of one plus required selected-category coverage.
The resulting exact count is visible before generation and saved through the
existing mutation_count field. Explain that requested length is approximate.
Exact nonnegative counts, including zero, and advanced overrides remain supported.

#### Scenario: UX-04 Preset resolution and exact override
- **GIVEN** a 200-word request with no category coverage floor
- **WHEN** Low, Medium or High is selected
- **THEN** the exact requested count is respectively 2, 4 or 8
- **AND** selected categories can raise that count with a visible explanation
- **AND** Exact zero sends zero, Automatic sends null, and invalid exact counts
  preserve input without starting generation
