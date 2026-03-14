# NEXORADOCS: Service layer for 'item' entity in Nexora SaaS multi-tenant architecture.
# NEXORADOCS: All functions enforce tenant_id isolation on every DB access path.
# NEXORADOCS: Pure Python functions — no class state — designed for dependency injection via FastAPI.

import json
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.item import Item
from backend.app.models.mixins import TenantMixin  # NEXORADOCS: Provides tenant_id scoping


# NEXORADOCS: Raised when an item is not found within the given tenant scope.
class ItemNotFoundError(Exception):
    """Raised when no item matches the given id + tenant_id combination."""
    pass


# NEXORADOCS: Raised on invalid or missing payload data.
class ItemValidationError(Exception):
    """Raised when required item fields are missing or invalid."""
    pass


# NEXORADOCS: Maximum allowed serialized size of metadata in characters.
_METADATA_MAX_SIZE = 10_000

# NEXORADOCS: Maximum number of keys allowed at the top level of metadata.
_METADATA_MAX_KEYS = 50

# NEXORADOCS: Maximum depth for nested metadata structures.
_METADATA_MAX_DEPTH = 3

# NEXORADOCS: Allowed value types for metadata fields.
_METADATA_ALLOWED_VALUE_TYPES = (str, int, float, bool, type(None))

# NEXORADOCS: Maximum length for individual string values inside metadata.
_METADATA_MAX_STRING_VALUE_LENGTH = 1_000

# NEXORADOCS: Maximum length for individual metadata keys.
_METADATA_MAX_KEY_LENGTH = 128

# NEXORADOCS: Sensitive keys that must never appear in metadata to prevent injection.
_METADATA_FORBIDDEN_KEYS = frozenset({
    "tenant_id", "id", "is_active", "created_at", "updated_at",
    "password", "secret", "token", "api_key", "auth", "role", "permissions",
})


