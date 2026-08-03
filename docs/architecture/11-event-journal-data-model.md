# Event Journal Data Model

## Purpose

This chapter defines the persistent data model for the Response Connect Event Journal.

Chapter 9 defines the wider Event Journal and operational architecture, including its relationship with:

* Desks;
* lifecycle transitions;
* Operational Logs;
* Audit Logs;
* Security Logs;
* Activity Streams;
* notifications;
* background jobs.

Chapter 10 defines the Desk Platform and operational hierarchy.

This chapter defines how Journal Entries, Journal References, classifications, relationships, metadata, correlation, and causation are stored and queried.

The Event Journal records immutable historical facts.

Domain tables remain authoritative for current state.

---

# Terminology

Response Connect uses the following terminology:

| Term              | Meaning                                                                    |
| ----------------- | -------------------------------------------------------------------------- |
| Event Journal     | The shared system-wide persistent history platform                         |
| Occurrence        | Something that happened in the business or system                          |
| Journal Entry     | The immutable record of an occurrence                                      |
| Event code        | Stable machine identifier describing the occurrence                        |
| Classification    | A category determining how a Journal Entry is used                         |
| Actor             | Who or what caused the occurrence                                          |
| Subject           | The primary record affected by the occurrence                              |
| Context           | The wider record or workflow containing the occurrence                     |
| Journal Reference | A stable Journal-owned identity representing an actor, subject, or context |
| Resource          | A business-domain record that may be represented by a Journal Reference    |
| Desk              | The operational responsibility boundary                                    |
| Activity Stream   | A filtered projection of Journal Entries                                   |
| Correlation       | A group of related occurrences                                             |
| Causation         | The immediate occurrence that caused another                               |

The implementation uses:

```text
app/journal/
```

and persistent model names such as:

```python
JournalEntry
JournalReference
```

This avoids confusion between Journal Entries and organised events managed through Event Medical.

---

# Journal References

Actor, subject, and context relationships are represented through stable Journal-owned reference records.

A Journal Reference preserves the identity and historical display information required by the Event Journal without requiring the Journal package to import every business-domain model.

Examples of records represented by Journal References include:

* User Accounts;
* Staff Members;
* Vehicles;
* Incidents;
* Patient Journeys;
* Shifts;
* Files;
* organised Event Medical events;
* integrations;
* schedulers;
* API clients;
* the Response Connect system.

A Journal Reference is not the authoritative business record.

The owning module remains authoritative for:

* current state;
* current display name;
* current lifecycle;
* current relationships;
* current permissions.

The Journal Reference provides a stable historical identity used by:

* Journal Entries;
* Activity Streams;
* Audit Logs;
* Operational Logs;
* Security Logs;
* correlation and investigation workflows.

---

# Data model objectives

The Event Journal data model must:

1. preserve immutable historical records;
2. provide one system-wide history platform;
3. support operational, audit, security, and system activity;
4. support Desk-aware activity;
5. support entries without a Desk where appropriate;
6. support stable actor, subject, and context identities;
7. avoid direct dependencies on every future business module;
8. provide database-enforced integrity between Journal Entries and Journal References;
9. preserve historical display information;
10. preserve correlation and causation;
11. support structured metadata;
12. remain practical for PostgreSQL;
13. support efficient timeline and Activity Stream queries;
14. minimise duplicated personal or sensitive data;
15. allow future archival and retention mechanisms;
16. prevent silent editing or deletion;
17. support local, system, integration, and external identities;
18. remain usable across all Response Connect modules.

---

# Core tables

The completed Event Journal data model requires:

```text
journal_entries
journal_references
journal_entry_classifications
```

## `journal_entries`

Stores immutable records of significant occurrences.

## `journal_references`

Stores stable Journal-owned identities representing actors, subjects, and contexts.

A single Journal Reference may appear in different roles across different Journal Entries.

For example, a Staff Member may be:

* the actor who updated another record;
* the subject of a qualification assignment;
* the context for a workforce Activity Stream.

## `journal_entry_classifications`

Associates each Journal Entry with one or more stable classifications.

Classification definitions are maintained through the Journal Reference Data vocabulary.

Additional supporting tables may be introduced later for:

* file relationships;
* retention;
* redaction;
* Journal Reference merges;
* notification relationships;
* external delivery records.

These are outside the initial implementation.

---

# Journal Entry model

The primary occurrence model is:

```python
JournalEntry
```

Table name:

```text
journal_entries
```

The completed model is expected to contain:

```text
id

event_code

occurred_at
recorded_at

actor_reference_id
subject_reference_id
context_reference_id

desk_id
desk_display_name

source
severity
visibility

summary
details

correlation_id
causation_id

metadata

created_at
```

The initial implementation may add these fields incrementally through focused vertical slices.

---

# Journal Entry identity

## `id`

Type:

```text
UUID
```

Properties:

* primary key;
* generated by Response Connect;
* immutable;
* never reused;
* externally safe to reference;
* contains no business meaning.

Example:

```python
id: UUID
```

Journal Entry identifiers are the canonical persistent identity of each entry.

A separate human-readable Journal number is not required initially.

User-facing workflows should normally identify the relevant business subject or context, such as:

* Incident number;
* Patient Journey number;
* Vehicle callsign;
* Shift reference;
* Desk name;
* Staff Member name.

