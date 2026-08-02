# Event Journal and Operational Model

## Purpose

This chapter defines how Response Connect represents operational activity, audit history, security activity, lifecycle transitions and system-generated events.

It establishes the architectural relationship between:

* the Event Journal;
* Desks;
* lifecycle transitions;
* the Operational Log;
* the Audit Log;
* security events;
* activity streams;
* notifications;
* background jobs;
* reporting.

This chapter is the architectural foundation for the operational platform.

Future modules must use these shared capabilities rather than introduce independent activity, audit or history tables without a specific Architecture Decision Record.

---

## Terminology and naming

Response Connect uses **Event Journal** as the name of the shared history platform.

An individual persistent record within the Event Journal is called a **Journal Entry**.

The term **Event Medical** refers to medical provision at organised public or private events. The shorter term **Event** may be used for a specific organised event where the Event Medical context is clear.

The implementation uses the `app/journal/` package and `JournalEntry` model names to avoid ambiguity between Event Journal records and Event Medical operations.

Stable event codes such as `vehicle.arrived_on_scene` describe the occurrence being recorded. They do not imply that the persistent model itself is named `Event`.

# Guiding principle

> Record each significant occurrence once, then present it through the views that need it.

Response Connect will maintain one persistent Event Journal containing immutable records of significant activity.

Operational Logs, Audit Logs, security views, record timelines and activity streams will be projections of that journal.

The Event Journal will not replace domain models.

Domain tables remain authoritative for current state.

The journal explains:

* what happened;
* when it happened;
* who or what caused it;
* which record was affected;
* where the work belonged;
* how it relates to other events.

---

# Design goals

The Event Journal and operational model should:

1. provide one consistent history platform;
2. prevent duplicate audit and operational logging systems;
3. preserve immutable business history;
4. support human-readable operational timelines;
5. support detailed administrative investigation;
6. support Desk-scoped operational views;
7. support record-specific activity streams;
8. support correlation across services and background jobs;
9. minimise sensitive-data duplication;
10. remain practical for a self-hosted PostgreSQL application;
11. integrate with lifecycle, notifications and reporting;
12. avoid the complexity of full event sourcing.

---

# Core concepts

## Event

An Event Journal entry records that something significant happened.

Examples include:

```text
incident.created
incident.status_changed
vehicle.assigned
vehicle.arrived_on_scene
staff.shift_signed_in
staff.shift_signed_out
clinical_grade.assigned
file.downloaded
permission.changed
authentication.login_failed
notification.delivery_failed
reference_data.synchronised
```

An event is a historical fact.

It must not be treated as an editable note or mutable status record.

## Actor

The actor is the person, account, service or system component responsible for the occurrence.

An actor may be:

* a User Account;
* a staff member;
* an automated system process;
* a Celery task;
* a scheduled job;
* an external integration;
* an API client;
* the Response Connect system itself.

The actor is distinct from the subject.

Example:

```text
Actor: Dispatcher Alex Smith
Subject: Vehicle A12
Event: vehicle.assigned
```

## Subject

The subject is the primary record or entity affected by the event.

Examples include:

* a Person;
* a User Account;
* a Staff Member;
* a Vehicle;
* an Incident;
* a Patient Journey;
* a Shift;
* a File;
* a Clinical Grade Assignment;
* a controlled document.

An event should normally have one primary subject.

Other related entities may be recorded through context or structured metadata.

## Context

The context is the wider record or workflow within which the event occurred.

Examples include:

```text
Subject: Vehicle A12
Context: Incident INC-2026-0042
Event: vehicle.arrived_on_scene
```

```text
Subject: Staff Member Alex Smith
Context: Shift SHIFT-2026-0831
Event: staff.shift_signed_in
```

```text
Subject: File 72f...
Context: Policy POL-2026-017
Event: file.downloaded
```

Context allows the same journal entry to appear in several relevant timelines without duplication.

## Desk

A Desk is the operational workspace or control boundary responsible for the work.

Examples include:

```text
Company Operations
Devon Patient Transport
Glastonbury Festival 2026
Fleet Control
Major Incident Control
```

Operational events should normally reference a Desk.

Administrative, security or system events may reference a Desk where it is relevant, but Desk membership is not mandatory for every event.

## Correlation

A correlation identifier groups events belonging to one broader workflow.

Example:

```text
staff.shift_signed_in
compliance.check_completed
vehicle.crew_assignment_confirmed
notification.sent
```

