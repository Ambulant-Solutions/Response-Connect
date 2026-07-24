from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class StaffMember(db.Model):
    __tablename__ = "staff_members"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    employee_number: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