A human-readable Journal Entry reference may be introduced later if operational or support requirements demonstrate a genuine need.

---

# Event code

## `event_code`

Type:

```text
string
```

Maximum length:

```text
120
```

Format:

```text
domain.action
```

Examples:

```text
vehicle.arrived_on_scene
staff.shift_signed_in
incident.created
authentication.login_failed
reference_data.synchronised
desk.moved
desk.archived
```

Rules:

1. lowercase only;
2. one dot separates the domain and action;
3. components use snake_case;
4. the code describes a completed fact;
5. the code remains stable after release;
6. the code must not contain editable display wording;
7. the code must be validated before persistence.

Recommended pattern:

```regex
^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$
```

Future multi-component domains require a separate design decision.

## Event-code ownership

Event codes are owned by the module recording the occurrence.

Examples:

```text
desk.created
desk.moved
desk.archived
vehicle.assigned
staff.shift_signed_in
```

The Journal package validates event-code format but does not own every business event code.

Business modules should define their event codes in code-owned constants or definitions.

The Journal must not provide administrator-configurable event codes.

---

# Timestamps

## `occurred_at`

The time the occurrence actually happened.

Type:

```text
timezone-aware datetime
```

Required:

```text
yes
```

Examples include:

* vehicle arrival time;
* actual staff sign-in time;
* event reported by an external integration;
* retrospective operational note time;
* actual file-processing completion time.

The recording service must reject naive timestamps.

## `recorded_at`

The time Response Connect persisted the Journal Entry.

Type:

```text
timezone-aware datetime
```

Required:

```text
yes
```

Default:

```text
current database time
```

`occurred_at` and `recorded_at` may differ.

This distinction supports:

* retrospective entries;
* offline systems;
* integration delays;
* queued processing;
* delayed synchronisation;
* corrected operational times.

## `created_at`

The database creation time.

For the initial implementation, `created_at` may be equivalent to `recorded_at`.

It remains useful for consistency with the wider platform and database-level inspection.

Journal Entries do not have `updated_at` because they are immutable.

---

# Journal Reference model

The Journal owns a stable reference model:

```python
JournalReference
```

Table name:

```text
journal_references
```

The model contains:

```text
id

reference_type
source_id
stable_key

display_name

created_at
```

---

# Journal Reference identity

## `id`

Type:

```text
UUID
```

Properties:

* primary key;
* generated by Response Connect;
* immutable;
* referenced by Journal Entries;
* remains stable for historical use.

The Journal Reference ID is not the same as the authoritative business-record ID.

---

# Reference type

## `reference_type`

A stable code describing the type of record represented.

Examples:

```text
user_account
staff_member
vehicle
incident
patient_journey
shift
file
desk
event_medical_event
integration
scheduler
api_client
system
```

Type:

```text
string
```

Suggested maximum length:

```text
100
```

Rules:

1. lowercase snake_case;
2. stable after release;
3. owned by the module registering the reference;
4. not derived from editable display wording;
5. suitable for query filtering and Activity Streams.

Recommended pattern:

```regex
^[a-z][a-z0-9_]*$
```

The Journal package validates the format but does not centrally own every reference type.

---

# Source ID

## `source_id`

The UUID of the authoritative record in its owning module.

Type:

```text
UUID
```

Nullable:

```text
yes
```

Examples:

```text
UserAccount.id
StaffMember.id
Vehicle.id
Incident.id
PatientJourney.id
FileObject.id
Desk.id
```

The Journal does not create a foreign key from `source_id` to every possible business table.

Doing so would couple the Journal package to every business module and require repeated Journal schema changes.

The registering business service is responsible for ensuring that the supplied source ID represents a valid record.

---

# Stable key

## `stable_key`

An optional stable textual identity for references without a local UUID.

Examples:

```text
system
scheduler:nightly
integration:moodle
api_client:external_dispatch
worker:file_processor
```

Type:

```text
string
```

Suggested maximum length:

```text
200
```

Nullable:

```text
yes
```

Rules:

1. lowercase;
2. stable after release;
3. must not contain secrets;
4. must not contain editable display wording;
5. must be unique within its reference type where present.

A Journal Reference must have at least one of:

```text
source_id
stable_key
```

A reference may have both where useful.

---

# Display name

## `display_name`

A minimal historical display label.

Examples:

```text
Alex Smith
Vehicle A12
Incident INC-2026-0042
Response Connect
Moodle Integration
Nightly Scheduler
```

Type:

```text
string
```

Suggested maximum length:

```text
255
```

Required:

```text
yes
```

The display name is a historical snapshot.

It is not automatically refreshed when the authoritative business record is renamed.

This ensures that past Journal Entries remain readable and reflect the label used at the time the reference was created.

Display names must avoid unnecessary sensitive information.

---

# Journal Reference uniqueness

Local business records should normally be unique by:

```text
reference_type + source_id
```

Non-local references should normally be unique by:

```text
reference_type + stable_key
```

The database should use conditional unique indexes so null values do not conflict.

Suggested indexes:

```text
UNIQUE(reference_type, source_id)
WHERE source_id IS NOT NULL
```

```text
UNIQUE(reference_type, stable_key)
WHERE stable_key IS NOT NULL
```

Repeated registration of the same identity must return the existing Journal Reference.

Journal Reference creation is therefore idempotent.

---

# Registering business records with the Journal

