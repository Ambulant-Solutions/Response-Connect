from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class HealthCheck(db.Model):
    __tablename__ = "health_checks"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ok")
