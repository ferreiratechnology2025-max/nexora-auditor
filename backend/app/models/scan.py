from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum
import uuid
import secrets


class ScanStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String, unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    anonymous_token = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, nullable=False, index=True)
    project_name = Column(String)
    source = Column(String)  # zip | github
    status = Column(Enum(ScanStatus), default=ScanStatus.pending)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    plan_selected = Column(String)  # laudo | correcao
    health_score_initial = Column(Float)
    health_score_final = Column(Float)
    findings_json = Column(JSON)
    report_hash = Column(String, unique=True, index=True)
    preference_id = Column(String)
    payment_id = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)

    user = relationship("User", back_populates="scans")

    def is_owned_by_user(self, user_id: int) -> bool:
        """
        Verifica explicitamente se o scan pertence ao usuário autenticado.
        Scans anônimos (user_id is None) NUNCA são considerados pertencentes
        a qualquer usuário autenticado.
        """
        if self.user_id is None:
            return False
        return self.user_id == user_id

    def is_anonymous(self) -> bool:
        """Retorna True se o scan foi criado sem autenticação."""
        return self.user_id is None

    def is_accessible_by_anonymous_token(self, token: str) -> bool:
        """
        Permite acesso a scans anônimos via token seguro gerado na criação.
        O token deve ter sido fornecido ao cliente no momento da criação do scan.
        """
        if not self.is_anonymous():
            return False
        if not token or not self.anonymous_token:
            return False
        return secrets.compare_digest(self.anonymous_token, token)

    @classmethod
    def generate_anonymous_token(cls) -> str:
        """Gera um token seguro para scans anônimos."""
        return secrets.token_urlsafe(32)

    @classmethod
    def get_by_public_id(cls, db, public_id: str, user_id: int = None, anonymous_token: str = None):
        """
        Busca scan por public_id com verificação explícita de autorização.

        - Se user_id fornecido: retorna apenas scans que pertencem ao usuário (user_id NOT NULL).
        - Se anonymous_token fornecido: retorna apenas scans anônimos com token válido.
        - Se nenhum fornecido: retorna None (acesso negado).

        Nunca retorna scans anônimos para usuários autenticados nem vice-versa.
        """
        if user_id is None and anonymous_token is None:
            return None

        query = db.query(cls).filter(cls.public_id == public_id)

        if user_id is not None:
            # Usuário autenticado: restringe a scans com user_id definido e igual
            query = query.filter(
                cls.user_id.isnot(None),
                cls.user_id == user_id
            )
            return query.first()

        if anonymous_token is not None:
            # Acesso anônimo: restringe a scans sem user_id e com token correspondente
            scan = query.filter(cls.user_id.is_(None)).first()
            if scan and scan.is_accessible_by_anonymous_token(anonymous_token):
                return scan
            return None

        return None

    @classmethod
    def get_by_report_hash(cls, db, report_hash: str, user_id: int = None, anonymous_token: str = None):
        """
        Busca scan por report_hash com verificação explícita de autorização.

        Mesma lógica de get_by_public_id: nunca mistura acesso autenticado e anônimo.
        """
        if user_id is None and anonymous_token is None:
            return None

        query = db.query(cls).filter(cls.report_hash == report_hash)

        if user_id is not None:
            query = query.filter(
                cls.user_id.isnot(None),
                cls.user_id == user_id
            )
            return query.first()

        if anonymous_token is not None:
            scan = query.filter(cls.user_id.is_(None)).first()
            if scan and scan.is_accessible_by_anonymous_token(anonymous_token):
                return scan
            return None

        return None

    @classmethod
    def get_user_scans(cls, db, user_id: int):
        """
        Retorna apenas scans autenticados do usuário.
        Scans anônimos (user_id IS NULL) são explicitamente excluídos.
        """
        if user_id is None:
            return []
        return db.query(cls).filter(
            cls.user_id.isnot(None),
            cls.user_id == user_id
        ).all()