Business modules register records through the public Journal API.

Conceptually:

```python
vehicle_reference = journal_reference_service.get_or_create(
    reference_type="vehicle",
    source_id=vehicle.id,
    display_name=vehicle.callsign,
)
```

The Journal package must not import the Vehicle model.

The owning Fleet service provides:

* the stable reference type;
* the source UUID;
* the historical display name.

The same pattern applies to:

* Staff Members;
* User Accounts;
* Incidents;
* Patient Journeys;
* Files;
* Shifts;
* organised events;
* integrations;
* schedulers;
* API clients.

Business modules must not create `JournalReference` rows directly through SQLAlchemy.

A public Journal Reference service should expose an idempotent method such as:

```python
JournalReferenceService.get_or_create(...)
```

The exact API will be defined during implementation.

---

# Resource concept

Many Response Connect records may conceptually be described as resources:

* people;
* vehicles;
* incidents;
* shifts;
* journeys;
* files;
* organised events;
* equipment;
* policies;
* qualifications;
* training courses.

The initial Journal implementation will not introduce a universal `Resource` database table or require business models to inherit from a shared Resource model.

Introducing such a broad abstraction now would create cross-platform coupling before the requirements of operational modules are sufficiently established.

Instead:

1. business modules continue owning their domain records;
2. Journal References provide stable historical identities;
3. Journal Entries reference those identities through real foreign keys;
4. a wider Resource platform may be introduced later through a separate architecture decision if repeated requirements justify it.

This preserves flexibility without sacrificing Journal referential integrity.

---

# Actor relationship

## `actor_reference_id`

Identifies who or what caused the occurrence.

Foreign key:

```text
journal_entries.actor_reference_id
    → journal_references.id
```

Nullable:

```text
no
```

Every completed Journal Entry must identify an actor.

System-generated entries use a stable system Journal Reference rather than a null actor.

Examples include:

```text
Response Connect
Nightly Scheduler
Moodle Integration
External Dispatch API
Alex Smith
```

Deletion behaviour:

```text
RESTRICT
```

Journal References used as actors must not be physically deleted.

---

# Subject relationship

## `subject_reference_id`

Identifies the primary record affected by the occurrence.

Foreign key:

```text
journal_entries.subject_reference_id
    → journal_references.id
```

Nullable:

```text
yes
```

Most business-domain entries should identify one primary subject.

Examples:

```text
Vehicle A12
Staff Member Alex Smith
Patient Journey PT-2026-0017
File 72f...
Desk Devon Patient Transport
```

Secondary related records must not be packed into the subject relationship.

They may be represented through:

* context;
* structured metadata;
* future additional Journal relationship support.

Deletion behaviour:

```text
RESTRICT
```

---

# Context relationship

## `context_reference_id`

Identifies the wider workflow or record containing the occurrence.

Foreign key:

```text
journal_entries.context_reference_id
    → journal_references.id
```

Nullable:

```text
yes
```

Example:

```text
Actor: Dispatcher Alex Smith
Subject: Vehicle A12
Context: Incident INC-2026-0042
Event code: vehicle.arrived_on_scene
```

Other examples include:

```text
Subject: Staff Member Alex Smith
Context: Shift SHIFT-2026-0831
Event code: staff.shift_signed_in
```

```text
Subject: File 72f...
Context: Policy POL-2026-017
Event code: file.downloaded
```

Subject and context may reference the same Journal Reference only when that accurately represents the occurrence.

Deletion behaviour:

```text
RESTRICT
```

---

# Reference integrity

Journal Entries do not store raw combinations such as:

```text
subject_type + subject_id
context_type + context_id
actor_type + actor_id
```

Instead, they use foreign keys to `journal_references`.

Benefits include:

* database-enforced integrity for Journal Entry relationships;
* one stable identity for repeated references;
* efficient Activity Stream queries by Journal Reference ID;
* readable history after business records are renamed or archived;
* support for system and external identities;
* Journal independence from business-domain models;
* a future path for record merges;
* simpler indexes;
* consistent actor, subject, and context handling.

The authoritative relationship represented by:

```text
reference_type
source_id
stable_key
```

is validated by the registering business service rather than through cross-module foreign keys.

---

# Desk reference

Desk is treated differently from general business references because it is a fundamental platform capability and operational scope.

Fields:

```text
desk_id
desk_display_name
```

## `desk_id`

Type:

```text
UUID
```

Foreign key:

```text
desks.id
```

Nullable:

```text
yes
```

Deletion behaviour:

```text
RESTRICT
```

A Desk referenced by Journal Entries must not be physically deleted.

Archived Desks remain valid historical references.

## `desk_display_name`

Type:

```text
string
```

Suggested maximum length:

```text
200
```

Nullable:

```text
yes
```

This stores the historical Desk display name used when the occurrence was recorded.

The snapshot remains unchanged if the Desk is later renamed.

## Desk requirement

The database permits `desk_id` to be null.

Business services may require a Desk for specific workflows.

Typically Desk-scoped occurrences include:

```text
vehicle.dispatched
vehicle.arrived_on_scene
staff.shift_signed_in
incident.created
patient_transport.started
operational.note_added
desk.moved
```

Potentially organisation-wide occurrences include:

```text
authentication.login_failed
reference_data.synchronised
permission.changed
organisation.settings_updated
background_job.failed
```

---

# Classification model

