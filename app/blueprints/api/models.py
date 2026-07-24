from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class ApiClient(db.Model):
    __tablename__ = "api_clients"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
