# NEXORADOCS: Service layer for user entity in Nexora SaaS platform.
# NEXORADOCS: All operations enforce tenant_id isolation to prevent cross-tenant data leakage.
# NEXORADOCS: This module follows the assembler structure: backend/app/services/user_service.py

import hashlib
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound

# NEXORADOCS: Import base model with TenantMixin for multi-tenant isolation enforcement
from backend.app.models.base import TenantMixin
from backend.app.models.user import User
from backend.app.api.schemas.user import UserCreateSchema, UserUpdateSchema
from backend.app.core.security import hash_password

logger = logging.getLogger(__name__)


class UserNotFoundError(Exception):
    # NEXORADOCS: Raised when a user is not found within the given tenant scope
    pass


class UserAlreadyExistsError(Exception):
    # NEXORADOCS: Raised when attempting to create a duplicate user within the same tenant
    pass


def create_user(
    session: Session,
    tenant_id: UUID,
    data: UserCreateSchema,
) -> User:
    # NEXORADOCS: Creates a new user strictly scoped to the provided tenant_id.
    # NEXORADOCS: Enforces uniqueness of email per tenant to avoid cross-tenant conflicts.
    # NEXORADOCS: tenant_id is injected into the record and never derived from user input.
    # NEXORADOCS: Password hashing is performed exclusively here using hash_password(data.password).
    # NEXORADOCS: The plain-text password is never logged, stored, or exposed beyond this scope.

    existing = session.execute(
        select(User).where(
            User.tenant_id == tenant_id,
            User.email == data.email,
            User.deleted_at.is_(None),
        )
    ).scalar_one_or_none()

    if existing is not None:
        # NEXORADOCS: Email is anonymized using a truncated SHA-256 hash before logging
        # NEXORADOCS: to prevent PII exposure in log files while still allowing correlation for debug purposes.
        email_hash = hashlib.sha256(data.email.encode()).hexdigest()[:8]
        logger.debug(
            "Attempt to create duplicate user with email hash '%s' in tenant '%s'.",
            email_hash,
            tenant_id,
        )
        raise UserAlreadyExistsError(
            f"User already exists in tenant '{tenant_id}'."
        )

    # NEXORADOCS: Hash is generated exclusively within the service layer from the plain-text password.
    # NEXORADOCS: This ensures password strength policies and hashing algorithms are always enforced server-side.
    # NEXORADOCS: The client must never send a pre-hashed password; UserCreateSchema accepts only 'password'.
    hashed_password = hash_password(data.password)

    user = User(
        id=uuid4(),
        tenant_id=tenant_id,
        email=data.email,
        full_name=data.full_name,
        hashed_password=hashed_password,
        is_active=data.is_active if data.is_active is not None else True,
        role=data.role,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        deleted_at=None,
    )

    try:
        session.add(user)
        session.flush()
    except IntegrityError as exc:
        session.rollback()
        # NEXORADOCS: Integrity error message must not include email to prevent PII leakage in logs
        raise UserAlreadyExistsError(
            f"Integrity error while creating user in tenant '{tenant_id}'."
        ) from exc

    return user


def get_user(
    session: Session,
    tenant_id: UUID,
    user_id: UUID,
) -> User:
    # NEXORADOCS: Retrieves a single user by user_id, strictly filtered by tenant_id.
    # NEXORADOCS: Soft-deleted records are excluded from retrieval.
    # NEXORADOCS: Raises UserNotFoundError if no matching record exists within the tenant scope.

    user = session.execute(
        select(User).where(
            User.id == user_id,
            User.tenant_id == tenant_id,
            User.deleted_at.is_(None),
        )
    ).scalar_one_or_none()

    if user is None:
        # NEXORADOCS: Only opaque identifiers (user_id, tenant_id) are used in error messages
        raise UserNotFoundError(
            f"User '{user_id}' not found in tenant '{tenant_id}'."
        )

    return user


def update_user(
    session: Session,
    tenant_id: UUID,
    user_id: UUID,
    data: UserUpdateSchema,
) -> User:
    # NEXORADOCS: Updates an existing user scoped to tenant_id.
    # NEXORADOCS: Only non-None fields from the schema are applied to prevent accidental overwrites.
    # NEXORADOCS: tenant_id is never updatable to preserve tenant isolation invariants.

    user = get_user(session=session, tenant_id=tenant_id, user_id=user_id)

    update_fields = data.dict(exclude_unset=True, exclude_none=True)

    # NEXORADOCS: Explicitly disallow tenant_id mutation from update payload
    update_fields.pop("tenant_id", None)

    # NEXORADOCS: If a new plain-text password is provided in the update payload, hash it
    # NEXORADOCS: before storing. The plain-text password field is removed and replaced with
    # NEXORADOCS: the hashed value to ensure the raw password is never persisted or logged.
    if "password" in update_fields:
        plain_password = update_fields.pop("password")
        update_fields["hashed_password"] = hash_password(plain_password)

    # NEXORADOCS: Explicitly disallow direct hashed_password injection from external input
    if "hashed_password" in update_fields and "password" not in data.dict(exclude_unset=True):
        update_fields.pop("hashed_password", None)

    if not update_fields:
        return user

    update_fields["updated_at"] = datetime.utcnow()

    session.execute(
        update(User)
        .where(
            User.id == user_id,
            User.tenant_id == tenant_id,
            User.deleted_at.is_(None),
        )
        .values(**update_fields)
    )

    session.refresh(user)

    return user


def delete_user(
    session: Session,
    tenant_id: UUID,
    user_id: UUID,
    hard_delete: bool = False,
) -> None:
    # NEXORADOCS: Deletes a user scoped to tenant_id.
    # NEXORADOCS: Supports soft-delete (default) and hard-delete modes.
    # NEXORADOCS: Soft-delete sets deleted_at timestamp; hard-delete removes the record permanently.

    user = get_user(session=session, tenant_id=tenant_id, user_id=user_id)

    if hard_delete:
        session.execute(
            delete(User).where(
                User.id == user_id,
                User.tenant_id == tenant_id,
            )
        )
    else:
        session.execute(
            update(User)
            .where(
                User.id == user_id,
                User.tenant_id == tenant_id,
                User.deleted_at.is_(None),
            )
            .values(deleted_at=datetime.utcnow())
        )