A Journal Entry may have multiple classifications.

Initial classifications include:

```text
operational
audit
security
system
```

Optional domain classifications may include:

```text
workforce
fleet
clinical
training
governance
patient_transport
event_medical
```

Classifications must not be stored as individual Boolean columns.

Avoid:

```text
is_operational
is_audit
is_security
is_system
is_fleet
is_workforce
```

This would require repeated schema migrations and create inconsistent filtering behaviour.

Use an association table.

Table name:

```text
journal_entry_classifications
```

Fields:

```text
journal_entry_id
classification_code
```

Primary key:

```text
journal_entry_id + classification_code
```

Rules:

* no duplicate classification per entry;
* codes use lowercase snake_case;
* at least one classification is required;
* classification codes are validated before persistence;
* unknown codes are rejected unless explicitly supported;
* classification relationships are immutable after creation.

Classification definitions are supplied through:

```text
app/journal/reference_data.py
```

---

# Source

## `source`

Describes how the occurrence entered Response Connect.

Initial values:

```text
web
api
worker
scheduler
integration
system
import
```

Type:

```text
string
```

Required:

```text
yes
```

Source definitions are supplied through Journal Reference Data.

The source code is stored directly on the Journal Entry as a stable snapshot.

This avoids requiring a join for ordinary timeline queries.

---

# Severity

## `severity`

Represents operational importance.

Initial values:

```text
information
warning
critical
```

Type:

```text
string
```

Required:

```text
yes
```

Default:

```text
information
```

Severity is not the same as a Python or container logging level.

An operationally critical Journal Entry may not represent a technical platform error.

---

# Visibility

## `visibility`

Represents the broad disclosure category of a Journal Entry.

Initial values:

```text
standard
restricted
confidential
security
clinical
```

Type:

```text
string
```

Required:

```text
yes
```

Default:

```text
standard
```

Visibility does not itself grant access.

The Journal query layer must combine:

* permission codes;
* Desk scope;
* Journal visibility;
* subject access;
* context access;
* module-specific rules.

---

# Summary

## `summary`

A concise human-readable description suitable for Activity Streams and logs.

Type:

```text
string
```

Maximum length:

```text
500
```

Required:

```text
yes
```

Example:

```text
Vehicle A12 arrived on scene.
```

Rules:

1. concise;
2. suitable for timeline display;
3. no secrets;
4. no complete clinical narratives;
5. no raw exception traces;
6. no unnecessary personal information;
7. no assumption that embedded markup is trusted.

The summary is an immutable historical snapshot.

---

# Details

## `details`

Optional additional human-readable context.

Type:

```text
text
```

Nullable:

```text
yes
```

Suggested service-level maximum:

```text
10,000 characters
```

Examples of acceptable details include:

* a short operational note;
* reason for a Desk transfer;
* brief clarification;
* authorised failure outcome;
* concise lifecycle reason.

Examples of unsuitable details include:

* complete patient reports;
* entire policy documents;
* raw stack traces;
* authentication tokens;
* complete staff records;
* complete request payloads.

Details must not become a duplicate domain record.

---

# Structured metadata

## `metadata`

Database type:

```text
JSONB
```

Database column name:

```text
metadata
```

Suggested SQLAlchemy attribute name:

```python
metadata_json
```

`metadata` has special meaning within SQLAlchemy declarative models, so the Python attribute should avoid that name.

Default:

```json
{}
```

Required:

```text
yes
```

Metadata supports occurrence-specific structured values.

Example:

```json
{
  "from_status": "mobile",
  "to_status": "on_scene",
  "incident_number": "INC-2026-0042"
}
```

Rules:

1. JSON serialisable;
2. dictionary/object at the top level;
3. documented keys;
4. no secrets;
5. no full database-row snapshots;
6. no arbitrary ORM serialisation;
7. no binary content;
8. bounded size;
9. validated before persistence;
10. limited to values relevant to the occurrence.

A future event-code metadata schema registry may validate metadata keys.

That capability is deferred.

---

# Correlation

## `correlation_id`

Type:

```text
UUID
```

Nullable:

```text
yes
```

Correlation groups Journal Entries belonging to one broader workflow.

Examples include:

* one incident workflow;
* one file-processing workflow;
* one password-reset workflow;
* one notification delivery chain;
* one reference-data synchronisation run;
* one lifecycle transition and its resulting notifications.

Correlation IDs do not require a foreign key.

They are identifiers shared across related entries.

---

# Causation

## `causation_id`

Type:

```text
UUID
```

Foreign key:

```text
journal_entries.id
```

Nullable:

```text
yes
```

Causation identifies the immediate Journal Entry that caused another entry.

Example:

```text
vehicle.declared_unavailable
        ↓
notification.queued
        ↓
notification.sent
```

Rules:

1. an entry cannot cause itself;
2. the causation reference must identify an existing Journal Entry;
3. causation does not replace correlation;
4. causation cycles must not be introduced;
5. cross-workflow causation should be avoided;
6. deletion behaviour is restrictive.

The initial implementation may enforce only direct self-reference prevention.

Deep causation-cycle validation may be added later.

---

# Immutability

Journal Entries are append-only.

Normal application code must not:

* update Journal Entries;
* delete Journal Entries;
* change classifications;
* replace metadata;
* change timestamps;
* change actor, subject, or context relationships;
* change Desk context;
* change display snapshots.

