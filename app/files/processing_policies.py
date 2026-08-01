from __future__ import annotations

import re
import uuid
from collections.abc import Iterable

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.catalogues import (
    CatalogueServiceBase,
    InvalidCatalogueCodeError,
    validate_catalogue_code,
    validate_colour,
    validate_icon,
    validate_sort_order,
)
from app.files.exceptions import (
    FileProcessingPolicyCodeConflictError,
    FileProcessingPolicyNameConflictError,
    FileProcessingPolicyNotFoundError,
    FileProcessingPolicyPersistenceError,
    InvalidFileProcessingPolicyError,
    ProtectedFileProcessingPolicyError,
)
from app.files.models import (
    FileCategory,
    FileProcessingExtensionRule,
    FileProcessingMimeTypeRule,
    FileProcessingPolicy,
)
from app.files.reference_data import (
    FILE_PROCESSING_POLICY_DATASET,
)
from app.reference_data import (
    ReferenceDataChange,
    ReferenceDataChangeType,
    ReferenceDataSynchronisationResult,
    ReferenceDatasetSynchroniser,
)
from app.reference_data.exceptions import (
    ReferenceDataConflictError,
    ReferenceDataSynchronisationError,
)

from app.files.commands import (
    CreateFileProcessingPolicyCommand,
    ReplaceFileProcessingRulesCommand,
    UpdateFileProcessingPolicyCommand,
)


_EXTENSION_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9_-]*$"
)

_MIME_TYPE_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9!#$&^_.+-]*/"
    r"[a-z0-9][a-z0-9!#$&^_.+-]*$"
)


