# Response Connect Developer Architecture Guide

## Purpose

This guide defines the architectural principles, shared vocabulary, conventions and approved implementation patterns for Response Connect.

It is intended for:

* core maintainers;
* external contributors;
* organisations developing local extensions;
* developers using AI-assisted coding tools;
* reviewers assessing proposed changes.

The guide explains not only how Response Connect is structured, but why significant architectural decisions have been made.

New modules and major changes should follow this guide unless a later Architecture Decision Record explicitly replaces an existing convention.

## Project vision

Response Connect is an open-source operational management platform for emergency response, healthcare and public safety organisations.

It provides reusable capabilities for managing:

* people;
* competencies and compliance;
* files and documents;
* organisational knowledge;
* locations;
* assets and equipment;
* vehicles;
* operational activity;
* workflows;
* notifications;
* audit records;
* reports and dashboards.

Ambulance and healthcare functionality is an important initial use case, but the core platform should remain reusable by other emergency response and public safety organisations.

## Guiding statement

> Response Connect is designed to outlive its original authors. Every architectural decision should make the project easier for the next contributor to understand, extend and maintain.

## Engineering motto

> Build capabilities once. Reuse them everywhere.

## Current architecture chapters

The following chapters have been created and form the current architecture baseline.

1. [Platform Principles](01-platform-principles.md)
   Defines the project’s non-negotiable architectural principles, including platform-first development, module ownership, service boundaries, immutable files, upgrade safety and self-hosting.

2. [Project Structure and Module Boundaries](02-project-structure.md)
   Defines the application layers, package organisation, module ownership, dependency direction, naming conventions and cross-module access rules.

3. [Module Conventions](03-module-conventions.md)
   Defines how modules should be structured, registered, tested, documented and reviewed, including permissions, audit integration, reference data, HTMX behaviour and the Definition of Done.

4. [Service-Layer Conventions](04-service-layer-conventions.md)
   Defines service responsibilities, transaction ownership, dependency injection, exceptions, validation, compensation, idempotency and testing expectations.

5. [Core Concepts and Shared Vocabulary](05-core-concepts.md)
   Defines the shared terminology used throughout the project, including files, documents, versions, evidence, catalogues, reference data, people, user accounts, competencies, workflows, audit events and notifications.

6. [Catalogue Framework](06-catalogue-framework.md)

7. [Platform Overview and Operational Architecture](07-platform-overview.md)

8. [Error Handling Architecture](08-exception-hierarchy.md)

9. [Event Journal and Operational Model](09-event-journal-and-operational-model.md)

## Planned architecture chapters

The following chapters remain planned and will be written as the corresponding platform capabilities are designed and implemented.

10. Competency Framework
11. Workflow and Notifications
12. UI and HTMX Patterns
13. Testing Standards
14. Coding Standards
15. Architecture Decisions
16. Platform Roadmap

The numbering may be extended as new platform capabilities require dedicated guidance.

## Recommended reading order

New contributors should read the current chapters in order:

```text
01 Platform Principles
        ↓
02 Project Structure
        ↓
03 Module Conventions
        ↓
04 Service-Layer Conventions
        ↓
05 Core Concepts
```

Together, these chapters define:

* what the project optimises for;
* where code belongs;
* what each module owns;
* how business workflows should be implemented;
* which terms contributors should use consistently.

Later chapters will build on this baseline rather than redefining it.

## Authority of this guide

The architecture guide is the default technical authority for the project.

Where code and documentation disagree:

1. determine whether the code reflects an intentional newer decision;
2. record that decision if it is intentional;
3. update the guide and affected tests;
4. otherwise, bring the code back into alignment with the documented architecture.

Architecture must not change silently through isolated implementation choices.

## Architecture Decision Records

The handbook describes the architecture as it currently stands.

Significant individual decisions should also be recorded as immutable Architecture Decision Records in a future ADR directory, for example:

```text
docs/
├── architecture/
└── adrs/
    ├── 0001-platform-first.md
    ├── 0002-s3-compatible-storage.md
    ├── 0003-stream-downloads-through-flask.md
    ├── 0004-immutable-file-objects.md
    └── 0005-service-layer-architecture.md
```

Each ADR should record:

* **Decision** — what was chosen.
* **Context** — why the decision was needed.
* **Alternatives considered** — other credible options.
* **Consequences** — benefits, limitations and future implications.
* **Status** — proposed, accepted, superseded or deprecated.

Accepted ADRs should not be rewritten to hide architectural history. A later change should be recorded in a new ADR that supersedes the earlier one.

## Relationship between the handbook and ADRs

The architecture guide explains:

> How Response Connect should be built today.

Architecture Decision Records explain:

> Why a significant decision was made and how the architecture reached its current state.

Both are required for long-term maintainability.

## Capability development process

Major platform capabilities should be developed through a consistent sequence:

1. **Architecture** — establish ownership, boundaries and design.
2. **Handbook** — document the approved conventions.
3. **Architecture decision** — record significant choices.
4. **Implementation** — build the capability through public services.
5. **Tests** — prove expected behaviour and failure handling.
6. **Documentation** — explain contributor and operational use.
7. **Review** — confirm the capability strengthens the platform.

This process should be applied to:

* catalogues;
* files;
* audit;
* reference data;
* competencies;
* workflows;
* notifications;
* search;
* reporting;
* reusable UI patterns.

## Design review questions

Before introducing a significant change, contributors and reviewers should ask:

1. Does this capability already exist?
2. Which module owns the concept?
3. Could another module reuse the proposed functionality?
4. Does this introduce a second way to perform an existing operation?
5. Does business logic remain inside services?
6. Are module boundaries preserved?
7. Are stable codes used where appropriate?
8. Is upgrade safety maintained?
9. Is self-hosted deployment still straightforward?
10. Are significant actions audited?
11. Can asynchronous behaviour be retried safely?
12. Can another contributor understand and extend the implementation?
13. Will the design still make sense after several years of development?
14. Does the change strengthen the platform?

## If you are unsure

When the correct design is unclear:

* choose the simpler implementation;
* reuse an existing capability;
* keep business logic in services;
* preserve module ownership;
* prefer explicit behaviour;
* use stable internal codes;
* protect upgrade safety;
* consider whether another module will need the same capability;
* avoid introducing a second pattern;
* document genuinely new architectural decisions.

## Change process

Changes to the architecture guide should be reviewed with the same care as production code.

A proposed architecture change should answer:

* What problem is being solved?
* Which module owns the capability?
* Does an existing service already address the requirement?
* Does the proposal introduce a competing implementation pattern?
* Can the result be reused elsewhere?
* Does it preserve local configuration during upgrades?
* Does it remain suitable for self-hosted installations?
* Does it add avoidable operational complexity?
* Is the behaviour testable?
* Is an ADR required?

## Living documentation

This is a living guide.

It should evolve as Response Connect grows, but established patterns must not be changed casually.

Stability, reliability and consistency are more valuable than repeatedly adopting newer or more fashionable approaches.

Documentation is part of implementation. A significant capability is not complete until the architecture guide, relevant ADRs, tests and developer documentation accurately describe it.
