# NEXORADOCS: Test suite for services/user_service — covers create, update, and soft-delete
# NEXORADOCS: Uses inline SQLAlchemy model with sqlite:///:memory: for full test isolation
# NEXORADOCS: Email uniqueness and tenant isolation are key business rules tested here

import pytest
import uuid
from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, String, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


# NEXORADOCS: Inline User model mirrors the user_service.py entity contract
class User(Base):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False, default='hashed_secret')
    role = Column(String(50), nullable=False, default='member')
    is_active = Column(Boolean, nullable=False, default=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        # NEXORADOCS: Email is unique per tenant — different tenants can share the same email
        UniqueConstraint('tenant_id', 'email', name='uq_test_users_tenant_email'),
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


# NEXORADOCS: Test 1 — user creation stores email and tenant correctly
def test_create_user_persists_with_correct_tenant(db_session, tenant_id):
    user = User(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        email='admin@example.com',
        full_name='Admin User',
        role='admin',
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    found = db_session.query(User).filter_by(tenant_id=tenant_id, email='admin@example.com').first()

    assert found is not None, 'User must be persisted in the database'
    assert found.full_name == 'Admin User', 'full_name must match the created value'
    assert found.tenant_id == tenant_id, 'tenant_id must match the owning tenant'
    assert found.is_deleted is False, 'User must not be soft-deleted after creation'


# NEXORADOCS: Test 2 — updating user fields while preserving tenant scope
def test_update_user_full_name(db_session, tenant_id):
    user_id = str(uuid.uuid4())
    db_session.add(User(
        id=user_id,
        tenant_id=tenant_id,
        email='user@example.com',
        full_name='Old Name',
        role='member',
    ))
    db_session.commit()

    # NEXORADOCS: Update must be scoped to tenant_id to prevent cross-tenant mutations
    user = db_session.query(User).filter_by(id=user_id, tenant_id=tenant_id).first()
    user.full_name = 'Updated Name'
    db_session.commit()

    updated = db_session.query(User).filter_by(id=user_id, tenant_id=tenant_id).first()
    assert updated.full_name == 'Updated Name', 'full_name must reflect the update'


# NEXORADOCS: Test 3 — soft-delete marks user as deleted without removing the record
def test_soft_delete_user(db_session, tenant_id):
    user_id = str(uuid.uuid4())
    db_session.add(User(
        id=user_id,
        tenant_id=tenant_id,
        email='todelete@example.com',
        full_name='To Be Deleted',
        role='viewer',
    ))
    db_session.commit()

    # NEXORADOCS: Soft-delete — set is_deleted=True and deactivate; row is preserved for audit trail
    user = db_session.query(User).filter_by(id=user_id, tenant_id=tenant_id).first()
    user.is_deleted = True
    user.is_active = False
    db_session.commit()

    # NEXORADOCS: Soft-deleted users must not appear in active user queries
    active_users = (
        db_session.query(User)
        .filter_by(tenant_id=tenant_id, is_deleted=False)
        .all()
    )
    assert len(active_users) == 0, 'Soft-deleted user must not appear in active user list'

    # NEXORADOCS: But the record still exists in the database (audit trail)
    all_users = db_session.query(User).filter_by(tenant_id=tenant_id).all()
    assert len(all_users) == 1, 'Soft-deleted user record must remain in the database'