These events may all share one correlation ID.

Correlation supports:

* workflow investigation;
* tracing;
* debugging;
* asynchronous processing;
* API integrations;
* reporting.

## Causation

A causation identifier records which earlier event directly caused a later event.

Example:

```text
staff.shift_signed_in
        ↓
compliance.check_completed
        ↓
notification.sent
```

Each later event may identify the event that caused it.

Correlation groups a workflow.

Causation records the direct chain within that workflow.

---

# Architectural decision: one Event Journal

Response Connect will use one persistent Event Journal rather than separate storage systems for:

* operational activity;
* audit records;
* security events;
* system-processing events;
* record timelines.

One event may be relevant to several views.

Example:

```text
staff.shift_signed_in
```

may be:

* operationally relevant;
* audit relevant;
* workforce relevant;
* visible on the Shift timeline;
* visible on the Staff Member timeline;
* visible on the Desk timeline.

The event should be stored once.

Its classifications and relationships determine where it appears.

---

# Event classifications

Events may belong to one or more classifications.

The initial shared classifications are:

```text
operational
audit
security
system
```

Business-domain classifications may also be introduced where useful, for example:

```text
workforce
clinical
fleet
training
governance
patient_transport
incident
```

These additional classifications must remain stable codes.

They should support filtering and presentation rather than replace module ownership.

## Operational events

Operational events describe real-world or workflow activity.

Examples include:

```text
incident.created
vehicle.dispatched
vehicle.arrived_on_scene
staff.shift_signed_in
patient_transport.started
desk.opened
work.transferred_between_desks
operational.note_added
```

Operational events are the principal source for the Operational Log.

## Audit events

Audit events record actions requiring accountability or historical traceability.

Examples include:

```text
record.created
record.updated
record.deleted
permission.changed
file.downloaded
competency.verified
policy.published
clinical_grade.assigned
```

Audit events may expose structured before-and-after values to appropriately authorised users.

## Security events

Security events record authentication and access activity.

Examples include:

```text
authentication.login_succeeded
authentication.login_failed
access.denied
account.locked
session.revoked
password_reset.requested
password_reset.completed
```

Security events require stricter visibility controls and careful data minimisation.

## System events

System events record significant automated processing.

Examples include:

```text
reference_data.synchronised
file.scan_completed
file.scan_failed
notification.delivery_failed
background_job.failed
integration.import_completed
integration.import_failed
```

System events are persistent business or operational history.

They are distinct from ordinary diagnostic logs.

---

# Domain classifications

Some events may also be classified by business area.

Examples include:

```text
clinical
fleet
workforce
training
governance
patient_transport
event_medical
```

A staff sign-in event could be classified as:

```text
operational
audit
workforce
```

A vehicle defect event could be:

```text
operational
audit
fleet
```

A failed login could be:

```text
security
audit
```

Classifications should not be implemented as a growing collection of Boolean database columns.

The implementation should support extensible stable classification codes.

---

# The Event Journal is not event sourcing

Response Connect will not initially use full event sourcing.

Domain tables remain the authoritative source of current state.

Examples:

* `Vehicle.status` stores the current vehicle status;
* `Incident.status` stores the current incident status;
* `ShiftAttendance` stores current and historical attendance records;
* `ClinicalGradeAssignment` stores grade assignments;
* `Desk.status` stores the current Desk state.

The Event Journal records the events that explain those state changes.

The application will not rebuild its current state by replaying all events.

## Reasons for this decision

Using domain tables for current state provides:

* simpler SQL queries;
* easier reporting;
* conventional migrations;
* simpler integrations;
* clearer transactional behaviour;
* easier contributor onboarding;
* lower operational complexity;
* more practical self-hosting.

The Event Journal still provides strong historical and audit capabilities without requiring full event-sourced architecture.

---

# Event persistence model

The initial Event Journal record should support:

```text
id
event_code

occurred_at
recorded_at

actor_type
actor_id
actor_display_name

subject_type
subject_id
subject_display_name

context_type
context_id
context_display_name

desk_id

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

Classification relationships should be stored separately or through a structured association rather than hard-coded Boolean fields.

## Stable event code

Every event uses a stable machine code.

Format:

```text
domain.action
```

Examples:

```text
vehicle.arrived_on_scene
staff.shift_signed_in
incident.created
file.downloaded
authentication.login_failed
```

Event codes must:

* use lowercase snake_case components;
* remain stable after release;
* describe completed facts;
* avoid editable display text;
* be validated through architecture tests.

## Occurred time

`occurred_at` is when the event happened.

This may be supplied by:

* the current request;
* an operational user;
* a device;
* an integration;
* a retrospective entry.

## Recorded time

`recorded_at` is when Response Connect persisted the event.

Occurred and recorded times may differ because of:

* offline working;
* delayed entry;
* integration delays;
* retrospective reporting;
* queued processing.

Both timestamps must be retained.

## Display snapshots

Actor, subject and context display names may be stored as historical snapshots.

This prevents old timelines becoming unreadable if a record is later renamed or deleted.

Snapshots must contain only the minimum text required for useful history.

The authoritative current name remains in the owning domain table.

## Source

The event source describes how the event entered the platform.

Initial examples include:

```text
web
api
worker
scheduler
integration
system
import
```

Source codes must be stable.

## Severity

Severity supports operational filtering.

Initial values may include:

```text
information
warning
critical
```

Severity is not the same as platform logging level.

An event may be operationally critical without representing a technical application error.

## Visibility

Visibility identifies the broad disclosure level of an event.

Possible initial values include:

```text
standard
restricted
confidential
security
clinical
```

Visibility is not a replacement for permission checks.

The query service must combine:

* event visibility;
* user permissions;
* Desk scope;
* subject access;
* module-specific restrictions.

## Summary

The summary is the short human-readable description used in timelines.

Example:

```text
Vehicle A12 arrived on scene.
```

## Details

Details provide optional additional human-readable context.

Details must not duplicate complete domain records.

## Metadata

Metadata stores structured event-specific values.

Example:

```json
{
  "from_status": "mobile",
  "to_status": "on_scene",
  "incident_number": "INC-2026-0042"
}
```

Metadata must:

* use documented keys;
* avoid secrets;
* avoid complete record snapshots;
* minimise personal information;
* remain JSON serialisable;
* be validated before persistence.

---

# Event immutability

Event Journal records are append-only.

After creation, an event must not be edited or deleted through normal application workflows.

This applies to:

* summaries;
* details;
* timestamps;
* actor information;
* classifications;
* metadata.

## Corrections

If an event is incorrect, the correction is another event.

Example:

```text
operational.note_added
        ↓
operational.note_corrected
```

The correction should reference the original event through metadata, subject context or causation.

The original event remains visible according to permissions.

## Redaction

Rare legal or security requirements may require limited redaction.

Redaction must not silently rewrite history.

A future redaction mechanism should:

* preserve the existence of the original event;
* record who authorised redaction;
* record when redaction occurred;
* create an audit event;
* retain protected data only where legally appropriate.

This capability is deferred.

---

# Operational Log

The Operational Log is a user-facing projection of the Event Journal.

It is not a separate table.

It consists primarily of events classified as:

```text
operational
```

The Operational Log should support:

* company-wide activity;
* Desk-specific activity;
* parent Desk activity including descendants;
* event and incident timelines;
* shift logs;
* vehicle activity;
* Patient Transport activity;
* manually entered notes;
* filtering;
* severity;
* record links;
* authorised attachments.

Operational views should prioritise concise human-readable summaries.

Technical implementation details should remain hidden.

---

# Audit Log

The Audit Log is an administrative projection of the same Event Journal.

It is not a second event store.

Audit views may expose:

* actor identity;
* source;
* subject and context identifiers;
* before-and-after values;
* changed fields;
* correlation and causation;
* request or task context;
* outcome;
* security classifications.

Audit access must be permission-controlled.

The Audit Log must not expose:

* passwords;
* tokens;
* secret configuration;
* complete clinical records;
* unnecessary personal information;
* raw infrastructure exception details.

---

# Security Log

The Security Log is a restricted projection of security-classified events.

It may include:

* login successes;
* login failures;
* denied access;
* account lockouts;
* session revocations;
* password-reset activity;
* permission changes;
* suspicious activity.

The Security Log must use strict permissions.

It should avoid confirming the existence of inaccessible accounts or records to unauthorised viewers.

---

# Activity Streams

An Activity Stream is a filtered projection of the Event Journal for a specific subject, context, Desk or audience.

Examples include:

* Staff Member activity;
* Vehicle history;
* Incident timeline;
* Patient Journey timeline;
* Shift timeline;
* Desk activity;
* Policy history;
* Clinical Grade Assignment history;
* File activity;
* User security activity.

Activity Streams allow different interfaces to present the same stored events without creating duplicate history models.

## Subject activity stream

Shows events where the record is the subject.

Example:

```text
Vehicle A12
├── allocated to Devon PTS
├── marked mobile
├── arrived at pickup
├── departed pickup
└── became available
```

## Context activity stream

Shows events belonging to a wider workflow.

Example:

```text
Incident INC-2026-0042
├── created
├── Vehicle A12 assigned
├── Vehicle A12 mobile
├── Vehicle A12 arrived
├── patient treatment started
└── incident closed
```

## Desk activity stream

Shows events recorded directly against a Desk and optionally its descendants.

## Actor activity stream

Shows actions performed by a User Account, staff member, integration or system process.

Actor streams are primarily administrative and audit-oriented.

---

# Desk-centred operational model

Desks are the principal operational context for work.

A Desk answers:

> Where does this work live?

Examples include:

```text
Company Operations
├── Corporate
├── Patient Transport
│   ├── Devon
│   ├── Cornwall
│   └── Somerset
├── Event Medical
│   ├── Glastonbury Festival 2026
│   └── Exeter Christmas Market
├── Ambulance Operations
└── Specialist Functions
    ├── Fleet Control
    └── Clinical Advice
