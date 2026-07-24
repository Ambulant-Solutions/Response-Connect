from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class ExternalForm(db.Model):
    __tablename__ = "external_forms"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    form_type: Mapped[str] = mapped_column(String(120), nullable=False)
    submitted_by: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
