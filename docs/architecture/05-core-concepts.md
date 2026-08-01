# Core Concepts and Shared Vocabulary

## Purpose

This document defines the core terms used throughout Response Connect.

Its purpose is to ensure that contributors use consistent language when discussing architecture, designing models, naming services and implementing workflows.

Many concepts in Response Connect are related but not interchangeable. For example:

* a file is not the same as a document;
* a person is not the same as a user account;
* a competency type is not the same as a competency record;
* reference data is not the same as organisation-created catalogue data;
* a workflow is not the same as an asynchronous task.

Consistent vocabulary reduces ambiguity, protects module boundaries and makes architecture discussions more precise.

# Platform terminology

## Platform

The platform is the collection of reusable capabilities that support Response Connect modules.

Examples include:

* authentication;
* permissions;
* catalogues;
* files;
* audit;
* reference data;
* notifications;
* workflows;
* search;
* reporting.

The platform should not contain business rules that only apply to one narrow operational area.

## Capability

A capability is reusable functionality provided by the platform or a shared domain module.

Examples include:

* storing and streaming files;
* recording audit events;
* sending notifications;
* managing configurable catalogues;
* assigning competencies;
* scheduling background work.

A capability may be used by several modules.

A capability is broader than an individual page or feature.

## Module

A module is a package that owns a coherent capability, domain concept or business workflow.

Examples include:

```text
files
audit
people
competencies
library
vehicles
incidents
```

A module owns:

* its records;
* its business rules;
* its lifecycle transitions;
* its public services;
* its permissions;
* its audit semantics.

A module is an implementation boundary.

## Feature

A feature is a user-facing or operational behaviour provided by one or more modules.

Examples include:

* uploading a training certificate;
* approving a policy;
* assigning a clinical grade;
* recording a vehicle inspection.

Features should be implemented using existing capabilities wherever possible.

A feature should not automatically become a new module.

## Business module

A business module implements workflows for a specific operational area.

Examples include:

* recruitment;
* event medical operations;
* patient transport;
* fleet management;
* incident management.

Business modules use platform and shared domain capabilities.

They should not implement alternative versions of those capabilities.

## Shared domain module

A shared domain module owns a concept used across several business areas.

Examples include:

* people;
* competencies;
* vehicles;
* equipment;
* locations;
* library records.

Shared domain modules sit between business modules and platform capabilities.

## Infrastructure provider

An infrastructure provider is an implementation of a technical dependency behind a platform interface.

Examples include:

* an S3-compatible file provider;
* an SMTP email provider;
* a future SMS provider;
* a Redis-backed task queue.

Business modules should not access providers directly.

# Identity and people terminology

## Person

A person is a real human being represented in Response Connect.

A person may exist without having access to the application.

Examples include:

* an employee;
* a volunteer;
* an applicant;
* a patient;
* an external contact;
* a contractor;
* a trainer.

The People module owns person identity records.

A person should not be created solely because a login is needed if an existing person record already represents the individual.

## User account

A user account represents authentication and application access.

A user account normally references one person.

A user account owns or participates in:

* login credentials;
* account activation state;
* roles;
* permissions;
* authentication history;
* application preferences.

A person and a user account are distinct concepts.

Not every person has a user account.

A user account should not duplicate personal identity fields already owned by the person record.

## Staff record

A staff record represents a person’s relationship with the organisation as a worker.

Depending on future design, this may include:

* employment status;
* staff number;
* start and end dates;
* department;
* manager;
* contractual information;
* operational availability.

A person may have more than one historical or concurrent organisational relationship.

The staff record should not own authentication credentials.

## Actor

An actor is the person, user account, service or system process responsible for an action.

Audit events may identify actors such as:

* an authenticated user;
* a background worker;
* a CLI command;
* an automated workflow;
* the system itself.

An actor is an audit concept, not necessarily a persistent domain model of its own.

# Organisation terminology

## Installation

An installation is one independently deployed instance of Response Connect.

Each installation has its own:

