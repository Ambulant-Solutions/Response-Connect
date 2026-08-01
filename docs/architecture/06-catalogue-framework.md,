# Catalogue Framework

## Purpose

This document defines the shared architecture for configurable catalogue records in Response Connect.

Catalogues provide stable, upgrade-safe reference structures for concepts such as:

* file types;
* location types;
* competency types;
* competency categories;
* employment types;
* vehicle types;
* document categories;
* incident classifications;
* status reasons;
* equipment types.

The Catalogue Framework exists to prevent every module from implementing its own lookup-table models, administration services, forms, routes and templates.

The framework should provide one consistent pattern while allowing individual catalogues to define their own additional rules and relationships.

# What is a catalogue?

A catalogue is a configurable collection of records used to classify, constrain or describe domain behaviour.

A catalogue record normally has:

* a UUID primary key;
* a stable internal code;
* a display name;
* an optional description;
* an icon;
* a display colour;
* a sort order;
* an active state;
* a system or custom ownership state;
* created and updated timestamps.

Examples include:

```text
File Types
├── mandatory_training
├── profile_photo
├── qualification
└── vehicle_photo
```

```text
Location Types
├── site
├── department
├── room
└── store
```

```text
Competency Categories
├── clinical_grade
├── qualification
├── mandatory_training
└── professional_registration
```

A catalogue is not simply any table containing names.

A record should use the Catalogue Framework when it represents configurable classification or behaviour shared by multiple domain records.

# Catalogue goals

The Catalogue Framework should provide:

* stable machine identifiers;
* editable user-facing labels;
* upgrade-safe system records;
* locally created custom records;
* consistent activation and deactivation;
* predictable sorting;
* reusable administration interfaces;
* common permission patterns;
* audit integration;
* repeatable reference-data synchronisation;
* consistent service APIs;
* reusable tests.

# Catalogue non-goals

The framework should not attempt to make every catalogue identical.

Some catalogues require additional domain-specific fields or relationships.

Examples include:

* file types have MIME-type and extension rules;
* location types have location capabilities;
* competency types have expiry and evidence rules;
* vehicle types may have operational classifications;
* document categories may form a hierarchy.

The shared framework provides common behaviour.

The owning module remains responsible for catalogue-specific business rules.

# Catalogue ownership

The generic Catalogue capability owns:

* common catalogue conventions;
* reusable service behaviour;
* stable-code protection;
* common activation and deactivation logic;
* generic query patterns;
* shared administration components;
* shared audit action conventions;
* reference-data integration patterns;
* catalogue test helpers.

The domain module owns:

* the concrete catalogue model;
* catalogue-specific fields;
* catalogue-specific validation;
* business meaning;
* relationships to domain records;
* catalogue-specific permissions where required;
* catalogue-specific seed definitions;
* any specialised administration UI.

For example, the Files module owns `FileType`.

The Catalogue Framework does not own the meaning of:

```text
mandatory_training
profile_photo
policy_document
```

It provides the common mechanisms used to manage those records.

# Shared catalogue fields

Concrete catalogue models should normally provide the following fields.

## `id`

A UUID primary key.

```python
id: Mapped[uuid.UUID]
```

Catalogue records must not use stable codes as primary keys.

UUIDs allow:

* safe relationships;
* local custom records;
* imports;
* external references;
* code changes without primary-key changes.

## `code`

A stable internal identifier.

Examples:

```text
mandatory_training
profile_photo
clinical_grade
rapid_response_vehicle
```

Codes should use lowercase snake_case.

The code:

* must be unique within its catalogue;
* must not depend on the display name;
* should normally be immutable after creation;
* is used by application logic and reference-data synchronisation;
* must not be silently changed through ordinary administration.

## `name`

The user-facing display name.

Examples:

```text
Mandatory Training Certificate
Profile Photograph
Clinical Grade
Rapid Response Vehicle
```

Names may normally be edited without affecting application logic.

Names should be unique within a catalogue where duplicate labels would be confusing.

Whether name uniqueness is case-sensitive should be defined consistently.

## `description`

Optional explanatory text.

Descriptions help administrators understand:

* intended use;
* constraints;
* operational meaning;
* differences between similar catalogue records.

Descriptions should not contain application-critical logic.

## `icon`

An Iconify icon identifier.

Response Connect currently uses the Tabler icon set through Iconify.

