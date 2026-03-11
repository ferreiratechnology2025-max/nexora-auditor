# NEXORADOCS: Test module for user entity - covers creation, read, and deletion with real SQLAlchemy session
# NEXORADOCS: Uses sqlite:///:memory: for isolated, ephemeral test database
# NEXORADOCS: Enforces tenant_id in all operations for multi-tenant isolation

import pytest
from sqlalchemy import create_engine, Column, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
import uuid

# NEXORADOCS: In-memory SQLite engine for test isolation
DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# NEXORADOCS: TenantMixin enforces tenant_id presence on every model that requires multi-tenant isolation
class TenantMixin:
    tenant_id = Column(String(36), nullable=False, index=True)


# NEXORADOCS: User model representing the user entity scoped to a tenant
class User(TenantMixin, Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


@pytest.fixture(scope="function")
def db_session():
    # NEXORADOCS: Creates all tables in memory before each test and drops them after for full isolation
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_tenant_id():
    # NEXORADOCS: Provides a consistent tenant_id for test operations
    return str(uuid.uuid4())


def test_create_user(db_session, sample_tenant_id):
    # NEXORADOCS: Business rule - user must always be scoped to a tenant_id
    user = User(
        id=str(uuid.uuid4()),
        tenant_id=sample_tenant_id,
        email="alice@nexora.io",
        full_name="Alice Nexora",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # NEXORADOCS: Assert user was persisted with correct tenant_id and fields
    assert user.id is not None
    assert user.tenant_id == sample_tenant_id
    assert user.email == "alice@nexora.io"
    assert user.full_name == "Alice Nexora"
    assert user.is_active is True


def test_read_user(db_session, sample_tenant_id):
    # NEXORADOCS: Business rule - reads must always filter by tenant_id to prevent cross-tenant data leakage
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        tenant_id=sample_tenant_id,
        email="bob@nexora.io",
        full_name="Bob Nexora",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    # NEXORADOCS: Query enforces tenant_id filter on every data access path
    fetched_user = (
        db_session.query(User)
        .filter(User.id == user_id, User.tenant_id == sample_tenant_id)
        .first()
    )

    assert fetched_user is not None
    assert fetched_user.id == user_id
    assert fetched_user.tenant_id == sample_tenant_id
    assert fetched_user.email == "bob@nexora.io"
    assert fetched_user.full_name == "Bob Nexora"

    # NEXORADOCS: Cross-tenant read must return None — tenant isolation validation
    other_tenant_id = str(uuid.uuid4())
    cross_tenant_result = (
        db_session.query(User)
        .filter(User.id == user_id, User.tenant_id == other_tenant_id)
        .first()
    )
    assert cross_tenant_result is None


def test_delete_user(db_session, sample_tenant_id):
    # NEXORADOCS: Business rule - deletion must be scoped to tenant_id to avoid accidental cross-tenant removal
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        tenant_id=sample_tenant_id,
        email="charlie@nexora.io",
        full_name="Charlie Nexora",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    # NEXORADOCS: Fetch with tenant_id filter before deletion to enforce isolation
    user_to_delete = (
        db_session.query(User)
        .filter(User.id == user_id, User.tenant_id == sample_tenant_id)
        .first()
    )
    assert user_to_delete is not None

    db_session.delete(user_to_delete)
    db_session.commit()

    # NEXORADOCS: Verify the user no longer exists in the tenant scope after deletion
    deleted_user = (
        db_session.query(User)
        .filter(User.id == user_id, User.tenant_id == sample_tenant_id)
        .first()
    )
    assert deleted_user is None

    # NEXORADOCS: Verify total user count in tenant is zero after deletion
    remaining_count = (
        db_session.query(User)
        .filter(User.tenant_id == sample_tenant_id)
        .count()
    )
    assert remaining_count == 0