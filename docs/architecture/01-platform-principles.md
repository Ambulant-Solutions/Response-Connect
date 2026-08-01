# Platform Principles

## 1. Platform before features

Response Connect should be developed as a reusable operational platform rather than a collection of unrelated features.

When functionality could be useful to multiple modules, it should normally be implemented as a shared platform capability.

Examples include:

* file management;
* audit logging;
* catalogue management;
* notifications;
* workflows;
* reference data;
* searching;
* reporting;
* reusable UI components.

A business module should not implement its own version of an existing platform capability.

## 2. Capabilities rather than isolated features

Development should focus on reusable capabilities.

For example, file management is not solely a feature of mandatory training. It is a capability used by:

* competencies;
* qualifications;
* vehicles;
* equipment;
* incidents;
* the document library;
* policies and procedures;
* communications;
* organisational records.

This approach reduces duplication and makes future modules easier to implement.

## 3. One approved way to perform each common task

The project should provide one clearly supported implementation pattern for each shared operation.

Examples include:

* one file manager;
* one audit service;
* one notification service;
* one catalogue pattern;
* one approach to HTMX forms;
* one permission system;
* one reference-data seeding mechanism.

Competing implementations should not be introduced without an explicit architecture decision.

Consistency is preferred over local cleverness.

## 4. Business modules do not access infrastructure directly

Business modules must not depend directly on infrastructure libraries or services.

Examples:

* routes must not import `boto3`;
* training services must not know whether files are stored in MinIO or Amazon S3;
* business modules must not connect directly to Redis;
* routes must not construct Celery messages manually when a platform task service exists;
* modules must not implement their own outbound email transport.

Infrastructure access should be provided through stable platform services.

## 5. Modules own their business logic

Each module owns its models, rules and workflows.

A module should not manipulate another module's records directly merely because the relevant SQLAlchemy model is importable.

Cross-module operations should use a documented service interface.

For example:

```python
competency_service.assign_competency(...)
```

is preferred to:

```python
db.session.add(CompetencyRecord(...))
```

from an unrelated module.

This preserves module boundaries and allows internal implementations to evolve.

## 6. No business logic in routes

Routes should:

1. receive and validate request-level input;
2. perform authentication and permission checks;
3. call an application service;
4. translate known application exceptions into HTTP responses;
5. return a template, redirect or structured response.

Routes should not contain substantial business rules, database workflows or infrastructure operations.

Business behaviour must remain testable without constructing an HTTP request.

## 7. Configuration before hard-coding

Organisations should be able to adapt Response Connect without modifying Python source code.

Configurable concepts should normally use catalogues or settings with stable internal codes.

Examples include:

* file types;
* competency types;
* clinical grades;
* vehicle types;
* employment types;
* locations;
* document categories;
* statuses;
* icons and display colours.

Configuration must not compromise the integrity of application rules. Values used by business logic should have stable codes that cannot be casually renamed.

## 8. Stable codes and editable labels

Reference and catalogue records should separate machine identity from display text.

For example:

```text
code: mandatory_training
name: Statutory and Mandatory Training
```

Application logic depends on `code`.

Users may be permitted to change `name`, description, icon, colour and ordering.

Stable codes make upgrades and reference-data synchronisation reliable.

## 9. Uploaded files are immutable

A stored file object must never be overwritten with different contents.

Replacing a document creates:

* a new object-storage key;
* a new `FileObject`;
* where appropriate, a new version record.

Immutability preserves:

* SHA-256 integrity;
* reliable audit trails;
* historic evidence;
* version rollback;
* approval history;
* retention enforcement.

A display record may point to a newer current version, but the earlier object remains unchanged until an authorised retention or purge process removes it.

## 10. Significant actions are audited

Important user and system actions should produce structured audit events.

Examples include:

* creation;
* editing;
* deletion;
* restoration;
* file upload;
* file download;
* approval;
* rejection;
* status changes;
* permission changes;
* assignment and removal of competencies.

Audit logging should be implemented through a shared service rather than ad hoc text messages.

Sensitive data must not be copied unnecessarily into audit payloads.

## 11. Upgrade safety is a primary requirement

A normal installation should be able to update Response Connect without losing local configuration or records.

The expected upgrade process should remain approximately:

```bash
git pull
docker compose up -d --build
docker compose exec web flask db upgrade
```

Application upgrades must preserve:

* locally edited catalogue labels;
* organisation settings;
* permissions and role assignments;
* branding;
* workflows;
* document histories;
* operational data.

Reference-data updates must use stable codes and must not blindly replace local customisations.

## 12. Database changes use migrations

All database schema changes must be represented by Alembic migrations through Flask-Migrate.

Production startup must not depend on calling `db.create_all()`.

Generated migrations must be inspected before application.

A migration must not contain unexplained changes to unrelated tables.

## 13. UUID primary keys

Domain and platform records should use UUID primary keys unless a documented reason supports another choice.

UUIDs:

* avoid exposing sequential record counts;
* are suitable for object keys and external references;
* reduce collision risk between imported datasets;
* support future integration and distributed workflows.