Examples:

```text
tabler:file-certificate
tabler:user-square-rounded
tabler:ambulance
tabler:map-pin
```

The field should store the complete icon identifier.

A safe module-specific default should be provided.

## `colour`

A display colour used in badges, catalogue lists and relevant visual indicators.

The stored format should be defined consistently, preferably as a hexadecimal colour:

```text
#0EA5A0
```

Colour must not be the only means of communicating state or meaning.

A catalogue-specific default should be provided.

## `sort_order`

An integer controlling default display order.

Sort order should:

* default to zero;
* be non-negative unless a specific catalogue requires otherwise;
* be followed by name or code as a stable secondary sort;
* not be used as a permanent machine identifier.

## `is_system`

Indicates whether Response Connect supplies and manages the stable identity of the record.

```text
is_system = true
```

System records:

* have protected codes;
* should normally not be physically deleted;
* may be updated through reference-data synchronisation;
* may allow local changes to selected display fields;
* should normally be deactivated when not used.

Custom records have:

```text
is_system = false
```

Custom records belong to the local installation and must not be overwritten by system synchronisation.

## `is_active`

Controls whether the record is available for new assignments or selections.

Inactive records:

* remain available for historical relationships;
* should be excluded from ordinary creation forms;
* should remain visible where existing records reference them;
* should not normally be physically deleted.

Activation is a lifecycle transition and should use a service method.

## `created_at`

A timezone-aware creation timestamp.

## `updated_at`

A timezone-aware last-update timestamp.

# Optional shared fields

Some catalogues may also need common optional fields.

## `is_default`

Marks a default choice where the domain requires one.

This field should only be added where default behaviour has a clear meaning.

The database should enforce any single-default constraint where practical.

## `is_selectable`

Distinguishes records available for direct selection from structural or grouping records.

This may be useful for hierarchical catalogues.

## `parent_id`

Supports hierarchy where categories may contain child records.

Hierarchy should not be added to all catalogues by default.

A catalogue should use parent relationships only when the domain genuinely requires them.

## `effective_from` and `effective_to`

Supports time-bound reference records.

This should be used only when historical effective dating is necessary.

Active state and effective dating are different concepts.

## `metadata`

Generic JSON metadata should not be added to the shared catalogue model by default.

Catalogue-specific behaviour should use explicit columns and relationships where practical.

Unstructured metadata tends to hide domain rules and weakens querying and validation.

# Shared model implementation

The initial framework should favour a reusable mixin rather than one universal catalogue table.

Different catalogues require:

* different tables;
* different relationships;
* different constraints;
* different lifecycle rules;
* different additional fields.

A mixin may provide common columns and helper properties.

A possible future structure is:

```python
class CatalogueRecordMixin:
    code: Mapped[str]
    name: Mapped[str]
    description: Mapped[str | None]
    icon: Mapped[str]
    colour: Mapped[str]
    sort_order: Mapped[int]
    is_system: Mapped[bool]
    is_active: Mapped[bool]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

Concrete models remain explicit:

```python
class FileType(
    CatalogueRecordMixin,
    db.Model,
):
    __tablename__ = "file_types"

    max_size_bytes: Mapped[int]
    category: Mapped[str]