```

A Desk may represent:

* a company-wide operational view;
* a service;
* a region;
* a control function;
* a temporary event;
* a major incident;
* a specialist function.

A Desk is not necessarily a physical location.

---

# Desk responsibilities

A Desk may scope:

* work queues;
* incidents;
* patient journeys;
* shifts;
* resources;
* tasks;
* communications;
* notifications;
* operational dashboards;
* Operational Log entries;
* access permissions.

Operational records should normally identify one primary Desk.

Examples:

| Record              | Primary Desk           |
| ------------------- | ---------------------- |
| Event               | Event Desk             |
| Incident            | CAD or Control Desk    |
| Patient Journey     | Patient Transport Desk |
| Shift               | Operational Desk       |
| Task                | Desk                   |
| Deployment          | Desk                   |
| Operational note    | Desk                   |
| Resource allocation | Desk                   |

---

# Desk hierarchy and event scope

Desks form a tree beneath one company-wide root Desk.

When querying events for a Desk, callers may choose:

```python
include_descendants=True
```

Example:

```text
Patient Transport
├── Devon
├── Cornwall
└── Somerset
```

A company-level or service-level user may view activity across all descendants.

A user scoped to Devon normally sees only Devon and any children beneath it.

Desk scope must be enforced in the query service.

It must not rely only on frontend filtering.

---

# Desk access

Desk access combines:

```text
Permission
+
Desk scope
```

Example:

```text
operations:view
Desk: Devon Patient Transport
Include descendants: true
```

Example:

```text
operations:dispatch
Desk: Glastonbury Festival 2026
Include descendants: false
```

The Event Journal query layer must apply Desk-aware authorisation.

Having a global permission code does not automatically grant access to every Desk.

---

# Lifecycle integration

Lifecycle services govern explicit transitions and time-bound relationships.

Examples include:

* Desk opening and closing;
* Staff Desk Access;
* staff Shift Attendance;
* Vehicle Desk Allocation;
* Clinical Grade Assignment;
* Competency holding;
* document approval;
* incident status;
* Patient Journey status.

Every significant successful lifecycle transition should record an Event Journal entry.

Example:

```text
Vehicle status:
available
    ↓
assigned
    ↓
mobile
    ↓
on_scene
    ↓
available
```

Each completed transition creates an event.

The domain table stores the current state.

The journal stores the transition history.

---

# Transactional event creation

Where possible, domain changes and Event Journal entries must commit in one database transaction.

Example:

```text
Clinical Grade Assignment created
+
clinical_grade.assigned event created
=
one transaction
```

This prevents:

* state changing without history;
* history being recorded for a failed state change.

The owning business service controls the transaction.

## Expected flow

```text
Validate command
        ↓
Load domain records
        ↓
Check permissions and Desk scope
        ↓
Apply lifecycle rules
        ↓
Prepare domain changes
        ↓
Prepare Event Journal entry
        ↓
