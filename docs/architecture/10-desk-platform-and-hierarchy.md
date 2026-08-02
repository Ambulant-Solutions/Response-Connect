# Desk Platform and Hierarchy

## Purpose

The Desk Platform defines how operational responsibility is organised within Response Connect.

A **Desk** is an operational responsibility boundary.

Every significant piece of operational work should belong to a Desk.

Examples include:

* Company Operations
* Patient Transport – Devon
* Event Medical – Glastonbury Festival 2027
* Fleet Control
* Clinical Advice
* Silver Command
* Recovery Coordination Cell

Desks are not departments, locations or teams, although they may represent any of these where appropriate.

Instead, they define **who is operationally responsible for work at a given point in time**.

The Desk Platform provides the organisational foundation for:

* Event Journal entries;
* Activity Streams;
* Operational Logs;
* Audit Logs;
* notifications;
* task ownership;
* operational dashboards;
* workload management;
* operational permissions.

---

# Design principles

The Desk Platform follows the following principles.

## Operational ownership

Every operational record should belong to one primary Desk.

Examples include:

* incidents;
* patient journeys;
* shifts;
* operational tasks;
* deployments;
* Journal Entries.

The owning Desk is responsible for operational coordination.

It is not necessarily the long-term owner of the underlying resource.

## Hierarchical structure

Desks form a tree.

Every Desk has exactly one parent except the root Desk.

Unlimited hierarchy depth is supported.

Example:

```text
Response Connect Organisation
├── Corporate
├── Patient Transport
│   ├── Devon
│   ├── Cornwall
│   └── Somerset
├── Event Medical
│   ├── Glastonbury Festival
│   └── Exeter Christmas Market
└── Fleet
```

## Stable identity

Every Desk has:

* immutable identifier;
* stable Desk code;
* editable display name.

Journal Entries reference immutable identifiers.

Users primarily see display names.

## Operational responsibility

A Desk represents responsibility rather than ownership.

Operational work may move between Desks throughout its lifecycle.

Each transfer should create a Journal Entry.

## Immutable history

Desk history is preserved.

Journal Entries continue referencing historical Desks even after a Desk is closed or archived.

---

# Core concepts

## Root Desk

Every installation contains exactly one root Desk.

The root Desk represents the organisation as a whole.

Properties:

* exactly one;
* cannot be deleted;
* cannot be archived;
* cannot be moved;
* cannot have a parent.

The root Desk exists primarily to anchor the hierarchy.

---

## Child Desks

Every non-root Desk has exactly one parent.

Examples:

* services;
* operational regions;
* event control rooms;
* major incidents;
* temporary coordination cells.

The hierarchy provides inheritance for:

* operational visibility;
* dashboards;
* reporting;
* workload summaries.

---

## Operational ownership

Operational ownership answers:

> Who is responsible for this work now?

Examples:

Vehicle A12

Organisation owner:

```text
Fleet
```

Operational owner:

```text
Event Medical
└── Glastonbury Festival
```

The organisational owner has not changed.

Operational responsibility has.

This distinction avoids moving resources permanently through organisational structures simply because they have been deployed.

---

## Organisational ownership

Long-term ownership remains with the appropriate business domain.

Examples:

| Resource           | Organisational owner |
| ------------------ | -------------------- |
| Vehicle            | Fleet                |
| Staff Member       | Workforce            |
| Equipment          | Fleet                |
| Clinical Guideline | Clinical Governance  |
| Training Course    | Training             |

Operational ownership changes frequently.

Organisational ownership changes rarely.

The two concepts must remain separate.

---

# Desk lifecycle

Desks follow a lifecycle.

Initial lifecycle:

```text
Planning
        ↓
Open
        ↓
Operational
        ↓
Closing
        ↓
Closed
        ↓
Archived
```

Not every Desk must pass through every state.

Examples:

Permanent Patient Transport Desks may remain operational indefinitely.

Temporary Event Medical Desks may progress from Planning to Archived within a few days.

Lifecycle transitions should be recorded in the Event Journal.

---

# Desk hierarchy rules

The following constraints apply.

## Single parent

Every Desk has exactly one parent except the root.

## No cycles

Hierarchy cycles are prohibited.

The following is invalid:

```text
A
└── B
    └── C
        └── A
```

Services must validate hierarchy updates.

## Unlimited depth

The hierarchy should support arbitrary depth.

Practical hierarchy depth is expected to remain relatively small.

---

# Desk movement

A Desk may move within the hierarchy.

Example:

```text
Operations
        ↓
Major Incident
        ↓
Recovery
```

The move:

* preserves Desk identity;
* preserves history;
* records a Journal Entry;
* updates future operational scope.

Past Journal Entries continue representing the historical hierarchy.

---

# Temporary Desks

Temporary Desks are first-class objects.

Examples:

* Event Medical control;
* Gold Command;
* Silver Command;
* Bronze Command;
* Tactical Coordination Group;
* Recovery Cell;
* temporary Patient Transport coordination.

Temporary Desks:

* may have children;
* may own work;
* may own Journal Entries;
* may be archived.

Archiving does not remove historical references.

---

# Desk scope

Permissions combine with Desk scope.

Examples:

Current Desk only

Current Desk plus descendants

Entire subtree

Whole organisation

Administrative override

Desk scope determines:

* Journal visibility;
* dashboard content;
* work queues;
* reporting.

---

# Desk permissions

Permissions answer:

> What may this user do?

Desk scope answers:

> Where may they do it?

Access requires both.

Example:

```text
Permission:
operations:view

Desk:
Patient Transport – Devon

Scope:
Current Desk + descendants
```

---

# Desk responsibilities

A Desk may coordinate:

* incidents;
* patient journeys;
* shifts;
* resources;
* deployments;
* operational tasks;
* communications;
* notifications.

The Desk does not necessarily own these records permanently.

---

# Relationship to the Event Journal

Journal Entries should normally reference a Desk.

Examples:

```text
vehicle.assigned
patient_transport.started
staff.shift_signed_in
incident.created
```

Some Journal Entries remain organisation-wide.

Examples:

```text
authentication.login_failed
reference_data.synchronised
organisation.settings_updated
```

Desk association should therefore be optional at the persistence level.

Business services may require Desk assignment for operational workflows.

---

# Relationship to Activity Streams

Desk Activity Streams present Journal Entries associated with:

* the Desk;
* optionally all descendant Desks.

Activity Streams support:

* operational dashboards;
* control rooms;
* incident management;
* workload monitoring.

---

# Relationship to Notifications

Notifications should inherit Desk context.

Example:

Vehicle declared unavailable

↓

Fleet Desk

↓

Notification sent to Fleet Controllers

Desk-aware notifications support targeted operational communication.

---

# Relationship to Lifecycle

Lifecycle transitions affecting Desk responsibility should create Journal Entries.

Examples:

* work transferred;
* Desk opened;
* Desk archived;
* operational ownership changed.

---

# Operational transfers

Operational work may transfer between Desks.

Example:

```text
Corporate Control

↓

Event Control

↓

Silver Command

↓

Recovery Coordination
```

Transfers preserve:

* history;
* correlation;
* operational accountability.

Transfers should not overwrite historical ownership.

---

# Visibility

Desk visibility is determined through:

* permissions;
* Desk scope;
* Journal visibility;
* module-specific rules.

Users should not gain access to another Desk merely through hierarchy awareness.

---

# Archiving

Archiving removes a Desk from active operational use.

Archived Desks:

* remain queryable;
* remain in history;
* remain referenced by Journal Entries.

Archiving must never invalidate historical records.

---

# Performance considerations

Desk queries should support:

* descendant expansion;
* parent lookup;
* breadcrumb generation;
* hierarchy validation;
* operational summaries.

Hierarchy traversal should remain efficient for large organisations.

---

# Proposed package structure

```text
app/
└── desks/
    ├── __init__.py
    ├── commands.py
    ├── exceptions.py
    ├── models.py
    ├── queries.py
    ├── services.py
    └── validators.py
```

---

# Proposed public API

```python
desk_service.create(...)
desk_service.update(...)
desk_service.move(...)
desk_service.archive(...)
desk_service.activate(...)
desk_service.deactivate(...)

desk_query.get(...)
desk_query.list(...)
desk_query.children(...)
desk_query.descendants(...)
desk_query.path(...)
```

Routes and templates should interact only through these public services.

---

# Testing requirements

Testing should cover:

* hierarchy creation;
* cycle prevention;
* parent validation;
* root protection;
* Desk movement;
* lifecycle transitions;
* descendant queries;
* breadcrumb generation;
* Journal integration;
* permission-aware queries.

Architecture tests should verify:

* Desk services do not import routes;
* Desk package exposes only public APIs;
* hierarchy invariants remain protected.

---

# Future integration

The Desk Platform is intended to become the common operational context for:

* Event Medical;
* Patient Transport;
* Workforce;
* Fleet;
* Clinical Governance;
* Training;
* Governance;
* future operational modules.

Business modules should integrate with Desks rather than creating independent operational ownership models.

---

# Design decisions

This chapter establishes the following architectural decisions.

1. Every installation has exactly one immutable root Desk.
2. Desks form a strict hierarchy with no cycles.
3. Operational ownership is distinct from organisational ownership.
4. Journal Entries reference operational responsibility through Desks.
5. Temporary Desks are first-class operational objects.
6. Archived Desks remain part of historical records.
7. Permissions combine with Desk scope.
8. Operational transfers preserve historical accountability.
9. Business modules must reuse the Desk Platform rather than implement alternative operational ownership structures.
10. The Desk Platform forms the primary operational context for Response Connect.
