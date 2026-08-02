# Response Connect Delivery Roadmap

## Purpose

This document is the active delivery roadmap for Response Connect.

It records:

* work already completed;
* work currently in progress;
* agreed future work;
* dependencies between capabilities;
* the intended build order;
* documentation and testing requirements;
* deferred ideas that must not be forgotten.

This roadmap should be reviewed before beginning any new development task.

When work is completed, deferred, superseded or newly agreed, this document must be updated in the same commit or pull request where practical.

This document is not a replacement for:

* architecture chapters;
* Architecture Decision Records;
* issue tracking;
* release milestones;
* module-specific implementation plans.

It provides the consolidated project-wide view.

---

# Working rules

Before starting any significant task:

1. Review this roadmap.
2. Confirm the task belongs to the current phase.
3. Confirm required dependencies are complete.
4. Check the relevant architecture chapter.
5. Identify whether an ADR is required.
6. Define the expected implementation, tests and documentation.
7. Avoid beginning unrelated work from a later phase.

When completing a task:

1. Run the relevant tests.
2. Run the full test suite.
3. Update architecture or developer documentation.
4. Update this roadmap.
5. Record any deferred work.
6. Commit with a clear message.
7. Push the completed changes to GitHub.

---

# Status key

```text
✅ Complete
🚧 In progress
⬜ Planned
⏸ Deferred
⚠ Needs review
❌ Superseded
```

---

# Current project status

## Current phase

```text
Platform Foundation and Consolidation
```

## Current objective

Complete and stabilise the reusable platform capabilities required before building major workforce and operational modules.

## Next implementation milestone

```text
Event Journal Foundation
```

This must not begin until the remaining consolidation tasks listed below are complete.

---

# Phase 1 — Core application foundation

## Application structure

* [x] ✅ Flask application factory.
* [x] ✅ PostgreSQL database integration.
* [x] ✅ Flask-SQLAlchemy.
* [x] ✅ Flask-Migrate and Alembic.
* [x] ✅ Docker-based development and deployment.
* [x] ✅ Redis container.
* [x] ✅ Background worker container.
* [x] ✅ HTMX-based server-rendered interface.
* [x] ✅ Iconify with Tabler icons.
* [x] ✅ Core Response Connect colour palette.
* [x] ✅ Base application layout.
* [x] ✅ Personal application area.
* [x] ✅ Organisation application area.
* [x] ✅ Organisation settings area.

## Authentication and permissions

* [x] ✅ User authentication foundation.
* [x] ✅ Roles and permissions foundation.
* [x] ✅ Permission decorators.
* [x] ✅ Settings routes protected by stable permission codes.
* [ ] ⚠ Review authentication and permissions against current platform conventions.
* [ ] ⬜ Add security-event integration when the Event Journal exists.
* [ ] ⬜ Add Desk-scoped authorisation after Desks are implemented.
* [ ] ⬜ Document the authentication and authorisation developer interface.

---

# Phase 2 — Developer architecture and handbook

## Completed architecture chapters

* [x] ✅ `01-platform-principles.md`
* [x] ✅ `02-project-structure.md`
* [x] ✅ `03-module-conventions.md`
* [x] ✅ `04-service-layer-conventions.md`
* [x] ✅ `05-core-concepts.md`
* [x] ✅ `06-catalogue-framework.md`
* [x] ✅ `07-platform-overview.md`
* [x] ✅ Architecture README updated.

## Planned architecture chapters

* [ ] ⬜ File and Content Platform.
* [ ] ⬜ Event Journal.
* [ ] ⬜ Lifecycle Platform.
* [ ] ⬜ Desks and Operational Scope.
* [ ] ⬜ Operational Log and Audit Log.
* [ ] ⬜ Reference Data.
* [ ] ⬜ Competency Framework.
* [ ] ⬜ Workflow and Notifications.
* [ ] ⬜ UI and HTMX Patterns.
* [ ] ⬜ Testing Standards.
* [ ] ⬜ Coding Standards.
* [ ] ⬜ Architecture Decision Record index.
* [ ] ⬜ Long-term platform roadmap.

## Architecture Decision Records

Create and maintain:

```text
docs/adrs/
```

Initial ADR backlog:

* [ ] ⬜ Platform-first architecture.
* [ ] ⬜ Single organisation per installation.
* [ ] ⬜ Service-layer transaction ownership.
* [ ] ⬜ S3-compatible object storage.
* [ ] ⬜ Streaming file downloads through Flask.
* [ ] ⬜ Immutable file objects.
* [ ] ⬜ Concrete catalogue tables with a shared framework.
* [ ] ⬜ Separation of classification and processing behaviour.
* [ ] ⬜ Event Journal rather than separate audit and operational stores.
* [ ] ⬜ Desks as the primary operational context.
* [ ] ⬜ Domain tables remain the source of current state.
* [ ] ⬜ No full event sourcing for the initial platform.

---

# Phase 3 — Files and content platform

## Storage infrastructure

* [x] ✅ MinIO S3-compatible storage running in Docker.
* [x] ✅ Storage accessible from web and worker containers.
* [x] ✅ S3 provider abstraction.
* [x] ✅ Bucket initialisation command.
* [x] ✅ Generated object keys.
* [x] ✅ Immutable file records.
* [x] ✅ SHA-256 hashing.
* [x] ✅ File metadata persistence.
* [x] ✅ Upload compensation after database failure.
* [x] ✅ Soft deletion.
* [x] ✅ Restoration.
* [x] ✅ Permanent purge.
* [x] ✅ Flask-streamed downloads.
* [x] ✅ File service tests.

