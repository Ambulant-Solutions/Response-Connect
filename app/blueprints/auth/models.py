from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class UserAccount(db.Model):
    __tablename__ = "user_accounts"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