class FileProcessingPolicyService(
    CatalogueServiceBase[FileProcessingPolicy]
):
    """
    Manage technical validation and processing policies for uploaded files.

    Public mutation methods own their database transaction.
    """

    model = FileProcessingPolicy

    def __init__(
        self,
        *,
        session: Session,
    ) -> None:
        super().__init__(session=session)

    def _base_query(self):
        return (
            select(FileProcessingPolicy)
            .options(
                selectinload(
                    FileProcessingPolicy.extension_rules
                ),
                selectinload(
                    FileProcessingPolicy.mime_type_rules
                ),
            )
        )

    def get(
        self,
        record_id: uuid.UUID,
    ) -> FileProcessingPolicy:
        policy = self.session.scalar(
            self._base_query().where(
                FileProcessingPolicy.id == record_id
            )
        )

        if policy is None:
            raise FileProcessingPolicyNotFoundError(
                f"File processing policy {record_id} "
                "does not exist."
            )

        return policy

    def get_by_code(
        self,
        code: str,
    ) -> FileProcessingPolicy:
        try:
            normalised_code = validate_catalogue_code(
                code
            )
        except InvalidCatalogueCodeError as exc:
            raise InvalidFileProcessingPolicyError(
                str(exc)
            ) from exc

        policy = self.session.scalar(
            self._base_query().where(
                FileProcessingPolicy.code
                == normalised_code
            )
        )

        if policy is None:
            raise FileProcessingPolicyNotFoundError(
                "No file processing policy exists with "
                f"code {normalised_code!r}."
            )

        return policy

    def get_active_by_code(
        self,
        code: str,
    ) -> FileProcessingPolicy:
        try:
            normalised_code = validate_catalogue_code(
                code
            )
        except InvalidCatalogueCodeError as exc:
            raise InvalidFileProcessingPolicyError(
                str(exc)
            ) from exc

        policy = self.session.scalar(
            self._base_query().where(
                FileProcessingPolicy.code
                == normalised_code,
                FileProcessingPolicy.is_active.is_(
                    True
                ),
            )
        )

        if policy is None:
            raise FileProcessingPolicyNotFoundError(
                "No active file processing policy exists "
                f"with code {normalised_code!r}."
            )

        return policy

    def create(
        self,
        command: CreateFileProcessingPolicyCommand,
    ) -> FileProcessingPolicy:
        values = self._validate_policy_values(
            code=command.code,
            name=command.name,
            category=command.category,
            max_size_bytes=command.max_size_bytes,
            extensions=command.extensions,
            mime_types=command.mime_types,
            icon=command.icon,
            colour=command.colour,
            sort_order=command.sort_order,
        )

        self._ensure_code_available(
            values["code"]
        )

        self._ensure_name_available(
            values["name"]
        )

        policy = FileProcessingPolicy(
            code=values["code"],
            name=values["name"],
            description=self._clean_description(
                command.description
            ),
            icon=values["icon"],
            colour=values["colour"],
            sort_order=values["sort_order"],
            is_system=command.is_system,
            is_active=command.is_active,
            category=values["category"],
            max_size_bytes=values[
                "max_size_bytes"
            ],
            requires_virus_scan=(
                command.requires_virus_scan
            ),
            generate_thumbnail=(
                command.generate_thumbnail
            ),
            generate_preview=(
                command.generate_preview
            ),
            enable_ocr=command.enable_ocr,
            optimise_image=command.optimise_image,
            extract_metadata=(
                command.extract_metadata
            ),
        )

        policy.extension_rules = [
            FileProcessingExtensionRule(
                extension=extension
            )
            for extension in values["extensions"]
        ]

        policy.mime_type_rules = [
            FileProcessingMimeTypeRule(
                mime_type=mime_type
            )
            for mime_type in values["mime_types"]
        ]

        self.session.add(policy)

        self._commit_policy_change(
            "The file processing policy could not "
            "be created."
        )

        return policy


    def update(
        self,
        policy_id: uuid.UUID,
        command: UpdateFileProcessingPolicyCommand,
    ) -> FileProcessingPolicy:
        policy = self.get(policy_id)

        values = self._validate_policy_values(
            code=policy.code,
            name=command.name,
            category=command.category,
            max_size_bytes=command.max_size_bytes,
            extensions=command.extensions,
            mime_types=command.mime_types,
            icon=command.icon,
            colour=command.colour,
            sort_order=command.sort_order,
        )

        self._ensure_name_available(
            values["name"],
            excluding_id=policy.id,
        )

        policy.name = values["name"]
        policy.description = (
            self._clean_description(
                command.description
            )
        )
        policy.icon = values["icon"]
        policy.colour = values["colour"]
        policy.sort_order = values["sort_order"]
        policy.category = values["category"]
        policy.max_size_bytes = values[
            "max_size_bytes"
        ]

        policy.requires_virus_scan = (
            command.requires_virus_scan
        )
        policy.generate_thumbnail = (
            command.generate_thumbnail
        )
        policy.generate_preview = (
            command.generate_preview
        )
        policy.enable_ocr = command.enable_ocr
        policy.optimise_image = (
            command.optimise_image
        )
        policy.extract_metadata = (
            command.extract_metadata
        )

        self._replace_extension_rules(
            policy,
            values["extensions"],
        )

        self._replace_mime_type_rules(
            policy,
            values["mime_types"],
        )

        self._commit_policy_change(
            "The file processing policy could not "
            "be updated."
        )

        return policy

    def activate(
        self,
        record_id: uuid.UUID,
    ) -> FileProcessingPolicy:
        policy = self.get(record_id)

        if policy.is_active:
            return policy

        policy.is_active = True

        self._commit_policy_change(
            "The file processing policy could not "
            "be activated."
        )

        return policy

    def deactivate(
        self,
        record_id: uuid.UUID,
    ) -> FileProcessingPolicy:
        policy = self.get(record_id)

        if not policy.is_active:
            return policy

        policy.is_active = False

        self._commit_policy_change(
            "The file processing policy could not "
            "be deactivated."
        )

        return policy

    def delete_custom(
        self,
        policy_id: uuid.UUID,
    ) -> None:
        policy = self.get(policy_id)

        if policy.is_system:
            raise ProtectedFileProcessingPolicyError(
                "System file processing policies "
                "cannot be deleted."
            )

        self.session.delete(policy)

        self._commit_policy_change(
            "The file processing policy could not "
            "be deleted."
        )

    def replace_rules(
        self,
        policy_id: uuid.UUID,
        command: ReplaceFileProcessingRulesCommand,
    ) -> FileProcessingPolicy:
        policy = self.get(policy_id)

        normalised_extensions = (
            self._normalise_extensions(
                command.extensions
            )
        )

        normalised_mime_types = (
            self._normalise_mime_types(
                command.mime_types
            )
        )

        self._validate_rule_presence(
            normalised_extensions,
            normalised_mime_types,
        )

        self._replace_extension_rules(
            policy,
            normalised_extensions,
        )

        self._replace_mime_type_rules(
            policy,
            normalised_mime_types,
        )

        self._commit_policy_change(
            "The processing-policy validation "
            "rules could not be updated."
        )

        return policy

    def _validate_policy_values(
        self,
        *,
        code: str,
        name: str,
        category: FileCategory | str,
        max_size_bytes: int,
        extensions: Iterable[str],
        mime_types: Iterable[str],
        icon: str,
        colour: str,
        sort_order: int,
    ) -> dict[str, object]:
        try:
            normalised_code = (
                validate_catalogue_code(code)
            )
            normalised_icon = validate_icon(icon)
            normalised_colour = validate_colour(
                colour
            )
            normalised_sort_order = (
                validate_sort_order(sort_order)
            )
        except (
            InvalidCatalogueCodeError,
            ValueError,
        ) as exc:
            raise InvalidFileProcessingPolicyError(
                str(exc)
            ) from exc

        normalised_name = name.strip()

        if not normalised_name:
            raise InvalidFileProcessingPolicyError(
                "A processing-policy name is required."
            )

        if len(normalised_name) > 120:
            raise InvalidFileProcessingPolicyError(
                "Processing-policy names must not "
                "exceed 120 characters."
            )

        normalised_category = (
            self._normalise_category(category)
        )

        if max_size_bytes <= 0:
            raise InvalidFileProcessingPolicyError(
                "Maximum file size must be greater "
                "than zero."
            )

        normalised_extensions = (
            self._normalise_extensions(extensions)
        )

        normalised_mime_types = (
            self._normalise_mime_types(mime_types)
        )

        self._validate_rule_presence(
            normalised_extensions,
            normalised_mime_types,
        )

        return {
            "code": normalised_code,
            "name": normalised_name,
            "category": normalised_category,
            "max_size_bytes": max_size_bytes,
            "extensions": normalised_extensions,
            "mime_types": normalised_mime_types,
            "icon": normalised_icon,
            "colour": normalised_colour,
            "sort_order": normalised_sort_order,
        }

    @staticmethod
    def _normalise_category(
        category: FileCategory | str,
    ) -> str:
        try:
            return FileCategory(category).value
        except ValueError as exc:
            valid_values = ", ".join(
                item.value
                for item in FileCategory
            )

            raise InvalidFileProcessingPolicyError(
                "Invalid file category. Expected one "
                f"of: {valid_values}."
            ) from exc

    @staticmethod
    def _normalise_extensions(
        extensions: Iterable[str],
    ) -> list[str]:
        normalised: set[str] = set()

        for value in extensions:
            extension = (
                value.strip()
                .lower()
                .lstrip(".")
            )

            if not extension:
                continue

            if len(extension) > 32:
                raise InvalidFileProcessingPolicyError(
                    "File extensions must not exceed "
                    "32 characters."
                )

            if not _EXTENSION_PATTERN.fullmatch(
                extension
            ):
                raise InvalidFileProcessingPolicyError(
                    f"Invalid file extension: "
                    f"{value!r}."
                )

            normalised.add(extension)

        return sorted(normalised)

    @staticmethod
    def _normalise_mime_types(
        mime_types: Iterable[str],
    ) -> list[str]:
        normalised: set[str] = set()

        for value in mime_types:
            mime_type = (
                value.split(";", 1)[0]
                .strip()
                .lower()
            )

            if not mime_type:
                continue

            if len(mime_type) > 255:
                raise InvalidFileProcessingPolicyError(
                    "MIME types must not exceed "
                    "255 characters."
                )

            if not _MIME_TYPE_PATTERN.fullmatch(
                mime_type
            ):
                raise InvalidFileProcessingPolicyError(
                    f"Invalid MIME type: "
                    f"{value!r}."
                )

            normalised.add(mime_type)

        return sorted(normalised)

    @staticmethod
    def _validate_rule_presence(
        extensions: list[str],
        mime_types: list[str],
    ) -> None:
        if not extensions:
            raise InvalidFileProcessingPolicyError(
                "At least one permitted file extension "
                "is required."
            )

        if not mime_types:
            raise InvalidFileProcessingPolicyError(
                "At least one permitted MIME type "
                "is required."
            )

    @staticmethod
    def _clean_description(
        description: str | None,
    ) -> str | None:
        if description is None:
            return None

        cleaned = description.strip()

        if not cleaned:
            return None

        if len(cleaned) > 500:
            raise InvalidFileProcessingPolicyError(
                "Descriptions must not exceed "
                "500 characters."
            )

        return cleaned

    def _ensure_code_available(
        self,
        code: str,
        *,
        excluding_id: uuid.UUID | None = None,
    ) -> None:
        statement = select(
            FileProcessingPolicy.id
        ).where(
            FileProcessingPolicy.code == code
        )

        if excluding_id is not None:
            statement = statement.where(
                FileProcessingPolicy.id
                != excluding_id
            )

        if self.session.scalar(statement) is not None:
            raise FileProcessingPolicyCodeConflictError(
                "A file processing policy already "
                f"uses code {code!r}."
            )

    def _ensure_name_available(
        self,
        name: str,
        *,
        excluding_id: uuid.UUID | None = None,
    ) -> None:
        statement = select(
            FileProcessingPolicy.id
        ).where(
            func.lower(
                FileProcessingPolicy.name
            ) == name.lower()
        )

        if excluding_id is not None:
            statement = statement.where(
                FileProcessingPolicy.id
                != excluding_id
            )

        if self.session.scalar(statement) is not None:
            raise FileProcessingPolicyNameConflictError(
                "A file processing policy already "
                f"uses name {name!r}."
            )

    @staticmethod
    def _replace_extension_rules(
        policy: FileProcessingPolicy,
        extensions: Iterable[str],
    ) -> None:
        """
        Reconcile extension rules without recreating unchanged records.

        Preserving matching child records avoids temporary unique-constraint
        conflicts during SQLAlchemy flush operations.
        """

        requested = set(extensions)

        existing_by_value = {
            rule.extension: rule
            for rule in policy.extension_rules
        }

        policy.extension_rules = [
            existing_by_value.get(extension)
            or FileProcessingExtensionRule(
                extension=extension
            )
            for extension in sorted(requested)
        ]

    @staticmethod
    def _replace_mime_type_rules(
        policy: FileProcessingPolicy,
        mime_types: Iterable[str],
    ) -> None:
        """
        Reconcile MIME-type rules without recreating unchanged records.
        """

        requested = set(mime_types)

        existing_by_value = {
            rule.mime_type: rule
            for rule in policy.mime_type_rules
        }

        policy.mime_type_rules = [
            existing_by_value.get(mime_type)
            or FileProcessingMimeTypeRule(
                mime_type=mime_type
            )
            for mime_type in sorted(requested)
        ]

    def _commit_policy_change(
        self,
        failure_message: str,
    ) -> None:
        try:
            self.session.commit()

        except IntegrityError as exc:
            self.session.rollback()

            constraint_name = (
                getattr(
                    getattr(
                        exc.orig,
                        "diag",
                        None,
                    ),
                    "constraint_name",
                    None,
                )
            )

            if constraint_name in {
                "uq_file_processing_policies_code",
                "file_processing_policies_code_key",
            }:
                raise (
                    FileProcessingPolicyCodeConflictError(
                        "A file processing policy with "
                        "that code already exists."
                    )
                ) from exc

            if constraint_name == (
                "uq_file_processing_policies_name"
            ):
                raise (
                    FileProcessingPolicyNameConflictError(
                        "A file processing policy with "
                        "that name already exists."
                    )
                ) from exc

            raise FileProcessingPolicyPersistenceError(
                failure_message
            ) from exc

        except SQLAlchemyError as exc:
            self.session.rollback()

            raise FileProcessingPolicyPersistenceError(
                failure_message
            ) from exc



