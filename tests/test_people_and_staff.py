from __future__ import annotations

import unittest
from datetime import date
from sqlalchemy import select
from app import create_app
from app.blueprints.auth.catalogue import (
    ensure_permission_catalogue,
)
from app.blueprints.auth.models import (
    Permission,
    Role,
    UserAccount,
    role_permissions,
    user_roles,
)
from app.blueprints.org.hr.models import StaffMember
from app.blueprints.people.models import Person
from app.extensions import db


TEST_TABLES = (
    Person.__table__,
    Permission.__table__,
    Role.__table__,
    UserAccount.__table__,
    StaffMember.__table__,
    role_permissions,
    user_roles,
)


class PeopleAndStaffTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
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

    def tearDown(self):
        db.session.remove()

        db.metadata.drop_all(
            bind=db.engine,
            tables=reversed(TEST_TABLES),
        )

        self.app_context.pop()

    def test_account_and_staff_record_share_person(self):
        person = Person(
            first_name="Alexandra",
            preferred_name="Alex",
            last_name="Morgan",
        )

        account = UserAccount(
            person=person,
            email="alex.morgan@example.org",
            password_hash="not-used",
        )

        staff_member = StaffMember(
            person=person,
            employee_number="RC-0001",
            start_date=date(2026, 7, 30),
        )

        db.session.add_all(
            [
                person,
                account,
                staff_member,
            ]
        )
        db.session.commit()

        self.assertIs(account.person, person)
        self.assertIs(staff_member.person, person)
        self.assertIs(person.user_account, account)
        self.assertIs(person.staff_member, staff_member)

        self.assertEqual(
            account.display_name,
            "Alex Morgan",
        )
        self.assertEqual(
            account.greeting_name,
            "Alex",
        )
        self.assertEqual(
            account.initials,
            "AM",
        )

    def test_account_does_not_require_staff_record(self):
        person = Person(
            first_name="Taylor",
            last_name="Jones",
        )

        account = UserAccount(
            person=person,
            email="applicant@example.org",
            password_hash="not-used",
        )

        db.session.add(account)
        db.session.commit()

        self.assertEqual(account.person, person)
        self.assertIsNone(person.staff_member)

    def test_staff_record_does_not_require_account(self):
        person = Person(
            first_name="Imported",
            last_name="Staff",
        )

        staff_member = StaffMember(
            person=person,
            employee_number="RC-0002",
        )

        db.session.add(staff_member)
        db.session.commit()

        self.assertEqual(staff_member.person, person)
        self.assertIsNone(person.user_account)
        self.assertEqual(
            staff_member.employment_status,
            "active",
        )

    def test_hr_permissions_are_seeded_for_admin(self):
        ensure_permission_catalogue()

        permission_names = set(
            db.session.scalars(
                select(Permission.name)
            ).all()
        )

        expected_names = {
            "hr:read",
            "hr:manage",
            "hr:manage_training",
            "hr:verify_training",
            "personal:upload_training",
        }

        admin_role = db.session.scalar(
            select(Role).where(Role.name == "admin")
        )

        staff_role = db.session.scalar(
            select(Role).where(Role.name == "staff")
        )

        self.assertTrue(
            expected_names.issubset(permission_names)
        )

        self.assertTrue(
            expected_names.issubset(
                admin_role.permission_names
            )
        )

        self.assertNotIn(
            "hr:manage",
            staff_role.permission_names,
        )

        self.assertIn(
            "personal:upload_training",
            staff_role.permission_names,
        )

        # Confirm reseeding restores mandatory default permissions.
        staff_role.permissions = [
            permission
            for permission in staff_role.permissions
            if permission.name != "personal:upload_training"
        ]
        db.session.commit()

        ensure_permission_catalogue()

        self.assertIn(
            "personal:upload_training",
            staff_role.permission_names,
        )


if __name__ == "__main__":
    unittest.main()