## Catalogue foundation for files

* [x] ✅ Shared Catalogue mixin.
* [x] ✅ Shared catalogue validators.
* [x] ✅ Shared catalogue exceptions.
* [x] ✅ Minimal base catalogue service.
* [x] ✅ File-processing policy model.
* [x] ✅ File extension rules.
* [x] ✅ File MIME-type rules.
* [x] ✅ Processing-policy service.
* [x] ✅ Immutable command objects.
* [x] ✅ Child-rule reconciliation.
* [x] ✅ Processing-policy model and service tests.

## File-processing policies

* [x] ✅ `generic_binary`
* [x] ✅ `pdf_document`
* [x] ✅ `standard_image`
* [x] ✅ `profile_photo`
* [x] ✅ `archive`
* [x] ✅ Reference-data definitions.
* [x] ✅ Idempotent synchronisation.
* [x] ✅ Dry-run support.
* [x] ✅ Structured platform logging.

## Remaining file platform work

* [ ] ⬜ Add `FileType`.
* [ ] ⬜ Link each `FileType` to a `FileProcessingPolicy`.
* [ ] ⬜ Add system and custom File Types.
* [ ] ⬜ Add File Type settings UI.
* [ ] ⬜ Link `FileObject` to `FileType`.
* [ ] ⬜ Enforce processing-policy validation during uploads.
* [ ] ⬜ Add scan status lifecycle.
* [ ] ⬜ Add quarantine behaviour.
* [ ] ⬜ Add ClamAV-compatible malware scanning integration.
* [ ] ⬜ Add thumbnail generation.
* [ ] ⬜ Add image optimisation.
* [ ] ⬜ Add file preview generation.
* [ ] ⬜ Add metadata extraction.
* [ ] ⬜ Add OCR extension point.
* [ ] ⬜ Add file derivatives.
* [ ] ⬜ Add file sets and generic version history.
* [ ] ⬜ Add file reconciliation commands.
* [ ] ⬜ Add orphaned-object detection.
* [ ] ⬜ Add missing-object detection.
* [ ] ⬜ Add retention-policy extension points.
* [ ] ⬜ Add audit and Event Journal integration.
* [ ] ⬜ Write the Files developer guide.
* [ ] ⬜ Write the Files architecture chapter.

---

# Phase 4 — Catalogue platform

## Implemented

* [x] ✅ Concrete catalogue table approach.
* [x] ✅ Shared catalogue model fields.
* [x] ✅ Stable-code validation.
* [x] ✅ System and custom record distinction.
* [x] ✅ Active and inactive lifecycle.
* [x] ✅ Shared read and lifecycle service behaviour.
* [x] ✅ Public catalogue package exports.
* [x] ✅ First concrete implementation through File Processing Policies.

## Remaining

* [ ] ⬜ Shared catalogue administration layout.
* [ ] ⬜ Shared table and filter components.
* [ ] ⬜ Shared system/custom badges.
* [ ] ⬜ Shared active/inactive actions.
* [ ] ⬜ Standard HTMX catalogue forms.
* [ ] ⬜ Standard catalogue route conventions.
* [ ] ⬜ Shared catalogue test helpers.
* [ ] ⬜ Catalogue architecture fitness tests.
* [ ] ⬜ Apply framework to File Types.
* [ ] ⬜ Apply framework to a second catalogue.
* [ ] ⬜ Review migration of existing Location Types.
* [ ] ⬜ Write `docs/developer/creating-a-catalogue.md`.

---

# Phase 5 — Reference Data platform

## Implemented

* [x] ✅ Immutable record definitions.
* [x] ✅ Dataset definitions.
* [x] ✅ Dataset registry.
* [x] ✅ Application-wide registry lifetime.
* [x] ✅ Dataset synchroniser interface.
* [x] ✅ Structured synchronisation result.
* [x] ✅ Create, update, unchanged and conflict results.
* [x] ✅ CLI dataset listing.
* [x] ✅ CLI dataset synchronisation.
* [x] ✅ Single-dataset synchronisation.
* [x] ✅ Dry-run mode.
* [x] ✅ Idempotent processing.
* [x] ✅ Custom-record conflict detection.
* [x] ✅ Locally owned display-field preservation.
* [x] ✅ Structured logging.

## Remaining

* [ ] ⬜ Generic validation of all registered datasets.
* [ ] ⬜ Reserved-code registry.
* [ ] ⬜ Dataset dependency ordering.
* [ ] ⬜ Deprecation handling.
* [ ] ⬜ Replacement-code metadata.
* [ ] ⬜ Upgrade command integration.
* [ ] ⬜ Audit and Event Journal integration.
* [ ] ⬜ Reference-data synchronisation tests independent of Files.
* [ ] ⬜ CLI failure and conflict tests.
* [ ] ⬜ Developer guide for creating datasets.
* [ ] ⬜ Architecture chapter for Reference Data.

---

# Phase 6 — Platform consolidation

## Command and service patterns

