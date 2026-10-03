from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from fastapi.testclient import TestClient

import main
import security
import tools.setup as tool_setup


def test_signed_session_expires_and_rejects_tampering(monkeypatch):
    monkeypatch.setattr(
        security,
        "settings",
        SimpleNamespace(session_secret="test-secret", session_max_age=60),
    )
    token = security.create_session_token(now=100)

    assert security.valid_session_token(token, now=159)
    assert not security.valid_session_token(token, now=160)
    assert not security.valid_session_token(token + "x", now=120)


def test_cloud_api_requires_login(monkeypatch):
    monkeypatch.setattr(main, "settings", SimpleNamespace(auth_enabled=True))
    monkeypatch.setattr(main, "valid_session_token", lambda token: token == "valid")
    client = TestClient(main.app)

    assert client.get("/api/commands").status_code == 401
    assert client.get("/api/commands", cookies={"raya_session": "valid"}).status_code == 200


def test_login_sets_secure_http_only_cookie(monkeypatch):
    monkeypatch.setattr(
        main,
        "settings",
        SimpleNamespace(
            auth_enabled=True,
            access_password="test-password",
            session_max_age=3600,
            cloud_mode=True,
        ),
    )
    monkeypatch.setattr(main, "create_session_token", lambda: "signed-test-session")
    monkeypatch.setattr(
        main,
        "valid_session_token",
        lambda token: token == "signed-test-session",
    )
    client = TestClient(main.app, base_url="https://testserver")

    response = client.post("/api/auth/login", json={"password": "test-password"})

    assert response.status_code == 200
    assert response.cookies.get("raya_session") == "signed-test-session"
    set_cookie = response.headers["set-cookie"].lower()
    assert "httponly" in set_cookie
    assert "secure" in set_cookie
    assert "samesite=strict" in set_cookie
    assert client.get("/api/commands").status_code == 200


def test_login_throttles_repeated_bad_passwords(monkeypatch):
    monkeypatch.setattr(
        main,
        "settings",
        SimpleNamespace(auth_enabled=True, access_password="correct"),
    )
    client = TestClient(main.app)

    for _ in range(5):
        assert client.post("/api/auth/login", json={"password": "wrong"}).status_code == 401
    response = client.post("/api/auth/login", json={"password": "wrong"})

    assert response.status_code == 429
    assert response.headers["retry-after"]


def test_cloud_registry_omits_local_machine_tools(monkeypatch):
    monkeypatch.setattr(tool_setup, "settings", SimpleNamespace(cloud_mode=True))

    registry = tool_setup.build_registry()

    assert not {
        "open_app",
        "open_url",
        "volume",
        "search_files",
        "create_folder",
        "list_connected_projects",
        "analyze_project",
        "search_project_code",
        "system_status",
    } & set(registry.names())
    assert "web_search" in registry.names()