```

This preserves database clarity while reducing repeated definitions.

# Why not use one universal catalogue table?

A single table such as:

```text
catalogue_records
```

with a `catalogue_name` discriminator would appear flexible but would create significant problems.

It would weaken:

* foreign-key clarity;
* catalogue-specific constraints;
* SQLAlchemy relationships;
* migration readability;
* database querying;
* domain ownership;
* type safety.

It would also encourage storing catalogue-specific behaviour in JSON fields.

Response Connect will use concrete catalogue tables with shared conventions and reusable services.

# Stable-code rules

Stable codes are central to the framework.

## Code format

Codes should:

* use lowercase snake_case;
* begin with a letter;
* contain only lowercase letters, numbers and underscores;
* be concise but descriptive;
* avoid organisation-specific branding in system records;
* remain suitable for long-term use.

A recommended validation pattern is:

```text
^[a-z][a-z0-9_]*$
```

## Code creation

Custom catalogue records require a code.

The administration interface may suggest a code based on the name, but the user must be able to review it before creation.

Once created, the code should normally become read-only.

## Code mutation

Ordinary service methods must not change stable codes.

A code change should require:

* a dedicated privileged migration or maintenance process;
* review of all code references;
* reference-data implications;
* audit recording;
* an architecture decision where the change affects system records.

## Code uniqueness

Codes must be unique within the catalogue.

Database constraints must enforce uniqueness.

Services should translate integrity errors into catalogue-specific duplicate-code exceptions.

## Code aliases

Code aliases should not be introduced initially.

Where a system code genuinely needs replacement, reference-data migration and explicit deprecation are preferable.

A future alias mechanism may be considered for integrations, but it should not weaken stable-code discipline.

# System and custom record ownership

System and custom records have different lifecycle rules.

## System records

System records are supplied by the project.

The system owns:

* the stable code;
* whether the record remains recognised by application logic;
* required structural relationships;
* fields explicitly documented as system-controlled.

The installation may own selected display fields, such as:

* name;
* description;
* icon;
* colour;
* sort order;
* active state.

The exact field ownership should be defined by the catalogue’s reference-data specification.

## Custom records

Custom records are created by local administrators.

The installation owns all editable fields.

Reference-data synchronisation must:

* leave custom records untouched;
* not reuse their codes;
* not convert them into system records silently;
* preserve their relationships.

## Reserved codes

System catalogue codes should be treated as reserved even if the related record is currently absent or deprecated.

A custom record must not be created using a reserved system code.

The Reference Data framework will define how reserved codes are registered and checked.

# Activation and deactivation

Catalogue records should normally be deactivated rather than deleted.

## Deactivation

Deactivation means:

* the record remains in the database;
* existing relationships remain valid;
* the record is excluded from ordinary new selections;
* historical pages can still display it;
* the action is audited.

A record referenced by active business data may still be deactivated unless the owning module defines a stronger restriction.

## Activation

Activation restores availability for new selection.

Activation should use an explicit service method and create an audit event.

## Query behaviour

Service methods should clearly distinguish:

```python
list_active()
list_all()
get_by_code(...)
get_active_by_code(...)
```

Ordinary form choices should use active records.

Historical record display must not fail merely because the related catalogue record is inactive.

# Deletion

Physical deletion should be exceptional.

## System records

System records must not be deleted through ordinary administration.

## Custom records

Custom records may only be deleted when:

* no domain records reference them;
* no audit or versioning requirement requires preservation;
* the owning module allows deletion;
* the action is authorised and audited.

Where a custom record has ever been used, deactivation will normally be preferable.

## Database behaviour

Foreign keys to catalogue records should normally use:

```text
ON DELETE RESTRICT
```

This prevents accidental loss of historical classification.

Cascade deletion should not normally be used for catalogue relationships.

# Catalogue service interface

The shared framework should provide reusable service behaviour while allowing concrete services to add domain methods.

A typical interface may include:

```python
class CatalogueService:
    def list_all(self) -> list[CatalogueRecord]:
        ...

    def list_active(self) -> list[CatalogueRecord]:
        ...

    def get(self, record_id: UUID) -> CatalogueRecord:
        ...

    def get_by_code(self, code: str) -> CatalogueRecord:
        ...

    def get_active_by_code(
        self,
        code: str,
    ) -> CatalogueRecord:
        ...

    def create_custom(
        self,
        *,
        code: str,
        name: str,
        description: str | None,
        icon: str,
        colour: str,
        sort_order: int,
        actor_id: UUID,
    ) -> CatalogueRecord:
        ...

    def update_display(
        self,
        record_id: UUID,
        *,
        name: str,
        description: str | None,
        icon: str,
        colour: str,
        sort_order: int,
        actor_id: UUID,
    ) -> CatalogueRecord:
        ...

    def activate(
        self,
        record_id: UUID,
        *,
        actor_id: UUID,
    ) -> CatalogueRecord:
        ...

    def deactivate(
        self,
        record_id: UUID,
        *,
        actor_id: UUID,
    ) -> CatalogueRecord:
        ...

    def delete_custom(
        self,
        record_id: UUID,
        *,
        actor_id: UUID,
    ) -> None:
        ...
```

Concrete services may extend the interface.

For example:

```python
class FileTypeService(CatalogueService):
    def replace_extension_rules(...):
        ...

    def replace_mime_type_rules(...):
        ...