* [x] ✅ Immutable command objects introduced.
* [x] ✅ File Processing Policy service updated.
* [x] ✅ Child collection reconciliation implemented.
* [x] ✅ Public service factories.
* [x] ✅ Public package exports reviewed for current Files and Catalogues work.
* [ ] ⬜ Review all existing platform package exports.
* [ ] ⬜ Standardise exception hierarchies.
* [ ] ⬜ Standardise service method names.
* [ ] ⬜ Review transaction boundaries.
* [ ] ⬜ Review complete typing coverage.
* [ ] ⬜ Review docstrings.
* [ ] ⬜ Remove obsolete modules and route files.
* [ ] ⬜ Review test database isolation.

## Platform logging

* [x] ✅ Shared structured logging helper.
* [x] ✅ File Processing Policy lifecycle logs.
* [x] ✅ Reference Data synchronisation logs.
* [x] ✅ Reference Data CLI logs.
* [x] ✅ Logging tests.
* [ ] ⬜ Review logging field naming.
* [ ] ⬜ Define standard event-name conventions.
* [ ] ⬜ Add structured formatter configuration.
* [ ] ⬜ Add environment-based log-level configuration.
* [ ] ⬜ Add request correlation identifiers.
* [ ] ⬜ Add task correlation identifiers.
* [ ] ⬜ Document sensitive-data logging rules.
* [ ] ⬜ Write `docs/developer/platform-logging.md`.

## Architecture fitness tests

Create:

```text
tests/architecture/
```

Required tests:

* [x] ✅ Platform modules do not import business blueprints.
* [x] ✅ Service modules do not import route modules.
* [ ] ⬜ Route modules do not contain direct cross-module persistence.
* [ ] ⬜ Reference-data dataset names are unique.
* [ ] ⬜ Reference-data codes are unique within each dataset.
* [ ] ⬜ Public `__all__` exports resolve successfully.
* [ ] ⬜ Stable permission-code format is valid.
* [ ] ⬜ Stable catalogue-code format is valid.
* [ ] ⬜ No obsolete job-position route module remains imported.
* [ ] ⬜ Platform modules do not depend on templates.
* [ ] ⬜ Business modules use public Files APIs.
* [ ] ⬜ No duplicate storage-provider implementation exists.

## Developer guides

Create:

```text
docs/developer/
```

Required guides:

* [ ] ⬜ Creating a module.
* [ ] ⬜ Creating a catalogue.
* [ ] ⬜ Creating a service.
* [ ] ⬜ Using command objects.
* [ ] ⬜ Adding Reference Data.
* [ ] ⬜ Working with files.
* [ ] ⬜ Testing services.
* [ ] ⬜ Platform logging.
* [ ] ⬜ HTMX route and form patterns.
* [ ] ⬜ Creating lifecycle relationships.
* [ ] ⬜ Recording Event Journal entries.
* [ ] ⬜ Working with Desk scope.

---

# Phase 7 — Event Journal platform

## Architecture

* [ ] ⬜ Write Event Journal architecture chapter.
* [ ] ⬜ Create ADR for unified Event Journal storage.
* [ ] ⬜ Define event classifications.
* [ ] ⬜ Define retention requirements.
* [ ] ⬜ Define sensitive-data rules.
* [ ] ⬜ Define before-and-after value rules.
* [ ] ⬜ Define event visibility rules.
* [ ] ⬜ Define actor, subject and context references.
* [ ] ⬜ Define Desk relationship.
* [ ] ⬜ Define correction and amendment behaviour.

## Core model

The Event Journal must support:

* [ ] ⬜ UUID identity.
* [ ] ⬜ Stable event code.
* [ ] ⬜ Occurred timestamp.
* [ ] ⬜ Recorded timestamp.
* [ ] ⬜ Actor type and identifier.
* [ ] ⬜ Actor display snapshot where needed.
* [ ] ⬜ Subject type and identifier.
* [ ] ⬜ Subject display snapshot where needed.
* [ ] ⬜ Context type and identifier.
* [ ] ⬜ Context display snapshot where needed.
* [ ] ⬜ Optional Desk.
* [ ] ⬜ Operational classification.
* [ ] ⬜ Audit classification.
* [ ] ⬜ System classification.
* [ ] ⬜ Security classification.
* [ ] ⬜ Severity.
* [ ] ⬜ Visibility.
* [ ] ⬜ Source.
* [ ] ⬜ Human-readable summary.
* [ ] ⬜ Optional details.
* [ ] ⬜ Correlation ID.
* [ ] ⬜ Causation ID.
* [ ] ⬜ Structured metadata.
* [ ] ⬜ Before-and-after values where appropriate.
* [ ] ⬜ Immutable persistence rules.

## Services

* [ ] ⬜ Event recording command.
* [ ] ⬜ Event recording service.
* [ ] ⬜ Operational-event helper.
* [ ] ⬜ Audit-event helper.
* [ ] ⬜ System-event helper.
* [ ] ⬜ Security-event helper.
* [ ] ⬜ Manual operational note command.
* [ ] ⬜ Correction event command.
* [ ] ⬜ Subject timeline query.
* [ ] ⬜ Context timeline query.
* [ ] ⬜ Desk timeline query.
* [ ] ⬜ Classification filters.
* [ ] ⬜ Correlation-chain query.
* [ ] ⬜ Permission-aware query layer.

## Testing

* [ ] ⬜ Events are immutable.
* [ ] ⬜ Event codes are stable and validated.
* [ ] ⬜ Event creation participates in domain transactions.
* [ ] ⬜ Failed domain transactions do not leave journal records.
* [ ] ⬜ Operational and audit classifications can overlap.
* [ ] ⬜ Sensitive metadata is rejected or redacted.
* [ ] ⬜ Correction events append rather than overwrite.
* [ ] ⬜ Timeline queries return deterministic ordering.
* [ ] ⬜ Desk scope is enforced when available.

