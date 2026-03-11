# NEXORADOCS: Test suite for backend/app/main.py — covers health check and app configuration
# NEXORADOCS: Uses direct function import to avoid HTTP dependency on test environment
# NEXORADOCS: All tests are synchronous and self-contained

import sys
import os

# Allow importing from backend/app without package installation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from main import app, health


def test_health_returns_ok():
    """NEXORADOCS: Health endpoint must return {'status': 'ok'} to pass load-balancer checks."""
    result = health()
    assert result == {'status': 'ok'}, "Health check must return status ok"


def test_app_has_title():
    """NEXORADOCS: FastAPI app title must be set so API docs are identifiable."""
    assert app.title == 'Nexora Generated API', "App title must match the configured value"


def test_health_route_registered():
    """NEXORADOCS: /health route must be registered so infrastructure probes can reach it."""
    routes = [route.path for route in app.routes]
    assert '/health' in routes, "/health route must be registered on the FastAPI app"
