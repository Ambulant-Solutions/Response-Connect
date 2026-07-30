from __future__ import annotations

import unittest
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
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
from app.blueprints.org.hr.models import (
    ClinicalGrade,
    JobPosition,
    StaffClinicalGradeAssignment,
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
    ClinicalGrade.__table__,
    StaffPositionAssignment.__table__,
    StaffClinicalGradeAssignment.__table__,
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

    def test_staff_position_assignment_history(self):
        today = date.today()

        person = Person(
            first_name="Jordan",
            last_name="Taylor",
        )

        staff_member = StaffMember(
            person=person,
            employee_number="RC-0100",
        )

        responder = JobPosition(
            name="First Responder",
            sort_order=10,
        )

        team_leader = JobPosition(
            name="Team Leader",
            sort_order=20,
        )

        previous_assignment = StaffPositionAssignment(
            staff_member=staff_member,
            position=responder,
            start_date=today - timedelta(days=365),
            end_date=today - timedelta(days=1),
        )

        current_assignment = StaffPositionAssignment(
            staff_member=staff_member,
            position=team_leader,
            start_date=today,
            is_primary=True,
        )

        db.session.add_all(
            [
                staff_member,
                responder,
                team_leader,
                previous_assignment,
                current_assignment,
            ]
        )
        db.session.commit()

        self.assertFalse(previous_assignment.is_current)
        self.assertTrue(current_assignment.is_current)
        self.assertTrue(current_assignment.is_primary)

        self.assertIn(
            previous_assignment,
            staff_member.position_assignments,
        )
        self.assertIn(
            current_assignment,
            staff_member.position_assignments,
        )
        self.assertIn(
            current_assignment,
            team_leader.staff_assignments,
        )


    def test_staff_clinical_grade_history(self):
        today = date.today()

        person = Person(
            first_name="Morgan",
            last_name="Lewis",
        )

        staff_member = StaffMember(
            person=person,
            employee_number="RC-0101",
        )

        responder_grade = ClinicalGrade(
            name="First Responder",
            abbreviation="FR",
            sort_order=10,
        )

        technician_grade = ClinicalGrade(
            name="Emergency Medical Technician",
            abbreviation="EMT",
            sort_order=20,
        )

        previous_assignment = StaffClinicalGradeAssignment(
            staff_member=staff_member,
            clinical_grade=responder_grade,
            start_date=today - timedelta(days=730),
            end_date=today - timedelta(days=1),
        )

        current_assignment = StaffClinicalGradeAssignment(
            staff_member=staff_member,
            clinical_grade=technician_grade,
            start_date=today,
            is_primary=True,
        )

        db.session.add_all(
            [
                staff_member,
                responder_grade,
                technician_grade,
                previous_assignment,
                current_assignment,
            ]
        )
        db.session.commit()

        self.assertFalse(previous_assignment.is_current)
        self.assertTrue(current_assignment.is_current)
        self.assertTrue(current_assignment.is_primary)

        self.assertIn(
            previous_assignment,
            staff_member.clinical_grade_assignments,
        )
        self.assertIn(
            current_assignment,
            staff_member.clinical_grade_assignments,
        )
        self.assertIn(
            current_assignment,
            technician_grade.staff_assignments,
        )


    def test_assignment_end_date_cannot_precede_start_date(self):
        today = date.today()

        person = Person(
            first_name="Casey",
            last_name="Williams",
        )

        staff_member = StaffMember(
            person=person,
            employee_number="RC-0102",
        )

        position = JobPosition(
            name="Operations Manager",
        )

        clinical_grade = ClinicalGrade(
            name="Paramedic",
            abbreviation="Para",
        )

        db.session.add_all(
            [
                staff_member,
                position,
                clinical_grade,
            ]
        )
        db.session.commit()

        invalid_position_assignment = StaffPositionAssignment(
            staff_member=staff_member,
            position=position,
            start_date=today,
            end_date=today - timedelta(days=1),
        )

        db.session.add(invalid_position_assignment)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        invalid_grade_assignment = StaffClinicalGradeAssignment(
            staff_member=staff_member,
            clinical_grade=clinical_grade,
            start_date=today,
            end_date=today - timedelta(days=1),
        )

        db.session.add(invalid_grade_assignment)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()


if __name__ == "__main__":
    unittest.main()