* application containers;
* database;
* Redis service;
* object storage configuration;
* local settings;
* operational data.

Response Connect currently assumes one organisation per installation.

Installation boundaries provide data isolation.

## Organisation

The organisation is the legal or operational entity using the installation.

Examples include:

* an ambulance service;
* an event medical provider;
* a search and rescue organisation;
* a community responder scheme.

Because the deployment model uses one organisation per installation, most operational records do not need an `organisation_id`.

The Organisation module still owns installation-wide identity and settings.

## Location

A location is a physical or organisational place represented within the installation.

Examples include:

* headquarters;
* ambulance station;
* office;
* department;
* equipment store;
* treatment room;
* controlled-drug cupboard.

Locations may form a hierarchy.

## Location type

A location type is a configurable catalogue record describing a class of location.

Examples include:

* site;
* department;
* room;
* store;
* vehicle base.

A location type defines classification and permitted capabilities.

It is not a location itself.

## Capability code

A capability code is a stable machine identifier representing behaviour understood by application logic.

For locations, examples may include:

```text
staff_base
vehicle_base
equipment_storage
medication_storage
```

Capability codes are not editable display labels.

# Catalogue and reference-data terminology

## Catalogue

A catalogue is a configurable collection of records used to classify, constrain or describe domain behaviour.

Examples include:

* file types;
* location types;
* competency types;
* employment types;
* vehicle types;
* document categories.

Catalogue records normally have:

* UUID identifiers;
* stable codes;
* display names;
* descriptions;
* icons;
* colours;
* sort ordering;
* active state;
* system or custom status.

Catalogues are managed through a shared interaction and service pattern.

## Catalogue record

A catalogue record is one entry in a catalogue.

Example:

```text
code: mandatory_training
name: Statutory and Mandatory Training
```

Application logic depends on the stable code.

Display fields may be locally customised where allowed.

## System catalogue record

A system catalogue record is supplied by Response Connect.

It normally has:

```text
is_system = true
```

The stable code is protected.

Locally editable display fields may include:

* name;
* description;
* icon;
* colour;
* sort order.

A system record should normally be deactivated rather than deleted when an organisation does not use it.

## Custom catalogue record

A custom catalogue record is created locally by the installation owner.

It normally has:

```text
is_system = false
```

Custom records must not be removed or overwritten by future reference-data synchronisation.

## Reference data

Reference data is system-supplied, upgrade-managed data identified by stable codes.

Examples include:

* permissions;
* initial roles;
* system file types;
* system competency categories;
* standard location capabilities.

Reference data is not simply any lookup table.

Reference data includes ownership rules for upgrades.

## Seed data

Seed data is data inserted to make an installation usable.

Seed data may include reference data, but the terms are not identical.

A basic test user may be seed data without being permanent reference data.

Seed logic must be safe to run repeatedly where practical.

## Reference-data synchronisation

Reference-data synchronisation is the process of bringing system-owned records into alignment with the installed application version.

It may:

* create missing system records;
* update fields explicitly owned by the system;
* preserve local display customisations;
* deactivate or supersede deprecated records;
* leave custom records untouched.

It must not blindly replace entire catalogue tables.

## Stable code

A stable code is an immutable or tightly protected machine identifier.

Examples include:

```text
mandatory_training
profile_photo
clinical_grade
paramedic
vehicle_insurance
```

Stable codes are used by:

* application logic;
* permissions;
* seed synchronisation;
* integrations;
* tests;
* reporting.

Display names must not be used as machine identifiers.

# File terminology

## File provider

A file provider is the infrastructure adapter responsible for storing and retrieving binary objects.

The initial provider uses S3-compatible storage.

Provider responsibilities include:

* bucket access;
* object upload;
* object retrieval;
* object deletion;
* existence checks;
* low-level storage errors.

The provider does not understand business meaning.

## File manager

The File Manager is the application-facing service that coordinates managed file workflows.

Its responsibilities include:

* validating upload limits;
* sanitising filenames;
* calculating SHA-256 hashes;
* generating object keys;
* storing file metadata;
* compensating after partial failure;
* soft deletion;
* restoration;
* purge;
* opening download streams.

Business modules use the File Manager rather than the provider.

## File object

A `FileObject` represents one immutable binary object stored through the Files module.

It records metadata such as:

* object key;
* bucket;
* original filename;
* MIME type;
* extension;
* size;
* SHA-256 hash;
* uploader;
* creation time;
* deletion state.

A `FileObject` is not the business document represented by the file.

A `FileObject` must never be overwritten with different content.

## Object key

An object key is the provider-level identifier for a stored object.

Response Connect uses generated keys such as:

```text
files/{file_uuid}/original
```

User-provided filenames must not be used as object keys.

An object key is not a filesystem path, even if it resembles one.

## Original filename

The original filename is the sanitised user-facing name associated with an uploaded file.

Examples include:

```text
manual-handling-certificate.pdf
vehicle-front-photo.jpg
```

The original filename is metadata.

It does not determine storage location.

## MIME type

A MIME type describes the declared media type of a file.

Examples include:

```text
application/pdf
image/jpeg
image/png
```

A MIME type supplied by a browser is not automatically trusted.

Future validation may inspect file signatures or detected content type.

## Extension

A file extension is the normalised suffix derived from a filename.

Examples include:

```text
pdf
jpg
png
```

Extensions are useful for display and preliminary validation.

They must not be treated as proof of file content.

## SHA-256 hash

A SHA-256 hash is a cryptographic digest calculated from the uploaded bytes.

It supports:

* integrity verification;
* duplicate detection;
* audit evidence;
* reconciliation;
* immutable-file guarantees.

Two files with the same hash have the same byte content, but may have different business meaning or filenames.

## File type

A file type is a catalogue record defining how a class of file may be used.

Examples include:

* profile photograph;
* mandatory training evidence;
* qualification certificate;
* vehicle photograph;
* insurance document;
* policy document.

A file type may define:

* allowed extensions;
* allowed MIME types;
* maximum size;
* image-processing requirements;
* virus-scanning requirements;
* preview behaviour;
* retention defaults.

A file type is not the same as a MIME type.

## File extension rule

A file extension rule records an extension permitted for a file type.

Example:

```text
file type: mandatory_training
extension: pdf
```

Extension rules should be modelled as records rather than comma-separated text where administration and querying benefit from the distinction.

## File MIME-type rule

A file MIME-type rule records a MIME type permitted for a file type.

Example:

```text
file type: mandatory_training
MIME type: application/pdf
```

Extension and MIME-type rules should normally both be evaluated.

## File category

A file category is a broad technical classification used for processing behaviour.

Examples include:

* image;
* document;
* spreadsheet;
* presentation;
* audio;
* video;
* archive;
* other.

File category is not the same as business file type.

Several file types may share the same technical category.

## File derivative

A file derivative is a generated file created from another `FileObject`.

Examples include:

* thumbnail;
* preview image;
* resized image;
* converted PDF preview;
* extracted text representation.

A derivative must have its own immutable storage identity.

The derivative relationship should record:

* source file;
* derivative type;
* generated file;
* generation status.

## Thumbnail

A thumbnail is an image derivative intended for compact display.

A thumbnail is not a replacement for the original file.

Thumbnail generation should be idempotent.

## Preview

A preview is a derivative or rendering suitable for display without downloading the original.

Examples include:

* a PDF preview image;
* a browser-friendly image conversion;
* a low-resolution representation.

Preview behaviour should remain separate from the original stored object.

## Scan status

Scan status represents the malware-scanning lifecycle of a managed file.

Expected states may include:

```text
pending
scanning
clean
infected
failed
not_required
```

A file marked infected must not be available through normal download routes.

A failed scan is not the same as a clean scan.

## Quarantine

Quarantine is a state in which a file exists but is restricted from ordinary use.

Possible reasons include:

* suspected malware;
* invalid content;
* failed processing;
* administrative review.

