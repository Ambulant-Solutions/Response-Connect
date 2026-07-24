from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class Organisation(db.Model):
    __tablename__ = "organisations"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    region: Mapped[str] = mapped_column(String(120), nullable=False)
