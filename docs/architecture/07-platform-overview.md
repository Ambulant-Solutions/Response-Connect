# Response Connect Platform Overview

## Purpose

This document provides a high-level overview of the Response Connect architecture.

It describes:

* the major platform capabilities;
* the shared organisational and operational domains;
* how modules depend on one another;
* how operational work is scoped through Desks;
* how lifecycle changes and events are recorded;
* the intended direction of the project.

This chapter is the architectural north star for Response Connect.

Detailed conventions remain in the other architecture chapters, but proposed features should be consistent with the model described here.

# Platform vision

Response Connect is an open-source operational management platform for ambulance, healthcare, emergency response and public safety organisations.

It is designed to support:

* organisational administration;
* workforce management;
* clinical competency and compliance;
* event medical operations;
* patient transport;
* incidents and dispatch;
* fleet and equipment;
* controlled documents;
* audit and governance;
* operational reporting.

The system is not intended to become a collection of disconnected administrative modules.

Its capabilities should form one coherent operational platform.

# Guiding principle

> Build capabilities once. Reuse them everywhere.

When several modules need the same behaviour, that behaviour should normally be implemented as a shared platform capability rather than recreated within each business module.

Examples include:

* file storage;
* catalogue management;
* reference-data synchronisation;
* lifecycle validation;
* event recording;
* audit;
* permissions;
* notifications;
* search;
* reporting.

# Architectural layers

Response Connect is organised into four broad layers.

```text
Business and operational modules
                ↓
Shared organisational domains
                ↓
Platform capabilities
                ↓
Infrastructure
```

Dependencies should generally flow downwards.

Lower layers must not depend on higher business layers.

# Infrastructure

Infrastructure provides the technical services required to run the application.

The initial infrastructure includes:

```text
Flask
PostgreSQL
Redis
Celery
S3-compatible object storage
Docker
```

Infrastructure integrations should be accessed through platform services.

Business modules must not call provider clients directly.

Examples:

* modules use `FileManager`, not the S3 client;
* modules use notification services, not SMTP directly;
* modules use lifecycle services, not duplicated date logic;
* modules use the Event Journal, not local activity-log tables.

# Platform capabilities

Platform capabilities provide reusable application behaviour that is independent of one operational use case.

## Authentication

Authentication establishes the identity of a user or system actor.

It owns:

* login and logout;
* account state;
* password or identity-provider integration;
* session management;
* authentication history.

Authentication does not decide what an authenticated actor may do.

That belongs to authorisation and permissions.

## Permissions and authorisation

Permissions use stable action codes such as:

```text
files:upload
hr:configure
library:approve
operations:dispatch
```

Authorisation may consider:

* user permissions;
* Desk scope;
* record ownership;
* assignment;
* lifecycle state;
* operational responsibility.

A user possessing a general permission may still be restricted to particular Desks or records.

## Catalogues

Catalogues provide configurable records used to classify or constrain domain behaviour.

Examples include:

* file types;
* Desk types;
* clinical grades;
* competency types;
* vehicle types;
* location types;
* document categories.

Catalogues use:

* UUID primary keys;
* stable codes;
* editable display names;
* system and custom ownership;
* activation and deactivation;
* shared service patterns.

## Reference Data

Reference Data defines system-supplied records and synchronises them safely during installation and upgrade.

It provides:

* immutable dataset definitions;
* a central registry;
* dataset synchronisers;
* dry-run support;
* conflict detection;
* idempotent execution;
* preservation of locally owned fields.

Catalogues define how records behave.

Reference Data defines which system records are supplied.

## Files and content

The Files platform manages immutable stored content.

It owns:

* file objects;
* S3-compatible storage;
* object keys;
* hashes;
* upload and download lifecycle;
* deletion, restoration and purge;
* processing policies;
* technical file validation;
* future derivatives, previews and scanning.

The Files platform does not own the business meaning of a policy, competency certificate, patient attachment or vehicle image.

Business modules reference files through public Files services.

## Platform logging

Platform logging supports:

* container logs;
* troubleshooting;
* operational monitoring;
* exception diagnosis;
* deployment and integration visibility.

Platform logs are not the permanent business audit record.