Quarantine is a lifecycle concept, not necessarily a separate storage bucket.

## Soft deletion

Soft deletion marks a file record as deleted while preserving the stored object.

Soft-deleted files are hidden from ordinary access.

Soft deletion allows:

* recovery;
* audit review;
* retention enforcement;
* delayed purge.

## Restoration

Restoration removes the soft-deleted state after verifying that the stored object still exists and that policy permits recovery.

## Purge

Purge permanently removes the stored object and its managed record, subject to retention and relationship rules.

Purge is distinct from deletion.

Purge should normally require elevated permission.

# Document and version terminology

## Document

A document is a business concept represented by one or more file versions or structured content records.

Examples include:

* a company policy;
* a clinical procedure;
* an insurance certificate;
* an equipment manual;
* a competency certificate.

A document may have:

* title;
* owner;
* category;
* lifecycle status;
* approval history;
* review date;
* current version.

A document is not merely a binary file.

## File set

A file set is a generic container grouping related file versions.

It provides a reusable version history independent of business-specific document rules.

A file set may track:

* its versions;
* its current version;
* its purpose;
* creation time.

Business modules may reference a file set.

## File version

A file version links one immutable `FileObject` into a version sequence.

A file version may contain:

* version number;
* display label;
* change summary;
* creator;
* creation time;
* file-set relationship.

A file version does not alter the underlying `FileObject`.

## Current version

The current version is the version selected for normal use.

Selecting a current version does not delete earlier versions.

The owning business module defines when a version becomes current.

## Version number

A version number is a sortable version identity.

Possible approaches include:

* sequential integers;
* major and minor numeric fields;
* semantic display labels.

The generic Files module should avoid assuming that every document uses the same business versioning scheme.

## Version label

A version label is user-facing text such as:

```text
1.0
1.1
2.0
2026 revision
Approved edition
```

The label may reflect domain-specific conventions.

## Superseded version

A superseded version is no longer current but remains part of the historical record.

Superseded does not mean deleted.

## Controlled document

A controlled document is a document governed by formal lifecycle rules.

Examples include:

* policies;
* procedures;
* standard operating procedures;
* clinical guidelines.

Controlled documents may require:

* ownership;
* approval;
* effective dates;
* review dates;
* publication;
* supersession;
* acknowledgement.

These rules belong to the Library or appropriate business module, not the Files module.

## Library document

A library document is a business record owned by the Library module.

It may reference a file set or structured content.

The Library module controls:

* title and reference;
* categories;
* ownership;
* approval;
* publication;
* review;
* supersession;
* audience.

## Evidence

Evidence is information supporting a business claim or record.

Examples include:

* a training certificate;
* a registration confirmation;
* a qualification document;
* a signed assessment;
* a photograph;
* an external verification reference.

Evidence may reference a `FileObject`, but evidence is not itself the file.

An evidence record may also contain:

* evidence type;
* verification status;
* verifier;
* issue date;
* notes;
* external reference.

# Competency terminology

## Competency

A competency is a recognised capability, qualification, registration, authorisation, training achievement or other compliance-related status associated with a person.

Examples include:

* FREC 4;
* paramedic registration;
* manual handling training;
* blue-light driving;
* medicines authorisation;
* major incident command;
* equipment competency.

Competency is used as an umbrella concept.

## Competency type

A competency type is a catalogue record defining the rules for a class of competency.

It may define:

* stable code;
* display name;
* category;
* whether it expires;
* default validity period;
* whether evidence is required;
* whether verification is required;
* whether multiple concurrent records are allowed;
* whether it contributes to operational grade;
* renewal behaviour;
* reminder rules.

A competency type is not proof that a person holds the competency.

## Competency record

A competency record represents a person’s individual holding, completion or assignment of a competency.

It may include:

* person;
* competency type;
* issue or completion date;
* expiry date;
* status;
* evidence;
* verifier;
* notes;
* renewal relationship.

A person may hold several competency records.

## Competency category

