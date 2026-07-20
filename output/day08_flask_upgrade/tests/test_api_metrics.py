"""Test /api/metrics 接口 —— 认证拦截 + 数据返回。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app

VALID_USER = {"username": "student", "password": "day07"}


def test_metrics_requires_login():
    """未登录直接访问 /api/metrics 应被重定向到登录页（302）。"""
    with app.test_client() as client:
        resp = client.get("/api/metrics")
        assert resp.status_code == 302, (
            f"未登录应返回 302 重定向，实际 {resp.status_code}"
        )
        assert "/login" in resp.headers["Location"], (
            f"重定向目标应为 /login，实际 {resp.headers.get('Location')}"
        )


def test_metrics_returns_data():
    """登录后访问 /api/metrics 返回 200，数据含 4 张指标卡。"""
    with app.test_client() as client:
        client.post("/login", data=VALID_USER)
        resp = client.get("/api/metrics")
        assert resp.status_code == 200

        data = resp.get_json()
        assert data["ok"] is True
        assert "metrics" in data

        metrics = data["metrics"]
        assert isinstance(metrics, list), f"metrics 应为 list，实际 {type(metrics)}"
        assert len(metrics) == 4, f"期望 4 条指标，实际 {len(metrics)}"

        for item in metrics:
            assert "label" in item, f"指标缺少 label: {item}"
            assert "value" in item, f"指标缺少 value: {item}"
            assert "note" in item, f"指标缺少 note: {item}"
