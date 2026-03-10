import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

jose = pytest.importorskip('jose')
passlib = pytest.importorskip('passlib')

from auth_handler import AuthError, decode_access_token, hash_password, login_user


SECRET_KEY = 'super-secret-for-tests'


def _build_user(username: str = 'alice'):
    return {
        'username': username,
        'password_hash': hash_password('123456'),
        'role': 'admin',
    }


def test_login_success_returns_valid_jwt_payload():
    user = _build_user()

    token = login_user(user_record=user, password='123456', secret_key=SECRET_KEY)
    payload = decode_access_token(token, SECRET_KEY)

    assert payload['sub'] == 'alice'
    assert payload['role'] == 'admin'
    assert 'exp' in payload


def test_login_with_wrong_password_raises_auth_error():
    user = _build_user('bob')

    with pytest.raises(AuthError):
        login_user(user_record=user, password='wrong-password', secret_key=SECRET_KEY)