Corrections create new Journal Entries.

The initial protection is architectural:

* no public update service;
* no public delete service;
* no edit routes;
* no administrative mutation interface;
* business modules use only the public recording API.

Future database protections may include:

* restricted database roles;
* update/delete rejection triggers;
* retention and legal-hold controls.

These are deferred until the core implementation is stable.

---

# Journal Reference lifecycle

Journal References are historical identities and must not normally be physically deleted.

A Journal Reference may remain after its authoritative business record is:

* archived;
* deactivated;
* deleted;
* merged;
* inaccessible to ordinary users.

The Journal Reference continues supporting historical Journal Entries.

A future Journal Reference merge mechanism may support cases where two business identities are merged.

Such a mechanism must not silently rewrite historical Journal Entries.

Possible future behaviour includes:

* retaining both Journal References;
* recording the merge relationship;
* redirecting future registration to the surviving reference;
* presenting combined Activity Streams where authorised.

This capability is deferred.

---

# Correction entries

A correction is a new Journal Entry.

Example event code:

```text
journal.entry_corrected
```

Metadata may contain:

```json
{
  "corrected_entry_id": "uuid",
  "reason": "Incorrect arrival time supplied"
}
```

The original Journal Entry remains unchanged.

The correction may use:

```text
causation_id = original entry ID
```

where appropriate.

Corrections must remain subject to normal permissions and visibility rules.

---

# Database relationships

## Desk relationship

```text
JournalEntry.desk_id
    → Desk.id
```

Deletion behaviour:

```text
RESTRICT
```

## Actor relationship

```text
JournalEntry.actor_reference_id
    → JournalReference.id
```

Deletion behaviour:

```text
RESTRICT
```

## Subject relationship

```text
JournalEntry.subject_reference_id
    → JournalReference.id
```

Deletion behaviour:

```text
RESTRICT
```

## Context relationship

```text
JournalEntry.context_reference_id
    → JournalReference.id
```

Deletion behaviour:

```text
RESTRICT
```

## Causation relationship

```text
JournalEntry.causation_id
    → JournalEntry.id
```

Deletion behaviour:

```text
RESTRICT
```

## Classification relationship

```text
JournalEntry
    1
    ↓
    many
JournalEntryClassification
```

Classification association rows belong to the Journal Entry.

They must not be changed after the entry has been recorded.

---

# Suggested SQLAlchemy model structure

```python
class JournalReference(db.Model):
    __tablename__ = "journal_references"

    id

    reference_type
    source_id
    stable_key

    display_name

    created_at
```

```python
class JournalEntry(db.Model):
    __tablename__ = "journal_entries"

    id

    event_code

    occurred_at
    recorded_at

    actor_reference_id
    subject_reference_id
    context_reference_id

    desk_id
    desk_display_name

    source
    severity
    visibility

    summary
    details

    correlation_id
    causation_id

    metadata_json

    created_at
```

```python
class JournalEntryClassification(db.Model):
    __tablename__ = "journal_entry_classifications"

    journal_entry_id
    classification_code
```

---

# Indexes

The Event Journal will grow continuously.

The initial completed schema should include indexes for common query paths.

## Journal Entry indexes

Required:

```text
recorded_at
occurred_at
event_code
desk_id
actor_reference_id
subject_reference_id
context_reference_id
correlation_id
causation_id
```

Recommended composite indexes:

```text
desk_id + occurred_at
actor_reference_id + occurred_at
subject_reference_id + occurred_at
context_reference_id + occurred_at
event_code + occurred_at
```

These support:

* Desk timelines;
* actor activity;
* subject Activity Streams;
* context timelines;
* event-code reporting;
* newest-first display.

## Journal Reference indexes

Required:

```text
reference_type
source_id
stable_key
```

Conditional unique indexes:

```text
reference_type + source_id
WHERE source_id IS NOT NULL
```

```text
reference_type + stable_key
WHERE stable_key IS NOT NULL
```

## Classification indexes

Required:

```text
classification_code
journal_entry_id
```

The composite primary key already supports lookup by Journal Entry.

An additional index on `classification_code` supports classification-filtered views.

---

# Constraints

## Journal Reference constraints

At least one identity field must be present:

```text
source_id IS NOT NULL
OR stable_key IS NOT NULL
```

Stable keys must be lowercase:

```text
stable_key IS NULL
OR stable_key = lower(stable_key)
```

Reference types must not be empty:

```text
char_length(reference_type) > 0
```

Display names must not be empty:

```text
char_length(display_name) > 0
```

## Journal Entry constraints

Event code must not be empty:

```text
char_length(event_code) > 0
```

Event code must be lowercase:

```text
event_code = lower(event_code)
```

Summary must not be empty:

```text
char_length(summary) > 0
```

Actor is required:

```text
actor_reference_id IS NOT NULL
```

Subject may be null.

Context may be null.

Desk may be null.

Causation must not reference the same entry:

```text
causation_id IS NULL
OR causation_id <> id
```

## Classification constraints

No duplicate classification may exist for one Journal Entry.

At least one classification must be supplied by the recording service.

The database may not be able to enforce the presence of at least one association row without triggers, so service-level validation is required.

---

# Historical snapshots

Historical snapshots include:

```text
JournalReference.display_name
JournalEntry.desk_display_name
JournalEntry.summary
JournalEntry.details
```

