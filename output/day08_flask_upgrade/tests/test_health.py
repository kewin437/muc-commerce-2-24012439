"""Test /health 端点 —— 确认服务存活，无需登录。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app


def test_health_returns_ok():
    """访问 /health 应返回 200 状态码，body 含 ok:true 和 service 字段。"""
    with app.test_client() as client:
        resp = client.get("/health")
        assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}"

        data = resp.get_json()
        assert data["ok"] is True, f"ok 字段应为 True，实际 {data.get('ok')}"
        assert "service" in data, f"缺少 service 字段，keys={list(data.keys())}"


def test_health_no_login_required():
    """/health 不需要登录即可访问。"""
    with app.test_client() as client:
        resp = client.get("/health")
        assert resp.status_code == 200