Commit once
```

## Failed transactions

If the transaction fails:

* the domain change must roll back;
* the journal event must roll back;
* no persistent event should remain;
* the technical failure should be handled through platform exceptions and logging.

---

# External systems and transactions

PostgreSQL transactions cannot include:

* object storage;
* email providers;
* Redis;
* Celery;
* external APIs;
* telephony;
* radio systems.

Workflows involving external systems require explicit sequencing, retry and compensation.

Example:

```text
Domain transaction commits
        ↓
Event recorded
        ↓
Outbox or task scheduled
        ↓
External action attempted
        ↓
Outcome event recorded
```

Response Connect should not claim atomicity across external services.

A transactional outbox pattern may be introduced when notification and integration requirements justify it.

---

# Notifications

Notifications should be event-driven.

Business services should record the significant event.

Notification rules or handlers then decide whether a notification is required.

Example:

```text
vehicle.declared_unavailable
        ↓
Event Journal
        ↓
Notification rule
        ↓
Fleet Manager notified
```

This avoids hard-coding notification delivery throughout business services.

## Notification relationship

A notification may reference:

* the source event;
* the recipient;
* delivery channel;
* delivery status;
* attempt history.

Notification outcomes may create system events such as:

```text
notification.queued
notification.sent
notification.delivery_failed
```

Routine notification delivery must not create excessive event volume without operational value.

---

# Background jobs

Significant background jobs should integrate with the Event Journal.

Possible events include:

```text
background_job.started
background_job.completed
background_job.failed
background_job.cancelled
```

Not every small technical task needs a persistent event.

Persistent job events are appropriate when the task is:

* operationally significant;
* audit relevant;
* externally visible;
* long-running;
* retryable;
* part of a regulated workflow.

Technical Celery execution details remain in platform logs.

## Job correlation

Background tasks should preserve the originating correlation ID.

Example:

```text
policy.published
        ↓
notification task queued
        ↓
notification.sent
```

All related events share the same correlation ID.

---

# Platform logging relationship

Platform logging and the Event Journal remain separate.

## Platform logs

Platform logs support:

* debugging;
* container monitoring;
* deployment diagnostics;
* exception traces;
* infrastructure failures;
* performance analysis.

## Event Journal

The Event Journal supports:

* operational history;
* audit;
* security history;
* record timelines;
* system-processing outcomes;
* governance reporting.

Example:

A database outage should appear in platform logs.

It does not necessarily need an Event Journal entry because the database may be unavailable.

A failed notification may produce:

* a platform warning or error log;
* a persistent `notification.delivery_failed` event.

---

# Manual operational notes

Users may add manual operational notes.

A note is stored as an event such as:

```text
operational.note_added
```

Example:

```text
Crew reports access delayed by a locked gate.
```

The event should record:

* author;
* occurred time;
* Desk;
* context;
* visibility;
* summary or details;
* optional file references.

Notes are immutable.

Corrections create a new event.

---

# Before-and-after values

Audit-relevant events may contain structured change data.

Example:

```json
{
  "before": {
    "status": "available"
  },
  "after": {
    "status": "assigned"
  }
}
```

Rules:

1. Store only changed fields.
2. Do not store secrets.
3. Avoid duplicating large text fields.
4. Do not store entire database rows.
5. Redact sensitive values.
6. Use stable field keys.
7. Restrict detailed values to authorised audit views.

Operational views may render a human-readable summary without displaying the structured values.

---

# Sensitive data

The Event Journal must not become a duplicate clinical, HR or patient database.

Avoid storing:

* full clinical narratives;
* complete patient demographics;
* passwords;
* tokens;
* secret keys;
* full document contents;
* complete staff records;
* unnecessary addresses;
* unnecessary contact details.

Store identifiers and minimal display snapshots.

Detailed information remains in the owning domain record and is accessed through that module’s permissions.

---

# Event visibility and authorisation

Event access is evaluated through a combination of:

* classification;
* visibility;
* permission codes;
* Desk scope;
* subject access;
* context access;
* module-specific rules.

Example:

A user may be permitted to view the operational timeline of an incident but not detailed clinical events associated with it.

The query service must support filtering or redaction before events reach templates or APIs.

---

# Event query services

The Event Journal should provide deliberate query services.

Initial examples include:

```python
event_query.list_for_subject(...)
event_query.list_for_context(...)
event_query.list_for_desk(...)
event_query.list_for_actor(...)
event_query.list_for_correlation(...)
event_query.list_operational(...)
event_query.list_audit(...)
event_query.list_security(...)
```

Queries should support:

* pagination;
* deterministic ordering;
* time ranges;
* event-code filtering;
* classification filtering;
* severity filtering;
* visibility checks;
* Desk descendants;
* authorised metadata disclosure.

Routes and templates should not construct raw Event Journal queries directly.

---

# Event rendering

Event codes require presentation renderers.

Example event:

```text
vehicle.arrived_on_scene
```

Possible operational rendering:

```text
Vehicle A12 arrived on scene at 14:27.
```

Possible audit rendering:

```text
Dispatcher Alex Smith recorded Vehicle A12 as on scene for Incident INC-2026-0042.
```

The same stored event may be rendered differently for different views.

Renderers must:

* use stable event codes;
* escape user-supplied text;
* handle missing historical records;
* respect visibility;
* avoid exposing metadata automatically.

---

# Reporting

The Event Journal supports historical reporting but does not replace all domain reporting.

Examples suited to event data include:

* number of incidents created;
* vehicle arrival activity;
* staff sign-in activity;
* authentication failures;
* policy publication events;
* failed notifications;
* operational activity by Desk.

Current-state reports should generally query domain tables.

Example:

```text
Current available vehicles
```

should query the Vehicle domain.

Example:

```text
Vehicle availability transitions during July
```

may use the Event Journal.

---

# Retention

Event retention requirements will vary by classification and domain.

The initial design should assume long-term retention.

Future retention policies may consider:

* operational events;
* security events;
* clinical events;
* governance records;
* system-processing events;
* temporary diagnostic events.

Deletion must not be introduced casually.

Retention, archival and legal hold require a separate architecture decision.

---

# Performance and scale

The Event Journal is expected to grow continuously.

Initial design requirements include:

* indexed `recorded_at`;
* indexed `occurred_at`;
* indexed `event_code`;
* indexed `desk_id`;
* indexed actor reference;
* indexed subject reference;
* indexed context reference;
* indexed `correlation_id`;
* deterministic pagination.

Large metadata fields should be avoided.

Queries should use bounded time ranges and pagination.

Future options may include:

* partitioning by time;
* archival tables;
* materialised reporting views;
* search indexing;
* tiered retention.

These should be introduced only when measured requirements justify them.

---

# Proposed package structure

```text
app/
└── events/
    ├── __init__.py
    ├── commands.py
    ├── constants.py
    ├── exceptions.py
    ├── models.py
    ├── queries.py
    ├── renderers.py
    ├── services.py
    ├── validators.py
    └── reference_data.py
