> **Status:** Active

This is the authoritative development roadmap for Response Connect.

The historical roadmap used during the initial platform development has
been archived as `ROADMAP_OLD.md`.

# Response Connect Roadmap

**Last Updated:** August 2026

---

# Project Status

## Current Phase

**Phase 7 – Operational Platform Foundation**

## Current Milestone

**Event Journal Core Platform**

## Current Status

* ✅ Platform Foundation & Consolidation complete
* ✅ Architecture Handbook Chapters 1–9 complete
* ✅ Shared platform exception hierarchy complete
* ✅ Public API architecture established
* ✅ Architecture fitness tests established
* ✅ 138 automated tests passing

## Current Objective

Build the shared operational platform that every business module will use:

1. Desk Hierarchy
2. Event Journal
3. Lifecycle Framework
4. Notifications
5. Activity Streams

These capabilities form the foundation for all operational modules.

---

# Guiding Principles

Development follows a consistent workflow:

```
Architecture
        ↓
Data Model
        ↓
Implementation
        ↓
Tests
        ↓
Architecture Tests
        ↓
Documentation
```

Every completed task must be reflected in this roadmap before being committed.

## Platform Principles

Response Connect is built around a small number of reusable platform services.

- Business modules communicate through public package APIs (`service.py`).
- Internal implementation services remain package-private.
- All significant operational activity is recorded in the immutable Event Journal.
- Desks define the operational context for work.
- Reference Data provides configurable vocabularies without code changes.
- Every new feature is developed test-first where practical.

---

# Active Roadmap

## Phase 7 – Operational Platform Foundation

### 7.1 Desk Platform

The Desk platform defines operational ownership and scope throughout Response Connect.

#### Architecture

* [X] Write detailed Desk architecture chapter.
* [X] Finalise Desk data model.
* [x] Define Desk lifecycle.
* [x] Define Desk permission model.
* [x] Add Desk architecture fitness tests.
* [x] Confirm public package import boundaries.

#### Core Platform

* [X] Create Desk package.
* [X] Implement Desk model.
* [X] Implement Desk service.
* [X] Implement Desk query service.
* [X] Implement Desk validators.
* [X] Implement Desk commands.
* [X] Implement Desk exceptions.
* [X] Create Desk migration.

#### Hierarchy

* [x] Parent/child hierarchy.
* [x] Prevent hierarchy cycles.
* [x] Prevent invalid parent assignment.
* [x] Desk movement.
* [x] Descendant queries.
* [x] Breadcrumb/path generation.
* [x] Desk activation/deactivation.
* [x] Desk archival.

#### Lifecycle

* [x] Add explicit Desk archival state.
* [x] Implement Desk activation.
* [x] Implement Desk deactivation.
* [x] Implement Desk archival.
* [x] Protect the root Desk.
* [x] Prevent invalid lifecycle transitions.
* [x] Add Desk lifecycle tests.

#### Testing

* [x] Model tests.
* [x] Service tests.
* [x] Query tests.
* [x] Public API architecture tests.
* [x] Hierarchy service tests.
* [x] Lifecycle tests.

#### Web administration — deferred

- [ ] Build Desk administration routes.
- [ ] Build Desk hierarchy/tree view.
- [ ] Build create and edit forms.
- [ ] Add Desk move workflow.
- [ ] Add activation, deactivation and archival actions.
- [ ] Add Desk detail view.
- [ ] Add permissions and Desk-scope management.
- [ ] Add HTMX interactions.
- [ ] Add route and UI tests.

#### Operational interface — future

- [ ] Add active Desk selection and working context.
- [ ] Add Desk dashboard.
- [ ] Add Desk Activity Stream.
- [ ] Add Desk Operational Log.
- [ ] Add Desk-scoped notifications and work queues.

---

### 7.2 Event Journal

The Event Journal is the immutable operational record for Response Connect. Every significant occurrence within the platform is recorded as a Journal Entry, providing a complete audit and operational timeline across all modules.

#### Architecture

- [x] Write Event Journal and Operational Model chapter.
- [x] Write Event Journal Data Model chapter.
- [x] Finalise Journal terminology and package structure.
- [x] Define the Journal platform architecture.
- [x] Define the Journal Reference architecture.
- [x] Introduce the public `JournalService` API.

#### Core Platform

- [x] Create the Journal package.
- [x] Implement Journal constants and reference data.
- [x] Implement Journal exceptions.
- [x] Implement immutable Journal commands.
- [x] Implement Journal validators.
- [x] Implement the Journal Entry model.
- [x] Implement the Journal Reference model.
- [x] Implement Journal database migrations.
- [x] Implement the Journal Reference service.
- [x] Implement the Journal Entry service.
- [x] Implement the public `JournalService`.
- [x] Support actor, subject, context and Desk relationships.
- [ ] Implement the Journal query service.
- [ ] Integrate Journal recording throughout platform modules.

#### Testing

- [x] Reference data tests.
- [x] Command tests.
- [x] Validator tests.
- [x] Journal Entry model tests.
- [x] Journal Reference model tests.
- [x] Journal Reference service tests.
- [x] Journal Entry service tests.
- [x] Public Journal service tests.
- [ ] Query service tests.
- [ ] Public API architecture tests.

#### Future Journal Features

