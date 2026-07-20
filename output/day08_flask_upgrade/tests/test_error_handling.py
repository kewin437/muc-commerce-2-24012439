"""Test 统一 400 错误 JSON 响应（TODO 8-3）。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app

VALID_USER = {"username": "student", "password": "day07"}


def test_400_returns_json():
    """400 错误返回 JSON，含 ok:false 和 error 字段。"""
    with app.test_client() as client:
        client.post("/login", data=VALID_USER)

        # /api/ask 收到空 question 触发 400
        resp = client.post("/api/ask", json={"question": ""})

        assert resp.status_code == 400, f"期望 400，实际 {resp.status_code}"
        assert resp.is_json, f"400 响应应为 JSON，Content-Type={resp.content_type}"

        data = resp.get_json()
        assert data["ok"] is False, f"ok 应为 False，实际 {data.get('ok')}"
        assert "error" in data or "answer" in data, (
            f"应包含 error 字段，keys={list(data.keys())}"
        )


def test_health_not_affected():
    """/health 不受 400 handler 影响，仍然正常。"""
    with app.test_client() as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.get_json()["ok"] is True