They may contain structured fields but must not expose secrets, file contents or unnecessary personal information.

## Event Journal

The Event Journal is the persistent, immutable record of significant application and operational events.

It underpins:

* the Operational Log;
* the Audit Log;
* record activity timelines;
* incident timelines;
* Desk timelines;
* system-event history;
* security-event history.

Domain tables remain the source of current state.

The Event Journal records what happened and how that state was reached.

## Lifecycle

The Lifecycle platform provides reusable behaviour for time-bound relationships and state changes.

Examples include:

* staff position assignments;
* clinical-grade assignments;
* competency holdings;
* Desk access;
* vehicle allocations;
* shift attendance;
* document approval;
* Desk opening and closing.

Lifecycle provides behaviour and validation rather than one universal assignment table.

Business modules retain ownership of their own relationship models.

## Notifications

The Notifications capability will provide reusable delivery of:

* in-application messages;
* email;
* future SMS or push notifications;
* reminders;
* workflow outcomes;
* expiry warnings;
* operational alerts.

Business modules should request notifications through the platform rather than call delivery providers directly.

## Search

Search will provide consistent discovery across authorised records.

Search results must respect:

* permissions;
* Desk scope;
* record lifecycle;
* module ownership;
* sensitive-data restrictions.

## Reporting

Reporting will provide:

* dashboards;
* operational summaries;
* compliance reporting;
* historical exports;
* defined metrics;
* future snapshots.

Reporting should consume domain data and Event Journal records without becoming the owner of operational state.

# Shared organisational domains

Shared domains represent core organisational concepts used by several business modules.

## Organisation

Each Response Connect installation currently represents one organisation.

The Organisation domain owns:

* legal and display identity;
* contact information;
* regional defaults;
* installation-wide settings.

Operational records do not require an organisation identifier while the one-organisation-per-installation model remains in place.

## People

The People domain represents real individuals.

A person may be:

* an employee;
* a volunteer;
* an applicant;
* a contractor;
* a patient;
* a contact;
* a trainer.

A Person is distinct from a User Account.

## Locations

Locations represent physical or organisational places.

Examples include:

* sites;
* stations;
* offices;
* departments;
* rooms;
* treatment centres;
* stores;
* cupboards.

Locations may form a hierarchy.

A Desk is not necessarily a physical location.

## Desks

A Desk is an operational control boundary and workspace.

Examples include:

```text
Company Operations
Patient Transport
Devon Patient Transport
Glastonbury Festival 2026
Major Incident Control
Fleet Control
```

Desks scope:

* operational work;
* dashboards;
* user access;
* resources;
* incidents;
* journeys;
* shifts;
* tasks;
* notifications;
* Operational Log entries.

Desks form a tree beneath one company-wide root Desk.

## Resources

A Resource is anything operationally available for assignment or deployment.

Examples include:

* people;
* vehicles;
* equipment;
* medical teams;
* treatment centres;
* radios;
* specialist units.

The underlying models remain distinct.

The Resource concept provides a common operational view of:

* availability;
* status;
* location;
* capabilities;
* allocation;
* assignment;
* history.

# Business and operational domains

Business modules compose platform and shared-domain capabilities.

## Workforce

The Workforce domain includes:

* staff records;
* job positions;
* position assignments;
* employment relationships;
* clinical grades;
* competencies;
* qualifications;
* mandatory training;
* compliance.

It uses:

* Catalogues;
* Reference Data;
* Lifecycle;
* Files;
* Event Journal;
* Notifications.

## Event medical operations

Event operations may include:

* event planning;
* Event Desks;
* staffing;
* vehicles and resources;
* incidents;
* treatment centres;
* tasking;
* operational notes;
* CAD functions;
* event reporting.

Each event may create its own Desk.

## Patient transport

Patient Transport may be organised into permanent regional Desks.

For example:

```text
Company Operations
└── Patient Transport
    ├── Devon
    ├── Cornwall
    └── Somerset
```

A Patient Transport Desk may show:

* unassigned journeys;
* active journeys;
* vehicles;
* crews;
* hospital delays;
* tasks;
* operational messages;
* Desk log.

## Incidents and CAD

Incident and CAD functions include:

* call receipt;
* incident creation;
* dispatch;
* resource allocation;
* status transitions;
* timeline management;
* communications;
* escalation;
* closure.

Each incident belongs to an operational Desk.

Incident activity is recorded through the Event Journal.

## Fleet

Fleet owns:

* vehicle identity;
* classifications;
* serviceability;
* maintenance;
* inspections;
* documents;
* defects.

Operational allocation to a Desk or deployment is handled through Lifecycle and recorded through the Event Journal.

## Equipment and stock

Equipment and stock modules may manage:

* equipment identity;
* categories;
* inspections;
* servicing;
* location;
* issue and return;
* allocation;
* expiry;
* supporting documents.

## Library and governance

The Library domain will manage controlled documents such as:

* policies;
* procedures;
* standard operating procedures;
* clinical guidelines;
* forms;
* manuals.

It will use:

* Files;
* versioning;
* approval lifecycle;
* Event Journal;
* notifications;
* acknowledgements;
* review schedules.

# Desks as the operational context

A Desk answers:

> Where does this work live?

Every operational record should normally have a clear primary Desk.

Examples:

| Record              | Primary operational context |
| ------------------- | --------------------------- |
| Event               | Event Desk                  |
| Incident            | Control or CAD Desk         |
| Patient journey     | Patient Transport Desk      |
| Shift               | Operational Desk            |
| Deployment          | Desk                        |
| Task                | Desk                        |
| Operational note    | Desk                        |
| Resource allocation | Desk                        |

Desk context simplifies:

* authorisation;
* filtering;
* reporting;
* dashboards;
* notifications;
* Event Journal queries;
* resource visibility.

# Desk hierarchy

There is one company-wide root Desk.

Example:

```text
Company Operations
├── Event Medical
│   ├── Glastonbury Festival 2026
│   └── Exeter Christmas Market
├── Patient Transport
│   ├── Devon
│   ├── Cornwall
│   └── Somerset
├── Ambulance Operations
│   ├── North Area
│   └── South Area
└── Specialist Functions
    ├── Fleet Control
    └── Clinical Advice
```

A parent Desk may include activity from its descendants.

A child Desk normally sees only its own activity and any descendants beneath it.

Hierarchy queries should support:

```python
list_ancestors(desk_id)
list_descendants(desk_id)
is_within_scope(candidate_desk_id, scope_desk_id)
```

PostgreSQL recursive queries are suitable for the initial implementation.

# Desk types and capabilities

Desk Type is a catalogue defining broad operational purpose.

Examples include:

```text
company
service
region
control
event
incident
dispatch
temporary
specialist
```

Desk capabilities use stable codes.

Examples include:

```text
operational_log
cad
incidents
patient_transport
event_control
resource_tracking
staff_sign_in
vehicle_tracking
tasks
communications
```

A Desk Type may supply default capabilities.

Individual Desks may have additional or restricted capabilities.

# Desk access

Access should combine:

```text
Permission
+
Desk scope
```

Examples:

```text
operations:view
Desk: Devon PTS
Include descendants: true
```

```text
operations:dispatch
Desk: Glastonbury Festival 2026
Include descendants: false
```

A user may have access to several Desks with different responsibilities.

Desk access must be checked on the server for every relevant request.

# Desk lifecycle

Desks may be permanent or temporary.

Operational states may include:

```text
planned
opening
open
restricted
closing
closed
archived
```

A temporary Event Desk may exist months before opening.

Closing a Desk does not delete it.

Its records and operational history remain available according to permission and retention rules.

Desk status transitions should use Lifecycle services and produce Event Journal entries.

# Event Journal model

The Event Journal records immutable events.

A journal event should support:

```text
id
event_code

occurred_at
recorded_at

actor
subject
context
Desk

category
severity
visibility
source

summary
details

correlation_id
causation_id

structured metadata
```

## Occurred and recorded times

`occurred_at` records when the event happened.

`recorded_at` records when Response Connect stored it.

These may differ due to:

* delayed entry;
* offline working;
* integration delays;
* retrospective correction.

## Actor

The actor may be:

* a user;
* a staff member;
* a background worker;
* an integration;
* the system.

## Subject

The subject is the primary thing affected.

Examples include:

* vehicle;
* person;
* shift attendance;
* competency record;
* file;
* incident.

## Context

The context is the wider operational record.

Examples include:

* Desk;
* incident;
* event;
* shift;
* patient journey;
* policy.

# Event classifications

One event may be relevant to several projections.

Rather than recording duplicate events, one immutable journal entry may be classified for:

* operational display;
* audit display;
* system monitoring;
* security review.

## Operational events

Examples:

```text
vehicle.arrived_on_scene
vehicle.cleared_scene
staff.shift_signed_in
staff.shift_signed_out
incident.created
incident.status_changed
patient_transport.started
work.transferred_between_desks
```

## Audit events

Examples:

```text
file.downloaded
record.updated
record.deleted
permission.changed
competency.verified
policy.published
```

## System events

Examples:

```text
reference_data.synchronised
file.scan_completed
notification.delivery_failed
integration.import_completed
```

## Security events

Examples:

```text
authentication.login_succeeded
authentication.login_failed
access.denied
account.locked
session.revoked
```

# Operational Log

The Operational Log is a user-facing projection of the Event Journal.

It should support:

* company-wide activity;
* Desk-specific timelines;
* event and incident timelines;
* shift logs;
* resource activity;
* manually entered operational notes;
* filters;
* structured event rendering.

Operational views should prioritise human-readable summaries.

Technical metadata remains available only where authorised and useful.

# Audit Log

The Audit Log is an administrative and governance projection of the same journal.

It may expose:

* actor;
* source;
* changed fields;
* before and after values;
* access events;
* request information;
* entity identifiers;
* correlation and causation;
* outcome.

The Audit Log is not a copy of platform container logs.

# Manual operational notes

Users may create operational notes through the Event Journal.

Examples include:

```text
Crew reports access delayed by locked gate.
Hospital advises approximately 45-minute handover delay.
Additional first aid post opened at the north entrance.
```

Notes should be immutable.

Corrections append a new event rather than silently changing history.

Supporting files may be linked through the Files platform.

# Typical command flow

A normal application command should follow this pattern:

```text
HTTP request
      ↓
Authentication and authorisation
      ↓
Route validates request input
      ↓
Business service receives command
      ↓
Lifecycle and domain validation
      ↓
Database changes prepared
      ↓
Audit or journal event prepared
      ↓
Single transaction commits
      ↓
Platform log records operational completion
      ↓
Notifications or asynchronous tasks scheduled
      ↓
HTML or HTMX response returned
```

Routes remain thin.

Services own the workflow and transaction.

Models own persistent state.

Templates own presentation.

# Typical operational workflow

Example: a vehicle arrives at an incident.

```text
Dispatcher or integration records arrival
                ↓
Incident service validates Desk and vehicle allocation
                ↓
Vehicle or deployment state is updated
                ↓
Database transaction commits
                ↓
Event Journal records vehicle.arrived_on_scene
                ↓
Incident timeline updates
                ↓
Desk Operational Log updates
                ↓
Company-level Operational Log may include the event
                ↓
Relevant dashboard metrics update
```

The event is recorded once and projected into several authorised views.

# Typical lifecycle workflow

Example: a staff member receives a clinical-grade assignment.

```text
Authorised user submits assignment
                ↓
Clinical-grade service validates:
- grade exists
- grade is active
- dates are valid
- assignment does not conflict
                ↓
Assignment model is created
                ↓
Event Journal records clinical_grade.assigned
                ↓
Compliance is recalculated
                ↓
Notifications may be scheduled
                ↓
Staff and audit timelines show the event
```

# Domain ownership

Every concept has one owning module.

Examples:

* Files owns `FileObject`.
* Desks owns Desk hierarchy and Desk access semantics.
* Fleet owns Vehicle.
* People owns Person.
* Workforce owns staff relationships.
* Competencies owns competency records.
* Events owns Event Journal persistence.
* Library owns controlled-document lifecycle.

Referencing another module’s record does not transfer ownership.

# Public service interfaces

Modules communicate through deliberate public services.

Preferred:

```python
desk_service.get_descendants(desk_id)
event_service.record(command)
file_manager.create_from_filestorage(...)
clinical_grade_service.assign(command)
```

