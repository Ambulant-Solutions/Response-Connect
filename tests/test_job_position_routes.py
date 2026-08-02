from __future__ import annotations

import unittest
import uuid
from datetime import date, timedelta
from unittest.mock import patch
from flask import g
from sqlalchemy import select

from app import create_app
from app.blueprints.auth.models import (
    Permission,
    Role,
    UserAccount,
    role_permissions,
    user_roles,
)
from app.blueprints.org.hr.models import (
    JobPosition,
    StaffMember,
    StaffPositionAssignment,
)
from app.blueprints.people.models import Person
from app.extensions import db


TEST_TABLES = (
    Person.__table__,
    Permission.__table__,
    Role.__table__,
    UserAccount.__table__,
    StaffMember.__table__,
    JobPosition.__table__,
    StaffPositionAssignment.__table__,
    role_permissions,
    user_roles,
)

JOB_POSITION_BASE_URL = (
    "/org/settings/workforce/job-positions"
)

class JobPositionRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "job-position-tests",
                "SQLALCHEMY_DATABASE_URI": (
                    "sqlite+pysqlite:///:memory:"
                ),
                "WTF_CSRF_ENABLED": False,
            }
        )

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.metadata.create_all(
            bind=db.engine,
            tables=TEST_TABLES,
        )

        self.client = self.app.test_client()

        read_permission = Permission(
            name="hr:read",
            description="View HR records",
            category="hr",
        )

        manage_permission = Permission(
            name="hr:manage",
            description="Manage HR records",
            category="hr",
        )
        
        configure_permission = Permission(
            name="hr:configure",
            description="Configure workforce settings",
            category="hr",
        )

        reader_role = Role(
            name="hr_reader",
            display_name="HR Reader",
            description="Read-only HR access",
        )
        reader_role.permissions.append(read_permission)

        manager_role = Role(
            name="hr_manager",
            display_name="HR Manager",
            description="HR management access",
        )
        manager_role.permissions.extend(
            [
                configure_permission,
            ]
        )

        self.reader = self.create_user(
            email="reader@example.org",
            role=reader_role,
        )

        self.manager = self.create_user(
            email="manager@example.org",
            role=manager_role,
        )

        self.no_access_user = self.create_user(
            email="staff@example.org",
        )

        db.session.add_all(
            [
                reader_role,
                manager_role,
            ]
        )
        db.session.commit()

    def tearDown(self):
        db.session.remove()

        db.metadata.drop_all(
            bind=db.engine,
            tables=reversed(TEST_TABLES),
        )

        self.app_context.pop()

    def create_user(
        self,
        *,
        email: str,
        role: Role | None = None,
    ) -> UserAccount:
        person = Person(
            first_name=email.split("@")[0].title(),
            last_name="User",
        )

        account = UserAccount(
            person=person,
            email=email,
            password_hash="not-used",
            is_active=True,
        )

        if role is not None:
            account.roles.append(role)

        db.session.add(account)

        return account

    def login_as(self, user: UserAccount) -> None:
        with self.client.session_transaction() as session:
            session.clear()
            session["_user_id"] = str(user.id)
            session["_fresh"] = True

        # Flask-Login caches current_user on the active app context.
        g.pop("_login_user", None)

    def test_position_list_requires_hr_read(self):
        response = self.client.get(
            "/org/settings/workforce/job-positions"
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            "/auth/login",
            response.headers["Location"],
        )

        self.login_as(self.no_access_user)

        response = self.client.get(
            "/org/settings/workforce/job-positions"
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/",
        )

    def test_hr_reader_cannot_access_job_position_settings(
        self,
    ) -> None:
        self.login_as(self.reader)

        response = self.client.get(
            JOB_POSITION_BASE_URL
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/",
        )

        response = self.client.get(
            f"{JOB_POSITION_BASE_URL}/new"
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/",
        )

    def test_configurator_can_list_positions(
        self,
    ) -> None:
        db.session.add_all(
            [
                JobPosition(
                    name="Operations Manager",
                    sort_order=20,
                ),
                JobPosition(
                    name="First Responder",
                    sort_order=10,
                ),
                JobPosition(
                    name="Clinical Manager",
                    sort_order=10,
                ),
            ]
        )
        db.session.commit()

        self.login_as(self.manager)

        with patch(
            "app.blueprints.org.settings.workforce.render_template",
            return_value="position-list",
        ) as render_template:
            response = self.client.get(
                JOB_POSITION_BASE_URL
            )

        self.assertEqual(response.status_code, 200)

        positions = (
            render_template.call_args.kwargs[
                "positions"
            ]
        )

        self.assertEqual(
            [position.name for position in positions],
            [
                "Clinical Manager",
                "First Responder",
                "Operations Manager",
            ],
        )

    def test_manager_can_create_and_edit_position(self):
        self.login_as(self.manager)

        response = self.client.post(
            "/org/settings/workforce/job-positions/new",
            data={
                "name": "  Training Manager  ",
                "description": (
                    "  Responsible for organisational training.  "
                ),
                "sort_order": "30",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.headers["Location"].endswith(
                "/org/settings/workforce/job-positions"
            )
        )

        position = db.session.scalar(
            select(JobPosition).where(
                JobPosition.name == "Training Manager"
            )
        )

        self.assertIsNotNone(position)
        self.assertEqual(
            position.description,
            "Responsible for organisational training.",
        )
        self.assertEqual(position.sort_order, 30)
        self.assertTrue(position.is_active)

        response = self.client.post(
            (
                f"/org/settings/workforce/job-positions/"
                f"{position.id}/edit"
            ),
            data={
                "name": "Head of Training",
                "description": "Leads training delivery.",
                "sort_order": "15",
            },
        )

        self.assertEqual(response.status_code, 302)

        db.session.refresh(position)

        self.assertEqual(
            position.name,
            "Head of Training",
        )
        self.assertEqual(
            position.description,
            "Leads training delivery.",
        )
        self.assertEqual(position.sort_order, 15)

    def test_duplicate_position_name_is_rejected_case_insensitively(
        self,
    ):
        position = JobPosition(
            name="Operations Manager",
        )

        db.session.add(position)
        db.session.commit()

        self.login_as(self.manager)

        with patch(
            "app.blueprints.org.settings.workforce.render_template",
            return_value="position-form",
        ) as render_template:
            response = self.client.post(
                "/org/settings/workforce/job-positions/new",
                data={
                    "name": "operations manager",
                    "description": "",
                    "sort_order": "0",
                },
            )

        self.assertEqual(response.status_code, 200)

        positions = db.session.scalars(
            select(JobPosition)
        ).all()

        self.assertEqual(len(positions), 1)

        form = render_template.call_args.kwargs[
            "form"
        ]

        self.assertIn(
            "This job-position name is already in use.",
            form.name.errors,
        )

    def test_position_with_current_assignment_cannot_be_deactivated(
        self,
    ):
        today = date.today()

        staff_member = StaffMember(
            person=Person(
                first_name="Current",
                last_name="Staff",
            ),
            employee_number="RC-0200",
        )

        position = JobPosition(
            name="Team Leader",
        )

        assignment = StaffPositionAssignment(
            staff_member=staff_member,
            position=position,
            start_date=today - timedelta(days=30),
        )

        db.session.add_all(
            [
                staff_member,
                position,
                assignment,
            ]
        )
        db.session.commit()

        self.login_as(self.manager)

        response = self.client.post(
            (
                f"/org/settings/workforce/job-positions/"
                f"{position.id}/deactivate"
            )
        )

        self.assertEqual(response.status_code, 302)

        db.session.refresh(position)
        self.assertTrue(position.is_active)

        # Once the assignment is historical, the position
        # may be retired without deleting that history.
        assignment.end_date = (
            today - timedelta(days=1)
        )
        db.session.commit()

        response = self.client.post(
            (
                f"/org/settings/workforce/job-positions/"
                f"{position.id}/deactivate"
            )
        )

        self.assertEqual(response.status_code, 302)

        db.session.refresh(position)
        self.assertFalse(position.is_active)

        response = self.client.post(
            (
                f"/org/settings/workforce/job-positions/"
                f"{position.id}/activate"
            )
        )

        self.assertEqual(response.status_code, 302)

        db.session.refresh(position)
        self.assertTrue(position.is_active)

    def test_unknown_position_returns_not_found(self):
        self.login_as(self.manager)

        response = self.client.get(
            (
                "/org/settings/workforce/job-positions/"
                f"{uuid.uuid4()}/edit"
            )
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()