---

# Phase 8 — Lifecycle platform

## Scope

Lifecycle provides reusable behaviour for time-bound relationships and explicit state changes.

It must not introduce one universal assignment table.

## Core behaviour

* [ ] ⬜ Date-range validation.
* [ ] ⬜ Start date cannot follow end date.
* [ ] ⬜ Effective-at-date checks.
* [ ] ⬜ Current relationship selection.
* [ ] ⬜ Historical relationship queries.
* [ ] ⬜ Future relationship queries.
* [ ] ⬜ Overlap detection.
* [ ] ⬜ Configurable single-current-assignment enforcement.
* [ ] ⬜ Explicit end operation.
* [ ] ⬜ Explicit cancellation operation.
* [ ] ⬜ Explicit suspension operation where required.
* [ ] ⬜ Explicit reactivation operation where required.
* [ ] ⬜ Lifecycle Event Journal integration.
* [ ] ⬜ Structured platform logs.
* [ ] ⬜ Reusable test helpers.

## First consumers

* [ ] ⬜ Staff Clinical Grade Assignment.
* [ ] ⬜ Desk Access Assignment.
* [ ] ⬜ Staff Desk Sign-in or Attendance.
* [ ] ⬜ Vehicle Desk Allocation.
* [ ] ⬜ Competency holdings.
* [ ] ⬜ Mandatory training records.

## Documentation

* [ ] ⬜ Lifecycle architecture chapter.
* [ ] ⬜ Developer lifecycle guide.
* [ ] ⬜ ADR for behaviour reuse without schema inheritance.

---

# Phase 9 — Desks and operational scope

## Desk architecture

* [ ] ⬜ Write Desks architecture chapter.
* [ ] ⬜ Create ADR for Desk-centred operational context.
* [ ] ⬜ Define root company Desk behaviour.
* [ ] ⬜ Define permanent and temporary Desks.
* [ ] ⬜ Define Desk hierarchy rules.
* [ ] ⬜ Define Desk status lifecycle.
* [ ] ⬜ Define Desk access model.
* [ ] ⬜ Define Desk capability model.
* [ ] ⬜ Define Desk transfer behaviour.
* [ ] ⬜ Define Desk-scoped authorisation.

## Desk Type catalogue

Initial system Desk Types:

* [ ] ⬜ `company`
* [ ] ⬜ `service`
* [ ] ⬜ `region`
* [ ] ⬜ `control`
* [ ] ⬜ `event`
* [ ] ⬜ `incident`
* [ ] ⬜ `dispatch`
* [ ] ⬜ `temporary`
* [ ] ⬜ `specialist`

## Desk capabilities

Initial capability codes:

* [ ] ⬜ `operational_log`
* [ ] ⬜ `cad`
* [ ] ⬜ `incidents`
* [ ] ⬜ `patient_transport`
* [ ] ⬜ `event_control`
* [ ] ⬜ `resource_tracking`
* [ ] ⬜ `staff_sign_in`
* [ ] ⬜ `vehicle_tracking`
* [ ] ⬜ `tasks`
* [ ] ⬜ `communications`

## Desk model

* [ ] ⬜ UUID.
* [ ] ⬜ Stable code.
* [ ] ⬜ Name.
* [ ] ⬜ Description.
* [ ] ⬜ Parent Desk.
* [ ] ⬜ Desk Type.
* [ ] ⬜ Operational status.
* [ ] ⬜ Timezone.
* [ ] ⬜ Optional default Location.
* [ ] ⬜ Optional opening time.
* [ ] ⬜ Optional closing time.
* [ ] ⬜ Active state.
* [ ] ⬜ Created and updated timestamps.

## Hierarchy queries

* [ ] ⬜ List ancestors.
* [ ] ⬜ List descendants.
* [ ] ⬜ Include or exclude current Desk.
* [ ] ⬜ Scope membership check.
* [ ] ⬜ Cycle prevention.
* [ ] ⬜ Root Desk protection.
* [ ] ⬜ Recursive PostgreSQL implementation.
* [ ] ⬜ Hierarchy tests.

## Access

* [ ] ⬜ User Desk Access model.
* [ ] ⬜ Permission or access-role mapping.
* [ ] ⬜ Include-descendants flag.
* [ ] ⬜ Effective dates.
* [ ] ⬜ Active-state evaluation.
* [ ] ⬜ Desk switcher.
* [ ] ⬜ Bookmarkable Desk URLs.
* [ ] ⬜ Server-side Desk-scope enforcement.
* [ ] ⬜ Company-wide access.
* [ ] ⬜ Multi-Desk access.

## Root Desk

* [ ] ⬜ Create one root Desk during installation or reference-data sync.
* [ ] ⬜ Root Desk cannot be deleted.
* [ ] ⬜ Root Desk has no parent.
* [ ] ⬜ Root Desk provides company-wide operational scope.

---

# Phase 10 — Operational Log and Audit Log

## Operational Log