```

# Generic service versus concrete services

The framework may provide a generic base service for common operations.

However, business modules should request concrete services:

```python
get_file_type_service()
get_location_type_service()
get_competency_type_service()
```

Avoid exposing a route that passes arbitrary model names into one generic service.

Concrete services preserve:

* type clarity;
* module ownership;
* specific validation;
* catalogue-specific permissions;
* readable audit events.

# Catalogue exceptions

The Catalogue Framework should define a common exception hierarchy.

Example:

```python
class CatalogueError(Exception):
    """Base exception for catalogue operations."""


class CatalogueRecordNotFoundError(CatalogueError):
    """Raised when a catalogue record cannot be found."""


class DuplicateCatalogueCodeError(CatalogueError):
    """Raised when a stable code is already in use."""


class DuplicateCatalogueNameError(CatalogueError):
    """Raised when a conflicting display name exists."""


class InvalidCatalogueCodeError(CatalogueError):
    """Raised when a stable code is malformed."""


class ProtectedSystemRecordError(CatalogueError):
    """Raised when a protected system operation is attempted."""


class CatalogueRecordInUseError(CatalogueError):
    """Raised when deletion is blocked by existing relationships."""


class CataloguePersistenceError(CatalogueError):
    """Raised when catalogue state cannot be persisted."""
