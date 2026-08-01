from __future__ import annotations

import uuid
from typing import Generic, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.catalogues.exceptions import (
    CataloguePersistenceError,
    CatalogueRecordNotFoundError,
)


CatalogueModel = TypeVar(
    "CatalogueModel"
)


class CatalogueServiceBase(
    Generic[CatalogueModel],
):
    """
    Minimal shared read and lifecycle behaviour for concrete catalogues.

    Concrete services remain responsible for create, update, delete and
    catalogue-specific validation.
    """

    model: type[CatalogueModel]

    def __init__(
        self,
        *,
        session: Session,
    ) -> None:
        self.session = session

    def list_all(
        self,
    ) -> list[CatalogueModel]:
        statement = self._base_query().order_by(
            self.model.sort_order,
            self.model.name,
        )

        return list(
            self.session.scalars(statement)
        )

    def list_active(
        self,
    ) -> list[CatalogueModel]:
        statement = (
            self._base_query()
            .where(
                self.model.is_active.is_(True)
            )
            .order_by(
                self.model.sort_order,
                self.model.name,
            )
        )

        return list(
            self.session.scalars(statement)
        )

    def get(
        self,
        record_id: uuid.UUID,
    ) -> CatalogueModel:
        record = self.session.get(
            self.model,
            record_id,
        )

        if record is None:
            raise CatalogueRecordNotFoundError(
                f"{self.model.__name__} "
                f"{record_id} does not exist."
            )

        return record

    def get_by_code(
        self,
        code: str,
    ) -> CatalogueModel:
        statement = self._base_query().where(
            self.model.code == code
        )

        record = self.session.scalar(
            statement
        )

        if record is None:
            raise CatalogueRecordNotFoundError(
                f"{self.model.__name__} "
                f"with code {code!r} does not exist."
            )

        return record

    def get_active_by_code(
        self,
        code: str,
    ) -> CatalogueModel:
        statement = self._base_query().where(
            self.model.code == code,
            self.model.is_active.is_(True),
        )

        record = self.session.scalar(
            statement
        )

        if record is None:
            raise CatalogueRecordNotFoundError(
                f"Active {self.model.__name__} "
                f"with code {code!r} does not exist."
            )

        return record

    def activate(
        self,
        record_id: uuid.UUID,
    ) -> CatalogueModel:
        record = self.get(record_id)

        if record.is_active:
            return record

        record.is_active = True
        self._commit(
            "The catalogue record could not be activated."
        )

        return record

    def deactivate(
        self,
        record_id: uuid.UUID,
    ) -> CatalogueModel:
        record = self.get(record_id)

        if not record.is_active:
            return record

        record.is_active = False
        self._commit(
            "The catalogue record could not be deactivated."
        )

        return record

    def _base_query(
        self,
    ) -> Select:
        return select(self.model)

    def _commit(
        self,
        failure_message: str,
    ) -> None:
        try:
            self.session.commit()
        except Exception as exc:
            self.session.rollback()

            raise CataloguePersistenceError(
                failure_message
            ) from exc