* [ ] ⬜ Company-wide Operational Log.
* [ ] ⬜ Desk-specific Operational Log.
* [ ] ⬜ Include-descendant filtering.
* [ ] ⬜ Manual operational notes.
* [ ] ⬜ Event rendering templates.
* [ ] ⬜ Filters by event code.
* [ ] ⬜ Filters by actor.
* [ ] ⬜ Filters by subject.
* [ ] ⬜ Filters by context.
* [ ] ⬜ Filters by time.
* [ ] ⬜ Severity filters.
* [ ] ⬜ Visibility rules.
* [ ] ⬜ Attachments through Files.
* [ ] ⬜ Correction entries.
* [ ] ⬜ Export.

## Audit Log

* [ ] ⬜ Administrative Audit Log.
* [ ] ⬜ Actor details.
* [ ] ⬜ Source details.
* [ ] ⬜ Before-and-after values.
* [ ] ⬜ Record identifiers.
* [ ] ⬜ Correlation and causation.
* [ ] ⬜ Permission checks.
* [ ] ⬜ Security-event view.
* [ ] ⬜ Access-event view.
* [ ] ⬜ Immutable export.
* [ ] ⬜ Retention controls.
* [ ] ⬜ Legal-hold extension point.

## Shared projections

* [ ] ⬜ Record activity timeline.
* [ ] ⬜ Person timeline.
* [ ] ⬜ Vehicle timeline.
* [ ] ⬜ Incident timeline.
* [ ] ⬜ Shift timeline.
* [ ] ⬜ Patient Journey timeline.
* [ ] ⬜ Policy history.
* [ ] ⬜ Competency history.

---

# Phase 11 — Workforce foundation

## Existing workforce work

* [x] ✅ Staff Member model foundation.
* [x] ✅ Job Positions.
* [x] ✅ Staff Position Assignments.
* [x] ✅ Job Position settings routes.
* [x] ✅ Job Position tests aligned with current settings routes.
* [x] ✅ Mandatory Training Course settings catalogue foundation.
* [ ] ⚠ Review existing workforce models against Lifecycle conventions.

## Clinical Grades

* [ ] ⬜ Clinical Grade catalogue.
* [ ] ⬜ Stable codes.
* [ ] ⬜ System and custom grades.
* [ ] ⬜ Grade settings UI.
* [ ] ⬜ Reference Data.
* [ ] ⬜ Service layer.
* [ ] ⬜ Command objects.
* [ ] ⬜ Structured logs.
* [ ] ⬜ Event Journal integration.
* [ ] ⬜ Staff Clinical Grade Assignment.
* [ ] ⬜ Effective dates.
* [ ] ⬜ Primary grade.
* [ ] ⬜ Restrictions.
* [ ] ⬜ Authorising user.
* [ ] ⬜ Overlap rules.
* [ ] ⬜ Tests.

## Competencies

* [ ] ⬜ Competency categories.
* [ ] ⬜ Competency Types.
* [ ] ⬜ Expiry rules.
* [ ] ⬜ Evidence requirements.
* [ ] ⬜ Verification requirements.
* [ ] ⬜ Renewal rules.
* [ ] ⬜ Grade-to-competency requirements.
* [ ] ⬜ Role-to-competency requirements.
* [ ] ⬜ Staff Competency Records.
* [ ] ⬜ Verification workflow.
* [ ] ⬜ Expiry and renewal.
* [ ] ⬜ Event Journal integration.
* [ ] ⬜ Notifications.
* [ ] ⬜ Tests.

## Mandatory Training

* [x] ✅ Course settings foundation.
* [ ] ⬜ Align Mandatory Training Courses with Competency Types.
* [ ] ⬜ Define training requirements.
* [ ] ⬜ Define requalification periods.
* [ ] ⬜ Staff completion records.
* [ ] ⬜ Certificate upload.
* [ ] ⬜ File Type for mandatory training evidence.
* [ ] ⬜ Verification.
* [ ] ⬜ Expiry.
* [ ] ⬜ Renewal.
* [ ] ⬜ Compliance evaluation.
* [ ] ⬜ Notifications.
* [ ] ⬜ Reports.

## Qualifications and registrations

* [ ] ⬜ Qualifications.
* [ ] ⬜ Awarding organisations.
* [ ] ⬜ Certificate numbers.
* [ ] ⬜ Issue and expiry dates.
* [ ] ⬜ Evidence.
* [ ] ⬜ Verification.
* [ ] ⬜ Professional registrations.
* [ ] ⬜ Registration numbers.
* [ ] ⬜ Regulator records.
* [ ] ⬜ External verification extension points.

## Compliance

* [ ] ⬜ Requirement evaluation.
* [ ] ⬜ Compliant state.
* [ ] ⬜ Expiring state.
* [ ] ⬜ Expired state.
* [ ] ⬜ Missing state.
* [ ] ⬜ Pending verification state.
* [ ] ⬜ Not applicable state.
* [ ] ⬜ Staff compliance profile.
* [ ] ⬜ Grade compliance.
* [ ] ⬜ Role compliance.
* [ ] ⬜ Desk deployment compliance.
* [ ] ⬜ Compliance dashboard.
* [ ] ⬜ Reports and exports.

---

# Phase 12 — Resource platform direction

People, vehicles and equipment remain separate domain models.

A shared operational Resource interface may later provide:

* [ ] ⬜ Resource identity.
* [ ] ⬜ Resource type.
* [ ] ⬜ Current status.
* [ ] ⬜ Current availability.
* [ ] ⬜ Current Desk.
* [ ] ⬜ Current location.
* [ ] ⬜ Capabilities.
* [ ] ⬜ Current allocation.
* [ ] ⬜ Activity timeline.
* [ ] ⬜ Search integration.