class FileProcessingPolicySynchroniser(
    ReferenceDatasetSynchroniser
):
    """
    Synchronise system file-processing policies while preserving locally
    owned display fields.
    """

    dataset = FILE_PROCESSING_POLICY_DATASET

    def __init__(
        self,
        *,
        service: FileProcessingPolicyService,
    ) -> None:
        self.service = service
        self.session = service.session

    def synchronise(
        self,
        *,
        dry_run: bool = False,
    ) -> ReferenceDataSynchronisationResult:
        result = ReferenceDataSynchronisationResult(
            dataset=self.dataset.name
        )

        try:
            for definition in self.dataset.records:
                self._synchronise_record(
                    definition,
                    result=result,
                    dry_run=dry_run,
                )

            if dry_run:
                self.session.rollback()
            else:
                self.session.commit()

            return result

        except ReferenceDataConflictError:
            self.session.rollback()
            raise

        except SQLAlchemyError as exc:
            self.session.rollback()

            raise ReferenceDataSynchronisationError(
                "File-processing policy reference data "
                "could not be synchronised."
            ) from exc

    def _synchronise_record(
        self,
        definition,
        *,
        result: ReferenceDataSynchronisationResult,
        dry_run: bool,
    ) -> None:
        policy = self.session.scalar(
            self.service._base_query().where(
                FileProcessingPolicy.code
                == definition.code
            )
        )

        if policy is None:
            policy = self._create_policy(
                definition
            )

            self.session.add(policy)
            self.session.flush()

            result.changes.append(
                ReferenceDataChange(
                    dataset=self.dataset.name,
                    code=definition.code,
                    change_type=(
                        ReferenceDataChangeType.CREATE
                    ),
                    changed_fields=tuple(
                        sorted(definition.values)
                    ),
                )
            )

            return

        if not policy.is_system:
            result.changes.append(
                ReferenceDataChange(
                    dataset=self.dataset.name,
                    code=definition.code,
                    change_type=(
                        ReferenceDataChangeType.CONFLICT
                    ),
                    message=(
                        "A custom processing policy already "
                        "uses this reserved system code."
                    ),
                )
            )

            raise ReferenceDataConflictError(
                "Custom file-processing policy "
                f"{definition.code!r} conflicts with "
                "system reference data."
            )

        changed_fields: list[str] = []

        for field_name in (
            definition.system_owned_fields
            - {"extensions", "mime_types"}
        ):
            expected_value = definition.values[
                field_name
            ]

            if getattr(
                policy,
                field_name,
            ) != expected_value:
                setattr(
                    policy,
                    field_name,
                    expected_value,
                )
                changed_fields.append(field_name)

        expected_extensions = set(
            definition.values["extensions"]
        )

        if (
            policy.allowed_extensions
            != expected_extensions
        ):
            self.service._replace_extension_rules(
                policy,
                sorted(expected_extensions),
            )
            changed_fields.append("extensions")

        expected_mime_types = set(
            definition.values["mime_types"]
        )

        if (
            policy.allowed_mime_types
            != expected_mime_types
        ):
            self.service._replace_mime_type_rules(
                policy,
                sorted(expected_mime_types),
            )
            changed_fields.append("mime_types")

        if changed_fields:
            result.changes.append(
                ReferenceDataChange(
                    dataset=self.dataset.name,
                    code=definition.code,
                    change_type=(
                        ReferenceDataChangeType.UPDATE
                    ),
                    changed_fields=tuple(
                        sorted(changed_fields)
                    ),
                )
            )
        else:
            result.changes.append(
                ReferenceDataChange(
                    dataset=self.dataset.name,
                    code=definition.code,
                    change_type=(
                        ReferenceDataChangeType.UNCHANGED
                    ),
                )
            )

    @staticmethod
    def _create_policy(
        definition,
    ) -> FileProcessingPolicy:
        values = definition.values

        policy = FileProcessingPolicy(
            code=definition.code,
            name=values["name"],
            description=values["description"],
            icon=values["icon"],
            colour=values["colour"],
            sort_order=values["sort_order"],
            is_system=True,
            is_active=values["is_active"],
            category=values["category"],
            max_size_bytes=values[
                "max_size_bytes"
            ],
            requires_virus_scan=values[
                "requires_virus_scan"
            ],
            generate_thumbnail=values[
                "generate_thumbnail"
            ],
            generate_preview=values[
                "generate_preview"
            ],
            enable_ocr=values["enable_ocr"],
            optimise_image=values[
                "optimise_image"
            ],
            extract_metadata=values[
                "extract_metadata"
            ],
        )

        policy.extension_rules = [
            FileProcessingExtensionRule(
                extension=extension
            )
            for extension in values[
                "extensions"
            ]
        ]

        policy.mime_type_rules = [
            FileProcessingMimeTypeRule(
                mime_type=mime_type
            )
            for mime_type in values[
                "mime_types"
            ]
        ]

        return policy