A competency category groups competency types by business meaning.

Examples include:

* clinical grade;
* qualification;
* mandatory training;
* professional registration;
* driving;
* internal authorisation;
* equipment competency;
* CPD.

A category is not necessarily a separate database model for every competency behaviour.

## Clinical grade

A clinical grade is a competency or grouped capability describing the level at which a person may practise operationally.

Examples may include:

* first aider;
* first responder;
* emergency care assistant;
* technician;
* paramedic;
* doctor.

Clinical grade should not be confused with:

* job title;
* employment position;
* pay grade;
* professional registration.

A person’s clinical grade may depend on several underlying competencies.

The final relationship will be defined in the Competency Framework.

## Qualification

A qualification is a formally awarded educational or vocational achievement.

Examples include:

* FREC 3;
* FREC 4;
* diploma;
* degree;
* teaching qualification.

A qualification may support a clinical grade but is not automatically the same thing.

## Training

Training is a learning activity or completed requirement.

Examples include:

* manual handling;
* safeguarding;
* infection prevention;
* basic life support.

Training may expire or require periodic renewal.

Training completion may be represented as a competency record.

## Mandatory training

Mandatory training is training required by law, regulation, policy, role or organisational standard.

Mandatory status may depend on:

* role;
* clinical grade;
* department;
* work activity;
* contract type.

A competency type may exist without being mandatory for every person.

Requirement assignment should be modelled separately from evidence of completion.

## Professional registration

A professional registration is an externally maintained authorisation or registration.

Examples include registration with:

* HCPC;
* GMC;
* NMC;
* another professional regulator.

Registration records may include:

* registration number;
* registered profession;
* issue date;
* expiry or renewal date;
* verification status.

Professional registration may be represented within the competency framework while retaining registration-specific fields.

## Internal authorisation

An internal authorisation is permission granted by the organisation.

Examples include:

* authority to administer a medicine;
* permission to drive a particular vehicle;
* permission to use specialist equipment;
* clinical sign-off;
* command authorisation.

Internal authorisation is distinct from an external qualification.

## Requirement

A requirement states that a person must hold a particular competency.

A requirement may arise from:

* role;
* clinical grade;
* department;
* location;
* activity;
* contract;
* legislation;
* organisational policy.

A requirement is not the same as a competency record.

## Compliance

Compliance is the evaluated state of a person or record against applicable requirements.

Possible results may include:

```text
compliant
expiring
expired
missing
pending_verification
not_applicable
```

Compliance is often derived rather than stored as one permanent truth.

## Expiry

Expiry is the point at which a competency record is no longer valid under its rules.

Expiry may be:

* explicit;
* calculated from issue date and validity period;
* absent for non-expiring competencies.

## Renewal

Renewal creates or recognises a new period of validity.

Renewal should normally create a new competency record or versioned history rather than overwriting the previous achievement.

## Verification

Verification is confirmation that a competency claim or evidence is authentic and acceptable.

Verification may be performed by:

* an authorised internal user;
* an automated external check;
* a regulator integration;
* a training provider.

Verification is distinct from approval where the business process requires both.

## Operational capability

Operational capability is the set of duties or roles a person is currently permitted to perform.

It may be derived from:

* active competencies;
* clinical grade;
* authorisations;
* current registration;
* training compliance;
* restrictions.

Operational capability should not be inferred from one editable job-title field.

# Workflow and lifecycle terminology

## Lifecycle

A lifecycle is the set of valid states and transitions for a record.

Example:

```text
draft
submitted
approved
published
superseded
archived
```

Lifecycle rules belong to the owning module.

## State

A state represents the current lifecycle condition of a record.

States should use stable codes.

Display labels may be configurable where appropriate.

## State transition

A state transition is an intentional change from one lifecycle state to another.

Transitions should be implemented through explicit service methods.

Example:

```python
library_service.publish(document_id, actor_id)
```

Avoid unrestricted direct status assignment.

## Workflow

A workflow is a coordinated sequence of actions, decisions or state transitions.