Do not create one universal resource table without a separate architecture decision.

---

# Phase 13 — Operational modules

## Event Medical

* [ ] ⬜ Event record.
* [ ] ⬜ Automatic Event Desk creation.
* [ ] ⬜ Event planning.
* [ ] ⬜ Event shifts.
* [ ] ⬜ Staff deployment.
* [ ] ⬜ Vehicle deployment.
* [ ] ⬜ Treatment centres.
* [ ] ⬜ Event incidents.
* [ ] ⬜ Event tasks.
* [ ] ⬜ Event Operational Log.
* [ ] ⬜ Event CAD view.
* [ ] ⬜ Event reporting.
* [ ] ⬜ Event closure and archive.

## Patient Transport

* [ ] ⬜ Permanent Patient Transport Desks.
* [ ] ⬜ Regional Desk hierarchy.
* [ ] ⬜ Journey requests.
* [ ] ⬜ Journey scheduling.
* [ ] ⬜ Crew allocation.
* [ ] ⬜ Vehicle allocation.
* [ ] ⬜ Journey status lifecycle.
* [ ] ⬜ Hospital delays.
* [ ] ⬜ Operational messaging.
* [ ] ⬜ PTS Operational Log.
* [ ] ⬜ PTS dashboards.
* [ ] ⬜ Reporting.

## Incidents and CAD

* [ ] ⬜ Incident record.
* [ ] ⬜ Incident numbers.
* [ ] ⬜ Incident classification.
* [ ] ⬜ Priority.
* [ ] ⬜ Location.
* [ ] ⬜ CAD Desk.
* [ ] ⬜ Resource dispatch.
* [ ] ⬜ Unit status.
* [ ] ⬜ Incident timeline.
* [ ] ⬜ Communications.
* [ ] ⬜ Escalation.
* [ ] ⬜ Incident closure.
* [ ] ⬜ Incident reporting.
* [ ] ⬜ Major Incident Desk support.

## Shifts and attendance

* [ ] ⬜ Shift Types.
* [ ] ⬜ Shift records.
* [ ] ⬜ Desk relationship.
* [ ] ⬜ Staff assignments.
* [ ] ⬜ Staff sign-in.
* [ ] ⬜ Staff sign-out.
* [ ] ⬜ Compliance validation.
* [ ] ⬜ Vehicle allocations.
* [ ] ⬜ Shift Operational Log.
* [ ] ⬜ Shift timeline.
* [ ] ⬜ Exceptions and late arrivals.

## Tasks and communications

* [ ] ⬜ Desk tasks.
* [ ] ⬜ Assignment.
* [ ] ⬜ Priority.
* [ ] ⬜ Due dates.
* [ ] ⬜ Completion lifecycle.
* [ ] ⬜ Comments.
* [ ] ⬜ Event Journal integration.
* [ ] ⬜ Operational messages.
* [ ] ⬜ Communications timeline.
* [ ] ⬜ Notifications.

---

# Phase 14 — Fleet and equipment

## Fleet

* [ ] ⬜ Vehicle Types.
* [ ] ⬜ Vehicle records.
* [ ] ⬜ Registration and identifiers.
* [ ] ⬜ Vehicle status.
* [ ] ⬜ Availability.
* [ ] ⬜ Maintenance.
* [ ] ⬜ Inspections.
* [ ] ⬜ Defects.
* [ ] ⬜ Insurance files.
* [ ] ⬜ Service documents.
* [ ] ⬜ Desk allocation.
* [ ] ⬜ Operational deployment.
* [ ] ⬜ Vehicle timeline.
* [ ] ⬜ Reporting.

## Equipment

* [ ] ⬜ Equipment Types.
* [ ] ⬜ Equipment records.
* [ ] ⬜ Serial numbers.
* [ ] ⬜ Location.
* [ ] ⬜ Status.
* [ ] ⬜ Inspection.
* [ ] ⬜ Servicing.
* [ ] ⬜ Calibration.
* [ ] ⬜ Assignment.
* [ ] ⬜ Issue and return.
* [ ] ⬜ Desk allocation.
* [ ] ⬜ Evidence and manuals.
* [ ] ⬜ Timeline.

## Stock

* [ ] ⬜ Stock categories.
* [ ] ⬜ Units of measure.
* [ ] ⬜ Storage locations.
* [ ] ⬜ Batch tracking.
* [ ] ⬜ Expiry.
* [ ] ⬜ Issue and receipt.
* [ ] ⬜ Minimum levels.
* [ ] ⬜ Reorder alerts.
* [ ] ⬜ Audit history.

---

# Phase 15 — Library and governance

## Library

* [ ] ⬜ Library Document.
* [ ] ⬜ Document categories.
* [ ] ⬜ File sets.
* [ ] ⬜ Versions.
* [ ] ⬜ Draft lifecycle.
* [ ] ⬜ Review.
* [ ] ⬜ Approval.
* [ ] ⬜ Publication.
* [ ] ⬜ Effective dates.
* [ ] ⬜ Review dates.
* [ ] ⬜ Supersession.
* [ ] ⬜ Archive.
* [ ] ⬜ Audience.
* [ ] ⬜ Acknowledgement.
* [ ] ⬜ Notifications.
* [ ] ⬜ Full history.
* [ ] ⬜ Search.

## Governance

