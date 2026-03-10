from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import declarative_mixin

@declarative_mixin
class TenantMixin:
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False, index=True)