Rules:

1. snapshots are plain text;
2. snapshots are minimal;
3. snapshots are immutable;
4. snapshots are not automatically refreshed;
5. snapshots remain after source records are renamed;
6. snapshots must minimise personal information.

The authoritative current display name remains in the owning domain record.

---

# Recording command

The completed immutable recording command should be:

```python
RecordJournalEntryCommand
```

Expected fields:

```text
event_code
occurred_at

actor_reference_id
subject_reference_id
context_reference_id

desk_id

classifications

source
severity
visibility

summary
details

correlation_id
causation_id

metadata
```

The service should resolve historical display snapshots from supplied Journal References and Desk data where appropriate.

Defaults must be deliberate and documented.

Routes must not provide hidden defaults that differ from other callers.

---

# Journal Reference command

The Journal Reference service should accept an immutable command or explicit keyword arguments containing:

```text
reference_type
source_id
stable_key
display_name
```

At least one of `source_id` or `stable_key` is required.

Registration must be idempotent.

Repeated registration of the same stable identity returns the existing Journal Reference.

The service must not silently overwrite the historical display name of an existing reference.

A future explicit rename or alias mechanism may be introduced separately.

---

# Recording service

The Journal recording service should expose:

```python
JournalEntryService.record(command)
```

Responsibilities:

1. validate the command;
2. validate the event code;
3. validate the occurrence timestamp;
4. validate summary and details;
5. validate classifications;
6. validate source;
7. validate severity;
8. validate visibility;
9. validate actor reference;
10. validate optional subject reference;
11. validate optional context reference;
12. validate optional Desk reference;
13. validate optional causation reference;
14. validate metadata;
15. create the Journal Entry;
16. create classification associations;
17. flush or commit according to transaction ownership;
18. translate persistence failures;
19. return the created Journal Entry.

No public update or delete methods should exist.

---

# Journal Reference service

The Journal Reference service should expose:

```python
JournalReferenceService.get_or_create(...)
```

Responsibilities:

1. validate the reference type;
2. validate `source_id`;
3. validate `stable_key`;
4. require at least one stable identity;
5. validate the display name;
6. return an existing reference for the same identity;
7. create a reference when none exists;
8. handle concurrent creation safely;
9. translate persistence failures;
10. preserve idempotent behaviour.

Read methods may include:

```python
get(reference_id)
find_by_source(reference_type, source_id)
find_by_stable_key(reference_type, stable_key)
```

---

# Transaction ownership

Journal recording must support two transaction patterns.

## Commit-owning recording

Suitable for standalone Journal activity:

```python
entry = journal_service.record(command)
```

The service commits or rolls back.

## Caller-owned unit of work

Required when a domain change and Journal Entry must commit together.

Example:

```text
Desk moved
+
desk.moved Journal Entry
=
one database transaction
```

The final API may provide:

```python
journal_service.record(
    command,
    commit=False,
)
```

or a separate method such as:

```python
journal_service.prepare(command)
```

The chosen API must make transaction ownership explicit.

Routes must not manually reconstruct Journal persistence behaviour.

---

# Query model

The Journal query service should eventually support:

```python
get(entry_id)

list_for_reference(reference_id)

list_for_actor(actor_reference_id)

list_for_subject(subject_reference_id)

list_for_context(context_reference_id)

list_for_desk(
    desk_id,
    include_descendants=False,
)

list_for_correlation(correlation_id)

list_operational(...)
list_audit(...)
list_security(...)
```

All list methods must support:

* pagination;
* deterministic ordering;
* date ranges;
* event-code filtering;
* classification filtering;
* severity filtering;
* visibility enforcement;
* authorised metadata disclosure.

Desk descendant expansion belongs to the Desk Platform.

The Journal query service may call the public Desk API to resolve permitted Desk IDs.

---

# Activity Streams

An Activity Stream is a filtered projection of Journal Entries.

## Reference Activity Stream

A Journal Reference Activity Stream may include entries where the reference appears as:

* actor;
* subject;
* context.

The caller should be able to select which roles are included.

## Subject Activity Stream

Shows occurrences affecting one business record.

Examples:

* Vehicle history;
* Staff Member history;
* File history;
* Shift history.

## Context Activity Stream

Shows occurrences belonging to a wider workflow.

Examples:

* Incident timeline;
* Patient Journey timeline;
* organised event timeline;
* policy lifecycle.

## Actor Activity Stream

Shows actions performed by a person, account, integration, scheduler, or system actor.

Actor streams are primarily audit and administrative views.

## Desk Activity Stream

Shows Journal Entries associated with a Desk and optionally its descendants.

---

# Desk dependency

The Journal depends on the Desk Platform only through:

```text
desk_id foreign key
Desk public query API
```

The Journal package must not contain Desk hierarchy logic.

Desk descendant expansion belongs to:

```text
DeskQueryService
```

The Journal may call the public Desk package API when resolving Desk scopes.

---

# Package dependencies

The intended dependency direction is:

```text
Business modules
        ↓
Journal public API
        ↓
Journal models and services
```

The Journal package must not import:

* Event Medical models;
* Patient Transport models;
* Fleet models;
* Workforce models;
* Clinical models;
* route blueprints;
* templates.

Business modules supply stable identities through the Journal Reference API.

Desk is the only initial direct platform-domain foreign key because it defines system-wide operational scope.