Avoid:

```python
db.session.add(OtherModuleModel(...))
```

from outside the owning module when business rules are involved.

Infrastructure providers and private helpers must not be imported into business modules.

# Transaction boundaries

A business service should normally own one transaction for one coherent workflow.

Database changes and journal records should generally commit together.

Example:

```text
Assignment created
+
Event Journal entry created
=
One database transaction
```

This prevents successful state changes without corresponding persistent history.

External systems such as S3 cannot share the database transaction.

Those workflows require compensation and reconciliation behaviour.

# Event recording rules

1. Events are immutable.
2. Events use stable codes.
3. Significant state transitions create events.
4. Domain tables remain the source of current state.
5. One occurrence should normally create one journal event.
6. Operational and audit views project the same event where appropriate.
7. Sensitive data is minimised.
8. Before and after data contains only meaningful changed fields.
9. Corrections append events.
10. Event recording should participate in the business transaction where possible.

# Platform logging rules

1. Platform logs are operational diagnostics.
2. Platform logs do not replace the Event Journal.
3. Logs use stable structured event names.
4. Logs do not include secrets or file contents.
5. Expected validation failures generally do not require exception logs.
6. Significant infrastructure failures should be logged.
7. Persistent business events belong in the Event Journal.

# Resource model direction

People, vehicles and equipment remain separate domain models.

A future Resource capability may provide a common operational interface for:

* current availability;
* current Desk;
* location;
* capabilities;
* assignments;
* status;
* activity history.

The Resource concept must not force unrelated domains into one universal table.

# Architectural non-goals

Response Connect will not initially use:

* full event sourcing;
* microservices;
* one universal catalogue table;
* one universal relationship table;
* one universal resource table;
* direct browser access to object storage;
* multiple competing activity-log systems;
* business logic in routes;
* hidden page-load seeding.

The platform should remain understandable and operable through a standard Docker installation.

# Current capability status

## Implemented or substantially implemented

* Flask application foundation;
* PostgreSQL persistence;
* Redis and worker foundation;
* S3-compatible file storage;
* immutable managed file records;
* Flask-streamed file downloads;
* catalogue primitives;
* file-processing policies;
* Reference Data registry and synchronisation;
* structured platform logging foundation;
* authentication and permission foundations.

## In progress

* Files processing and validation integration;
* platform logging consolidation;
* developer guides;
* architecture fitness tests;
* public API review.

## Planned foundational capabilities

* Event Journal;
* Lifecycle platform;
* Desk hierarchy;
* Desk-scoped access;
* Operational Log;
* Audit Log;
* notifications;
* search;
* reporting.

## Planned business capabilities

* clinical grades;
* competencies;
* mandatory training;
* qualifications;
* evidence;
* compliance;
* event control;
* CAD;
* patient transport;
* operational resource management;
* controlled document library.

# Recommended implementation order

The next foundational work should proceed in this order.

## Phase 1 — Complete current consolidation

* finish platform logging tests;
* add architecture fitness tests;
* document public service patterns;
* review package exports;
* validate Reference Data datasets.

## Phase 2 — Event Journal

* define immutable event model;
* define command objects;
* implement recording service;
* implement actor, subject, context and Desk references;
* support operational, audit, system and security classification;
* add query services;
* test transactional event creation.

## Phase 3 — Lifecycle

* shared date validation;
* overlap detection;
* current and historical relationship queries;
* lifecycle transition helpers;
* Event Journal integration;
* reference tests.

## Phase 4 — Desks

* Desk Type catalogue;
* root company Desk;
* hierarchical Desk model;
* descendant and ancestor queries;
* Desk capabilities;
* Desk access assignments;
* Desk lifecycle;
* Desk selection and routing context.

## Phase 5 — Operational and Audit projections

* Operational Log view;
* Audit Log view;
* Desk timeline;
* subject timeline;
* context timeline;
* filters;
* permissions;
* export.

## Phase 6 — Workforce foundation

* Clinical Grades;
* grade assignments;
* competency types;
* mandatory training requirements;
* evidence;
* compliance.

## Phase 7 — Operational modules

* event control;
* incidents;
* CAD;
* patient transport;
* shifts;
* resource deployment;
* fleet activity;
* operational dashboards.