* [ ] ⬜ Internal audits.
* [ ] ⬜ Findings.
* [ ] ⬜ Actions.
* [ ] ⬜ Risks.
* [ ] ⬜ Controls.
* [ ] ⬜ Incidents and complaints.
* [ ] ⬜ Evidence.
* [ ] ⬜ Reports.
* [ ] ⬜ CQC-oriented governance views.

---

# Phase 16 — Notifications and automation

* [ ] ⬜ Notification model.
* [ ] ⬜ Notification Types.
* [ ] ⬜ In-application delivery.
* [ ] ⬜ Email delivery.
* [ ] ⬜ Delivery status.
* [ ] ⬜ Retry behaviour.
* [ ] ⬜ User preferences.
* [ ] ⬜ Notification templates.
* [ ] ⬜ Expiry reminders.
* [ ] ⬜ Task reminders.
* [ ] ⬜ Workflow notifications.
* [ ] ⬜ Operational alerts.
* [ ] ⬜ Event Journal integration.
* [ ] ⬜ Structured platform logs.
* [ ] ⬜ Worker tests.

---

# Phase 17 — Search and reporting

## Search

* [ ] ⬜ Global search service.
* [ ] ⬜ Module search providers.
* [ ] ⬜ Permission-aware results.
* [ ] ⬜ Desk-aware results.
* [ ] ⬜ Search filters.
* [ ] ⬜ File metadata search.
* [ ] ⬜ Library search.
* [ ] ⬜ People search.
* [ ] ⬜ Operational record search.

## Reporting

* [ ] ⬜ Metric definitions.
* [ ] ⬜ Dashboard framework.
* [ ] ⬜ Desk dashboards.
* [ ] ⬜ Compliance dashboards.
* [ ] ⬜ Operational dashboards.
* [ ] ⬜ Historical snapshots.
* [ ] ⬜ Exports.
* [ ] ⬜ Scheduled reports.
* [ ] ⬜ Access controls.

---

# Phase 18 — Testing and quality

## Test infrastructure

* [x] ✅ Pytest installed.
* [x] ✅ Pytest import path configured.
* [x] ✅ Files tests.
* [x] ✅ Catalogue validator tests.
* [x] ✅ Processing-policy service tests.
* [x] ✅ Platform logging tests.
* [x] ✅ Job Position route tests updated.
* [ ] ⬜ Dedicated PostgreSQL test database.
* [ ] ⬜ Isolated MinIO test bucket.
* [ ] ⬜ Worker integration tests.
* [ ] ⬜ Migration tests.
* [ ] ⬜ Reference-data framework tests.
* [ ] ⬜ Architecture fitness tests.
* [ ] ⬜ Accessibility testing.
* [ ] ⬜ End-to-end browser tests.
* [ ] ⬜ Performance tests.
* [ ] ⬜ Security tests.

## CI

* [ ] ⬜ GitHub Actions test workflow.
* [ ] ⬜ Formatting check.
* [ ] ⬜ Linting.
* [ ] ⬜ Static typing.
* [ ] ⬜ Unit tests.
* [ ] ⬜ Integration tests.
* [ ] ⬜ Architecture tests.
* [ ] ⬜ Reference-data validation.
* [ ] ⬜ Migration validation.
* [ ] ⬜ Documentation-link checks.
* [ ] ⬜ Container build.
* [ ] ⬜ Dependency vulnerability checks.

---

# Phase 19 — Documentation and contributor experience

## Repository documentation

* [ ] ⬜ Main README review.
* [ ] ⬜ Installation guide.
* [ ] ⬜ Upgrade guide.
* [ ] ⬜ Backup and restore guide.
* [ ] ⬜ MinIO and external S3 guide.
* [ ] ⬜ Redis and worker guide.
* [ ] ⬜ Configuration reference.
* [ ] ⬜ Security guide.
* [ ] ⬜ Contribution guide.
* [ ] ⬜ Code of Conduct.
* [ ] ⬜ Release process.
* [ ] ⬜ Support policy.
* [ ] ⬜ Roadmap process.

## Developer examples

Create canonical examples for:

* [ ] ⬜ Good module.
* [ ] ⬜ Good service.
* [ ] ⬜ Good catalogue.
* [ ] ⬜ Good Reference Data dataset.
* [ ] ⬜ Good lifecycle relationship.
* [ ] ⬜ Good Event Journal integration.
* [ ] ⬜ Good Desk-scoped route.
* [ ] ⬜ Good HTMX form.
* [ ] ⬜ Good service tests.

## User and administrator guides

* [ ] ⬜ User guide platform selected.
* [ ] ⬜ Administrator guide platform selected.
* [ ] ⬜ In-application help strategy.
* [ ] ⬜ Suggestions and enhancement platform.
* [ ] ⬜ Documentation versioning.
* [ ] ⬜ Release-specific documentation.

---

# Phase 20 — Deployment and operations

* [x] ✅ Docker application deployment.
* [x] ✅ PostgreSQL service.
* [x] ✅ Redis service.
* [x] ✅ Worker service.
* [x] ✅ MinIO service.
* [ ] ⬜ Production Compose review.
* [ ] ⬜ Development Compose overrides.
* [ ] ⬜ Health checks.
* [ ] ⬜ Startup dependency handling.
* [ ] ⬜ Automatic database upgrade strategy.
* [ ] ⬜ Automatic Reference Data synchronisation strategy.
* [ ] ⬜ Backup strategy.
* [ ] ⬜ Restore testing.
* [ ] ⬜ MinIO backup.
* [ ] ⬜ External S3 configuration.
* [ ] ⬜ Log collection.
* [ ] ⬜ Monitoring.
* [ ] ⬜ Metrics.
* [ ] ⬜ Alerting.
* [ ] ⬜ Deployment documentation.
* [ ] ⬜ Release images.
* [ ] ⬜ Upgrade testing.