Small internal association or sequence tables may use another key strategy where justified.

## 14. Timezone-aware timestamps

Stored timestamps should be timezone-aware.

System-generated timestamps should represent UTC at the database and application layers.

Display conversion should happen using installation or user timezone settings.

Naive timestamps should not be introduced into new models.

## 15. Application exceptions hide third-party details

Platform and business services should raise application-defined exceptions.

Routes and calling modules should not need to understand:

* `botocore` exceptions;
* raw SQLAlchemy exceptions;
* Redis client errors;
* SMTP transport exceptions;
* provider-specific API errors.

Original exceptions should be retained through exception chaining and appropriate logging.

## 16. Asynchronous tasks are idempotent

A task must remain safe when:

* delivered more than once;
* retried after partial failure;
* restarted following worker failure;
* executed after another worker has already completed it.

Tasks such as thumbnail generation, reference-data synchronisation and virus scanning should check existing state before creating duplicate results.

External side effects, particularly email and SMS delivery, require explicit idempotency controls.

## 17. Self-hosting is a first-class deployment model

Response Connect must remain practical to deploy through Docker on infrastructure controlled by the installation owner.

Core functionality must not require a proprietary hosted service.

External services may be supported as optional alternatives where they use documented platform interfaces.

A default installation should remain understandable and operable by a technically capable system administrator without specialist cloud infrastructure.

## 18. Open-source and mature technology are preferred

Technology selection should prioritise:

1. reliability;
2. maintainability;
3. active support;
4. genuine open-source availability;
5. self-hosting suitability;
6. interoperability;
7. long-term stability.

Novelty is not itself a benefit.

The existing use of Flask, PostgreSQL, HTMX, Redis, Celery, Docker and S3-compatible storage reflects this principle.

## 19. Security is enforced at the application boundary

Possession of a database identifier or object key must never grant access by itself.

Routes must perform:

* authentication;
* permission checks;
* ownership or scope checks;
* state checks, such as deleted or quarantined status.

S3 credentials must never be supplied to end users.

Sensitive file downloads are streamed through authorised Flask routes.

## 20. Tests are part of implementation

A feature is not complete when its code appears to work manually.

New capabilities should include tests covering:

* successful behaviour;
* validation failures;
* permission failures;
* missing records;
* relevant state transitions;
* retry or compensation behaviour;
* significant regression risks.

Tests should focus primarily on public service behaviour rather than internal implementation details.

## 21. Consistency is more valuable than local optimisation

Response Connect should optimise primarily for:

1. reliability;
2. maintainability;
3. configurability;
4. consistency;
5. extensibility.

Performance remains important, but premature optimisation should not weaken the architecture or create multiple implementation patterns.

Optimisation should be evidence-led and should preserve the public platform interfaces wherever practical.

## 22. Reusable user-interface patterns

Common interface elements should be built as reusable components.

Examples include:

* catalogue lists;
* forms;
* confirmation dialogs;
* file pickers;
* activity timelines;
* status badges;
* empty states;
* search panels;
* pagination;
* HTMX error responses.

A consistent UI reduces training requirements and prevents each module from developing its own interaction model.

## 23. Accessibility is a requirement

New user interfaces should be:

* keyboard accessible;
* understandable without relying solely on colour;
* correctly labelled for assistive technologies;
* structured with semantic HTML;
* usable at common responsive breakpoints;
* explicit about loading, success and failure states.

Accessibility should be part of implementation rather than a future cosmetic pass.

## 24. Local customisation must remain distinguishable from system data

System-provided reference data and organisation-created records must be distinguishable.

Catalogue models will normally include fields such as:

```text
is_system
is_active
```

System records may permit editing of display fields while restricting changes to stable codes or deletion.

Organisation-created records should remain unaffected by future system seed updates unless explicitly migrated.

## 25. Architecture changes are intentional and documented

Significant departures from established patterns require an explicit architecture decision.

A decision should identify:

* the problem;
* the selected approach;
* alternatives considered;
* expected benefits;
* known trade-offs;
* migration implications;
* any superseded guidance.

Architecture must not drift through isolated convenience changes.

# Non-negotiable rules

The following rules apply unless superseded by a documented architecture decision:

1. Business modules do not import infrastructure clients directly.
2. Business logic does not live in routes.
3. Modules do not manipulate another module's records without a service boundary.
4. Uploaded objects are immutable.
5. Significant actions are audited.
6. Reference records use stable internal codes.
7. Database changes use Alembic migrations.
8. New modules include tests.
9. Asynchronous tasks are idempotent.
10. Self-hosted deployment remains fully supported.
11. Sensitive file downloads pass through authorised application routes.
12. A shared capability must not be reimplemented independently by a business module.

# Definition of success

The architecture is working successfully when a contributor unfamiliar with the codebase can:

1. identify the correct module for a change;
2. find an established pattern for the capability;
3. implement the change without duplicating platform behaviour;
4. add appropriate permissions, audit events and tests;
5. understand why the pattern exists;
6. submit a change that feels consistent with the rest of Response Connect.