---

# Source-of-truth rules

Domain tables remain authoritative for:

* current state;
* current display name;
* current ownership;
* current operational assignment;
* current relationships;
* active lifecycle.

Journal References remain authoritative for:

* stable Journal identity;
* historical display identity;
* Activity Stream identity.

Journal Entries remain authoritative for:

* historical occurrences;
* recorded actor;
* historical subject and context relationships;
* historical Desk context;
* operational timelines;
* audit history;
* security history;
* correlation;
* causation.

---

# Sensitive data

The Event Journal must not become a duplicate clinical, HR, workforce, or patient database.

Avoid storing:

* complete clinical narratives;
* complete patient demographics;
* passwords;
* tokens;
* secret keys;
* complete documents;
* full staff records;
* unnecessary addresses;
* unnecessary contact details;
* raw request bodies;
* raw exception traces.

Store:

* stable references;
* minimal display snapshots;
* concise summaries;
* limited structured metadata.

Detailed information remains in the owning domain module and is accessed under that module’s permissions.

---

# Retention

The initial implementation must not delete Journal Entries or Journal References.

Future retention work may include:

* archival;
* legal hold;
* classification-based retention;
* security-event retention;
* clinical-event retention;
* partitioning;
* redaction;
* protected deletion workflows.

These require separate architecture decisions.

Retention must not be implemented casually through ordinary CRUD operations.

---

# Partitioning

Do not partition the initial Journal tables.

Partitioning introduces migration, deployment, and operational complexity.

The initial implementation should use:

* appropriate indexes;
* bounded queries;
* pagination;
* measured performance data.

Partitioning may be introduced when production volume demonstrates a need.

---

# Attachments

Journal Entries must not directly store binary attachments.

Future attachments should use the Files platform through a linking table.

Possible future table:

```text
journal_entry_files
```

Fields:

```text
journal_entry_id
file_object_id
relationship_code
```

This is deferred from the initial implementation.

---

# Reference Data

The Journal package defines stable vocabulary through:

```text
app/journal/reference_data.py
```

Initial datasets include:

```text
journal.classifications
journal.sources
journal.severities
journal.visibilities
```

These datasets define stable codes and display information.

The values may later be synchronised into suitable catalogue models where required.

Event codes and Journal Reference types remain code-owned contracts and are not ordinary configurable Reference Data.

---

# Exceptions

Suggested Journal exceptions include:

```text
JournalError
InvalidJournalEntryError
JournalEntryNotFoundError
JournalEntryVisibilityError
JournalEntryConflictError
JournalPersistenceError

InvalidJournalReferenceError
JournalReferenceNotFoundError
JournalReferenceConflictError
JournalReferencePersistenceError
```

Mappings:

| Exception                          | Platform category       |
| ---------------------------------- | ----------------------- |
| `InvalidJournalEntryError`         | `ValidationError`       |
| `JournalEntryNotFoundError`        | `NotFoundError`         |
| `JournalEntryVisibilityError`      | `PermissionDeniedError` |
| `JournalEntryConflictError`        | `ConflictError`         |
| `JournalPersistenceError`          | `PersistenceError`      |
| `InvalidJournalReferenceError`     | `ValidationError`       |
| `JournalReferenceNotFoundError`    | `NotFoundError`         |
| `JournalReferenceConflictError`    | `ConflictError`         |
| `JournalReferencePersistenceError` | `PersistenceError`      |

Raw SQLAlchemy exceptions must not escape public service boundaries.

---

# Testing requirements

## Journal Reference model tests

Test:

* UUID identity;
* required display name;
* required reference type;
* source-ID registration;
* stable-key registration;
* requirement for at least one identity;
* source uniqueness;
* stable-key uniqueness;
* lowercase stable-key constraint;
* timestamps;
* indexes and constraints.

## Journal Reference validator tests

Test:

* valid reference types;
* invalid reference types;
* valid stable keys;
* invalid stable keys;
* required identity;
* display-name validation;
* length limits.

## Journal Reference service tests

Test:

* successful local reference creation;
* successful system reference creation;
* idempotent source-ID registration;
* idempotent stable-key registration;
* concurrent conflict handling;
* invalid command handling;
* persistence rollback;
* domain-specific exception translation.

## Journal Entry model tests

Test:

* UUID identity;
* required fields;
* event-code length;
* timestamp storage;
* actor foreign key;
* optional subject foreign key;
* optional context foreign key;
* nullable Desk;
* Desk foreign key;
* JSONB metadata;
* correlation;
* causation self-reference constraint;
* classification uniqueness;
* indexes and constraints.

## Command tests

Test:

* immutability;
* defaults;
* classification handling;
* metadata copying;
* nullable relationships;
* timezone handling.

## Validator tests

Test:

* valid event codes;
* invalid event codes;
* valid timestamps;
* naive timestamps;
* valid classifications;
* unknown classifications;
* valid sources;
* valid severity;
* valid visibility;
* metadata object requirement;
* empty summaries;
* maximum lengths.

## Recording service tests

Test:

* successful recording;
* actor validation;
* subject recording;
* context recording;
* Desk-scoped recording;
* organisation-wide recording;
* multiple classifications;
* causation;
* correlation;
* invalid command translation;
* missing reference;
* missing Desk;
* missing causation entry;
* persistence rollback;
* caller-owned transaction participation.