A workflow may span several modules.

Examples include:

* uploading and verifying competency evidence;
* submitting and approving a policy;
* onboarding a new staff member;
* reviewing an incident.

A workflow may be synchronous, asynchronous or mixed.

## Workflow service

A workflow service coordinates several capabilities for one business outcome.

Examples include:

```text
MandatoryTrainingUploadWorkflow
PolicyPublicationWorkflow
StaffOnboardingWorkflow
```

Workflow services sit above the participating modules.

They do not transfer ownership of the underlying records.

## Background task

A background task is a unit of work executed asynchronously by Celery.

Examples include:

* malware scanning;
* thumbnail generation;
* sending an email;
* recalculating compliance;
* processing an import.

A task is not automatically a workflow.

Tasks should call reusable services.

## Idempotency

Idempotency means repeating an operation produces the same correct result without harmful duplication.

Background tasks and externally retried operations must be designed for idempotency.

## Compensation

Compensation is a corrective operation performed when a workflow partially succeeds across systems that cannot share one transaction.

Example:

* an S3 upload succeeds;
* database persistence fails;
* the uploaded object is removed.

Compensation is not the same as a database rollback.

## Reconciliation

Reconciliation is the process of detecting and correcting inconsistent state after compensation cannot fully restore the system.

Examples include:

* orphaned S3 objects;
* database records whose objects are missing;
* failed audit delivery;
* incomplete external notification state.

# Audit terminology

## Audit event

An audit event is an immutable record that a significant action or system event occurred.

It may contain:

* timestamp;
* actor;
* action code;
* module;
* entity type;
* entity identifier;
* summary;
* relevant before and after values;
* request context;
* outcome.

Audit events must not be edited to rewrite history.

## Action code

An action code is a stable identifier for the event type.

Examples include:

```text
file.uploaded
file.downloaded
file.deleted
competency.assigned
competency.verified
library.document_published
```

Action codes are machine identifiers.

Human-readable descriptions may be localised or changed.

## Audit subject

The audit subject is the primary entity affected by an event.

Examples include:

* a file;
* a person;
* a competency record;
* a library document;
* a role.

An event may refer to additional related entities.

## Before and after data

Before and after data records meaningful changed values.

It should not contain unnecessary full model dumps.

Sensitive information should be omitted or redacted.

## Activity timeline

An activity timeline is a user-facing presentation of relevant audit or domain events.

An activity timeline may filter and translate audit events.

It is not a replacement for the underlying audit record.

# Permission terminology

## Permission

A permission is a stable code representing an allowed application action.

Examples include:

```text
files:view
files:upload
files:delete
competencies:assign
library:approve
```

Permissions describe actions, not job titles.

## Role

A role is a named collection of permissions assigned to user accounts.

Examples include:

* administrator;
* training manager;
* fleet manager;
* staff member.

Roles may be system-provided or locally configured.

## Authorisation

Authorisation is the decision that an actor may perform an action on a particular resource.

Authorisation may consider:

* permissions;
* ownership;
* relationship;
* record scope;
* lifecycle state;
* assignment;
* organisational policy.

Possessing a general permission may not be sufficient for every record.

## Authentication

Authentication establishes the identity of the user or system actor.

Authentication and authorisation are distinct.

A logged-in user is not automatically authorised for every action.

# Notification terminology

## Notification

A notification is a message or application record intended to inform a recipient of something.

Examples include:

* competency expiry warning;
* policy review reminder;
* task assignment;
* approval outcome.

A notification may be delivered through one or more channels.

## Notification channel

A notification channel is a delivery mechanism.

Examples include:

* in-application notification;
* email;
* SMS;
* push notification.

Business modules should request notifications through the Notifications capability rather than sending directly through a channel provider.

## Notification template

A notification template defines reusable content for a notification type.

Templates may include:

* stable code;
* subject;
* body;
* available variables;
* supported channels.

## Notification event

A notification event is the business occurrence that may cause notifications.

