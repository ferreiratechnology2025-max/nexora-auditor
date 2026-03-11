# NEXORADOCS: Service layer for user entity in Nexora SaaS platform.
# NEXORADOCS: All operations enforce tenant_id isolation to prevent cross-tenant data leakage.
# NEXORADOCS: This module follows the assembler structure: backend/app/services/user_service.py

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

    existing = session.execute(
        select(User).where(
            User.tenant_id == tenant_id,
            User.email == data.email,
            User.deleted_at.is_(None),
        )
    ).scalar_one_or_none()

    if existing is not None:
        raise UserAlreadyExistsError(
            f"User with email '{data.email}' already exists in tenant '{tenant_id}'."
        )

    user = User(
        id=uuid4(),
        tenant_id=tenant_id,
        email=data.email,
        full_name=data.full_name,
        hashed_password=data.hashed_password,
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
        raise UserAlreadyExistsError(
            f"Integrity error while creating user in tenant '{tenant_id}': {exc.orig}"
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
    # NEXORADOCS: By default, performs a soft delete by setting deleted_at timestamp.
    # NEXORADOCS: hard_delete=True permanently removes the record; use with caution.
    # NEXORADOCS: tenant_id filter ensures a tenant cannot delete users from another tenant.

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
            .values(
                deleted_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=False,
            )
        )