```

## Commands

Commands describe event-recording requests.

## Models

Models own persistent Event Journal records and classification relationships.

## Services

Services validate and record events.

## Queries

Queries provide authorised Activity Streams and log projections.

## Renderers

Renderers convert event codes and metadata into human-readable output.

## Reference Data

Reference Data may define:

* system event classifications;
* event sources;
* severity values;
* visibility values.

Event codes themselves should normally remain code-owned contracts rather than configurable catalogue rows.

---

# Initial service API

The initial public API may include:

```python
event_service.record(command)
event_service.record_operational(command)
event_service.record_audit(command)
event_service.record_security(command)
event_service.record_system(command)
event_service.add_operational_note(command)
event_service.record_correction(command)
```

Convenience methods should build one consistent event model.

They must not create separate persistence paths.

---

# Event command requirements

A recording command should include:

```text
event_code
occurred_at
actor
subject
context
desk
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

Not every field is mandatory for every event.

Defaults must be explicit and documented.

Commands should be immutable.

---

# Error handling

Event Journal exceptions should use the shared platform hierarchy.

Suggested exceptions include:

```text
EventJournalError
InvalidEventError
EventNotFoundError
EventVisibilityError
EventPersistenceError
EventCorrectionError
```

Possible categories:

| Exception               | Platform category                   |
| ----------------------- | ----------------------------------- |
| `InvalidEventError`     | `ValidationError`                   |
| `EventNotFoundError`    | `NotFoundError`                     |
| `EventVisibilityError`  | `PermissionDeniedError`             |
| `EventPersistenceError` | `PersistenceError`                  |
| `EventCorrectionError`  | `ConflictError` or `LifecycleError` |

Raw SQLAlchemy errors must not escape the service boundary.

---

# Testing requirements

## Model tests

Test:

* required fields;
* stable event-code format;
* timestamp behaviour;
* immutable rules;
* correlation and causation;
* classification relationships;
* indexes and constraints.

## Service tests

Test:

* valid event recording;
* invalid commands;
* transactional behaviour;
* metadata validation;
* actor, subject and context references;
* Desk relationship;
* overlapping classifications;
* correction behaviour;
* persistence failure translation.

## Query tests

Test:

* subject streams;
* context streams;
* Desk streams;
* descendant Desk scope;
* classification filters;
* visibility;
* pagination;
* deterministic ordering;
* correlation chains.

## Architecture tests

Test:

* event codes use stable format;
* business modules use the public Events API;
* modules do not create independent audit-log tables;
* Event Journal services do not import routes;
* Event Journal queries enforce authorisation boundaries;
* event exception classes follow the shared hierarchy.

---

# Implementation sequence

## Phase 1 — Architecture and decisions

1. Complete this architecture chapter.
2. Create the related ADRs.
3. Define stable event vocabulary conventions.
4. Define classification, source, severity and visibility values.
5. Update the roadmap.

## Phase 2 — Core Event Journal

1. Create the Events package.
2. Add exception hierarchy.
3. Add immutable command objects.
4. Add Event Journal models.
5. Add migration.
6. Add recording service.
7. Add transactional tests.
8. Add public exports.

## Phase 3 — Query and Activity Streams

1. Add subject queries.
2. Add context queries.
3. Add actor queries.
4. Add correlation queries.
5. Add classification filters.
6. Add rendering foundation.
7. Add pagination.

## Phase 4 — Lifecycle integration

1. Build Lifecycle platform.
2. Record significant lifecycle transitions.
3. Ensure state and event records commit together.
4. Add reusable lifecycle event helpers.

## Phase 5 — Desks

1. Build Desk hierarchy.
2. Add Desk access.
3. Add Desk-aware Event Journal queries.
4. Add company-wide and Desk-specific streams.
5. Add Operational Log views.

## Phase 6 — Audit and security views

1. Add Audit Log projection.
2. Add Security Log projection.
3. Add detailed metadata permissions.
4. Add export.

## Phase 7 — Notifications and jobs

1. Add event-driven notification handlers.
2. Preserve correlation through background tasks.
3. Record significant job outcomes.
4. Avoid excessive low-value events.

---

# Non-goals

The initial Event Journal will not provide:

* full event sourcing;
* event replay to reconstruct domain state;
* distributed streaming infrastructure;
* Kafka or similar brokers;
* cross-installation event federation;
* blockchain or cryptographic verification;
* arbitrary user-created event codes;
* unrestricted metadata;
* automatic notification for every event;
* persistent records for every diagnostic log message.

---

# Architecture decisions

The following decisions are established by this chapter and should also be recorded as ADRs.

## ADR-0001 — Unified Event Journal

### Decision

Response Connect will maintain one persistent append-only Event Journal for operational, audit, security and significant system events.

### Consequence

Modules must not create independent audit-log or operational-history tables unless a later ADR explicitly permits it.

## ADR-0002 — Current state remains in domain tables

### Decision

Domain tables remain authoritative for current state.

The Event Journal records historical facts and transitions.

### Consequence

Response Connect will not use full event sourcing for the initial platform.

## ADR-0003 — Desk-centred operational scope

### Decision

Desks are the primary operational context for work, access, dashboards, resources and operational activity.

### Consequence

Operational Event Journal queries and views must be Desk aware.

## ADR-0004 — Notifications are event-driven

### Decision

Notifications should normally be produced in response to recorded events.

### Consequence

Business modules record domain events rather than directly embedding delivery logic throughout services.

## ADR-0005 — Lifecycle transitions create events

### Decision

Significant successful lifecycle transitions must produce immutable Event Journal entries.

### Consequence

Lifecycle services and business state changes must integrate transactionally with the Event Journal where possible.

## ADR-0006 — Activity Streams are projections

### Decision

Record histories, Desk timelines, Operational Logs, Audit Logs and Security Logs are filtered projections of the Event Journal.

### Consequence

These interfaces must not introduce duplicate persistence models for the same occurrence.

---

# Decision summary

Response Connect will use one immutable Event Journal as the shared history platform.

Operational Logs, Audit Logs, Security Logs and Activity Streams will be projections of the journal.

Domain tables remain authoritative for current state.

Desks provide the operational scope for work and event visibility.

Lifecycle transitions create events.

Notifications and significant background-job outcomes are driven by or correlated with recorded events.

This architecture provides consistent operational and audit history without adopting full event sourcing or distributed event-streaming complexity.