```

Concrete modules may subclass or translate these into more specific exceptions.

# Transaction behaviour

Public catalogue mutation methods should normally own their database transaction.

A method should:

1. validate the requested transition;
2. update the record and related rule records;
3. create the audit event;
4. commit once;
5. roll back on failure;
6. raise an application exception.

Multi-step catalogue editing should not commit after every child-rule change.

For example, updating a `FileType` and replacing its extension and MIME rules should use one transaction.

# Audit integration

Significant catalogue actions must be audited.

Common action codes may include:

```text
catalogue.record_created
catalogue.record_updated
catalogue.record_activated
catalogue.record_deactivated
catalogue.record_deleted
catalogue.reference_data_synced
```

Where domain meaning matters, use more specific action codes:

```text
file_type.created
file_type.updated
file_type.deactivated
location_type.updated
competency_type.activated
```

Audit events should include:

* catalogue name or entity type;
* record UUID;
* stable code;
* actor;
* meaningful changed fields;
* system or custom status;
* outcome.

Stable codes should not be recorded as changed through ordinary updates because they are immutable.

# Permissions

Each catalogue administration area should define stable permission codes.

A common pattern is:

```text
{module}:view_{catalogue}
{module}:manage_{catalogue}
```

Examples:

```text
files:view_types
files:manage_types
locations:view_types
locations:manage_types
competencies:view_types
competencies:manage_types
```

Where viewing is part of normal module access, a separate view-types permission may be unnecessary.

Permission design should reflect actual user responsibilities rather than mechanically creating permissions for every route.

The framework should not require one universal permission capable of editing every catalogue.

# Administration interface

Catalogue administration should use one consistent interaction pattern.

A standard catalogue page should provide:

* page title and explanation;
* search;
* active/inactive filter;
* system/custom filter where useful;
* sortable or ordered record list;
* status badges;
* system/custom indicators;
* add-custom-record action;
* edit action;
* activate/deactivate action;
* protected deletion action where supported;
* clear empty states;
* HTMX-enhanced updates;
* full-page fallback.

A typical layout is:

```text
┌─────────────────────────────────────────────────────┐
│ File Types                                  [+ New] │
│ Configure upload categories and validation rules.  │
├─────────────────────────────────────────────────────┤
│ Search...       Status: Active      Source: All    │
├─────────────────────────────────────────────────────┤
│ Icon │ Name │ Code │ Source │ Status │ Actions     │
├─────────────────────────────────────────────────────┤
│  📄  │ ...  │ ...  │ System │ Active │ Edit       │
└─────────────────────────────────────────────────────┘
```

# Generic UI components

The framework should provide reusable templates for:

* catalogue page header;
* filter bar;
* catalogue table shell;
* record row status badges;
* system/custom badge;
* enable/disable confirmation;
* form field groups;
* empty state;
* pagination where needed;
* validation summary.

Concrete catalogues may supply custom columns and form sections.

The framework should not force complex catalogue-specific relationships into a generic key-value editor.

# HTMX behaviour

Catalogue pages should support both normal requests and HTMX partial updates.

Recommended interactions include:

* search and filters update the table;
* create and edit forms load into a modal or drawer;
* successful saves update the relevant row or table;
* activation changes update status without a full reload;
* server-side validation returns the form with status `422`;
* redirects remain available for non-HTMX requests.

The service and validation behaviour must remain identical for both request types.

# Forms

The shared framework may provide common form fields or mixins for:

* code;
* name;
* description;
* icon;
* colour;
* sort order;
* active state.

System records should normally render the code field as read-only.

Custom record creation should allow code entry.

Editing an existing custom record should also treat the code as read-only unless a dedicated maintenance operation exists.

Catalogue-specific forms may extend the common fields.

For example, a `FileTypeForm` may include:

* category;
* maximum size;
* scanning requirement;
* thumbnail requirement;
* allowed extensions;
* allowed MIME types.

# Search

Catalogue search should normally match:

* code;
* name;
* description.

Search should be:

* case-insensitive;
* server-side;
* compatible with HTMX;
* deterministic;
* safely parameterised.

Small catalogues may return all records without pagination, but the common service should not assume every catalogue will remain small.

# Sorting

Default catalogue ordering should normally be:

```text
sort_order ASC
name ASC
```

Where active records should appear first, the UI may apply:

```text
is_active DESC
sort_order ASC
name ASC
```

The exact order should be explicit in the concrete service.

Manual drag-and-drop ordering may be added later but is not required for the initial framework.

# Validation

Common validation should include:

* valid stable-code format;
* unique code;
* required name;
* name length;
* icon format;
* valid colour format;
* non-negative sort order;
* protected system fields;
* valid lifecycle transition.

Catalogue-specific validation belongs to the concrete module.

Examples include:

* file-type maximum size must be positive;
* competency validity period must be valid;
* a location type may require at least one capability;
* a vehicle type may require a category.

# Names and uniqueness

Catalogue names should normally be unique within the catalogue.

Case-insensitive uniqueness is preferable where the database supports it cleanly.

If database-level case-insensitive uniqueness is not implemented initially, services should check normalised names and database constraints should still protect exact duplicates.

The architecture should avoid allowing records that appear identical to users.

# Reference-data integration

System catalogue records are managed through the Reference Data framework.

Each system record definition should include:

* stable code;
* default display name;
* default description;
* default icon;
* default colour;
* default sort order;
* active or deprecated state;
* system-owned fields;
* locally editable fields;
* catalogue-specific rules.

Synchronisation should:

1. find by stable code;
2. create missing system records;
3. mark the record as system-owned;
4. update only system-owned fields;
5. preserve locally owned fields;
6. leave custom records unchanged;
7. handle deprecated records explicitly;
8. record the synchronisation outcome.

System records must not be seeded merely because an administrator opens the catalogue page.

# Deprecation

Reference catalogue records may become deprecated.

Deprecation should not normally delete them.

A deprecated system record may be:

* marked inactive;
* retained for historical references;
* assigned a replacement code in reference-data definitions;
* hidden from new selections;
* documented in release notes.

Automatic migration of existing domain records to a replacement should only occur when the semantic equivalence is certain.

# Catalogue relationships

Catalogues may have child rule records or many-to-many relationships.

Examples include:

```text
FileType
├── FileExtensionRule
└── FileMimeTypeRule
```

```text
LocationType
└── LocationCapability
```

```text
CompetencyType
├── RequiredEvidenceType
└── RenewalRule
```

Child rules should:

* have explicit tables;
* use foreign keys;
* be managed by the owning catalogue service;
* participate in the same transaction as the parent update;
* be included in audit summaries where meaningful.

Comma-separated strings should not be used for independently manageable rules.

# Catalogue inheritance

The initial framework will not support catalogue inheritance.

A record should not automatically inherit arbitrary fields from another catalogue record unless the domain model clearly requires it.

Where grouping is needed, use explicit categories or relationships.

Inheritance can create unclear effective rules and difficult administration.

# Catalogue snapshots and historical display

Business records should generally retain foreign keys to catalogue records rather than copying all catalogue display fields.

This allows display-label updates to appear consistently.

However, some legally or operationally significant records may require snapshots of selected values.

Examples include:

* the exact grade label shown on an issued document;
* the version of a requirement used during a compliance decision;
* an external report that must remain historically fixed.

Snapshot behaviour belongs to the owning business module and should be explicit.

# Import and export

Generic catalogue import and export may be added later.

An eventual export format should include:

* stable code;
* display fields;
* source status;
* active state;
* catalogue-specific rules.

Import must not allow an ordinary administrator to overwrite protected system identities without validation.

Initial implementation should focus on reliable in-application administration and reference-data synchronisation.

# Caching

Catalogue records are likely to be read frequently.

Caching should not be introduced until query behaviour is measured.

When caching is added, invalidation must occur after:

* create;
* update;
* activate;
* deactivate;
* reference-data synchronisation.

The service interface should allow caching to be added without changing callers.

# Generic repository abstraction

The Catalogue Framework will not introduce a generic repository layer solely to wrap SQLAlchemy CRUD.

The service should express catalogue behaviour directly.

Reusable query and mutation helpers are appropriate where they reduce duplication, but they must not obscure:

* model ownership;
* transaction behaviour;
* catalogue-specific validation;
* exception semantics.

# Initial implementation sequence

The Catalogue Framework should be implemented incrementally.

## Phase 1 — Common backend conventions

* common catalogue mixin;
* common exceptions;
* shared stable-code validation;
* shared service base or helpers;
* common query behaviour;
* lifecycle methods;
* test helpers.

## Phase 2 — First concrete catalogue

Implement `FileType` using the framework.

This will validate support for:

* common catalogue fields;
* system/custom ownership;
* child extension rules;
* child MIME-type rules;
* additional processing settings;
* transaction-safe editing;
* reference data.

## Phase 3 — Shared administration UI

Build reusable:

* list layout;
* filters;
* table shell;
* badges;
* forms;
* HTMX responses;
* activation confirmation;
* empty states.

## Phase 4 — Apply to another catalogue

Adapt an existing catalogue, likely Location Types, where doing so does not destabilise working behaviour.

This validates that the framework is genuinely reusable rather than tailored only to File Types.

## Phase 5 — Reference-data integration

Connect catalogue system records to the shared Reference Data framework.

# `FileType` as the reference implementation

`FileType` should become the first full implementation of the Catalogue Framework.

It is a suitable reference because it requires both common and specialised behaviour.

Common behaviour includes:

* stable code;
* editable label;
* description;
* icon;
* colour;
* active state;
* system/custom state;
* sort order.

Specialised behaviour includes:

* technical file category;
* maximum file size;
* allowed extensions;
* allowed MIME types;
* scan requirements;
* thumbnail requirements;
* preview behaviour.

The File Types administration screen should demonstrate the preferred pattern for future catalogues.

# Migration of existing catalogues

Existing catalogues should not be rewritten merely to achieve superficial uniformity.

A migration to the shared framework should occur when:

* the common implementation is stable;
* tests protect existing behaviour;
* the change simplifies future maintenance;
* data migration is safe;
* the UI remains consistent.

Location Types may become the second implementation, but their capability relationships and existing screens must be preserved.

# Testing requirements

The shared framework should include tests for common behaviour.

## Model tests

* code uniqueness;
* name constraints;
* sort-order checks;
* system/custom state;
* active state;
* timestamp behaviour.

## Service tests

* list active records;
* get by UUID;
* get by code;
* create custom record;
* reject invalid code;
* reject duplicate code;
* update editable fields;
* protect stable code;
* activate;
* deactivate;
* block system deletion;
* delete unused custom record;
* block deletion when in use;
* rollback on persistence failure;
* audit integration.

## Reference-data tests

* create missing system record;
* repeat synchronisation safely;
* preserve custom records;
* preserve locally owned display fields;
* update system-owned fields;
* handle deprecated records;
* reject code conflicts with custom data.

## Route tests

* authentication;
* permissions;
* full-page list;
* HTMX list;
* search;
* filters;
* create validation;
* edit validation;
* activation;
* deactivation;
* protected deletion;
* inaccessible actions hidden from the UI.

## Accessibility tests or checks

* labels associated with controls;
* status not communicated by colour alone;
* keyboard-usable modal or drawer;
* meaningful button labels;
* validation errors announced and linked;
* table headings correctly structured.

# Definition of Done for a catalogue

A catalogue implementation is complete when all applicable items are satisfied.

## Model

* [ ] Uses UUID primary keys.
* [ ] Uses a stable unique code.
* [ ] Separates code and display name.
* [ ] Includes active state.
* [ ] Distinguishes system and custom records.
* [ ] Includes timestamps.
* [ ] Defines appropriate database constraints.
* [ ] Uses restrictive foreign-key deletion behaviour.

## Service

* [ ] Exposes explicit concrete service methods.
* [ ] Protects stable codes.
* [ ] Supports active and all-record queries.
* [ ] Handles create and update transactions.
* [ ] Supports activation and deactivation.
* [ ] Defines deletion rules.
* [ ] Raises application exceptions.
* [ ] Creates audit events.
* [ ] Is tested without HTTP.

## Reference data

* [ ] System records use stable codes.
* [ ] Synchronisation is idempotent.
* [ ] Field ownership is defined.
* [ ] Custom records are preserved.
* [ ] Deprecated records are handled.
* [ ] Reserved codes are protected.

## User interface

* [ ] Uses the shared catalogue layout.
* [ ] Supports full-page and HTMX behaviour.
* [ ] Provides search and relevant filters.
* [ ] Shows system/custom status.
* [ ] Shows active/inactive status.
* [ ] Provides clear empty states.
* [ ] Uses accessible forms and actions.
* [ ] Hides actions the user cannot perform.

## Documentation

* [ ] Catalogue ownership is documented.
* [ ] Stable codes are documented.
* [ ] Permissions are documented.
* [ ] Special validation rules are documented.
* [ ] Reference-data definitions are documented.
* [ ] Relevant architecture decisions are recorded.

# Architecture decision: concrete catalogues with a shared framework

## Decision

Response Connect will implement concrete catalogue tables owned by their domain modules while sharing common model conventions, service behaviour, reference-data rules and administration components.

Stable codes will identify records used by application logic.

System and custom catalogue records will coexist safely.

## Context

The application requires many configurable classifications.

Implementing each independently would create duplicated code, inconsistent administration and unsafe upgrade behaviour.

Using one universal catalogue table would weaken database relationships and force catalogue-specific behaviour into unstructured fields.

## Alternatives considered

### Independent catalogue implementations

This would provide maximum local freedom but would duplicate models, routes, forms, templates and seed logic.

### One universal catalogue table

This would reduce table count but would weaken foreign keys, constraints, type clarity and domain ownership.

### Hard-coded Python enums

Enums are appropriate for some internal technical states but are unsuitable for organisation-configurable labels, ordering and activation.

### JSON configuration

JSON would be simple to load but difficult to administer, constrain, relate, audit and upgrade safely.

## Consequences

Benefits:

* consistent catalogue behaviour;
* clear database relationships;
* stable machine identifiers;
* local configurability;
* upgrade-safe system records;
* reusable administration UI;
* reduced duplication;
* clear domain ownership.

Trade-offs:

* concrete models still require some repeated declarations;
* the shared framework must avoid becoming overly abstract;
* catalogue-specific services remain necessary;
* system/local field ownership must be documented carefully;
* existing catalogues may require gradual migration.

# Related documents

* [Platform Principles](01-platform-principles.md)
* [Project Structure and Module Boundaries](02-project-structure.md)
* [Module Conventions](03-module-conventions.md)
* [Service-Layer Conventions](04-service-layer-conventions.md)
* [Core Concepts and Shared Vocabulary](05-core-concepts.md)

# Future considerations

The following are intentionally deferred:

* catalogue import and export;
* catalogue aliases;
* translation and localisation;
* catalogue inheritance;
* drag-and-drop ordering;
* effective-dated catalogues;
* field-level local override tracking;
* catalogue caching;
* formal module manifests;
* externally distributed catalogue packs;
* automated migration from legacy lookup tables.

These should be introduced only after the initial framework has been proven through multiple concrete catalogues.

# Review checklist

When reviewing a catalogue implementation, confirm:

* the concept genuinely belongs in a configurable catalogue;
* the owning module is clear;
* the catalogue uses a concrete table;
* the stable code is protected;
* display labels are separate from machine identity;
* system and custom ownership are distinguished;
* reference-data synchronisation preserves local records;
* inactive records remain valid historically;
* deletion is restricted appropriately;
* business rules are implemented in a concrete service;
* child rules use explicit relationships;
* audit events cover significant actions;
* the UI follows the shared catalogue pattern;
* full-page and HTMX behaviour are consistent;
* tests cover upgrade and lifecycle behaviour;
* the implementation does not make the shared framework specific to one catalogue.