- [ ] Correlation IDs.
- [ ] Causation IDs.
- [ ] Event classifications.
- [ ] Visibility model.
- [ ] Severity model.
- [ ] Source model.
- [ ] Structured metadata.
- [ ] Historical display snapshots.
- [ ] Timeline projection API.
- [ ] Full-text Journal search.
- [ ] Event retention and archival policies.

#### Platform Integration

- [ ] Integrate Desks with `JournalService`.
- [ ] Integrate Workforce module.
- [ ] Integrate Fleet module.
- [ ] Integrate Event Medical module.
- [ ] Integrate Patient Transport module.
- [ ] Integrate Documents module.
- [ ] Integrate Notifications module.

---

### 7.3 Lifecycle Framework

* [ ] Define lifecycle architecture.
* [ ] Lifecycle commands.
* [ ] Lifecycle services.
* [ ] Lifecycle validation.
* [ ] Lifecycle transitions.
* [ ] Lifecycle events.
* [ ] Transaction integration.
* [ ] Tests.

---

### 7.4 Notifications

* [ ] Notification architecture.
* [ ] Notification model.
* [ ] Event-driven notification engine.
* [ ] Delivery framework.
* [ ] Retry handling.
* [ ] Tests.

---

### 7.5 Activity Streams

* [ ] Subject activity stream.
* [ ] Context activity stream.
* [ ] Desk activity stream.
* [ ] Actor activity stream.
* [ ] Correlation view.
* [ ] Operational Log.
* [ ] Audit Log.
* [ ] Security Log.
* [ ] Timeline rendering.

---

### 7.6 Platform Hardening (Remaining)

These items were intentionally deferred and should be completed during Phase 7.

#### Exceptions

* [ ] Review Email exception hierarchy.
* [ ] Review Jobs exception hierarchy.
* [ ] Review Location exception hierarchy.
* [ ] Ensure public services do not leak provider exceptions.
* [ ] Ensure public services do not leak raw persistence exceptions.

#### Logging

* [ ] Review platform logging conventions.
* [ ] Standardise structured logging.
* [ ] Review audit logging integration.

#### Public APIs

* [ ] Review remaining public exports.
* [ ] Review service naming consistency.
* [ ] Review transaction boundaries.
* [ ] Review package documentation.

---

### 8.1 Desk → Journal Integration

- [x] Add Desk Journal event-code definitions.
- [x] Inject the public `JournalService` into `DeskService`.
- [x] Record `desk.created`.
- [x] Record `desk.updated`.
- [x] Capture structured update metadata.
- [x] Ignore no-op updates.
- [x] Record `desk.moved`.
- [x] Capture previous and current parent metadata.
- [x] Make Desk mutations and Journal recording atomic.
- [ ] 🚧 Record Desk lifecycle transitions.
- [ ] Record processing-policy changes.

---

# Future Roadmap

## Phase 8 – Operational Modules

The following modules will be built on the shared operational platform.

### Event Medical

* Incidents
* Deployments
* Resources
* CAD
* Medical Records
* Event Planning

### Patient Transport

* Journeys
* Bookings
* Dispatch
* Scheduling
* Vehicles
* Crews

### Workforce

* Staff
* Availability
* Shifts
* Qualifications
* Competencies
* Mandatory Training

### Fleet

* Vehicles
* Equipment
* Maintenance
* Defects
* Availability

### Clinical

* Clinical Governance
* Medicines
* Guidelines
* Competencies
* Audits

### Training

* Courses
* Qualifications
* Assessments
* Certificates

### Governance

* Policies
* Risk
* Incidents
* Compliance

---

## Phase 9 – Integration & Platform

* REST API
* External Integrations
* Mobile Support
* Reporting
* Dashboards
* Search
* Automation
* Analytics

---

# Completed Milestones

## Platform Foundation & Consolidation

Completed:

* Shared exception hierarchy.
* Reference Data framework.
* Files platform.
* Immutable command pattern.
* Public package APIs.
* Architecture fitness tests.
* Structured logging foundation.
* Exception architecture review.
* Built-in exception review.
* Password-reset exception refactor.
* Reference Data registry configuration hardening.
* Public export verification.
* Stable identifier architecture.
* Architecture documentation.
* README refresh.

---

## Architecture Handbook

Completed chapters:

* Chapter 1 – Architectural Overview
* Chapter 2 – Project Structure
* Chapter 3 – Reference Data
* Chapter 4 – Files
* Chapter 5 – Public APIs
* Chapter 6 – Stable Identifiers
* Chapter 7 – Logging
* Chapter 8 – Exception Hierarchy
* Chapter 9 – Event Journal and Operational Model

---

## Testing

Current automated test suite:

* ✅ 138 tests passing

Future architectural additions should continue expanding architecture fitness tests alongside functional tests.

---

# Documentation

Core documents:

* README.md
* ROADMAP.md
* Architecture Handbook
* Decision Records
* Developer Guides (planned)

Architecture remains the authoritative source for design decisions.

---

# Working Agreement

For every development task:

1. Review this roadmap.
2. Select the next active task.
3. Complete implementation.
4. Add or update automated tests.
5. Update architecture documentation if required.
6. Update this roadmap.
7. Commit and push changes.

This roadmap is the authoritative development plan for Response Connect and should always reflect the current state of the project.