def _validate_metadata(metadata: Optional[dict]) -> dict:
    # NEXORADOCS: Central metadata validation — enforces size, structure, depth, and key allowlist.
    if metadata is None:
        return {}

    if not isinstance(metadata, dict):
        raise ItemValidationError("Field 'metadata' must be a dictionary.")

    # NEXORADOCS: Serialize to JSON to measure total payload size and detect non-serializable types.
    try:
        serialized = json.dumps(metadata, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ItemValidationError(
            f"Field 'metadata' contains non-serializable or invalid values: {exc}"
        )

    if len(serialized) > _METADATA_MAX_SIZE:
        raise ItemValidationError(
            f"Field 'metadata' exceeds maximum allowed size of {_METADATA_MAX_SIZE} characters."
        )

    _validate_metadata_structure(metadata, depth=0)

    return metadata


def _validate_metadata_structure(obj: Any, depth: int) -> None:
    # NEXORADOCS: Recursively validates metadata structure, depth, key constraints, and value types.
    if depth > _METADATA_MAX_DEPTH:
        raise ItemValidationError(
            f"Field 'metadata' exceeds maximum nesting depth of {_METADATA_MAX_DEPTH}."
        )

    if isinstance(obj, dict):
        if len(obj) > _METADATA_MAX_KEYS:
            raise ItemValidationError(
                f"Field 'metadata' dict at depth {depth} exceeds maximum of {_METADATA_MAX_KEYS} keys."
            )
        for key, value in obj.items():
            if not isinstance(key, str):
                raise ItemValidationError(
                    "Field 'metadata' keys must be strings."
                )
            if len(key) > _METADATA_MAX_KEY_LENGTH:
                raise ItemValidationError(
                    f"Field 'metadata' key '{key[:50]}...' exceeds maximum key length of {_METADATA_MAX_KEY_LENGTH}."
                )
            key_lower = key.lower().strip()
            if key_lower in _METADATA_FORBIDDEN_KEYS:
                raise ItemValidationError(
                    f"Field 'metadata' contains forbidden key '{key}'."
                )
            _validate_metadata_structure(value, depth=depth + 1)

    elif isinstance(obj, list):
        if len(obj) > _METADATA_MAX_KEYS:
            raise ItemValidationError(
                f"Field 'metadata' list at depth {depth} exceeds maximum of {_METADATA_MAX_KEYS} items."
            )
        for item in obj:
            _validate_metadata_structure(item, depth=depth + 1)

    else:
        if not isinstance(obj, _METADATA_ALLOWED_VALUE_TYPES):
            raise ItemValidationError(
                f"Field 'metadata' contains a value of disallowed type '{type(obj).__name__}'. "
                f"Allowed types: str, int, float, bool, null."
            )
        if isinstance(obj, str) and len(obj) > _METADATA_MAX_STRING_VALUE_LENGTH:
            raise ItemValidationError(
                f"Field 'metadata' contains a string value exceeding maximum length of "
                f"{_METADATA_MAX_STRING_VALUE_LENGTH} characters."
            )


def create_item(
    session: Session,
    tenant_id: UUID,
    name: str,
    description: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Item:
    # NEXORADOCS: Creates a new item scoped strictly to tenant_id.
    # NEXORADOCS: Business rule — name is mandatory; description and metadata are optional.
    # NEXORADOCS: metadata is validated against schema, size, and forbidden keys before use.
    if not name or not name.strip():
        raise ItemValidationError("Field 'name' is required and cannot be blank.")

    validated_metadata = _validate_metadata(metadata)

    item = Item(
        id=uuid4(),
        tenant_id=tenant_id,           # NEXORADOCS: Tenant isolation enforced at creation.
        name=name.strip(),
        description=description.strip() if description else None,
        metadata=validated_metadata,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_active=True,
    )

    session.add(item)
    session.flush()  # NEXORADOCS: Flush to get DB-generated values without committing the outer transaction.
    return item


def get_item(
    session: Session,
    tenant_id: UUID,
    item_id: UUID,
) -> Item:
    # NEXORADOCS: Retrieves a single item by id, always filtered by tenant_id.
    # NEXORADOCS: Business rule — cross-tenant access is structurally impossible here.
    stmt = (
        select(Item)
        .where(Item.id == item_id)
        .where(Item.tenant_id == tenant_id)   # NEXORADOCS: Hard tenant gate.
        .where(Item.is_active == True)        # NEXORADOCS: Soft-deleted items are invisible.
    )
    result = session.execute(stmt).scalar_one_or_none()

    if result is None:
        raise ItemNotFoundError(
            f"Item '{item_id}' not found for tenant '{tenant_id}'."
        )

    return result


def update_item(
    session: Session,
    tenant_id: UUID,
    item_id: UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Item:
    # NEXORADOCS: Updates mutable fields of an existing item within the tenant scope.
    # NEXORADOCS: Business rule — at least one updatable field must be provided.
    # NEXORADOCS: Business rule — tenant_id is immutable and never updated.
    # NEXORADOCS: metadata is validated against schema, size, and forbidden keys before use.
    if name is None and description is None and metadata is None:
        raise ItemValidationError(
            "At least one of 'name', 'description', or 'metadata' must be provided for update."
        )

    item = get_item(session=session, tenant_id=tenant_id, item_id=item_id)
    # NEXORADOCS: get_item already enforces tenant_id + active check; no duplicate filter needed.

    if name is not None:
        if not name.strip():
            raise ItemValidationError("Field 'name' cannot be set to blank.")
        item.name = name.strip()

    if description is not None:
        item.description = description.strip()

    if metadata is not None:
        # NEXORADOCS: Validate metadata before replacing — caller supplies full dict to replace existing.
        validated_metadata = _validate_metadata(metadata)
        item.metadata = validated_metadata

    item.updated_at = datetime.now(timezone.utc)

    session.flush()  # NEXORADOCS: Persist changes within the current unit of work.
    return item


def delete_item(
    session: Session,
    tenant_id: UUID,
    item_id: UUID,
    hard_delete: bool = False,
) -> None:
    # NEXORADOCS: Deletes an item within the tenant scope.
    # NEXORADOCS: Business rule — default is soft-delete (is_active=False) for audit trail.
    # NEXORADOCS: Business rule — hard_delete=True performs physical row removal; use with caution.
    item = get_item(session=session, tenant_id=tenant_id, item_id=item_id)
    # NEXORADOCS: get_item guarantees tenant_id match before any destructive operation.

    if hard_delete:
        session.delete(item)
    else:
        item.is_active = False
        item.updated_at = datetime.now(timezone.utc)

    session.flush()  # NEXORADOCS: Finalise within unit of work; caller controls commit.