# Design review questions

Before adding a new capability, ask:

1. Which module owns this concept?
2. Is it infrastructure, platform, shared domain or business behaviour?
3. Which Desk does the operational work belong to?
4. Does the action require an Event Journal entry?
5. Is the event operational, audit, system or security relevant?
6. Does the relationship require Lifecycle behaviour?
7. Is a catalogue or Reference Data record required?
8. Does the capability need file evidence?
9. Are permissions combined with Desk scope?
10. Does the implementation introduce a duplicate pattern?
11. Can the service own one coherent transaction?
12. Can the feature be tested without HTTP?
13. Will a company-wide view and Desk-specific view behave consistently?
14. Does the implementation preserve immutable history?
15. Does the design remain practical for self-hosted deployment?

# Architecture decision: Desk-centred operational platform

## Decision

Response Connect will use Desks as the primary operational context for work, access, resources and activity.

A shared immutable Event Journal will underpin Operational Logs, Audit Logs and activity timelines.

Lifecycle services will govern time-bound relationships and state transitions.

Business modules will compose these capabilities rather than create independent operational-context, assignment or activity-log implementations.

## Context

Operational work may belong to:

* the organisation as a whole;
* a service;
* a region;
* a permanent control function;
* a temporary event;
* an incident;
* a specialist operational area.

Users need focused views of work while senior staff may require visibility across parent and child operational areas.

Operational actions and system changes also overlap significantly with audit requirements.

Separate unrelated systems for operational logs, audit logs and module timelines would duplicate information and create inconsistent history.

## Alternatives considered

### Independent logs per module

This would be locally simple but would duplicate models, permissions, filters and rendering.

### Separate Operational and Audit databases

This would provide strong conceptual separation but would duplicate events that are both operationally and administratively significant.

### Full event sourcing

This would make the journal the authoritative source of state but would introduce substantial complexity in development, migrations, reporting and self-hosted operation.

### Organisation-wide records without Desk context

This would be simpler initially but would make access, filtering, operational dashboards and control-room workflows difficult to scale.

## Consequences

Benefits:

* coherent operational context;
* hierarchical visibility;
* reusable access scoping;
* unified operational and audit history;
* consistent record timelines;
* easier CAD and control-room design;
* reusable resource allocation;
* reduced duplication;
* better reporting and investigation capability.

Trade-offs:

* Desk scope must be considered by many operational queries;
* event permissions require careful design;
* Event Journal growth and retention must be managed;
* hierarchical access adds complexity;
* event rendering requires stable templates and metadata conventions;
* Desk transfers and multi-Desk visibility require explicit workflows.

# Related documents

* [Platform Principles](01-platform-principles.md)
* [Project Structure and Module Boundaries](02-project-structure.md)
* [Module Conventions](03-module-conventions.md)
* [Service-Layer Conventions](04-service-layer-conventions.md)
* [Core Concepts and Shared Vocabulary](05-core-concepts.md)
* [Catalogue Framework](06-catalogue-framework.md)

# Future considerations

The following are intentionally deferred:

* Desk federation across installations;
* cross-organisation mutual-aid Desks;
* geospatial Desk boundaries;
* offline event synchronisation;
* real-time WebSocket updates;
* radio and telephony integration;
* advanced resource optimisation;
* event replay;
* full event sourcing;
* event archival tiers;
* legal hold;
* cryptographic journal verification;
* external audit export standards;
* materialised hierarchy paths;
* dynamic capability plugins.

These should be introduced only when concrete operational requirements justify them.

# Review checklist

When reviewing a new operational feature, confirm:

* it has a clear owning module;
* it has a primary Desk where appropriate;
* Desk access is checked server-side;
* parent and descendant scope are handled deliberately;
* significant actions create one immutable journal event;
* operational and audit views do not create duplicate events;
* lifecycle transitions are explicit;
* current domain state remains in domain tables;
* platform logs and persistent events remain distinct;
* file evidence uses the Files platform;
* stable codes identify event and catalogue types;
* sensitive data is minimised;
* services own workflows and transactions;
* history is appended rather than rewritten;
* the implementation strengthens the shared operational platform.