---

# Immediate ordered backlog

The following order should be followed unless a documented decision changes it.

## Current consolidation

1. [ ] ⬜ Add architecture fitness tests.
2. [ ] ⬜ Complete public API review.
3. [ ] ⬜ Review platform exception consistency.
4. [ ] ⬜ Complete platform logging conventions.
5. [ ] ⬜ Create initial developer guides.
6. [ ] ⬜ Remove obsolete files and route implementations.
7. [ ] ⬜ Run and stabilise the full test suite.
8. [ ] ⬜ Update this roadmap.

## Event Journal

9. [ ] ⬜ Write Event Journal architecture chapter.
10. [ ] ⬜ Create Event Journal ADR.
11. [ ] ⬜ Define event model and migration.
12. [ ] ⬜ Implement event commands and service.
13. [ ] ⬜ Add transactional event recording.
14. [ ] ⬜ Add event queries.
15. [ ] ⬜ Add Event Journal tests.
16. [ ] ⬜ Update this roadmap.

## Lifecycle

17. [ ] ⬜ Write Lifecycle architecture chapter.
18. [ ] ⬜ Implement lifecycle validators and queries.
19. [ ] ⬜ Implement overlap detection.
20. [ ] ⬜ Integrate Lifecycle with Event Journal.
21. [ ] ⬜ Add lifecycle test helpers.
22. [ ] ⬜ Update this roadmap.

## Desks

23. [ ] ⬜ Write Desks architecture chapter.
24. [ ] ⬜ Create Desk Type catalogue.
25. [ ] ⬜ Create Desk model and hierarchy.
26. [ ] ⬜ Create root company Desk.
27. [ ] ⬜ Implement hierarchy queries.
28. [ ] ⬜ Implement Desk capabilities.
29. [ ] ⬜ Implement Desk access.
30. [ ] ⬜ Integrate Desks with Lifecycle and Event Journal.
31. [ ] ⬜ Add Desk settings UI.
32. [ ] ⬜ Add Desk switcher and scoped routes.
33. [ ] ⬜ Update this roadmap.

## Operational and Audit Logs

34. [ ] ⬜ Add Operational Log projection.
35. [ ] ⬜ Add Audit Log projection.
36. [ ] ⬜ Add manual operational notes.
37. [ ] ⬜ Add timelines.
38. [ ] ⬜ Add filters and permissions.
39. [ ] ⬜ Add export.
40. [ ] ⬜ Update this roadmap.

## Files and workforce

41. [ ] ⬜ Add File Types.
42. [ ] ⬜ Integrate File Types into upload validation.
43. [ ] ⬜ Add Clinical Grades.
44. [ ] ⬜ Add Staff Clinical Grade Assignments.
45. [ ] ⬜ Add Competency Types.
46. [ ] ⬜ Align Mandatory Training with Competencies.
47. [ ] ⬜ Add evidence uploads.
48. [ ] ⬜ Add compliance evaluation.
49. [ ] ⬜ Add expiry notifications.
50. [ ] ⬜ Update this roadmap.

---

# Deferred but retained ideas

These concepts are intentionally deferred but must remain visible.

* [ ] ⏸ Full plugin system.
* [ ] ⏸ Formal module manifests.
* [ ] ⏸ Real-time WebSocket operational updates.
* [ ] ⏸ Offline operation and later event synchronisation.
* [ ] ⏸ Full event sourcing.
* [ ] ⏸ Cross-installation Desk federation.
* [ ] ⏸ Mutual-aid organisation sharing.
* [ ] ⏸ Geospatial Desk boundaries.
* [ ] ⏸ AI-assisted metadata extraction.
* [ ] ⏸ AI-assisted operational summaries.
* [ ] ⏸ Advanced resource optimisation.
* [ ] ⏸ Telephony integration.
* [ ] ⏸ Radio integration.
* [ ] ⏸ External CAD integrations.
* [ ] ⏸ Cryptographic Event Journal verification.
* [ ] ⏸ Legal-hold support.
* [ ] ⏸ Tiered Event Journal archival.
* [ ] ⏸ Catalogue import and export.
* [ ] ⏸ Catalogue localisation.
* [ ] ⏸ Materialised Desk hierarchy paths.
* [ ] ⏸ Generic Resource API.

---

# Roadmap maintenance

This document should be updated when:

* a task is completed;
* a task begins;
* a task is deferred;
* an architectural decision changes the order;
* a new capability is agreed;
* an existing concept is superseded;
* testing reveals missing work;
* implementation introduces follow-up requirements.

Do not remove incomplete work merely because it is inconvenient.

Use the deferred section when a valid idea is deliberately postponed.

Use Architecture Decision Records when the roadmap changes because of a significant architectural decision.

---

# Next action

The next task is:

```text
Add the first architecture fitness tests under tests/architecture/.
```

Before beginning that work:

* review the Architecture chapters;
* confirm the current full test suite passes;
* confirm obsolete Job Position route files are not still imported;
* update this roadmap to mark Architecture Fitness Tests as in progress.
