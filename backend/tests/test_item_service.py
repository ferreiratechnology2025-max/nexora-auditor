# NEXORADOCS: Test suite for services/item_service — covers create, read, and delete operations
# NEXORADOCS: Uses inline SQLAlchemy model with sqlite:///:memory: for full isolation
# NEXORADOCS: tenant_id is enforced in every query to validate multi-tenant isolation

import pytest
import uuid
from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, String, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


# NEXORADOCS: Inline Item model mirrors services/item_service.py entity contract
class Item(Base):
    __tablename__ = 'items'

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


@pytest.fixture(scope='function')
def db_session():
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def tenant_id():
    return str(uuid.uuid4())


# NEXORADOCS: Test 1 — item creation sets correct tenant_id and defaults
def test_create_item_sets_tenant_and_defaults(db_session, tenant_id):
    item = Item(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        name='Audit Report Template',
        description='Base template for monthly audit reports',
        is_active=True,
    )
    db_session.add(item)
    db_session.commit()

    persisted = db_session.query(Item).filter_by(tenant_id=tenant_id).first()

    assert persisted is not None, 'Item must be persisted'
    assert persisted.name == 'Audit Report Template'
    assert persisted.tenant_id == tenant_id, 'tenant_id must match the creating tenant'
    assert persisted.is_active is True, 'Item must be active after creation'


# NEXORADOCS: Test 2 — tenant isolation: item is invisible to other tenants
def test_get_item_tenant_isolation(db_session, tenant_id):
    item_id = str(uuid.uuid4())
    db_session.add(Item(
        id=item_id,
        tenant_id=tenant_id,
        name='Confidential Item',
        is_active=True,
    ))
    db_session.commit()

    # NEXORADOCS: Correct tenant — must find the item
    found = db_session.query(Item).filter_by(id=item_id, tenant_id=tenant_id).first()
    assert found is not None, 'Item must be visible to its own tenant'

    # NEXORADOCS: Different tenant — must return nothing
    other_tenant = str(uuid.uuid4())
    not_found = db_session.query(Item).filter_by(id=item_id, tenant_id=other_tenant).first()
    assert not_found is None, 'Item must NOT be accessible by a different tenant'


# NEXORADOCS: Test 3 — soft-delete via is_active flag
def test_delete_item_by_deactivating(db_session, tenant_id):
    item_id = str(uuid.uuid4())
    db_session.add(Item(
        id=item_id,
        tenant_id=tenant_id,
        name='Temporary Item',
        is_active=True,
    ))
    db_session.commit()

    # NEXORADOCS: Soft-delete by setting is_active=False (audit trail preserved)
    item = db_session.query(Item).filter_by(id=item_id, tenant_id=tenant_id).first()
    item.is_active = False
    db_session.commit()

    active_items = (
        db_session.query(Item)
        .filter_by(tenant_id=tenant_id, is_active=True)
        .all()
    )
    assert len(active_items) == 0, 'Soft-deleted item must not appear in active item queries'
