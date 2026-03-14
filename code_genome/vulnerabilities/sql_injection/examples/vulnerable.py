# EXEMPLO: SQL Injection via concatenação de string
# NÃO use este código em produção

import sqlite3

def get_user_by_name(db_path: str, username: str):
    """VULNERÁVEL: concatena username diretamente na query."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Payload de ataque: username = "' OR '1'='1"
    query = "SELECT * FROM users WHERE username='" + username + "'"
    cursor.execute(query)  # CRÍTICO: executa SQL arbitrário
    return cursor.fetchall()

def get_order(db_path: str, order_id):
    """VULNERÁVEL: f-string com input do usuário."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM orders WHERE id={order_id}")
    return cursor.fetchone()
