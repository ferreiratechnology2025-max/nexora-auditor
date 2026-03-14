# CORREÇÃO: SQL Injection — uso de parametrização
import sqlite3
from sqlalchemy import select, text
from sqlalchemy.orm import Session

def get_user_by_name_safe(db_path: str, username: str):
    """SEGURO: usa placeholders parametrizados."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchall()

def get_order_safe(session: Session, order_id: int):
    """SEGURO: SQLAlchemy com tipagem e ORM."""
    # ORM — sem SQL raw
    from app.models import Order
    return session.get(Order, int(order_id))  # cast explícito para int

def get_order_raw_safe(session: Session, order_id: int):
    """SEGURO: SQL raw com parametrização explícita."""
    result = session.execute(
        text("SELECT * FROM orders WHERE id = :id"),
        {"id": int(order_id)},
    )
    return result.fetchone()
