from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class JobApplication(db.Model):
    __tablename__ = "job_applications"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    applicant_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    cover_letter: Mapped[str] = mapped_column(Text, nullable=True)
