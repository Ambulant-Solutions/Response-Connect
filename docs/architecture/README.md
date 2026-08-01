# Response Connect Developer Architecture Guide

## Purpose

This guide defines the architectural principles, conventions and approved implementation patterns for Response Connect.

It is intended for:

* core maintainers;
* external contributors;
* organisations developing local extensions;
* developers using AI-assisted coding tools;
* reviewers assessing proposed changes.

The guide explains not only how Response Connect is structured, but why particular architectural decisions have been made.

New modules and significant changes should follow this guide unless an architecture decision explicitly replaces an existing convention.

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

## Architecture guide contents

1. [Platform principles](01-platform-principles.md)
2. Project structure
3. Module conventions
4. Service-layer conventions
5. Catalogue framework
6. File platform
7. Audit framework
8. Reference data
9. Competency framework
10. Workflow and notifications
11. UI and HTMX patterns
12. Testing standards
13. Coding standards
14. Architecture decisions
15. Platform roadmap

Documents will be added as the relevant platform capabilities are designed and implemented.

## Authority of this guide

The architecture guide is the default technical authority for the project.

Where code and documentation disagree:

1. determine whether the code reflects an intentional newer decision;
2. record the decision if it is intentional;
3. update the guide and affected tests;
4. otherwise, bring the code back into alignment with the documented architecture.

Architecture should not change silently through isolated implementation choices.

## Architecture decision records

Significant technical decisions should be recorded in the relevant guide document.

Each decision should explain:

* **Decision** — what has been chosen.
* **Context** — what problem or requirement led to the decision.
* **Alternatives considered** — other credible options.
* **Consequences** — benefits, limitations and future implications.

Examples include:

* using S3-compatible object storage;
* streaming file downloads through Flask;
* treating uploaded objects as immutable;
* using services rather than cross-module database access;
* building a shared catalogue framework;
* implementing competencies through a configurable framework.

## Change process

Changes to the architecture guide should be reviewed with the same care as production code.

A proposed change should answer:

* Does it strengthen or weaken module boundaries?
* Does it introduce a second way to perform an existing capability?
* Can the solution be reused elsewhere?
* Does it preserve upgrade safety?
* Does it remain suitable for self-hosted installations?
* Does it increase avoidable operational complexity?
* Is the behaviour adequately testable?

## Living documentation

This is a living guide.

It should evolve as Response Connect grows, but established patterns should not be changed casually. Stability and consistency are more valuable than repeatedly adopting newer or more fashionable approaches.
