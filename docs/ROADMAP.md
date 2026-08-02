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

**Desk Hierarchy Platform**

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

---

# Active Roadmap

## Phase 7 – Operational Platform Foundation

### 7.1 Desk Platform

The Desk platform defines operational ownership and scope throughout Response Connect.

#### Architecture

* [ ] Write detailed Desk architecture chapter.
* [ ] Finalise Desk data model.
* [ ] Define Desk lifecycle.
* [ ] Define Desk permission model.

#### Core Platform

* [X] Create Desk package.
* [ ] Implement Desk model.
* [ ] Implement Desk service.
* [ ] Implement Desk query service.
* [X] Implement Desk validators.
* [X] Implement Desk commands.
* [X] Implement Desk exceptions.
* [ ] Create Desk migration.

#### Hierarchy

* [ ] Root Desk.
* [ ] Parent/child hierarchy.
* [ ] Prevent hierarchy cycles.
* [ ] Prevent invalid parent assignment.
* [ ] Desk activation/deactivation.
* [ ] Desk movement.
* [ ] Historical Desk preservation.

#### Testing

* [ ] Model tests.
* [ ] Service tests.
* [ ] Query tests.
* [ ] Architecture tests.

---

### 7.2 Event Journal

The Event Journal records immutable Journal Entries describing operational occurrences.

#### Architecture

* [x] Write Event Journal and Operational Model chapter.
* [x] Write Event Journal data model chapter.
* [x] Finalise Journal terminology and package naming.
* [x] Define initial Journal schema.
* [x] Define classification and metadata models

#### Core Platform

* [ ] Create Journal package.
* [ ] Implement Journal Entry model.
* [ ] Implement recording commands.
* [ ] Implement recording service.
* [ ] Implement query service.
* [ ] Implement validators.
* [ ] Implement exceptions.
* [ ] Create migration.

#### Journal Features

* [ ] Correlation IDs.
* [ ] Causation IDs.
* [ ] Event classifications.
* [ ] Visibility model.
* [ ] Severity model.
* [ ] Source model.
* [ ] Structured metadata.
* [ ] Historical display snapshots.

#### Testing

* [ ] Model tests.
* [ ] Service tests.
* [ ] Query tests.
* [ ] Architecture tests.

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
