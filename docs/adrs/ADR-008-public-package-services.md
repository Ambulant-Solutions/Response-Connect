# ADR-008 — Public Package Services

## Status

Accepted

## Context

Response Connect consists of independent platform packages such as:

- Journal
- Desks
- Files
- Notifications
- Identity
- Workforce
- Fleet

Each package contains multiple internal implementation classes.

Without a defined public entry point, business modules would begin importing
internal services directly, increasing coupling and making future refactoring
difficult.

## Decision

Every platform package exposes a single public service through:

    app/<package>/service.py

Business modules may depend only upon this public service.

Internal implementation modules, including:

    services.py
    validators.py
    commands.py
    models.py

are considered package-private implementation details.

## Consequences

Packages gain:

- a stable public API;
- freedom to refactor internals;
- lower coupling;
- simpler imports;
- consistent architecture across the project.

Business modules must not import implementation services directly.

Instead they import:

    from app.<package> import <Package>Service

## Examples

Good:

    from app.journal import JournalService

Bad:

    from app.journal.services import JournalEntryService