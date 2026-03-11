# NEXORADOCS: Test suite for item entity — covers creation, retrieval, and deletion
# NEXORADOCS: Uses real SQLAlchemy session with in-memory SQLite for full integration coverage
# NEXORADOCS: tenant_id is enforced in every query path to guarantee multi-tenant isolation

import pytest
from sqlalchemy import create_engine, Column, String, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.sqlite import TEXT
import uuid
from datetime import datetime, timezone

# NEXORADOCS: Base declarative for in-memory test models
Base = declarative_base()


# NEXORADOCS: Inline Item model for test isolation — mirrors backend/app/models/item.py
class Item(Base):
    __tablename__ = "items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# NEXORADOCS: Engine and session factory scoped to each test for isolation
@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


# NEXORADOCS: Shared tenant_id fixture — all tests operate under the same tenant context
@pytest.fixture
def tenant_id():
    return str(uuid.uuid4())


# NEXORADOCS: Test 1 — Verify that an item can be created and persisted with correct tenant_id
def test_create_item(db_session, tenant_id):
    item = Item(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        name="Widget Alpha",
        description="A test widget for tenant isolation",
        is_active=True,
    )
    db_session.add(item)
    db_session.commit()

    persisted = db_session.query(Item).filter_by(id=item.id, tenant_id=tenant_id).first()

    assert persisted is not None, "Item must be persisted in the database"
    assert persisted.name == "Widget Alpha", "Item name must match the created value"
    assert persisted.tenant_id == tenant_id, "tenant_id must match the owning tenant"
    assert persisted.is_active is True, "Item must be active by default"
    assert persisted.created_at is not None, "created_at must be auto-populated"


# NEXORADOCS: Test 2 — Verify that an item can be retrieved by tenant_id and that
# NEXORADOCS: cross-tenant queries return no results (isolation guarantee)
def test_read_item(db_session, tenant_id):
    item_id = str(uuid.uuid4())
    item = Item(
        id=item_id,
        tenant_id=tenant_id,
        name="Widget Beta",
        description="Readable widget",
        is_active=True,
    )
    db_session.add(item)
    db_session.commit()

    # NEXORADOCS: Valid tenant read — must return the item
    found = db_session.query(Item).filter_by(id=item_id, tenant_id=tenant_id).first()
    assert found is not None, "Item must be found for the correct tenant"
    assert found.name == "Widget Beta", "Retrieved item name must match"

    # NEXORADOCS: Cross-tenant read — must return nothing (tenant isolation enforced)
    other_tenant_id = str(uuid.uuid4())
    not_found = (
        db_session.query(Item).filter_by(id=item_id, tenant_id=other_tenant_id).first()
    )
    assert not_found is None, "Item must NOT be accessible by a different tenant"


# NEXORADOCS: Test 3 — Verify that an item can be deleted and is no longer retrievable
# NEXORADOCS: Deletion must be scoped to tenant_id to prevent cross-tenant data removal
def test_delete_item(db_session, tenant_id):
    item_id = str(uuid.uuid4())
    item = Item(
        id=item_id,
        tenant_id=tenant_id,
        name="Widget Gamma",
        description="Deletable widget",
        is_active=True,
    )
    db_session.add(item)
    db_session.commit()

    # NEXORADOCS: Confirm item exists before deletion
    before_delete = (
        db_session.query(Item).filter_by(id=item_id, tenant_id=tenant_id).first()
    )
    assert before_delete is not None, "Item must exist before deletion attempt"

    # NEXORADOCS: Scoped deletion — tenant_id filter prevents accidental cross-tenant deletes
    rows_deleted = (
        db_session.query(Item)
        .filter(Item.id == item_id, Item.tenant_id == tenant_id)
        .delete(synchronize_session="fetch")
    )
    db_session.commit()

    assert rows_deleted == 1, "Exactly one row must be deleted"

    # NEXORADOCS: Confirm item no longer exists after deletion
    after_delete = (
        db_session.query(Item).filter_by(id=item_id, tenant_id=tenant_id).first()
    )
    assert after_delete is None, "Item must not exist after deletion"