Examples include:

```text
competency.expiring
policy.review_due
task.assigned
```

The event and the delivered notification are distinct records.

# UI terminology

## Full-page response

A full-page response renders the complete application page, including layout and navigation.

Every core workflow should remain understandable and usable through standard browser navigation where practical.

## HTMX partial

An HTMX partial is a server-rendered HTML fragment returned for an HTMX request.

It should not contain a separate implementation of business behaviour.

## Component

A component is a reusable UI fragment or interaction pattern.

Examples include:

* status badge;
* catalogue table;
* modal form;
* file picker;
* empty state;
* activity timeline.

A component is not necessarily a JavaScript component.

## Empty state

An empty state is the UI presented when no records are available.

It should explain:

* what the section contains;
* why it may be empty;
* the next available action, if authorised.

## Error state

An error state communicates that an operation failed and what the user can reasonably do next.

Internal exception details must not be exposed.

# Reporting terminology

## Operational report

An operational report presents current or historical business data for decision-making.

## Dashboard

A dashboard presents selected metrics, alerts and summaries for a role or operational purpose.

A dashboard should not become the only way to access underlying records.

## Metric

A metric is a defined quantitative measure.

Metrics should have documented calculation rules.

## Snapshot

A snapshot records calculated or exported data at a point in time.

Snapshots may be necessary where later source-data changes must not alter historical reports.

# Architecture decision: shared vocabulary

## Decision

Response Connect will use a documented shared vocabulary for platform, file, document, competency, workflow, audit and identity concepts.

Model, service, route and documentation names should align with this vocabulary unless an explicit architecture decision introduces a more precise term.

## Context

Related concepts such as files, documents, evidence, qualifications and competencies can easily be used interchangeably.

Inconsistent terminology would create:

* unclear module ownership;
* duplicated models;
* confusing service APIs;
* difficult migrations;
* inconsistent user interfaces;
* misunderstandings between contributors.

## Alternatives considered

### Allow terminology to evolve independently by module

This would provide local freedom but would cause incompatible meanings and duplicated concepts.

### Define vocabulary only in code comments

This would make terminology difficult to discover and would not guide architecture discussions.

### Use industry-specific terminology everywhere

This could make the core platform less reusable outside one healthcare or ambulance context.

## Consequences

Benefits:

* clearer architecture discussions;
* more consistent model and service names;
* better module boundaries;
* reduced duplication;
* easier contributor onboarding;
* more reusable platform concepts.

Trade-offs:

* contributors must check the glossary before introducing new terms;
* some domain modules may require narrower subtypes;
* terminology changes may require coordinated documentation and code updates;
* user-facing labels may differ from internal architectural terms.

# Related documents

* [Platform Principles](01-platform-principles.md)
* [Project Structure and Module Boundaries](02-project-structure.md)
* [Module Conventions](03-module-conventions.md)
* [Service-Layer Conventions](04-service-layer-conventions.md)

# Future considerations

The following concepts will require more detailed definition in later chapters:

* catalogue inheritance and catalogue-specific rules;
* reference-data ownership at individual-field level;
* file-set and file-version numbering;
* document acknowledgement;
* competency equivalence;
* competency requirement assignment;
* derived operational capability;
* workflow definitions and workflow instances;
* notification preferences;
* audit retention;
* event publishing;
* reporting snapshots.

Later chapters may refine these concepts but should preserve the distinctions established here.

# Review checklist

When reviewing terminology in code or documentation, confirm:

* a file is not being treated as the business document;
* immutable file objects are preserved;
* evidence is modelled separately from stored bytes where needed;
* person, user account and staff relationship are not conflated;
* competency types and competency records are distinct;
* qualifications, training and registrations are represented as competency categories or specialisations rather than unrelated duplicate frameworks;
* catalogue and reference data are not used as interchangeable terms;
* workflows and background tasks are distinguished;
* audit events use stable action codes;
* permissions describe actions rather than roles;
* new terms have a clear owner and do not duplicate an existing concept.