## Query tests

Test:

* actor Activity Stream;
* subject Activity Stream;
* context Activity Stream;
* Desk timeline;
* descendant Desk scope;
* correlation timeline;
* pagination;
* deterministic ordering;
* date filtering;
* classification filtering;
* visibility enforcement.

## Architecture tests

Test:

* Journal exceptions use the shared platform hierarchy;
* Journal services do not import routes;
* Journal models do not import business modules;
* event codes use stable format;
* reference types use stable format;
* business modules use the public Journal API;
* no independent audit-log table is introduced;
* Journal models do not expose update or delete services;
* Journal package exports are explicit.

---

# Initial migration sequence

The Journal is implemented incrementally.

## Migration 1 — Initial Journal Entry

Creates:

```text
journal_entries
```

Initial fields:

```text
id
event_code
occurred_at
recorded_at
summary
details
created_at
```

## Migration 2 — Journal References

Creates:

```text
journal_references
```

Including:

* source-ID uniqueness;
* stable-key uniqueness;
* identity constraints;
* indexes.

## Migration 3 — Entry relationships

Adds:

```text
actor_reference_id
subject_reference_id
context_reference_id
desk_id
desk_display_name
```

## Migration 4 — Classification and vocabulary

Adds:

```text
source
severity
visibility
journal_entry_classifications
```

## Migration 5 — Workflow relationships

Adds:

```text
correlation_id
causation_id
metadata
```

Incremental migrations make each slice easier to test and review.

---

# Implementation sequence

1. Complete the initial Journal Entry recording service.
2. Add Journal Reference exceptions.
3. Add Journal Reference commands.
4. Add Journal Reference validators.
5. Implement the `JournalReference` model.
6. Create the Journal Reference migration.
7. Add Journal Reference model tests.
8. Implement `JournalReferenceService`.
9. Add Journal Reference service tests.
10. Export the Journal Reference public API.
11. Add Journal Reference architecture tests.
12. Add actor, subject, and context foreign keys to `JournalEntry`.
13. Add the optional Desk foreign key and Desk snapshot.
14. Extend `RecordJournalEntryCommand`.
15. Extend `JournalEntryService`.
16. Add classification relationships.
17. Add source, severity, and visibility.
18. Add correlation and causation.
19. Add structured metadata.
20. Implement Journal queries.
21. Add Activity Streams.
22. Add Operational, Audit, and Security projections.
23. Integrate domain services with the Journal.
24. Add the web interface only after the backend platform reaches the same quality standard as the Desk Platform.

---

# Non-goals

The initial Event Journal will not provide:

* full event sourcing;
* domain-state reconstruction through event replay;
* a universal Resource database model;
* Kafka or similar distributed brokers;
* cross-installation Journal federation;
* blockchain or cryptographic verification;
* administrator-created event codes;
* unrestricted metadata;
* persistent records for every diagnostic log line;
* editable Journal Entries;
* physical deletion through normal workflows;
* automatic Journal Reference display-name updates;
* direct foreign keys from Journal References to every business table.

---

# Design decisions

This chapter establishes the following architectural decisions.

1. The Event Journal is a single system-wide history platform.
2. The persistent occurrence record is named `JournalEntry`.
3. The implementation package is `app/journal/`.
4. Journal Entries are immutable and append-only.
5. Domain tables remain authoritative for current state.
6. Actor, subject, and context use stable `JournalReference` records.
7. Journal Entries use real foreign keys to Journal References.
8. Journal References identify local records through `reference_type` and `source_id`.
9. Journal References identify system or external records through `stable_key`.
10. Journal Reference registration is idempotent.
11. Business modules register their records through the public Journal API.
12. Business modules must not create Journal models directly.
13. The Journal package does not import business-domain models.
14. Desk remains a direct nullable foreign key because it is a core platform dependency and operational scope.
15. Desk display names are stored as historical snapshots.
16. A universal Resource model is deferred until broader operational requirements justify it.
17. Classifications use an association table rather than Boolean columns.
18. Journal metadata uses PostgreSQL JSONB.
19. PostgreSQL enum types are not used initially.
20. The initial Journal tables are not partitioned.
21. Journal Entries and Journal References are not physically deleted through ordinary workflows.
22. Corrections are recorded as new Journal Entries.
23. Event codes are stable code-owned contracts.
24. Reference types are stable code-owned contracts.
25. Journal Reference Data defines classifications, sources, severities, and visibility values.
26. Journal Entry relationships use restrictive deletion behaviour.
27. The Journal must support both commit-owning and caller-owned transaction workflows.
28. Activity Streams, Operational Logs, Audit Logs, and Security Logs are projections of the same stored Journal Entries.

---

# Decision summary

Response Connect will maintain one system-wide immutable Event Journal.

Each significant occurrence is stored as one `JournalEntry`.

Actors, subjects, and contexts are represented by stable Journal-owned `JournalReference` records.

Journal Entries use real foreign keys to those references, providing relational integrity without coupling the Journal package to every business-domain model.

Business modules remain authoritative for their own records and register stable historical identities through the public Journal API.

Desk remains a direct optional foreign key because it defines operational scope across the platform.

Domain tables store current state.

Journal Entries store historical occurrences.

Activity Streams, Operational Logs, Audit Logs, and Security Logs are authorised projections of that shared history.
