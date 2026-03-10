"""
Testes unitários do gene Auth JWT - meta ~70% cobertura.
"""
import os
import sys

# Permite importar code do gene quando rodando testes na pasta auth
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import pytest

# Importa após ajustar path
from auth_logic import (
    hash_password,
    verify_password,
    create_token,
    verify_token,
    DEFAULT_EXP_HOURS,
)


class TestHashPassword:
    def test_hash_returns_hex_string(self):
        out = hash_password("senha123")
        assert isinstance(out, str)
        assert len(out) == 64
        assert all(c in "0123456789abcdef" for c in out)

    def test_same_password_same_hash(self):
        a = hash_password("x")
        b = hash_password("x")
        assert a == b

    def test_different_passwords_different_hash(self):
        a = hash_password("a")
        b = hash_password("b")
        assert a != b

    def test_salt_changes_hash(self):
        h1 = hash_password("x", salt="s1")
        h2 = hash_password("x", salt="s2")
        assert h1 != h2


class TestVerifyPassword:
    def test_correct_password_returns_true(self):
        hashed = hash_password("secret")
        assert verify_password("secret", hashed) is True

    def test_wrong_password_returns_false(self):
        hashed = hash_password("secret")
        assert verify_password("wrong", hashed) is False

    def test_same_salt_required(self):
        hashed = hash_password("x", salt="s1")
        assert verify_password("x", hashed, salt="s1") is True
        assert verify_password("x", hashed, salt="s2") is False


@pytest.mark.skipif(
    __import__("auth_logic").jwt is None,
    reason="PyJWT não instalado",
)
class TestJWT:
    def test_create_token_returns_string(self):
        t = create_token({"sub": "user1"})
        assert isinstance(t, str)
        assert len(t) > 0

    def test_verify_token_returns_payload(self):
        payload = {"sub": "user1", "role": "admin"}
        t = create_token(payload)
        out = verify_token(t)
        assert out["sub"] == "user1"
        assert out["role"] == "admin"
        assert "exp" in out
        assert "iat" in out

    def test_verify_token_wrong_secret_raises(self):
        t = create_token({"sub": "u"}, secret="secret-a")
        with pytest.raises(Exception):
            verify_token(t, secret="secret-b")

    def test_expiration_in_future(self):
        t = create_token({"sub": "u"}, exp_hours=1)
        out = verify_token(t)
        from datetime import datetime, timezone
        assert out["exp"] > datetime.now(timezone.utc).timestamp()

